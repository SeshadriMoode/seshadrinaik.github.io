"""Turn-cost proxies that still use the axes in the pre network.

80 m per extra arm already removes treated edges from all 2,307 AON paths
before the policy penalty, so it is not a post-treatment check. 5 m and
10 m still load the axes.
"""
from __future__ import annotations

import json
import sys

import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import run_assignment as ra
import od_fit_sensitivity as ofs


def main() -> None:
    axes = ra.load_axes()
    clip = axes.buffer(ra.BUFFER_M)
    print("loading OSM", flush=True)
    osm = json.loads(ra.OSM.read_text(encoding="utf-8"))
    G = ra.build_digraph(osm, clip, axes)
    ra.inject_principal(G, ra.load_principal_lines())
    G0 = ra.copy_edge_attrs(G)
    edges, uv_to_i, _length, _d_axis, treated = ra.edge_tables(G0)
    treated_set = set(int(i) for i, t in enumerate(treated) if t)
    zones = ra.load_zones(G0)
    zone_nodes = list(zones["node"])
    pop = zones["pop"].to_numpy(float)
    print("AON pre", flush=True)
    dist, paths = ra.od_paths(G0, zone_nodes, uv_to_i)
    T0 = ra.gravity(pop, dist, ra.GRAV_BETA)
    counts = pd.read_csv(ra.COUNTS, dtype={"station_id": str})
    st = ra.snap_stations(G0, counts, uv_to_i, ra.SNAP_STATION_M)
    se = st["edge_i"].to_numpy(int)
    q_obs = st["q_pre"].to_numpy(float)
    T_s, _k = ra.scale_to_counts(T0, paths, len(edges), se, q_obs)
    print("GLS", flush=True)
    T, res = ra.furness_fit(T_s, paths, len(edges), se, q_obs, lam=5e4, maxiter=25)
    print("GLS nit", res.nit, flush=True)
    n_use0 = sum(1 for eids in paths.values() if treated_set.intersection(eids.tolist()))
    print("unpenalised OD using treated", n_use0, "of", len(paths), flush=True)

    rows = []
    for metres in (5.0, 10.0, 80.0):
        print("delay", metres, flush=True)
        G_j = ofs.add_junction_delay(G0, metres)
        edges_j, uv_j, length_j, d_j, t_j = ra.edge_tables(G_j)
        tset = set(int(i) for i, t in enumerate(t_j) if t)
        _, paths_j = ra.od_paths(G_j, zone_nodes, uv_j)
        G_jp = ra.penalise_treated(G_j, ra.TREATED_COST)
        _, paths_jp = ra.od_paths(G_jp, zone_nodes, uv_j)
        n_use = sum(1 for eids in paths_j.values() if tset.intersection(eids.tolist()))
        n_diff = sum(
            1
            for k in set(paths_j) | set(paths_jp)
            if k not in paths_j
            or k not in paths_jp
            or len(paths_j[k]) != len(paths_jp[k])
            or (paths_j[k] != paths_jp[k]).any()
        )
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
        rec = {
            "metres_per_extra_arm": metres,
            "pre_corr": fitj["corr"],
            "pre_mape": fitj["mape"],
            "od_using_treated_pre": n_use,
            "n_paths_differ": n_diff,
            "sim_delta_q_250_500m": sim250,
            "sim_sign_positive": bool(sim250 > 0),
            "LTR": de["LTR"],
            "NR": de["NR"],
            "NVTR": de["NVTR"],
        }
        rows.append(rec)
        print(rec, flush=True)

    out = ra.OUT / "junction_delay_light.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
