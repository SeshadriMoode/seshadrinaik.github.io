"""Stated 15 s turn-cost recode and perpendicular egress snaps.

Original-method robustness, not a second paper.
Does not invent EMEF, metro destinations, or congested assignment.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely import wkt
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform, unary_union
from shapely.strtree import STRtree
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_accessibility" / "working"))
from compute_access import (  # noqa: E402
    CAR15,
    CAR30,
    csr_time,
    cumulative,
    hansen,
    load_graph,
    load_snaps,
    network_dist_to_treated,
    od_times,
    zone_index,
)

NET = ROOT / "03_network" / "working"
INP = ROOT / "02_inventory" / "input"
OUT = ROOT / "04_accessibility" / "working"
ACC = OUT / "access_sections.csv"

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
TURN_S = 15.0
THROUGH_COS = 0.8
PERP_COS = 0.4
EGRESS_MAX_M = 200.0
HANSEN_BETA = 0.05

ON_AXIS = [
    2065, 2067, 2069, 2070, 2071, 2072,
    2091, 2092, 2093, 2096,
    2141, 2143, 2144, 2146, 2147,
]


def load_axes_utm():
    fc = json.loads((INP / "phase1_principal.geojson").read_text(encoding="utf-8"))
    lines = [
        shp_transform(lambda x, y, z=None: TO_UTM.transform(x, y), shape(f["geometry"]))
        for f in fc["features"]
    ]
    return unary_union(lines)


def axis_heading(axes, x, y):
    p = Point(x, y)
    d = axes.project(p)
    p0 = axes.interpolate(max(d - 10.0, 0.0))
    p1 = axes.interpolate(min(d + 10.0, axes.length))
    dx, dy = p1.x - p0.x, p1.y - p0.y
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def edge_heading(G, u, v):
    dx = G.nodes[v]["x"] - G.nodes[u]["x"]
    dy = G.nodes[v]["y"] - G.nodes[u]["y"]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def treated_nodes(G: nx.DiGraph) -> set:
    s = set()
    for u, v, d in G.edges(data=True):
        if d.get("treated"):
            s.add(u)
            s.add(v)
    return s


def node_has_perp(G, node, ax_h, treated):
    hx, hy = ax_h
    for _, w, d in G.out_edges(node, data=True):
        if d.get("treated"):
            continue
        ex, ey = edge_heading(G, node, w)
        if abs(ex * hx + ey * hy) <= PERP_COS:
            return True
    return False


def snap_egress(G: nx.DiGraph, snaps: pd.DataFrame, axes, treated: set) -> pd.DataFrame:
    """Move listed on-axis centroids onto the nearest untreated perpendicular."""
    out = snaps.copy()
    candidates = [n for n in G.nodes() if n not in treated]
    if not candidates:
        candidates = list(G.nodes())
    xy = np.array([[G.nodes[n]["x"], G.nodes[n]["y"]] for n in candidates])
    meta = []
    for seccio in ON_AXIS:
        row = out.loc[out.seccio == seccio]
        if row.empty:
            continue
        r = row.iloc[0]
        ax_h = axis_heading(axes, float(r.x), float(r.y))
        dxy = xy - np.array([float(r.x), float(r.y)])
        dist = np.hypot(dxy[:, 0], dxy[:, 1])
        order = np.argsort(dist)
        chosen = None
        chosen_d = None
        for k in order:
            if dist[k] > EGRESS_MAX_M:
                break
            n = candidates[int(k)]
            if node_has_perp(G, n, ax_h, treated):
                chosen, chosen_d = n, float(dist[k])
                break
        if chosen is None:
            for k in order:
                if dist[k] > EGRESS_MAX_M:
                    break
                chosen, chosen_d = candidates[int(k)], float(dist[k])
                break
        if chosen is None:
            meta.append({"seccio": int(seccio), "ok": False})
            continue
        idx = out.index[out.seccio == seccio][0]
        out.at[idx, "node_x"] = chosen[0]
        out.at[idx, "node_y"] = chosen[1]
        out.at[idx, "snap_m"] = round(chosen_d, 1)
        out.at[idx, "snapped"] = True
        meta.append(
            {
                "seccio": int(seccio),
                "ok": True,
                "snap_m": round(chosen_d, 1),
                "node": [chosen[0], chosen[1]],
            }
        )
    out["node"] = [
        None if not bool(s) else (float(x), float(y))
        for s, x, y in zip(out.snapped, out.node_x, out.node_y)
    ]
    out["egress_connector"] = out.seccio.isin(ON_AXIS)
    return out, meta


def turn_penalty(cosang: float) -> float:
    if cosang >= THROUGH_COS:
        return 0.0
    return TURN_S


def line_graph_csr(G: nx.DiGraph):
    """Dual graph: nodes are directed edges; turn friction on dual links."""
    edges = list(G.edges())
    eidx = {e: i for i, e in enumerate(edges)}
    n_e = len(edges)
    time_e = np.array([float(G[u][v]["time"]) for u, v in edges], dtype=float)
    heading = [edge_heading(G, u, v) for u, v in edges]
    in_at = {n: [] for n in G.nodes()}
    out_at = {n: [] for n in G.nodes()}
    for (u, v), i in eidx.items():
        out_at[u].append(i)
        in_at[v].append(i)
    rows, cols, data = [], [], []
    n_turn = 0
    for v in G.nodes():
        for i_in in in_at[v]:
            h1 = heading[i_in]
            for i_out in out_at[v]:
                h2 = heading[i_out]
                cosang = h1[0] * h2[0] + h1[1] * h2[1]
                pen = turn_penalty(cosang)
                if pen > 0:
                    n_turn += 1
                rows.append(i_in)
                cols.append(i_out)
                data.append(float(time_e[i_out] + pen))
    mat_dual = csr_matrix((data, (rows, cols)), shape=(n_e, n_e))
    return {
        "mat_dual": mat_dual,
        "eidx": eidx,
        "edges": edges,
        "time_e": time_e,
        "out_at": out_at,
        "in_at": in_at,
        "n_dual": n_e,
        "n_turn_links": n_turn,
        "n_dual_links": len(data),
    }


def od_times_turn(dual, orig_nodes, dest_nodes, limit_s: float) -> np.ndarray:
    """Shortest paths with 15 s non-through turns. orig/dest are primal nodes."""
    n_e = dual["n_dual"]
    n_o = len(orig_nodes)
    super_rows, super_cols, super_data = [], [], []
    for i, o in enumerate(orig_nodes):
        for ei in dual["out_at"].get(o, []):
            super_rows.append(n_e + i)
            super_cols.append(ei)
            super_data.append(float(dual["time_e"][ei]))
    mat = dual["mat_dual"]
    n = n_e + n_o
    r0, c0 = mat.nonzero()
    r = np.concatenate([r0, np.asarray(super_rows, dtype=int)])
    c = np.concatenate([c0, np.asarray(super_cols, dtype=int)])
    v = np.concatenate([mat.data, np.asarray(super_data, dtype=float)])
    full = csr_matrix((v, (r, c)), shape=(n, n))
    sources = np.arange(n_e, n_e + n_o)
    dist = dijkstra(full, directed=True, indices=sources, limit=limit_s, min_only=False)
    # dist shape (n_o, n); columns 0..n_e-1 are dual nodes
    t = np.full((n_o, len(dest_nodes)), np.inf)
    for j, d in enumerate(dest_nodes):
        inc = dual["in_at"].get(d, [])
        if not inc:
            continue
        t[:, j] = np.min(dist[:, inc], axis=1)
    return t


def queen_moran(sections: pd.DataFrame, values: np.ndarray) -> dict:
    """Moran's I under queen contiguity of census-section polygons."""
    geoms = list(sections["geom"])
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
                if geoms[i].intersection(geoms[j]).area == 0 or geoms[i].touches(geoms[j]):
                    neigh[i].append(j)
                    neigh[j].append(i)
    z = np.asarray(values, dtype=float)
    z = z - np.nanmean(z)
    wsum = 0.0
    num = 0.0
    for i, nbrs in enumerate(neigh):
        if not nbrs or not np.isfinite(z[i]):
            continue
        for j in nbrs:
            if not np.isfinite(z[j]):
                continue
            num += z[i] * z[j]
            wsum += 1.0
    den = float(np.nansum(z * z))
    if wsum == 0 or den == 0:
        return {"I": None, "n": n, "mean_neighbors": 0.0}
    I = (n / wsum) * (num / den)
    mean_nb = float(np.mean([len(x) for x in neigh]))
    return {"I": round(float(I), 3), "n": n, "mean_neighbors": round(mean_nb, 2), "W": int(wsum)}


