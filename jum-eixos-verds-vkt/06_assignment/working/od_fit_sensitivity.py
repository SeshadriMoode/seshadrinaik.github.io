"""OD-fit and routing sensitivities on the locked demand-fixed assignment.

Reuses the v1.0 graph, gravity prior and pre/post AON paths. Does not change
the primary LTR/NR/NVTR numbers. Writes od_fit_sensitivity.csv and
od_fit_diagnostics.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_assignment as ra


def add_junction_delay(G, metres_per_extra_arm: float = 80.0):
    H = ra.copy_edge_attrs(G)
    deg = {n: H.degree(n) for n in H.nodes()}
    for _u, v, d in H.edges(data=True):
        extra = metres_per_extra_arm * max(deg[v] - 2, 0) / 2.0
        d["length"] = d["length"] + extra
    return H


def sim_bin(st, q0, q1, se, bin_name: str) -> float:
    m = st["did_bin"].to_numpy() == bin_name
    if not m.any():
        return float("nan")
    return float((q1[se] - q0[se])[m].mean())


def station_diag(pred, obs) -> dict:
    pred = np.asarray(pred, float)
    obs = np.asarray(obs, float)
    ratio = pred / np.maximum(obs, 1.0)
    zero = pred < 1.0
    wild = (ratio > 3.0) | ((ratio < 1.0 / 3.0) & ~zero)
    return {
        "n_stations": int(len(obs)),
        "n_unhit_pred_lt1": int(zero.sum()),
        "share_unhit": round(float(zero.mean()), 3),
        "n_ratio_outside_1_to_3": int(wild.sum()),
        "share_ratio_outside_1_to_3": round(float(wild.mean()), 3),
        "median_pred_over_obs": round(float(np.median(ratio[~zero])) if (~zero).any() else float("nan"), 3),
    }


def main() -> None:
    OUT = ra.OUT
    axes = ra.load_axes()
    clip = axes.buffer(ra.BUFFER_M)
    print("loading OSM", flush=True)
    osm = json.loads(ra.OSM.read_text(encoding="utf-8"))
    print("building digraph", flush=True)
    G = ra.build_digraph(osm, clip, axes)
    ra.inject_principal(G, ra.load_principal_lines())
    G0 = ra.copy_edge_attrs(G)
    edges, uv_to_i, length, d_axis, _treated = ra.edge_tables(G0)
    zones = ra.load_zones(G0)
    zone_nodes = list(zones["node"])
    pop = zones["pop"].to_numpy(float)

    print("AON paths pre", flush=True)
    dist, paths = ra.od_paths(G0, zone_nodes, uv_to_i)
    T0 = ra.gravity(pop, dist, ra.GRAV_BETA)
    counts = pd.read_csv(ra.COUNTS, dtype={"station_id": str})
    st = ra.snap_stations(G0, counts, uv_to_i, ra.SNAP_STATION_M)
    se = st["edge_i"].to_numpy(int)
    q_obs = st["q_pre"].to_numpy(float)
    T_s, k = ra.scale_to_counts(T0, paths, len(edges), se, q_obs)

    print("AON paths post (treated x100)", flush=True)
    G_post = ra.penalise_treated(G0, ra.TREATED_COST)
    _dist_p, paths_p = ra.od_paths(G_post, zone_nodes, uv_to_i)

    rows = []

    def record(name, T, q0, q1, fit, res=None, extra=None):
        de = ra.decompose(
            float((q0 * length / 1000).sum()),
            float((q1 * length / 1000).sum()),
            d_axis,
            length,
            q0,
            q1,
        )
        rec = {
            "spec": name,
            "pre_corr": fit["corr"],
            "pre_mape": fit["mape"],
            "pre_rmse": fit["rmse"],
            "optimizer_success": None if res is None else bool(res.success),
            "optimizer_nit": None if res is None else int(res.nit),
            "sim_delta_q_250_500m": sim_bin(st, q0, q1, se, "250_500m"),
            "sim_sign_250_500m_positive": bool(sim_bin(st, q0, q1, se, "250_500m") > 0),
            "sim_delta_q_on_immediate": sim_bin(st, q0, q1, se, "on_or_immediate"),
            "LTR": de["LTR"],
            "NR": de["NR"],
            "NVTR": de["NVTR"],
            "obs_delta_q_250_500m": float(st.loc[st["did_bin"] == "250_500m", "delta_q"].mean()),
        }
        if extra:
            rec.update(extra)
        rows.append(rec)
        print(name, "corr", fit["corr"], "sim250", round(rec["sim_delta_q_250_500m"], 1), flush=True)

    print("gravity + median k, no ODME", flush=True)
    q0 = ra.assign(T_s, paths, len(edges))
    q1 = ra.assign(T_s, paths_p, len(edges))
    record("gravity_scale_only", T_s, q0, q1, ra.fit_report(q0, se, q_obs), extra={"lambda": None, "maxiter": None})

    for lam, mx, label in (
        (5e3, 25, "gls_lambda_5e3_maxiter_25"),
        (5e4, 25, "gls_lambda_5e4_maxiter_25_primary"),
        (5e5, 25, "gls_lambda_5e5_maxiter_25"),
        (5e4, 80, "gls_lambda_5e4_maxiter_80"),
    ):
        print("fit", label, flush=True)
        T, res = ra.furness_fit(T_s, paths, len(edges), se, q_obs, lam=lam, maxiter=mx)
        q0 = ra.assign(T, paths, len(edges))
        q1 = ra.assign(T, paths_p, len(edges))
        record(
            label,
            T,
            q0,
            q1,
            ra.fit_report(q0, se, q_obs),
            res=res,
            extra={
                "lambda": lam,
                "maxiter": mx,
                "factor_a_min": res.factor_a_range[0],
                "factor_a_max": res.factor_a_range[1],
                "factor_g_min": res.factor_g_range[0],
                "factor_g_max": res.factor_g_range[1],
            },
        )
        if label.endswith("primary"):
            T_pre = T
            q_pre = q0
            diag = station_diag(q0[se], q_obs)
            diag.update(
                {
                    "optimizer_success": bool(res.success),
                    "optimizer_nit": int(res.nit),
                    "optimizer_message": str(res.message),
                    "factor_a_min": res.factor_a_range[0],
                    "factor_a_max": res.factor_a_range[1],
                    "factor_g_min": res.factor_g_range[0],
                    "factor_g_max": res.factor_g_range[1],
                    "n_od_pairs_pre": int(len(paths)),
                    "n_zones": int(len(zones)),
                }
            )
            pd.DataFrame([diag]).to_csv(OUT / "od_fit_diagnostics.csv", index=False)
            print("diagnostics", diag, flush=True)

    print("junction delay 80 m per extra arm, same OD", flush=True)
    G_j = add_junction_delay(G0, 80.0)
    edges_j, uv_j, length_j, d_j, _t = ra.edge_tables(G_j)
    print("AON paths with junction delay", flush=True)
    _d0, paths_j = ra.od_paths(G_j, zone_nodes, uv_j)
    G_jp = ra.penalise_treated(G_j, ra.TREATED_COST)
    _d1, paths_jp = ra.od_paths(G_jp, zone_nodes, uv_j)
    # re-snap stations onto the delayed graph's edge table
    st_j = ra.snap_stations(G_j, counts, uv_j, ra.SNAP_STATION_M)
    se_j = st_j["edge_i"].to_numpy(int)
    q0j = ra.assign(T_pre, paths_j, len(edges_j))
    q1j = ra.assign(T_pre, paths_jp, len(edges_j))
    fitj = ra.fit_report(q0j, se_j, st_j["q_pre"].to_numpy(float))
    de = ra.decompose(
        float((q0j * length_j / 1000).sum()),
        float((q1j * length_j / 1000).sum()),
        d_j,
        length_j,
        q0j,
        q1j,
    )
    rows.append(
        {
            "spec": "junction_delay_80m_same_OD",
            "pre_corr": fitj["corr"],
            "pre_mape": fitj["mape"],
            "pre_rmse": fitj["rmse"],
            "optimizer_success": None,
            "optimizer_nit": None,
            "sim_delta_q_250_500m": sim_bin(st_j, q0j, q1j, se_j, "250_500m"),
            "sim_sign_250_500m_positive": bool(sim_bin(st_j, q0j, q1j, se_j, "250_500m") > 0),
            "sim_delta_q_on_immediate": sim_bin(st_j, q0j, q1j, se_j, "on_or_immediate"),
            "LTR": de["LTR"],
            "NR": de["NR"],
            "NVTR": de["NVTR"],
            "obs_delta_q_250_500m": float(st_j.loc[st_j["did_bin"] == "250_500m", "delta_q"].mean()),
            "lambda": None,
            "maxiter": None,
        }
    )
    print(
        "junction",
        "corr",
        fitj["corr"],
        "sim250",
        round(rows[-1]["sim_delta_q_250_500m"], 1),
        flush=True,
    )

    pd.DataFrame(rows).to_csv(OUT / "od_fit_sensitivity.csv", index=False)
    print("wrote", OUT / "od_fit_sensitivity.csv", flush=True)


if __name__ == "__main__":
    main()
