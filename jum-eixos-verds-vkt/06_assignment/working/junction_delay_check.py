"""Junction-delay AON on a copy of the unpenalised graph.

The earlier od_fit_sensitivity row was invalid: penalise_treated used a
shallow NetworkX copy, so G already had treated cost x100 before delay was
added, and pre/post paths were identical. This script copies edge attributes
first, then adds 80 m per extra junction arm, then applies treated x100.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_assignment as ra
import od_fit_sensitivity as ofs


def main() -> None:
    axes = ra.load_axes()
    clip = axes.buffer(ra.BUFFER_M)
    print("loading OSM", flush=True)
    osm = json.loads(ra.OSM.read_text(encoding="utf-8"))
    print("building digraph", flush=True)
    G = ra.build_digraph(osm, clip, axes)
    ra.inject_principal(G, ra.load_principal_lines())
    G0 = ra.copy_edge_attrs(G)
    edges, uv_to_i, length, d_axis, _t = ra.edge_tables(G0)
    zones = ra.load_zones(G0)
    zone_nodes = list(zones["node"])
    pop = zones["pop"].to_numpy(float)

    print("AON paths pre (unpenalised)", flush=True)
    dist, paths = ra.od_paths(G0, zone_nodes, uv_to_i)
    T0 = ra.gravity(pop, dist, ra.GRAV_BETA)
    counts = pd.read_csv(ra.COUNTS, dtype={"station_id": str})
    st = ra.snap_stations(G0, counts, uv_to_i, ra.SNAP_STATION_M)
    se = st["edge_i"].to_numpy(int)
    q_obs = st["q_pre"].to_numpy(float)
    T_s, k = ra.scale_to_counts(T0, paths, len(edges), se, q_obs)
    print("median k", k, flush=True)

    print("GLS primary (lambda 5e4, maxiter 25)", flush=True)
    T, res = ra.furness_fit(T_s, paths, len(edges), se, q_obs, lam=5e4, maxiter=25)
    print("GLS nit", res.nit, "success", res.success, flush=True)

    print("junction delay on unpenalised copy", flush=True)
    G_j = ofs.add_junction_delay(G0, 80.0)
    edges_j, uv_j, length_j, d_j, _t = ra.edge_tables(G_j)
    print("AON pre with junction delay", flush=True)
    _d0, paths_j = ra.od_paths(G_j, zone_nodes, uv_j)
    G_jp = ra.penalise_treated(G_j, ra.TREATED_COST)
    print("AON post with junction delay + treated x100", flush=True)
    _d1, paths_jp = ra.od_paths(G_jp, zone_nodes, uv_j)

    n_diff = sum(
        1
        for k in set(paths_j) | set(paths_jp)
        if k not in paths_j
        or k not in paths_jp
        or len(paths_j[k]) != len(paths_jp[k])
        or (paths_j[k] != paths_jp[k]).any()
    )
    print("OD pairs with different pre/post paths", n_diff, "of", len(paths_j), flush=True)

    st_j = ra.snap_stations(G_j, counts, uv_j, ra.SNAP_STATION_M)
    se_j = st_j["edge_i"].to_numpy(int)
    q0j = ra.assign(T, paths_j, len(edges_j))
    q1j = ra.assign(T, paths_jp, len(edges_j))
    fitj = ra.fit_report(q0j, se_j, st_j["q_pre"].to_numpy(float))
    de = ra.decompose(
        float((q0j * length_j / 1000).sum()),
        float((q1j * length_j / 1000).sum()),
        d_j,
        length_j,
        q0j,
        q1j,
    )
    sim250 = ofs.sim_bin(st_j, q0j, q1j, se_j, "250_500m")
    sim_imm = ofs.sim_bin(st_j, q0j, q1j, se_j, "on_or_immediate")
    row = {
        "spec": "junction_delay_80m_same_OD",
        "pre_corr": fitj["corr"],
        "pre_mape": fitj["mape"],
        "pre_rmse": fitj["rmse"],
        "n_paths_differ": n_diff,
        "n_od_pairs_pre": len(paths_j),
        "sim_delta_q_250_500m": sim250,
        "sim_sign_250_500m_positive": bool(sim250 > 0),
        "sim_delta_q_on_immediate": sim_imm,
        "LTR": de["LTR"],
        "NR": de["NR"],
        "NVTR": de["NVTR"],
        "obs_delta_q_250_500m": float(st_j.loc[st_j["did_bin"] == "250_500m", "delta_q"].mean()),
    }
    out = ra.OUT / "junction_delay_check.csv"
    pd.DataFrame([row]).to_csv(out, index=False)
    print(row, flush=True)
    print("wrote", out, flush=True)

    # Replace the invalid all-zero row in od_fit_sensitivity.csv.
    sens = pd.read_csv(ra.OUT / "od_fit_sensitivity.csv")
    sens = sens.loc[sens["spec"] != "junction_delay_80m_same_OD"].copy()
    extra = {c: None for c in sens.columns}
    extra.update({k: row.get(k) for k in extra if k in row})
    extra["spec"] = "junction_delay_80m_same_OD"
    extra["sim_sign_250_500m_positive"] = row["sim_sign_250_500m_positive"]
    extra["obs_delta_q_250_500m"] = row["obs_delta_q_250_500m"]
    extra["pre_corr"] = row["pre_corr"]
    extra["pre_mape"] = row["pre_mape"]
    extra["pre_rmse"] = row["pre_rmse"]
    extra["sim_delta_q_250_500m"] = row["sim_delta_q_250_500m"]
    extra["sim_delta_q_on_immediate"] = row["sim_delta_q_on_immediate"]
    extra["LTR"] = row["LTR"]
    extra["NR"] = row["NR"]
    extra["NVTR"] = row["NVTR"]
    sens = pd.concat([sens, pd.DataFrame([extra])], ignore_index=True)
    sens.to_csv(ra.OUT / "od_fit_sensitivity.csv", index=False)
    print("updated od_fit_sensitivity.csv", flush=True)


if __name__ == "__main__":
    main()
