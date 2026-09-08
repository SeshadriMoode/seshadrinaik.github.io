"""Estimated cumulative-opportunity accessibility from simulated times.

A_i(t) = sum_j pop_j * 1[T_ij <= t], including j = i (T_ii = 0).
T_ij is simulated shortest-path time. Do not call A_i observed.
"""
from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

ROOT = Path(__file__).resolve().parents[2]
NET = ROOT / "03_network" / "working"
OUT = ROOT / "04_accessibility" / "working"

CAR15 = 15 * 60.0
CAR30 = 30 * 60.0
WALK15 = 15 * 60.0
HANSEN_BETA = 0.05  # per minute; robustness only
BANDS = [
    (0, 250, "0-250m"),
    (250, 500, "250-500m"),
    (500, 1000, "500m-1km"),
    (1000, 2000, "1-2km"),
    (2000, 3500, "2-3.5km"),
    (3500, 1e12, ">3.5km"),
]


def load_graph(name: str) -> nx.DiGraph:
    with (NET / name).open("rb") as f:
        return pickle.load(f)


def load_snaps(name: str) -> pd.DataFrame:
    z = pd.read_csv(NET / name)
    z["node"] = [
        None if not bool(s) else (float(x), float(y))
        for s, x, y in zip(z.snapped, z.node_x, z.node_y)
    ]
    return z


def csr_time(G: nx.DiGraph):
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    rows, cols, data = [], [], []
    for u, v, d in G.edges(data=True):
        rows.append(idx[u])
        cols.append(idx[v])
        data.append(float(d["time"]))
    n = len(nodes)
    mat = csr_matrix((data, (rows, cols)), shape=(n, n))
    return mat, nodes, idx


def zone_index(snaps: pd.DataFrame, idx: dict) -> pd.DataFrame:
    z = snaps.loc[snaps.snapped].copy()
    z["gi"] = z["node"].map(idx)
    z = z.loc[z["gi"].notna()].copy()
    z["gi"] = z["gi"].astype(int)
    return z.reset_index(drop=True)


def cumulative(times_s: np.ndarray, pop: np.ndarray, cutoff_s: float):
    """times_s shape (n_orig, n_dest). Own zone is 0."""
    reach = np.isfinite(times_s) & (times_s <= cutoff_s)
    a = reach @ pop
    n_dest = reach.sum(axis=1)
    return a, n_dest


def hansen(times_s: np.ndarray, pop: np.ndarray, beta: float) -> np.ndarray:
    tmin = times_s / 60.0
    w = np.where(np.isfinite(tmin), np.exp(-beta * tmin), 0.0)
    return w @ pop


def od_times(mat, origins_i: np.ndarray, dest_i: np.ndarray, limit_s: float) -> np.ndarray:
    dist = dijkstra(mat, directed=True, indices=origins_i, limit=limit_s, min_only=False)
    return dist[:, dest_i]


def network_dist_to_treated(G: nx.DiGraph, snaps: pd.DataFrame) -> pd.Series:
    treated = set()
    for u, v, d in G.edges(data=True):
        if d.get("treated"):
            treated.add(u)
            treated.add(v)
    if not treated:
        return pd.Series(np.nan, index=snaps.index)
    U = G.to_undirected()
    dmap = nx.multi_source_dijkstra_path_length(U, treated, weight="length")
    out = []
    for n in snaps["node"]:
        if n is None:
            out.append(np.nan)
        else:
            out.append(dmap.get(n, np.nan))
    return pd.Series(out, index=snaps.index)


def band_label(d: float) -> str:
    if not np.isfinite(d):
        return "unsnapped"
    for lo, hi, name in BANDS:
        if lo <= d < hi:
            return name
    return ">3.5km"


