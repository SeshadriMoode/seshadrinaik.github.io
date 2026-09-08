"""Moran's I permutation inference and +30 s turn stress-test.

Does not overwrite access_sections.csv (15 s results stay locked).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.csgraph import dijkstra

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_accessibility" / "working"))
from compute_access import (  # noqa: E402
    CAR15,
    CAR30,
    cumulative,
    load_graph,
    load_snaps,
    zone_index,
)
from turn_egress import (  # noqa: E402
    ON_AXIS,
    THROUGH_COS,
    line_graph_csr,
    load_section_geoms,
    od_times_turn,
    turn_penalty,
)

OUT = ROOT / "04_accessibility" / "working"
NET = ROOT / "03_network" / "working"
N_PERM = 999
RNG = np.random.default_rng(20260907)


def queen_neighbors(geoms) -> list[list[int]]:
    from shapely.strtree import STRtree

    tree = STRtree(geoms)
    n = len(geoms)
    neigh = [[] for _ in range(n)]
    for i, g in enumerate(geoms):
        hits = tree.query(g)
        for j in np.atleast_1d(hits):
            j = int(j)
            if j <= i:
                continue
            if i != j and (geoms[i].touches(geoms[j]) or geoms[i].intersects(geoms[j])):
                inter = geoms[i].intersection(geoms[j])
                if inter.area == 0 or geoms[i].touches(geoms[j]):
                    neigh[i].append(j)
                    neigh[j].append(i)
    return neigh


def moran_I(z: np.ndarray, neigh: list[list[int]]) -> tuple[float, float]:
    z = np.asarray(z, dtype=float)
    zc = z - np.nanmean(z)
    num = 0.0
    wsum = 0.0
    for i, nbrs in enumerate(neigh):
        if not nbrs or not np.isfinite(zc[i]):
            continue
        for j in nbrs:
            if not np.isfinite(zc[j]):
                continue
            num += zc[i] * zc[j]
            wsum += 1.0
    den = float(np.nansum(zc * zc))
    n = int(np.isfinite(z).sum())
    if wsum == 0 or den == 0:
        return float("nan"), 0.0
    return (n / wsum) * (num / den), wsum


def moran_perm(values: np.ndarray, neigh: list[list[int]]) -> dict:
    I_obs, wsum = moran_I(values, neigh)
    n = int(np.isfinite(values).sum())
    e_i = -1.0 / (n - 1) if n > 1 else float("nan")
    if not np.isfinite(I_obs):
        return {"I": None, "n": n, "W": int(wsum), "E_I": e_i}
    z0 = np.asarray(values, dtype=float).copy()
    I_perm = np.empty(N_PERM, dtype=float)
    for r in range(N_PERM):
        RNG.shuffle(z0)
        I_perm[r], _ = moran_I(z0, neigh)
    mu = float(np.mean(I_perm))
    sd = float(np.std(I_perm, ddof=1))
    z = (float(I_obs) - mu) / sd if sd > 0 else float("nan")
    extreme = np.sum(np.abs(I_perm - e_i) >= np.abs(float(I_obs) - e_i))
    p = (int(extreme) + 1) / (N_PERM + 1)
    return {
        "I": round(float(I_obs), 3),
        "E_I": round(e_i, 4),
        "z": None if not np.isfinite(z) else round(z, 2),
        "p_perm": round(p, 4),
        "n": n,
        "W": int(wsum),
        "n_perm": N_PERM,
    }


def run_moran() -> dict:
    g = pd.read_csv(OUT / "access_sections.csv")
    on = set(ON_AXIS)
    off = g.loc[g.snapped.fillna(False) & ~g.seccio.isin(on)].copy()
    geoms_df = load_section_geoms(off.seccio.to_numpy())
    neigh = queen_neighbors(list(geoms_df["geom"]))
    mean_nb = float(np.mean([len(x) for x in neigh]))
    out = {"mean_neighbors": round(mean_nb, 2)}
    for key, col in [
        ("car15_x100", "pct_car15"),
        ("car15_drop", "pct_car15_drop"),
        ("car15_turn", "pct_car15_turn"),
        ("hansen", "pct_H"),
    ]:
        print("Moran", key, flush=True)
        out[key] = moran_perm(off[col].to_numpy(), neigh)
    return out


def run_turn(seconds: float) -> dict:
    import turn_egress as te
    from compute_access import csr_time
    from turn_egress import load_axes_utm, snap_egress, treated_nodes

    te.TURN_S = float(seconds)
    print(f"load graphs turn={seconds}", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    snaps = load_snaps("sections_snapped_car.csv")
    axes = load_axes_utm()
    snaps_e, _ = snap_egress(G_pre, snaps, axes, treated_nodes(G_pre))
    _, _, idx_pre = csr_time(G_pre)
    z = zone_index(snaps_e, idx_pre)
    seccio = z["seccio"].to_numpy()
    pop = z["pop"].to_numpy(dtype=float)
    node_by = snaps_e.set_index("seccio")["node"]
    orig_nodes = [node_by.loc[int(s)] for s in seccio]
    mask_off = ~pd.Series(seccio).isin(ON_AXIS).to_numpy()

    print("dual", seconds, "s", flush=True)
    dual_pre = line_graph_csr(G_pre)
    dual_post = line_graph_csr(G_post)
    t_pre = od_times_turn(dual_pre, orig_nodes, orig_nodes, CAR30)
    t_post = od_times_turn(dual_post, orig_nodes, orig_nodes, CAR30)
    np.fill_diagonal(t_pre, 0.0)
    np.fill_diagonal(t_post, 0.0)
    a_pre, _ = cumulative(t_pre, pop, CAR15)
    a_post, _ = cumulative(t_post, pop, CAR15)
    pct = np.where(a_pre > 0, 100.0 * (a_post - a_pre) / a_pre, np.nan)
    off = pct[mask_off]
    n_neg = int(np.nansum(off < -1e-9))
    return {
        "turn_s": seconds,
        "n_off": int(mask_off.sum()),
        "median_pct": round(float(np.nanmedian(off)), 4),
        "median_dA": round(float(np.nanmedian(a_post[mask_off] - a_pre[mask_off])), 1),
        "n_negative": n_neg,
        "min_pct": round(float(np.nanmin(off)), 4),
        "n_turn_links": dual_pre["n_turn_links"],
    }


def main():
    moran = run_moran()
    print(json.dumps(moran, indent=2), flush=True)
    turn30 = run_turn(30.0)
    print(json.dumps(turn30, indent=2), flush=True)
    out = {"moran_I_off_axis": moran, "turn_30s": turn30}
    (OUT / "moran_turn30_meta.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
