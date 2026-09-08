"""Distance-bin DiD on observed working-day MADT (ΔQ).

This is the causal volume step, not the contribution. It does not estimate
VKT, LTR, NR, NVTR, or a mobility-footprint radius.

Identification (locked):
  Sample A = Eixos Verds phase 1 (works 16 Aug 2022 – spring 2023)
  Pre  = 2018–2019
  Drop = 2020–2021 (COVID) and Aug 2022–May 2023 (works); 2023 unused
  Post = 2024–2025
  Exposure = undirected network distance to phase-1 axes
  Outcome = monthly Laborable IMD (Codi_tipus_dia = 2)

2022 H1 is an event-study marker only (tactical regime still in place,
permanent works not yet started). It is not in the main DiD.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.stats import norm as gaussian, t as student_t

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "02_counter_audit" / "raw"
EXPOSURE = ROOT / "04_geometry" / "working" / "station_network_distance_to_phase1.csv"
OUT = ROOT / "05_did_delta_q" / "working"
FIG = ROOT / "05_did_delta_q" / "figures"

PRE_YEARS = {2018, 2019}
POST_YEARS = {2024, 2025}
MIN_MONTHS = 6

BIN_ORDER = [
    "on_or_immediate",
    "0_250m",
    "250_500m",
    "500_1000m",
    "1_2km",
    "control_gt2km",
]
BIN_LABEL = {
    "on_or_immediate": "on / immediate (<=40 m)",
    "0_250m": "0-250 m",
    "250_500m": "250-500 m",
    "500_1000m": "500 m-1 km",
    "1_2km": "1-2 km",
    "control_gt2km": ">2 km (control)",
}

# 2020 tactical counted streets that are NOT the 2022 green axes.
# These are confounders for 2018–19 vs 2024–25, not the study sample.
TAC2020_OTHER = {
    "ARAGO",
    "VALENCIA",
    "GRAN VIA",
    "PAU CLARIS",
    "ROGER DE LLURIA",
    "PELAI",
    "INDUSTRIA",
    "RONDA UNIVERSITAT",
    "RONDA DE LA UNIVERSITAT",
    "PLACA UNIVERSITAT",
    "CASTILLEJOS",
}
PHASE1_AXIS = {"CONSELL DE CENT", "GIRONA", "ROCAFORT", "COMTE BORRELL", "BORRELL"}


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def norm(s: str) -> str:
    s = strip_accents(str(s)).upper()
    s = s.replace("'", " ").replace("’", " ").replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def counted_street(desc: str) -> str:
    return norm(str(desc).split(" - ")[0])


def street_group(desc: str) -> str:
    street = counted_street(desc)
    if street in PHASE1_AXIS or street in {"GIRONA", "C GIRONA"}:
        return "phase1_axis"
    if street in TAC2020_OTHER or street.startswith("GRAN VIA"):
        return "tac2020_other"
    return "other"


def control_bin(network_bin: str) -> str:
    if network_bin in {"gt_2km_control", "outside_graph_control"}:
        return "control_gt2km"
    return network_bin


def ols_hc1(y: np.ndarray, x: np.ndarray):
    n, k = x.shape
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    e = y - x @ beta
    xtx_inv = np.linalg.inv(x.T @ x)
    meat = x.T @ (e[:, None] ** 2 * x)
    vcov = xtx_inv @ meat @ xtx_inv * (n / (n - k))
    se = np.sqrt(np.clip(np.diag(vcov), 0, None))
    return beta, se


def ols_conley(y: np.ndarray, x: np.ndarray, xy: np.ndarray, cutoff_m: float):
    """Bartlett kernel spatial HAC (Conley 1999) on collapsed station residuals."""
    n, k = x.shape
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    e = y - x @ beta
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(axis=2))
    w = np.clip(1.0 - d / cutoff_m, 0.0, None)
    xe = x * e[:, None]
    meat = xe.T @ w @ xe
    xtx_inv = np.linalg.inv(x.T @ x)
    vcov = xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.clip(np.diag(vcov), 0, None))
    return beta, se


def ols_cluster(y: np.ndarray, x: np.ndarray, groups: np.ndarray):
    n, k = x.shape
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    e = y - x @ beta
    meat = np.zeros((k, k))
    g_ids = pd.unique(groups)
    for g in g_ids:
        idx = groups == g
        score = x[idx].T @ e[idx]
        meat += np.outer(score, score)
    g = len(g_ids)
    meat *= (g / max(g - 1, 1)) * ((n - 1) / max(n - k, 1))
    xtx_inv = np.linalg.inv(x.T @ x)
    vcov = xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.clip(np.diag(vcov), 0, None))
    return beta, se


def load_laborable(years: list[int]) -> pd.DataFrame:
    frames = []
    for y in years:
        path = RAW / f"{y}_aforament_detall_valor.csv"
        df = pd.read_csv(path, encoding="utf-8-sig")
        df["year"] = pd.to_numeric(df["Any"], errors="coerce")
        df["month"] = pd.to_numeric(df["Mes"], errors="coerce")
        df["day_code"] = pd.to_numeric(df["Codi_tipus_dia"], errors="coerce")
        df["q"] = pd.to_numeric(df["Valor_IMD"], errors="coerce")
        df["station_id"] = df["Id_aforament"].astype(str).str.strip()
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out = out.loc[
        (out["day_code"] == 2)
        & (out["q"] > 0)
        & (out["q"] < 200_000)
        & out["year"].notna()
        & out["month"].notna()
    ].copy()
    return out[["station_id", "year", "month", "q"]]


def collapse_stations(
    exp: pd.DataFrame,
    pre: pd.DataFrame,
    post: pd.DataFrame,
    min_pre: int,
    min_post: int,
) -> pd.DataFrame:
    pre_g = pre.groupby("station_id").agg(q_pre=("q", "mean"), n_pre=("q", "size"))
    post_g = post.groupby("station_id").agg(q_post=("q", "mean"), n_post=("q", "size"))
    st = (
        exp.set_index("station_id")
        .join(pre_g, how="inner")
        .join(post_g, how="inner")
        .reset_index()
    )
    st = st.loc[(st["n_pre"] >= min_pre) & (st["n_post"] >= min_post)].copy()
    st["delta_q"] = st["q_post"] - st["q_pre"]
    st["delta_log_q"] = np.log(st["q_post"]) - np.log(st["q_pre"])
    return st


def collapsed_did(stations: pd.DataFrame, treated_bins: list[str]) -> pd.DataFrame:
    y = stations["delta_q"].to_numpy(float)
    ylog = stations["delta_log_q"].to_numpy(float)
    x = np.column_stack(
        [np.ones(len(stations))]
        + [stations["did_bin"].eq(b).astype(float).to_numpy() for b in treated_bins]
    )
    beta, se = ols_hc1(y, x)
    blog, selog = ols_hc1(ylog, x)
    rows = []
    for i, b in enumerate(["control_gt2km", *treated_bins]):
        sub = stations.loc[stations["did_bin"] == b]
        did = 0.0 if i == 0 else float(beta[i])
        dlog = 0.0 if i == 0 else float(blog[i])
        pre_mean = float(sub["q_pre"].mean()) if len(sub) else np.nan
        rows.append(
            {
                "bin": b,
                "label": BIN_LABEL[b],
                "n_stations": int(len(sub)),
                "q_pre_mean": round(pre_mean, 1),
                "q_post_mean": round(float(sub["q_post"].mean()), 1),
                "delta_q_mean": round(float(sub["delta_q"].mean()), 1),
                "did_q_vs_control": round(did, 1),
                "did_q_se": round(float(se[i]), 1),
                "did_log_vs_control": round(dlog, 4),
                "did_log_se": round(float(selog[i]), 4),
                "did_over_pre_pct": (
                    0.0
                    if i == 0
                    else (round(100.0 * did / pre_mean, 2) if pre_mean else np.nan)
                ),
            }
        )
    return pd.DataFrame(rows)


def year_means(panel: pd.DataFrame, stations: pd.DataFrame) -> pd.DataFrame:
    keep = set(stations["station_id"])
    use = panel.loc[panel["station_id"].isin(keep)].copy()
    g = (
        use.groupby(["did_bin", "year", "station_id"], as_index=False)["q"]
        .mean()
        .groupby(["did_bin", "year"], as_index=False)
        .agg(n=("q", "size"), q_mean=("q", "mean"), q_median=("q", "median"))
    )
    return g


def event_did(panel: pd.DataFrame, stations: pd.DataFrame) -> pd.DataFrame:
    """Station-year mean Q minus 2019, DiD vs control. 2022 = Jan–Jul only."""
    keep = set(stations["station_id"])
    p = panel.loc[panel["station_id"].isin(keep)].copy()
    p["period"] = np.where(
        (p["year"] == 2022) & (p["month"] <= 7),
        "2022_h1",
        p["year"].astype(int).astype(str),
    )
    p = p.loc[p["period"].isin(["2018", "2019", "2022_h1", "2024", "2025"])]
    sy = p.groupby(["station_id", "did_bin", "period"], as_index=False)["q"].mean()
    ref = sy.loc[sy["period"] == "2019", ["station_id", "q"]].rename(
        columns={"q": "q_2019"}
    )
    sy = sy.merge(ref, on="station_id", how="inner")
    sy["delta_vs_2019"] = sy["q"] - sy["q_2019"]
    treated = [b for b in BIN_ORDER if b != "control_gt2km"]
    rows = []
    for period in ["2018", "2022_h1", "2024", "2025"]:
        sub = sy.loc[sy["period"] == period].copy()
        # keep stations in every bin that have this period
        y = sub["delta_vs_2019"].to_numpy(float)
        x_cols = [sub["did_bin"].eq(b).astype(float).to_numpy() for b in treated]
        x = np.column_stack([np.ones(len(sub)), *x_cols])
        beta, se = ols_hc1(y, x)
        for i, b in enumerate(["control_gt2km", *treated]):
            n = int((sub["did_bin"] == b).sum())
            rows.append(
                {
                    "period": period,
                    "bin": b,
                    "label": BIN_LABEL[b],
                    "n": n,
                    "did_vs_control": 0.0 if i == 0 else round(float(beta[i]), 1),
                    "se": round(float(se[i]), 1),
                    "control_delta_vs_2019": round(float(beta[0]), 1),
                }
            )
    return pd.DataFrame(rows)


def plot_decay(did: pd.DataFrame, path: Path, title: str) -> None:
    plot = did.loc[did["bin"] != "control_gt2km"].copy()
    plot["_ord"] = plot["bin"].map({b: i for i, b in enumerate(BIN_ORDER)})
    plot = plot.sort_values("_ord")
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    x = np.arange(len(plot))
    ax.axhline(0, color="#333", lw=0.8)
    ax.bar(
        x,
        plot["did_q_vs_control"],
        yerr=plot["did_q_se"],
        color="#3d5a80",
        ecolor="#1d3557",
        capsize=4,
        width=0.65,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(plot["label"], rotation=20, ha="right")
    ax.set_ylabel("ΔQ vs >2 km control (vehicles / working day)")
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_event_raw(ym: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    year_x = {2018: -1, 2019: 0, 2022: 0.7, 2024: 1.5, 2025: 2.2}
    ax.axhline(0, color="#333", lw=0.8)
    ax.axvline(0.35, color="#999", lw=0.8, ls="--")
    for b in BIN_ORDER:
        sub = ym.loc[ym["did_bin"] == b].copy()
        if sub.empty:
            continue
        ref = sub.loc[sub["year"] == 2019, "q_mean"]
        if ref.empty:
            continue
        q0 = float(ref.iloc[0])
        sub = sub.sort_values("year")
        xs = [year_x[int(y)] for y in sub["year"]]
        ys = [float(q) - q0 for q in sub["q_mean"]]
        ax.plot(xs, ys, marker="o", label=BIN_LABEL[b], lw=1.4)
    ax.set_xticks([-1, 0, 0.7, 1.5, 2.2])
    ax.set_xticklabels(["2018", "2019", "2022 H1\n(tactical still)", "2024", "2025"])
    ax.set_ylabel("Mean working-day MADT minus 2019 (vehicles / day)")
    ax.set_title("Raw bin path vs 2019 (not DiD, not VKT)")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    exp = pd.read_csv(EXPOSURE, dtype={"station_id": str})
    exp["station_id"] = exp["station_id"].str.strip()
    exp["did_bin"] = exp["network_bin"].map(control_bin)
    exp["street_group"] = exp["desc"].map(street_group)
    exp["is_gran_via"] = exp["desc"].map(lambda s: counted_street(s).startswith("GRAN VIA"))
    exp["is_tac2020_other"] = exp["street_group"].eq("tac2020_other")

    panel = load_laborable([2018, 2019, 2022, 2024, 2025])
    panel = panel.merge(
        exp[
            [
                "station_id",
                "desc",
                "network_m",
                "network_bin",
                "did_bin",
                "street_group",
                "is_gran_via",
                "is_tac2020_other",
                "euclid_m",
            ]
        ],
        on="station_id",
        how="inner",
    )
    panel.to_csv(OUT / "monthly_laborable_panel.csv", index=False)

    pre = panel.loc[panel["year"].isin(PRE_YEARS)]
    post = panel.loc[panel["year"].isin(POST_YEARS)]
    st = collapse_stations(exp, pre, post, MIN_MONTHS, MIN_MONTHS)
    st.to_csv(OUT / "station_delta_q.csv", index=False)

    treated = [b for b in BIN_ORDER if b != "control_gt2km"]
    did_main = collapsed_did(st, treated)
    did_main.insert(0, "spec", "main_2018_19_vs_2024_25")
    did_main.to_csv(OUT / "did_two_period.csv", index=False)

    st_notac = st.loc[~st["is_tac2020_other"]].copy()
    did_notac = collapsed_did(st_notac, treated)
    did_notac.insert(0, "spec", "drop_tac2020_other_streets")
    did_notac.to_csv(OUT / "did_drop_tac2020.csv", index=False)

    st_nogv = st.loc[~st["is_gran_via"]].copy()
    did_nogv = collapsed_did(st_nogv, treated)
    did_nogv.insert(0, "spec", "drop_gran_via")
    did_nogv.to_csv(OUT / "did_drop_gran_via.csv", index=False)

    # Permanent on top of tactical: 2022 H1 vs 2024-25. Not Nello-Deakin.
    pre_h1 = panel.loc[(panel["year"] == 2022) & (panel["month"] <= 7)]
    st_inc = collapse_stations(exp, pre_h1, post, 5, MIN_MONTHS)
    did_inc = collapsed_did(st_inc, treated)
    did_inc.insert(0, "spec", "incremental_2022h1_vs_2024_25")
    did_inc.to_csv(OUT / "did_incremental_2022h1.csv", index=False)
    st_inc.to_csv(OUT / "station_delta_q_incremental_2022h1.csv", index=False)

    treated = [b for b in BIN_ORDER if b != "control_gt2km"]
    y_inc = st_inc["delta_q"].to_numpy(float)
    x_inc = np.column_stack(
        [np.ones(len(st_inc))]
        + [st_inc["did_bin"].eq(b).astype(float).to_numpy() for b in treated]
    )
    xy_inc = np.array(
        [TO_UTM.transform(float(lon), float(lat)) for lon, lat in zip(st_inc["lon"], st_inc["lat"])]
    )
    street_inc = st_inc["desc"].map(counted_street).to_numpy()
    _b, se_c500 = ols_conley(y_inc, x_inc, xy_inc, 500.0)
    _b, se_c1000 = ols_conley(y_inc, x_inc, xy_inc, 1000.0)
    _b, se_cl = ols_cluster(y_inc, x_inc, street_inc)
    inf_rows = []
    for i, b in enumerate(["control_gt2km", *treated]):
        inf_rows.append(
            {
                "bin": b,
                "n": int((st_inc["did_bin"] == b).sum()),
                "did_q_vs_control": 0.0 if i == 0 else round(float(_b[i]), 1),
                "se_hc1": round(float(did_inc.loc[did_inc["bin"] == b, "did_q_se"].iloc[0]), 1),
                "se_conley_500m": round(float(se_c500[i]), 1),
                "se_conley_1000m": round(float(se_c1000[i]), 1),
                "se_cluster_street": round(float(se_cl[i]), 1),
            }
        )
    pd.DataFrame(inf_rows).to_csv(OUT / "did_incremental_spatial_se.csv", index=False)

    def alt_bin(m):
        if m <= 200:
            return "0-200 m"
        if m <= 400:
            return "200-400 m"
        if m <= 700:
            return "400-700 m"
        if m <= 1200:
            return "700 m-1.2 km"
        if m <= 2000:
            return "1.2-2 km"
        return ">2 km (control)"

    st_alt = st_inc.copy()
    st_alt["did_bin"] = st_alt["network_m"].map(alt_bin)
    alt_order = [
        "0-200 m",
        "200-400 m",
        "400-700 m",
        "700 m-1.2 km",
        "1.2-2 km",
        ">2 km (control)",
    ]
    y_a = st_alt["delta_q"].to_numpy(float)
    treated_a = [b for b in alt_order if b != ">2 km (control)"]
    x_a = np.column_stack(
        [np.ones(len(st_alt))] + [st_alt["did_bin"].eq(b).astype(float).to_numpy() for b in treated_a]
    )
    beta_a, se_a = ols_hc1(y_a, x_a)
    alt_rows = []
    for i, b in enumerate([">2 km (control)", *treated_a]):
        sub = st_alt.loc[st_alt["did_bin"] == b]
        alt_rows.append(
            {
                "bin": b,
                "n": int(len(sub)),
                "did_q_vs_control": 0.0 if i == 0 else round(float(beta_a[i]), 1),
                "se_hc1": round(float(se_a[i]), 1),
            }
        )
    pd.DataFrame(alt_rows).to_csv(OUT / "did_incremental_alt_bins.csv", index=False)

    # Same months in post as in pre (Jan–Jul), so calendar mix is not the 250–500 m result.
    post_h1 = panel.loc[panel["year"].isin(POST_YEARS) & (panel["month"] <= 7)]
    st_h1h1 = collapse_stations(exp, pre_h1, post_h1, 5, 5)
    did_h1h1 = collapsed_did(st_h1h1, treated)
    did_h1h1.insert(0, "spec", "incremental_2022h1_vs_2024_25_h1")
    did_h1h1.to_csv(OUT / "did_incremental_h1_vs_h1.csv", index=False)

    # Observed mean ΔQ at 250–500 m versus the simulated constant +1,700 (sign test).
    sim_250 = 1699.6
    d250 = st_inc.loc[st_inc["did_bin"] == "250_500m", "delta_q"].to_numpy(float)
    n250 = int(len(d250))
    m250 = float(d250.mean())
    sd250 = float(d250.std(ddof=1))
    se250 = sd250 / np.sqrt(n250)
    t250 = (m250 - sim_250) / se250
    p250 = 2.0 * student_t.sf(abs(t250), n250 - 1)
    se_did_250 = float(did_inc.loc[did_inc["bin"] == "250_500m", "did_q_se"].iloc[0])
    zcrit = 1.96
    ncp = sim_250 / se_did_250
    power_did = float(
        1.0 - gaussian.cdf(zcrit - ncp) + gaussian.cdf(-zcrit - ncp)
    )
    pd.DataFrame(
        [
            {
                "bin": "250_500m",
                "n": n250,
                "obs_mean_delta_q": round(m250, 1),
                "obs_sd": round(sd250, 1),
                "obs_se_mean": round(se250, 1),
                "sim_fixed": sim_250,
                "t_obs_minus_sim": round(t250, 2),
                "p_two_sided": float(f"{p250:.2e}"),
                "did_q_vs_control": float(
                    did_inc.loc[did_inc["bin"] == "250_500m", "did_q_vs_control"].iloc[0]
                ),
                "did_se_hc1": se_did_250,
                "power_detect_sim_did_alpha05": round(power_did, 3),
            }
        ]
    ).to_csv(OUT / "obs_vs_sim_250_500_test.csv", index=False)

    # volume-weighted bin means (descriptive; not a second causal model)
    wrows = []
    ctrl_w = np.average(
        st.loc[st["did_bin"] == "control_gt2km", "delta_q"],
        weights=st.loc[st["did_bin"] == "control_gt2km", "q_pre"],
    )
    for b in BIN_ORDER:
        sub = st.loc[st["did_bin"] == b]
        wdelta = float(np.average(sub["delta_q"], weights=sub["q_pre"]))
        wrows.append(
            {
                "bin": b,
                "label": BIN_LABEL[b],
                "n": int(len(sub)),
                "q_pre_total": round(float(sub["q_pre"].sum()), 1),
                "delta_q_weighted": round(wdelta, 1),
                "did_weighted_vs_control": round(wdelta - ctrl_w, 1),
            }
        )
    pd.DataFrame(wrows).to_csv(OUT / "did_volume_weighted_descriptive.csv", index=False)

    ym = year_means(
        panel.loc[
            panel["year"].isin(PRE_YEARS | POST_YEARS)
            | ((panel["year"] == 2022) & (panel["month"] <= 7))
        ],
        st,
    )
    ym.to_csv(OUT / "year_bin_means.csv", index=False)

    ev = event_did(panel, st)
    ev.to_csv(OUT / "event_year_did.csv", index=False)

    plot_decay(
        did_main,
        FIG / "did_decay_main.png",
        "Observed dQ by network distance to phase-1 axes\n(2018-19 vs 2024-25, working-day MADT; not VKT)",
    )
    plot_decay(
        did_notac,
        FIG / "did_decay_drop_tac2020.png",
        "Observed dQ, dropping 2020-tactical counted streets\n(stacked-treatment robustness; not VKT)",
    )
    plot_decay(
        did_inc,
        FIG / "did_decay_incremental_2022h1.png",
        "Incremental observed dQ: 2022 H1 vs 2024-25\n(permanent green axes on top of the 2020 tactical regime; not VKT)",
    )
    plot_event_raw(ym, FIG / "event_path_vs_2019.png")

    print("stations in DiD", len(st))
    print(did_main.to_string(index=False))
    print("drop tac2020 n", len(st_notac))
    print(did_notac.to_string(index=False))
    print("incremental 2022H1 n", len(st_inc))
    print(did_inc.to_string(index=False))
    print("street groups", st["street_group"].value_counts().to_dict())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