def summarise(df: pd.DataFrame, col_dA: str, col_pct: str, col_Apre: str) -> pd.DataFrame:
    rows = []
    for name in [b[2] for b in BANDS] + ["city"]:
        sub = df if name == "city" else df.loc[df.band_net == name]
        if name == "city":
            sub = df.loc[df.snapped]
        if sub.empty:
            continue
        rows.append(
            {
                "band": name,
                "n": int(len(sub)),
                "pop": float(sub["pop"].sum()),
                "A_pre_mean": float(sub[col_Apre].mean()),
                "dA_mean": float(sub[col_dA].mean()),
                "dA_median": float(sub[col_dA].median()),
                "dA_min": float(sub[col_dA].min()),
                "dA_max": float(sub[col_dA].max()),
                "pct_mean": float(sub[col_pct].mean()),
                "n_loss": int((sub[col_dA] < -0.5).sum()),
                "n_gain": int((sub[col_dA] > 0.5).sum()),
                "pop_weighted_pct": float(
                    np.average(sub[col_pct], weights=sub["pop"]) if sub["pop"].sum() else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def walk_access(G: nx.DiGraph, snaps: pd.DataFrame, cutoff_s: float) -> np.ndarray:
    z = snaps.loc[snaps.snapped].copy()
    nodes = list(z["node"])
    pop = z["pop"].to_numpy(dtype=float)
    n = len(nodes)
    a = np.zeros(n)
    n_dest = np.zeros(n, dtype=int)
    for i, src in enumerate(nodes):
        if src not in G:
            continue
        dist = nx.single_source_dijkstra_path_length(G, src, cutoff=cutoff_s, weight="time")
        reach = 0.0
        nd = 0
        for j, dst in enumerate(nodes):
            t = 0.0 if i == j else dist.get(dst)
            if t is None:
                continue
            if t <= cutoff_s:
                reach += pop[j]
                nd += 1
        a[i] = reach
        n_dest[i] = nd
        if (i + 1) % 200 == 0:
            print(f"walk {i+1}/{n}", flush=True)
    out = snaps.copy()
    out["A_walk15"] = np.nan
    out["n_walk15"] = np.nan
    out.loc[z.index, "A_walk15"] = a
    out.loc[z.index, "n_walk15"] = n_dest
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    snaps_car = load_snaps("sections_snapped_car.csv")
    snaps_drop = load_snaps("sections_snapped_car_drop.csv")
    snaps_walk = load_snaps("sections_snapped_walk.csv")

    print("load car graphs", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    G_drop = load_graph("car_post_drop.pkl")

    snaps_car = snaps_car.copy()
    snaps_car["d_axis_net_m"] = network_dist_to_treated(G_pre, snaps_car)

    print("csr pre/post", flush=True)
    mat_pre, nodes_pre, idx_pre = csr_time(G_pre)
    mat_post, nodes_post, idx_post = csr_time(G_post)
    if nodes_pre != nodes_post:
        raise RuntimeError("car_pre and car_post node order differs; cannot share dest index")
    z = zone_index(snaps_car, idx_pre)
    assert z["gi"].notna().all()
    orig_i = z["gi"].to_numpy()
    dest_i = orig_i
    pop = z["pop"].to_numpy(dtype=float)

    print("dijkstra car pre/post", flush=True)
    t_pre = od_times(mat_pre, orig_i, dest_i, CAR30)
    t_post = od_times(mat_post, orig_i, dest_i, CAR30)
    np.fill_diagonal(t_pre, 0.0)
    np.fill_diagonal(t_post, 0.0)

    a15_pre, n15_pre = cumulative(t_pre, pop, CAR15)
    a15_post, n15_post = cumulative(t_post, pop, CAR15)
    a30_pre, n30_pre = cumulative(t_pre, pop, CAR30)
    a30_post, n30_post = cumulative(t_post, pop, CAR30)
    h_pre = hansen(t_pre, pop, HANSEN_BETA)
    h_post = hansen(t_post, pop, HANSEN_BETA)

    print("csr drop", flush=True)
    mat_drop, _, idx_drop = csr_time(G_drop)
    zd = zone_index(snaps_drop, idx_drop)
    # align destinations/origins to car-pre section order
    zd = zd.set_index("seccio")
    gi_drop = []
    keep = []
    for s in z["seccio"]:
        if s in zd.index and pd.notna(zd.loc[s, "gi"]):
            gi_drop.append(int(zd.loc[s, "gi"]))
            keep.append(True)
        else:
            gi_drop.append(-1)
            keep.append(False)
    gi_drop = np.array(gi_drop)
    ok = np.array(keep)
    t_drop = np.full((len(z), len(z)), np.inf)
    if ok.any():
        sub = gi_drop[ok]
        dist = dijkstra(mat_drop, directed=True, indices=sub, limit=CAR30)
        # dest columns: only ok dests exist on drop graph
        dest_cols = np.full(len(z), -1)
        dest_cols[ok] = np.arange(ok.sum())
        # dist shape (n_ok_orig, n_drop_nodes)
        t_sub = dist[:, sub]
        t_drop[np.ix_(ok, ok)] = t_sub
        for k in range(ok.sum()):
            t_drop[np.where(ok)[0][k], np.where(ok)[0][k]] = 0.0
    a15_drop, n15_drop = cumulative(t_drop, pop, CAR15)
    a30_drop, n30_drop = cumulative(t_drop, pop, CAR30)

    scores = z[
        [
            "seccio",
            "codi_barri",
            "nom_barri",
            "nom_districte",
            "x",
            "y",
            "d_axis_m",
            "pop",
            "snap_m",
        ]
    ].copy()
    scores["snapped"] = True
    scores["d_axis_net_m"] = snaps_car.set_index("seccio").loc[scores.seccio, "d_axis_net_m"].to_numpy()
    scores["A_car15_pre"] = a15_pre
    scores["A_car15_post"] = a15_post
    scores["dA_car15"] = a15_post - a15_pre
    scores["pct_car15"] = np.where(a15_pre > 0, 100.0 * scores["dA_car15"] / a15_pre, np.nan)
    scores["n_car15_pre"] = n15_pre
    scores["n_car15_post"] = n15_post
    scores["A_car30_pre"] = a30_pre
    scores["A_car30_post"] = a30_post
    scores["dA_car30"] = a30_post - a30_pre
    scores["pct_car30"] = np.where(a30_pre > 0, 100.0 * scores["dA_car30"] / a30_pre, np.nan)
    scores["n_car30_pre"] = n30_pre
    scores["n_car30_post"] = n30_post
    scores["A_car15_drop"] = a15_drop
    scores["dA_car15_drop"] = a15_drop - a15_pre
    scores["pct_car15_drop"] = np.where(a15_pre > 0, 100.0 * scores["dA_car15_drop"] / a15_pre, np.nan)
    scores["A_car30_drop"] = a30_drop
    scores["dA_car30_drop"] = a30_drop - a30_pre
    scores["H_car_pre"] = h_pre
    scores["H_car_post"] = h_post
    scores["dH_car"] = h_post - h_pre
    scores["pct_H"] = np.where(h_pre > 0, 100.0 * scores["dH_car"] / h_pre, np.nan)
    scores["band_net"] = scores["d_axis_net_m"].map(band_label)
    scores["band_euclid"] = scores["d_axis_m"].map(band_label)

    print("walk 15 min", flush=True)
    G_walk = load_graph("walk.pkl")
    walk = walk_access(G_walk, snaps_walk, WALK15)
    scores = scores.merge(
        walk[["seccio", "A_walk15", "n_walk15"]],
        on="seccio",
        how="left",
    )
    # unsnapped car row (Montbau) still in walk
    missing = snaps_car.loc[~snaps_car.snapped, ["seccio", "codi_barri", "nom_barri", "nom_districte", "x", "y", "d_axis_m", "pop", "snap_m"]].copy()
    if len(missing):
        missing["snapped"] = False
        for c in scores.columns:
            if c not in missing.columns:
                missing[c] = np.nan
        missing["A_walk15"] = walk.set_index("seccio").loc[missing.seccio, "A_walk15"].to_numpy()
        missing["n_walk15"] = walk.set_index("seccio").loc[missing.seccio, "n_walk15"].to_numpy()
        missing["band_net"] = "unsnapped"
        missing["band_euclid"] = missing["d_axis_m"].map(band_label)
        scores = pd.concat([scores, missing[scores.columns]], ignore_index=True)

    scores = scores.sort_values("seccio").reset_index(drop=True)
    scores.to_csv(OUT / "access_sections.csv", index=False)

    ok = scores.loc[scores.snapped].copy()
    s15 = summarise(ok, "dA_car15", "pct_car15", "A_car15_pre")
    s15.insert(0, "measure", "car15_x100")
    s15d = summarise(ok, "dA_car15_drop", "pct_car15_drop", "A_car15_pre")
    s15d.insert(0, "measure", "car15_drop")
    s30 = summarise(ok, "dA_car30", "pct_car30", "A_car30_pre")
    s30.insert(0, "measure", "car30_x100")
    sh = summarise(ok, "dH_car", "pct_H", "H_car_pre")
    sh.insert(0, "measure", "hansen_beta0.05")
    summary = pd.concat([s15, s15d, s30, sh], ignore_index=True)
    summary.to_csv(OUT / "access_summary_bands.csv", index=False)

    meta = {
        "computed_utc": datetime.now(timezone.utc).isoformat(),
        "measure": "cumulative_opportunity_population_2022",
        "T_ij": "simulated",
        "A_i": "estimated",
        "self_zone_included": True,
        "car15_s": CAR15,
        "car30_s": CAR30,
        "walk15_s": WALK15,
        "hansen_beta_per_min": HANSEN_BETA,
        "n_origins_car": int(ok.shape[0]),
        "city_dA_car15_mean": float(ok["dA_car15"].mean()),
        "city_dA_car15_median": float(ok["dA_car15"].median()),
        "city_pct_car15_mean": float(ok["pct_car15"].mean()),
        "n_loss_car15": int((ok["dA_car15"] < -0.5).sum()),
        "n_gain_car15": int((ok["dA_car15"] > 0.5).sum()),
        "max_loss_car15": float(ok["dA_car15"].min()),
        "max_loss_seccio": int(ok.loc[ok["dA_car15"].idxmin(), "seccio"]),
        "walk_delta": "zero_by_construction",
        "exposure_band": "undirected_network_distance_to_treated_on_car_pre",
    }
    (OUT / "access_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(s15.to_string(index=False))


if __name__ == "__main__":
    main()
