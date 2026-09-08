"""Robustness on the same simulated car times: Hansen betas and a parallel delay.

Does not recompute walk. Does not invent jobs. Writes off-axis medians only.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from copy import deepcopy
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from shapely import wkt
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform

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
    od_times,
    zone_index,
)

NET = ROOT / "03_network" / "working"
INP = ROOT / "02_inventory" / "input"
OUT = ROOT / "04_accessibility" / "working"
ACC = OUT / "access_sections.csv"

from pyproj import Transformer

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)


def try_amenity_weights(z: pd.DataFrame, t_pre, t_post, mask_off):
    """OSM amenity nodes aggregated to census sections. Optional robustness."""
    import requests
    from shapely import wkt as _wkt

    south, west, north, east = 41.32, 2.05, 41.47, 2.23
    q = f"""
    [out:json][timeout:180];
    node["amenity"~"^(school|university|kindergarten|college|hospital|clinic|doctors|pharmacy|library|community_centre)$"]({south},{west},{north},{east});
    out;
    """
    try:
        r = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": q},
            timeout=200,
            headers={"User-Agent": "accessibility-rsr-research/0.1"},
        )
        r.raise_for_status()
        els = r.json().get("elements", [])
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    if len(els) < 50:
        return {"ok": False, "error": f"too_few_nodes_{len(els)}"}
    sec = json.loads((INP / "seccions_censals.json").read_text(encoding="utf-8"))
    polys = []
    for s in sec:
        poly = _wkt.loads(s["geometria_etrs89"])
        seccio = int(s["codi_districte"]) * 1000 + int(s["codi_seccio_censal"])
        polys.append((seccio, poly))
    counts = {s: 0 for s, _ in polys}
    for el in els:
        lon, lat = el.get("lon"), el.get("lat")
        if lon is None:
            continue
        x, y = TO_UTM.transform(lon, lat)
        p = Point(x, y)
        for seccio, poly in polys:
            if poly.contains(p) or poly.touches(p):
                counts[seccio] += 1
                break
    o = np.array([float(counts.get(int(s), 0.0)) for s in z["seccio"]])
    a_pre, _ = cumulative(t_pre, o, CAR15)
    a_post, _ = cumulative(t_post, o, CAR15)
    med_pct, med_d = off_median_pct(a_pre, a_post, mask_off)
    return {
        "ok": True,
        "n_nodes": int(len(els)),
        "n_in_sections": int(sum(counts.values())),
        "sections_with_amenity": int(sum(1 for v in counts.values() if v > 0)),
        "off_median_pct_car15_x100": round(med_pct, 3),
        "off_median_dA": round(med_d, 2),
        "note": "O_j = OSM amenity node count (education, health, library, community). Not jobs.",
    }


def consell_heading():
    fc = json.loads((INP / "phase1_principal.geojson").read_text(encoding="utf-8"))
    feat = next(f for f in fc["features"] if f["properties"]["axis"] == "consell_de_cent")
    ln = shp_transform(lambda x, y, z=None: TO_UTM.transform(x, y), shape(feat["geometry"]))
    x1, y1 = ln.coords[0]
    x2, y2 = ln.coords[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def slow_parallels(G: nx.DiGraph, factor: float = 1.2) -> tuple[nx.DiGraph, dict]:
    hx, hy = consell_heading()
    H = G.copy()
    n_slow = 0
    km = 0.0
    for u, v, d in G.edges(data=True):
        if d.get("treated"):
            continue
        da = d.get("d_axis")
        if da is None or not (80.0 <= float(da) <= 400.0):
            continue
        x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
        x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
        ex, ey = x2 - x1, y2 - y1
        ne = math.hypot(ex, ey) or 1.0
        if abs(ex * hx + ey * hy) / ne < 0.8:
            continue
        H[u][v]["time"] = float(d["time"]) * factor
        n_slow += 1
        km += float(d["length"]) / 1000.0
    return H, {"n_edges": n_slow, "directed_km": round(km, 2), "factor": factor}


def off_median_pct(pre, post, mask):
    pct = np.where(pre[mask] > 0, 100.0 * (post[mask] - pre[mask]) / pre[mask], np.nan)
    return float(np.nanmedian(pct)), float(np.nanmedian(post[mask] - pre[mask]))


def main():
    scores = pd.read_csv(ACC)
    off = (scores["snapped"] == True) & (scores["d_axis_net_m"] > 0)
    on = (scores["snapped"] == True) & (scores["d_axis_net_m"] == 0)
    on_tab = scores.loc[on, ["seccio", "nom_barri", "pop", "pct_car15", "pct_car15_drop"]].sort_values("pct_car15")
    on_tab.to_csv(OUT / "on_axis_all.csv", index=False)
    stubborn = scores.loc[scores.seccio.isin([2065, 2144, 2093]), ["seccio", "nom_barri", "pop", "pct_car15", "pct_car15_drop"]]
    stubborn.to_csv(OUT / "on_axis_stubborn.csv", index=False)

    print("load graphs", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    snaps = load_snaps("sections_snapped_car.csv")
    mat_pre, nodes_pre, idx_pre = csr_time(G_pre)
    z = zone_index(snaps, idx_pre)
    orig_i = z["gi"].to_numpy()
    pop = z["pop"].to_numpy(dtype=float)
    seccio = z["seccio"].to_numpy()
    dnet = scores.set_index("seccio").loc[seccio, "d_axis_net_m"].to_numpy()
    mask_off = dnet > 0

    print("dijkstra pre/post", flush=True)
    t_pre = od_times(mat_pre, orig_i, orig_i, CAR30)
    mat_post, _, idx_post = csr_time(G_post)
    t_post = od_times(mat_post, orig_i, orig_i, CAR30)
    np.fill_diagonal(t_pre, 0.0)
    np.fill_diagonal(t_post, 0.0)

    amenity = try_amenity_weights(z, t_pre, t_post, mask_off)

    betas = {}
    for b in (0.03, 0.05, 0.08):
        hp = hansen(t_pre, pop, b)
        ho = hansen(t_post, pop, b)
        med_pct, med_d = off_median_pct(hp, ho, mask_off)
        # barri ranking: nearby vs far using dnet
        pct = np.where(hp > 0, 100.0 * (ho - hp) / hp, np.nan)
        corr = float(pd.Series(pct[mask_off]).corr(pd.Series(dnet[mask_off])))
        betas[str(b)] = {
            "off_median_pct": round(med_pct, 3),
            "off_median_dA": round(med_d, 1),
            "corr_pct_distance_off": round(corr, 3),
        }

    print("parallel 1.2", flush=True)
    G_para, para_meta = slow_parallels(G_post, 1.2)
    mat_para, _, _ = csr_time(G_para)
    t_para = od_times(mat_para, orig_i, orig_i, CAR30)
    np.fill_diagonal(t_para, 0.0)
    a15_pre, _ = cumulative(t_pre, pop, CAR15)
    a15_para, _ = cumulative(t_para, pop, CAR15)
    a15_post, _ = cumulative(t_post, pop, CAR15)
    med_para, d_para = off_median_pct(a15_pre, a15_para, mask_off)
    med_x100, d_x100 = off_median_pct(a15_pre, a15_post, mask_off)

    # corridor implied speed
    # 2136 -> 2067 already known; recompute minutes
    sidx = {int(s): i for i, s in enumerate(seccio)}
    i_src, i_dst = sidx[2136], sidx[2067]
    tpre_min = float(t_pre[i_src, i_dst] / 60.0)
    tpost_min = float(t_post[i_src, i_dst] / 60.0)
    # Euclidean between centroids
    row_src = scores.loc[scores.seccio == 2136].iloc[0]
    row_dst = scores.loc[scores.seccio == 2067].iloc[0]
    dist_m = math.hypot(float(row_src.x) - float(row_dst.x), float(row_src.y) - float(row_dst.y))
    impl_pre = (dist_m / 1000.0) / (tpre_min / 60.0)

    meta = {
        "design": "single_contemporary_graph_recode",
        "hansen_beta": betas,
        "parallel_1.2_on_consell_aligned_80_400m": {
            **para_meta,
            "off_median_pct_car15": round(med_para, 3),
            "off_median_dA_car15": round(d_para, 1),
            "x100_off_median_pct_car15": round(med_x100, 3),
        },
        "corridor_2136_2067": {
            "euclidean_km": round(dist_m / 1000.0, 2),
            "t_pre_min": round(tpre_min, 2),
            "t_post_min": round(tpost_min, 2),
            "implied_kmh_pre": round(impl_pre, 1),
        },
        "on_axis_n": int(on.sum()),
        "off_axis_n": int(off.sum()),
        "amenity_osm": amenity,
    }
    (OUT / "robustness_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(stubborn.to_string(index=False))


if __name__ == "__main__":
    main()