def load_section_geoms(seccio_order: np.ndarray) -> pd.DataFrame:
    sec = json.loads((INP / "seccions_censals.json").read_text(encoding="utf-8"))
    rows = []
    for s in sec:
        seccio = int(s["codi_districte"]) * 1000 + int(s["codi_seccio_censal"])
        rows.append({"seccio": seccio, "geom": wkt.loads(s["geometria_etrs89"])})
    g = pd.DataFrame(rows).set_index("seccio").loc[list(seccio_order)].reset_index()
    return g


def off_median(pre, post, mask):
    pct = np.where(pre[mask] > 0, 100.0 * (post[mask] - pre[mask]) / pre[mask], np.nan)
    dA = post[mask] - pre[mask]
    return float(np.nanmedian(pct)), float(np.nanmedian(dA))


def main():
    print("load graphs", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    G_drop = load_graph("car_post_drop.pkl")
    axes = load_axes_utm()
    snaps = load_snaps("sections_snapped_car.csv")
    snaps_drop = load_snaps("sections_snapped_car_drop.csv")

    print("egress snaps", flush=True)
    snaps_e, meta_pre = snap_egress(G_pre, snaps, axes, treated_nodes(G_pre))
    snaps_d, meta_drop = snap_egress(G_drop, snaps_drop, axes, treated_nodes(G_drop))
    snaps_e["d_axis_net_m"] = network_dist_to_treated(G_pre, snaps_e)
    snaps_e.drop(columns=["node"]).to_csv(NET / "sections_snapped_car_egress.csv", index=False)
    snaps_d.drop(columns=["node"]).to_csv(NET / "sections_snapped_car_drop_egress.csv", index=False)

    print("csr link-time", flush=True)
    mat_pre, _, idx_pre = csr_time(G_pre)
    mat_post, _, idx_post = csr_time(G_post)
    z = zone_index(snaps_e, idx_pre)
    orig_i = z["gi"].to_numpy()
    pop = z["pop"].to_numpy(dtype=float)
    seccio = z["seccio"].to_numpy()
    t_pre = od_times(mat_pre, orig_i, orig_i, CAR30)
    t_post = od_times(mat_post, orig_i, orig_i, CAR30)
    np.fill_diagonal(t_pre, 0.0)
    np.fill_diagonal(t_post, 0.0)

    print("csr drop", flush=True)
    mat_drop, _, idx_drop = csr_time(G_drop)
    zd = zone_index(snaps_d, idx_drop).set_index("seccio")
    gi_drop, keep = [], []
    for s in seccio:
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
        t_sub = dist[:, sub]
        t_drop[np.ix_(ok, ok)] = t_sub
        ii = np.where(ok)[0]
        t_drop[ii, ii] = 0.0

    print("line graph + turn-cost dijkstra (this is the slow step)", flush=True)
    dual_pre = line_graph_csr(G_pre)
    dual_post = line_graph_csr(G_post)
    orig_nodes = [z.loc[i, "node"] if "node" in z.columns else None for i in z.index]
    # zone_index does not keep node; rebuild from snaps
    node_by = snaps_e.set_index("seccio")["node"]
    orig_nodes = [node_by.loc[int(s)] for s in seccio]
    t_turn_pre = od_times_turn(dual_pre, orig_nodes, orig_nodes, CAR30)
    t_turn_post = od_times_turn(dual_post, orig_nodes, orig_nodes, CAR30)
    np.fill_diagonal(t_turn_pre, 0.0)
    np.fill_diagonal(t_turn_post, 0.0)

    dnet = snaps_e.set_index("seccio").loc[seccio, "d_axis_net_m"].to_numpy()
    mask_off = ~pd.Series(seccio).isin(ON_AXIS).to_numpy()
    # after egress, former on-axis are local-egress; off-axis city result excludes them
    # so that the 15 do not re-enter the choropleth as ordinary off-axis
    mask_off = mask_off & np.isfinite(dnet)

    a15_pre, _ = cumulative(t_pre, pop, CAR15)
    a15_post, _ = cumulative(t_post, pop, CAR15)
    a15_drop, _ = cumulative(t_drop, pop, CAR15)
    a15_tp, _ = cumulative(t_turn_pre, pop, CAR15)
    a15_to, _ = cumulative(t_turn_post, pop, CAR15)
    a30_pre, _ = cumulative(t_pre, pop, CAR30)
    a30_post, _ = cumulative(t_post, pop, CAR30)
    h_pre = hansen(t_pre, pop, HANSEN_BETA)
    h_post = hansen(t_post, pop, HANSEN_BETA)

    med_x100, d_x100 = off_median(a15_pre, a15_post, mask_off)
    med_drop, d_drop = off_median(a15_pre, a15_drop, mask_off)
    med_turn, d_turn = off_median(a15_tp, a15_to, mask_off)
    med_h, d_h = off_median(h_pre, h_post, mask_off)

    pct_x100 = np.where(a15_pre > 0, 100.0 * (a15_post - a15_pre) / a15_pre, np.nan)
    pct_drop = np.where(a15_pre > 0, 100.0 * (a15_drop - a15_pre) / a15_pre, np.nan)
    pct_turn = np.where(a15_tp > 0, 100.0 * (a15_to - a15_tp) / a15_tp, np.nan)
    pct_h = np.where(h_pre > 0, 100.0 * (h_post - h_pre) / h_pre, np.nan)

    print("Moran's I", flush=True)
    geoms = load_section_geoms(seccio[mask_off])
    moran = {
        "car15_x100": queen_moran(geoms, pct_x100[mask_off]),
        "car15_drop": queen_moran(geoms, pct_drop[mask_off]),
        "car15_turn": queen_moran(geoms, pct_turn[mask_off]),
        "hansen": queen_moran(geoms, pct_h[mask_off]),
    }

    # corridor 2136 -> 2067 under link time and turns
    sidx = {int(s): i for i, s in enumerate(seccio)}
    corridor = {}
    if 2136 in sidx and 2067 in sidx:
        i, j = sidx[2136], sidx[2067]
        corridor = {
            "t_pre_min": round(float(t_pre[i, j] / 60.0), 2),
            "t_post_min": round(float(t_post[i, j] / 60.0), 2),
            "t_turn_pre_min": round(float(t_turn_pre[i, j] / 60.0), 2),
            "t_turn_post_min": round(float(t_turn_post[i, j] / 60.0), 2),
        }

    egress_pct = []
    for s in ON_AXIS:
        if s not in sidx:
            continue
        i = sidx[s]
        egress_pct.append(
            {
                "seccio": int(s),
                "pct_x100": round(float(pct_x100[i]), 2),
                "pct_drop": round(float(pct_drop[i]), 2),
                "pct_turn": round(float(pct_turn[i]), 2),
                "d_axis_net_m": round(float(dnet[i]), 1) if np.isfinite(dnet[i]) else None,
            }
        )

    # write scores used by maps: merge onto existing access file walk columns
    old = pd.read_csv(ACC)
    scores = z[["seccio", "codi_barri", "nom_barri", "nom_districte", "x", "y", "d_axis_m", "pop", "snap_m"]].copy()
    scores["snapped"] = True
    scores["d_axis_net_m"] = dnet
    scores["egress_connector"] = scores.seccio.isin(ON_AXIS)
    scores["A_car15_pre"] = a15_pre
    scores["A_car15_post"] = a15_post
    scores["dA_car15"] = a15_post - a15_pre
    scores["pct_car15"] = pct_x100
    scores["A_car15_drop"] = a15_drop
    scores["dA_car15_drop"] = a15_drop - a15_pre
    scores["pct_car15_drop"] = pct_drop
    scores["A_car15_turn_pre"] = a15_tp
    scores["A_car15_turn_post"] = a15_to
    scores["pct_car15_turn"] = pct_turn
    scores["A_car30_pre"] = a30_pre
    scores["A_car30_post"] = a30_post
    scores["dA_car30"] = a30_post - a30_pre
    scores["pct_car30"] = np.where(a30_pre > 0, 100.0 * scores["dA_car30"] / a30_pre, np.nan)
    scores["H_car_pre"] = h_pre
    scores["H_car_post"] = h_post
    scores["dH_car"] = h_post - h_pre
    scores["pct_H"] = pct_h
    keep_old = [c for c in ("n_car15_pre", "n_car15_post", "n_car30_pre", "n_car30_post", "A_walk15", "n_walk15", "band_net", "band_euclid") if c in old.columns]
    scores = scores.merge(old[["seccio"] + keep_old], on="seccio", how="left")
    # restore unsnapped Montbau
    missing = old.loc[~old.snapped].copy()
    if len(missing):
        for c in scores.columns:
            if c not in missing.columns:
                missing[c] = np.nan
        scores = pd.concat([scores, missing[scores.columns]], ignore_index=True)
    scores = scores.sort_values("seccio").reset_index(drop=True)
    scores.to_csv(OUT / "access_sections.csv", index=False)
    pd.DataFrame(egress_pct).to_csv(OUT / "on_axis_egress.csv", index=False)

    out = {
        "turn_s": TURN_S,
        "through_cos": THROUGH_COS,
        "dual_pre": {
            "n_dual": dual_pre["n_dual"],
            "n_dual_links": dual_pre["n_dual_links"],
            "n_turn_links": dual_pre["n_turn_links"],
        },
        "dual_post": {
            "n_dual": dual_post["n_dual"],
            "n_dual_links": dual_post["n_dual_links"],
            "n_turn_links": dual_post["n_turn_links"],
        },
        "egress_pre": meta_pre,
        "egress_drop": meta_drop,
        "off_axis_n": int(mask_off.sum()),
        "off_median_pct_car15_x100": round(med_x100, 3),
        "off_median_dA_car15_x100": round(d_x100, 1),
        "off_median_pct_car15_drop": round(med_drop, 3),
        "off_median_dA_car15_drop": round(d_drop, 1),
        "off_median_pct_car15_turn": round(med_turn, 3),
        "off_median_dA_car15_turn": round(d_turn, 1),
        "off_median_pct_hansen": round(med_h, 3),
        "corridor_2136_2067": corridor,
        "moran_I_off_axis": moran,
        "egress_pct": egress_pct,
        "nobody_gains_x100": bool(np.nanmax(pct_x100[mask_off]) <= 0),
        "nobody_gains_turn": bool(np.nanmax(pct_turn[mask_off]) <= 0),
    }
    (OUT / "turn_egress_meta.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in {"egress_pre", "egress_drop", "egress_pct"}}, indent=2))
    print(pd.DataFrame(egress_pct).to_string(index=False))


if __name__ == "__main__":
    main()
