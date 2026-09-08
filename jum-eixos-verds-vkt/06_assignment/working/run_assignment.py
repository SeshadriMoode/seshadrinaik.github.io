"""Count-constrained assignment for LTR / NR / NVTR (Step 6).

Open-data procedure, not a measurement of network VKT.

Prior OD: gravity on 2022 padro population by barri, AON on the OSM
motorised graph. Count constraint: origin/destination scaling (Furness)
to match working-day MADT at aforament stations.

Scenarios (labels are locked):
  estimated_pre      — gravity + counts on the pre network (2022 H1 Q)
  simulated_fixed    — same OD, phase-1 centreline cost x100 (forced-turn proxy)
  estimated_elastic  — refit OD to 2024-25 Q on the penalised network

ATM/EMEF is not in the repo. This prior is a placeholder until that file
arrives. Through-traffic from outside the 3.5 km buffer is aliased into
local OD via the count fit. Do not call the output measured VKT.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import requests
from scipy.optimize import minimize
from shapely import wkt
from shapely.geometry import LineString, Point
from shapely.ops import transform, unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / "04_geometry" / "working"
DID = ROOT / "05_did_delta_q" / "working"
OUT = ROOT / "06_assignment" / "working"
FIG = ROOT / "06_assignment" / "figures"
RAW = OUT / "raw"

OSM = GEO / "osm_highways_phase1_buffer.json"
AXES = GEO / "phase1_principal.geojson"
COUNTS = DID / "station_delta_q_incremental_2022h1.csv"

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
HEADERS = {"User-Agent": "network-vkt-rsr-research/0.1"}

BUFFER_M = 3500
SNAP_ZONE_M = 500
SNAP_STATION_M = 80
TREATED_M = 20
TREATED_COST = 100.0
GRAV_BETA = 2.0
LOCAL_M = 40.0
RINGS = [40, 250, 500, 1000, 2000, 3500]
HIGHWAY_OK = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
}

BARRIS_URL = "https://opendata-ajuntament.barcelona.cat/data/dataset/808daafa-d9ce-48c0-925a-fa5afdb1ed41/resource/75197dfe-0306-4c5e-9643-34948af07fb6/download"
PAD_URL = "https://opendata-ajuntament.barcelona.cat/data/dataset/2f6e0561-30f4-44a0-8446-e27442d4754c/resource/78b965d3-b2dc-4f23-91b9-59caa45bc334/download"


def to_utm(geom):
    return transform(lambda x, y, z=None: TO_UTM.transform(x, y), geom)


def download() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    files = {"barris.json": BARRIS_URL, "2022_pad_mdbas.csv": PAD_URL}
    for name, url in files.items():
        dest = RAW / name
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        r = requests.get(url, headers=HEADERS, timeout=180)
        r.raise_for_status()
        dest.write_bytes(r.content)


def load_axes():
    from shapely.geometry import shape

    fc = json.loads(AXES.read_text(encoding="utf-8"))
    return unary_union([to_utm(shape(f["geometry"])) for f in fc["features"]])


def load_principal_lines():
    from shapely.geometry import shape

    fc = json.loads(AXES.read_text(encoding="utf-8"))
    return {f["properties"]["axis"]: to_utm(shape(f["geometry"])) for f in fc["features"]}


def nearest_from(G: nx.DiGraph, nodes, x: float, y: float, max_m: float):
    best, best_d = None, 1e18
    for n in nodes:
        d = G.nodes[n]
        dist = math.hypot(d["x"] - x, d["y"] - y)
        if dist < best_d:
            best, best_d = n, dist
    if best is None or best_d > max_m:
        return None, best_d
    return best, best_d


def inject_principal(G: nx.DiGraph, lines: dict, snap_m: float = 22.0, stitch_m: float = 40.0, step_m: float = 12.0):
    """Put the as-built ~4.85 km centrelines on the graph.

    OSM has retagged parts of Consell de Cent off the motorised extract.
    Injected edges carry traffic in the pre network and are penalised post.
    Vertices snap to existing OSM nodes at crossings; new nodes in gaps are
    stitched to the nearest OSM node within stitch_m.
    """
    osm_nodes = list(G.nodes())
    n_new = 0
    n_snap = 0
    injected_m = 0.0
    for _name, line in lines.items():
        nseg = max(int(line.length / step_m), 1)
        chain = []
        for i in range(nseg + 1):
            p = line.interpolate(i * line.length / nseg)
            n_osm, d_osm = nearest_from(G, osm_nodes, p.x, p.y, snap_m)
            if n_osm is not None:
                chain.append(n_osm)
                n_snap += 1
                continue
            n = node_key(p.x, p.y)
            if n not in G:
                G.add_node(n, x=n[0], y=n[1])
                n_new += 1
                n_grid, d_grid = nearest_from(G, osm_nodes, p.x, p.y, stitch_m)
                if n_grid is not None:
                    conn = max(d_grid, 0.5)
                    for u, v in ((n, n_grid), (n_grid, n)):
                        if not G.has_edge(u, v):
                            G.add_edge(u, v, length=conn, d_axis=0.0, treated=False)
            chain.append(n)
        for a, b in zip(chain, chain[1:]):
            if a == b:
                continue
            length = math.hypot(a[0] - b[0], a[1] - b[1])
            if length < 0.5:
                continue
            for u, v in ((a, b), (b, a)):
                if G.has_edge(u, v) and G[u][v].get("treated"):
                    continue
                G.add_edge(u, v, length=length, d_axis=0.0, treated=True)
                injected_m += length
    return {
        "n_new_nodes": n_new,
        "n_snapped_vertices": n_snap,
        "injected_directed_km": round(injected_m / 1000.0, 3),
    }


def node_key(x, y):
    return (round(x, 1), round(y, 1))


def edge_along_axis(x1, y1, x2, y2, axes_utm, d_mid: float) -> bool:
    """True only for links that run along the green axis, not the crossing stub."""
    if d_mid > 15.0:
        return False
    mid = Point((x1 + x2) / 2.0, (y1 + y2) / 2.0)
    d = axes_utm.project(mid)
    p0 = axes_utm.interpolate(max(d - 8.0, 0.0))
    p1 = axes_utm.interpolate(min(d + 8.0, axes_utm.length))
    tx, ty = p1.x - p0.x, p1.y - p0.y
    nt = math.hypot(tx, ty) or 1.0
    ex, ey = x2 - x1, y2 - y1
    ne = math.hypot(ex, ey) or 1.0
    return abs(ex * tx + ey * ty) / (ne * nt) >= 0.8


def build_digraph(osm: dict, clip, axes_utm):
    G = nx.DiGraph()
    for el in osm.get("elements", []):
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        if tags.get("highway") not in HIGHWAY_OK:
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        coords = [TO_UTM.transform(p["lon"], p["lat"]) for p in geom]
        oneway = str(tags.get("oneway", "no")).lower()
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            p1, p2 = Point(x1, y1), Point(x2, y2)
            if not (
                clip.contains(p1)
                or clip.contains(p2)
                or clip.intersects(LineString([(x1, y1), (x2, y2)]))
            ):
                continue
            length = math.hypot(x2 - x1, y2 - y1)
            if length < 0.5:
                continue
            n1, n2 = node_key(x1, y1), node_key(x2, y2)
            G.add_node(n1, x=n1[0], y=n1[1])
            G.add_node(n2, x=n2[0], y=n2[1])
            d_axis = float(Point((x1 + x2) / 2.0, (y1 + y2) / 2.0).distance(axes_utm))
            treated = edge_along_axis(x1, y1, x2, y2, axes_utm, d_axis)
            if oneway in {"yes", "true", "1"}:
                dirs = [(n1, n2)]
            elif oneway in {"-1", "reverse"}:
                dirs = [(n2, n1)]
            else:
                dirs = [(n1, n2), (n2, n1)]
            for u, v in dirs:
                if G.has_edge(u, v) and G[u][v]["length"] <= length:
                    continue
                G.add_edge(u, v, length=length, d_axis=d_axis, treated=treated)
    return G


def copy_edge_attrs(G: nx.DiGraph) -> nx.DiGraph:
    """Copy the graph with independent edge-attribute dicts.

    NetworkX ``copy()`` shares those dicts, so a later treated-cost or
    junction-delay mutation would rewrite the pre network in place.
    """
    H = nx.DiGraph()
    for n, d in G.nodes(data=True):
        H.add_node(n, **d)
    for u, v, d in G.edges(data=True):
        H.add_edge(u, v, **dict(d))
    return H


def penalise_treated(G: nx.DiGraph, factor: float) -> nx.DiGraph:
    H = copy_edge_attrs(G)
    for u, v, d in H.edges(data=True):
        if d.get("treated"):
            d["length"] = d["length"] * factor
    return H


def edge_tables(G: nx.DiGraph):
    edges = list(G.edges())
    uv_to_i = {uv: i for i, uv in enumerate(edges)}
    length = np.array([G[u][v]["length"] for u, v in edges], dtype=float)
    d_axis = np.array([G[u][v]["d_axis"] for u, v in edges], dtype=float)
    treated = np.array([bool(G[u][v]["treated"]) for u, v in edges])
    return edges, uv_to_i, length, d_axis, treated


def snap_node(G: nx.DiGraph, x: float, y: float, max_m: float):
    best, best_d = None, 1e18
    for n, d in G.nodes(data=True):
        dist = math.hypot(d["x"] - x, d["y"] - y)
        if dist < best_d:
            best, best_d = n, dist
    if best is None or best_d > max_m:
        return None, best_d
    return best, best_d


def point_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 < 1e-9:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def snap_stations(G, stations: pd.DataFrame, uv_to_i: dict, max_m: float):
    rows = []
    for r in stations.itertuples(index=False):
        x, y = TO_UTM.transform(float(r.lon), float(r.lat))
        node, nd = snap_node(G, x, y, max_m)
        if node is None:
            continue
        best_i, best_d = None, 1e18
        for u, v in list(G.out_edges(node)) + list(G.in_edges(node)):
            i = uv_to_i.get((u, v))
            if i is None:
                continue
            d = point_seg_dist(x, y, u[0], u[1], v[0], v[1])
            if d < best_d:
                best_d, best_i = d, i
        if best_i is None or best_d > max_m:
            continue
        rows.append(
            {
                "station_id": str(r.station_id),
                "desc": r.desc,
                "did_bin": r.did_bin,
                "q_pre": float(r.q_pre),
                "q_post": float(r.q_post),
                "delta_q": float(r.delta_q),
                "edge_i": int(best_i),
                "snap_m": round(best_d, 1),
                "is_tac2020_other": bool(r.is_tac2020_other),
            }
        )
    return pd.DataFrame(rows)


def load_zones(G: nx.DiGraph) -> pd.DataFrame:
    barris = json.loads((RAW / "barris.json").read_text(encoding="utf-8"))
    pad = pd.read_csv(RAW / "2022_pad_mdbas.csv")
    pop = pad.groupby("Codi_Barri", as_index=False)["Valor"].sum().rename(
        columns={"Valor": "pop", "Codi_Barri": "codi"}
    )
    pop["codi"] = pop["codi"].astype(int)
    rows = []
    for b in barris:
        poly = wkt.loads(b["geometria_etrs89"])
        c = poly.centroid
        node, snap = snap_node(G, c.x, c.y, SNAP_ZONE_M)
        rows.append(
            {
                "codi": int(b["codi_barri"]),
                "name": b["nom_barri"],
                "district": b["nom_districte"],
                "x": c.x,
                "y": c.y,
                "node": node,
                "snap_m": snap,
            }
        )
    z = pd.DataFrame(rows).merge(pop, on="codi", how="left")
    z["pop"] = z["pop"].fillna(0)
    z = z.loc[z["node"].notna()].reset_index(drop=True)
    return z


def od_paths(G: nx.DiGraph, zone_nodes: list, uv_to_i: dict):
    n = len(zone_nodes)
    dist = np.full((n, n), np.inf)
    paths: dict[tuple[int, int], np.ndarray] = {}
    for i, src in enumerate(zone_nodes):
        pred, dmap = nx.dijkstra_predecessor_and_distance(G, src, weight="length")
        for j, dst in enumerate(zone_nodes):
            if i == j or dst not in dmap:
                continue
            dist[i, j] = dmap[dst]
            chain = [dst]
            cur = dst
            ok = True
            seen = set()
            while cur != src:
                if cur in seen or cur not in pred or not pred[cur]:
                    ok = False
                    break
                seen.add(cur)
                cur = pred[cur][0]
                chain.append(cur)
            if not ok:
                continue
            chain.reverse()
            eids = []
            for a, b in zip(chain, chain[1:]):
                k = uv_to_i.get((a, b))
                if k is None:
                    eids = []
                    break
                eids.append(k)
            if eids:
                paths[i, j] = np.array(eids, dtype=np.int32)
    return dist, paths


def gravity(pop: np.ndarray, dist: np.ndarray, beta: float) -> np.ndarray:
    n = len(pop)
    T = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j or not np.isfinite(dist[i, j]) or dist[i, j] < 1:
                continue
            T[i, j] = pop[i] * pop[j] / (dist[i, j] ** beta)
    return T


def assign(T: np.ndarray, paths: dict, n_edges: int) -> np.ndarray:
    q = np.zeros(n_edges)
    for (i, j), eids in paths.items():
        t = T[i, j]
        if t <= 0:
            continue
        q[eids] += t
    return q


def scale_to_counts(T: np.ndarray, paths, n_edges, station_e, q_obs) -> tuple[np.ndarray, float]:
    q = assign(T, paths, n_edges)
    pred = q[station_e]
    mask = pred > 1
    if not mask.any():
        return T, 1.0
    k = float(np.median(q_obs[mask] / pred[mask]))
    k = max(k, 1e-9)
    return T * k, k


def furness_fit(T0: np.ndarray, paths, n_edges, station_e, q_obs, lam: float = 1.0, maxiter: int = 25):
    n = T0.shape[0]
    x0 = np.zeros(2 * n)

    def unpack(x):
        a, g = x[:n], x[n:]
        # pin first dest
        g = g - g[0]
        return T0 * np.exp(a[:, None] + g[None, :])

    def obj(x):
        T = unpack(x)
        q = assign(T, paths, n_edges)
        r = q[station_e] - q_obs
        return 0.5 * float(r @ r) + 0.5 * lam * float(x @ x)

    res = minimize(obj, x0, method="L-BFGS-B", options={"maxiter": maxiter, "ftol": 1e-5})
    T = unpack(res.x)
    T[np.diag_indices(n)] = 0
    a, g = res.x[:n], res.x[n:]
    res.factor_a_range = (float(np.min(a)), float(np.max(a)))
    res.factor_g_range = (float(np.min(g - g[0])), float(np.max(g - g[0])))
    return T, res


def vkt_by_ring(q: np.ndarray, length: np.ndarray, d_axis: np.ndarray, rings=RINGS):
    vkt = q * length / 1000.0
    rows = []
    prev = 0.0
    for r in rings:
        m = (d_axis > prev) & (d_axis <= r)
        rows.append({"ring_m": r, "vkt": float(vkt[m].sum()), "n_edges": int(m.sum())})
        prev = r
    return pd.DataFrame(rows), float(vkt.sum())


def fit_report(q, station_e, q_obs) -> dict:
    pred = q[station_e]
    resid = pred - q_obs
    mape = float(np.mean(np.abs(resid) / np.maximum(q_obs, 1)))
    rmse = float(np.sqrt(np.mean(resid**2)))
    if pred.std() < 1e-6 or q_obs.std() < 1e-6:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(pred, q_obs)[0, 1])
    return {"n": int(len(q_obs)), "rmse": round(rmse, 1), "mape": round(mape, 3), "corr": round(corr, 3)}


def decompose(vkt_pre, vkt_post, d_axis, length, q_pre, q_post, local_m=LOCAL_M):
    local = d_axis <= local_m
    dvkt = (q_post - q_pre) * length / 1000.0
    d_local = float(dvkt[local].sum())
    d_else = float(dvkt[~local].sum())
    d_tot = d_local + d_else
    return {
        "local_m": local_m,
        "vkt_pre_local": float((q_pre[local] * length[local] / 1000).sum()),
        "vkt_post_local": float((q_post[local] * length[local] / 1000).sum()),
        "vkt_pre_else": float((q_pre[~local] * length[~local] / 1000).sum()),
        "vkt_post_else": float((q_post[~local] * length[~local] / 1000).sum()),
        "vkt_pre": vkt_pre,
        "vkt_post": vkt_post,
        "LTR": -d_local,
        "NR": d_else,
        "NVTR": -d_tot,
        "delta_vkt_total": d_tot,
    }


def footprint(rings: pd.DataFrame, col: str) -> dict:
    mag = rings[col].abs().to_numpy(float)
    tot = float(mag.sum())
    if tot <= 0:
        return {"radius_m": None, "share_at_radius": None, "rule": "share_of_abs_dvkt"}
    cum = 0.0
    for r, a in zip(rings["ring_m"], mag):
        cum += a
        if cum / tot >= 0.8:
            return {
                "radius_m": int(r),
                "share_at_radius": round(cum / tot, 3),
                "rule": "smallest_D_with_80pct_of_abs_dVKT",
            }
    return {
        "radius_m": int(rings["ring_m"].max()),
        "share_at_radius": 1.0,
        "rule": "smallest_D_with_80pct_of_abs_dVKT",
    }


def plot_decomp(rows: list[dict], path: Path) -> None:
    labs = [r["scenario"] for r in rows]
    x = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.axhline(0, color="#333", lw=0.8)
    w = 0.25
    ax.bar(x - w, [r["LTR"] for r in rows], w, label="LTR (local reduction)", color="#1d3557")
    ax.bar(x, [r["NR"] for r in rows], w, label="NR (elsewhere change)", color="#e07a5f")
    ax.bar(x + w, [r["NVTR"] for r in rows], w, label="NVTR = LTR - NR", color="#2a9d8f")
    ax.set_xticks(x)
    ax.set_xticklabels(labs, rotation=15, ha="right")
    ax.set_ylabel("vehicle-km / working day (estimated)")
    ax.set_title("LTR / NR / NVTR inside the 3.5 km graph (not measured VKT)")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_rings(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.axhline(0, color="#333", lw=0.8)
    ax.bar(df["ring_label"], df["delta_vkt"], color="#3d5a80")
    ax.set_ylabel("dVKT (veh-km / working day)")
    ax.set_title("Simulated dVKT by network distance (demand-fixed; not measured)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_fit(pred, obs, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    ax.scatter(obs, pred, s=12, alpha=0.6, c="#1d3557")
    m = max(float(np.max(obs)), float(np.max(pred)))
    ax.plot([0, m], [0, m], color="#999", lw=0.8)
    ax.set_xlabel("observed working-day MADT")
    ax.set_ylabel("assigned flow on snapped edge")
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def archive_v01() -> None:
    dest = OUT / "v0.1"
    src = OUT / "vkt_decomposition.csv"
    if not src.exists() or (dest / "vkt_decomposition.csv").exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "vkt_decomposition.csv",
        "vkt_by_network_ring.csv",
        "observed_vs_simulated_delta_q.csv",
        "count_fit_stations.csv",
        "run_meta.json",
        "stations_snapped.csv",
        "zones_in_graph.csv",
    ):
        p = OUT / name
        if p.exists():
            shutil.copy2(p, dest / name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    archive_v01()
    download()

    axes = load_axes()
    clip = axes.buffer(BUFFER_M)
    print("loading OSM", flush=True)
    osm = json.loads(OSM.read_text(encoding="utf-8"))
    print("building digraph", flush=True)
    G = build_digraph(osm, clip, axes)
    print("digraph nodes", G.number_of_nodes(), "edges", G.number_of_edges(), flush=True)
    inj = inject_principal(G, load_principal_lines())
    print("injected", inj, flush=True)
    edges, uv_to_i, length, d_axis, treated = edge_tables(G)
    print("treated edges", int(treated.sum()), "length_km", round(float(length[treated].sum() / 1000), 2), flush=True)

    zones = load_zones(G)
    zones.to_csv(OUT / "zones_in_graph.csv", index=False)
    print("zones snapped", len(zones), "pop", int(zones["pop"].sum()), flush=True)
    zone_nodes = list(zones["node"])
    pop = zones["pop"].to_numpy(float)

    print("AON paths on pre network", flush=True)
    dist, paths = od_paths(G, zone_nodes, uv_to_i)
    print("od pairs with path", len(paths), flush=True)
    T0 = gravity(pop, dist, GRAV_BETA)

    counts = pd.read_csv(COUNTS, dtype={"station_id": str})
    st = snap_stations(G, counts, uv_to_i, SNAP_STATION_M)
    st.to_csv(OUT / "stations_snapped.csv", index=False)
    print("stations snapped", len(st))
    se = st["edge_i"].to_numpy(int)
    q_pre_obs = st["q_pre"].to_numpy(float)
    q_post_obs = st["q_post"].to_numpy(float)

    T_s, k = scale_to_counts(T0, paths, len(edges), se, q_pre_obs)
    print("gravity scale k", round(k, 6))
    print("fitting pre OD to 2022 H1 counts")
    T_pre, res_pre = furness_fit(T_s, paths, len(edges), se, q_pre_obs, lam=5e4)
    q_pre = assign(T_pre, paths, len(edges))
    pre_fit = fit_report(q_pre, se, q_pre_obs)
    print("pre fit", pre_fit, "success", res_pre.success, "fun", round(res_pre.fun, 1))

    G_post = penalise_treated(G, TREATED_COST)
    print("AON paths on penalised post network")
    dist_p, paths_p = od_paths(G_post, zone_nodes, uv_to_i)
    print("od pairs post", len(paths_p))

    q_fixed = assign(T_pre, paths_p, len(edges))
    vkt_pre = float((q_pre * length / 1000).sum())
    vkt_fixed = float((q_fixed * length / 1000).sum())

    def mean_sim_dq(q, q0=None, bin_name="250_500m"):
        m = st["did_bin"].to_numpy() == bin_name
        if not m.any():
            return float("nan")
        base = q_pre if q0 is None else q0
        return float((q[se] - base[se])[m].mean())

    def gravity_beta_row(beta, T_use, q0, q1, fit, success, k_scale):
        v0 = float((q0 * length / 1000).sum())
        v1 = float((q1 * length / 1000).sum())
        de = decompose(v0, v1, d_axis, length, q0, q1)
        sim_250 = mean_sim_dq(q1, q0, "250_500m")
        return {
            "gravity_beta": beta,
            "primary": bool(abs(beta - GRAV_BETA) < 1e-9),
            "gravity_k": k_scale,
            "pre_corr": fit.get("corr"),
            "pre_mape": fit.get("mape"),
            "pre_rmse": fit.get("rmse"),
            "furness_success": bool(success),
            "LTR": de["LTR"],
            "NR": de["NR"],
            "NVTR": de["NVTR"],
            "sim_delta_q_on_immediate": mean_sim_dq(q1, q0, "on_or_immediate"),
            "sim_delta_q_250_500m": sim_250,
            "sim_sign_250_500m_positive": bool(sim_250 > 0),
            "obs_delta_q_250_500m": float(
                st.loc[st["did_bin"] == "250_500m", "delta_q"].mean()
            ),
        }

    print("gravity impedance sensitivity beta=1,2,3 (same AON paths)", flush=True)
    beta_rows = [
        gravity_beta_row(GRAV_BETA, T_pre, q_pre, q_fixed, pre_fit, res_pre.success, k)
    ]
    for beta in (1.0, 3.0):
        print("gravity beta", beta, flush=True)
        T0b = gravity(pop, dist, beta)
        Tsb, kb = scale_to_counts(T0b, paths, len(edges), se, q_pre_obs)
        Tb, resb = furness_fit(Tsb, paths, len(edges), se, q_pre_obs, lam=5e4)
        q0b = assign(Tb, paths, len(edges))
        q1b = assign(Tb, paths_p, len(edges))
        fitb = fit_report(q0b, se, q_pre_obs)
        print("beta", beta, "fit", fitb, "success", resb.success, "sim_250", round(mean_sim_dq(q1b, q0b), 1), flush=True)
        beta_rows.append(gravity_beta_row(beta, Tb, q0b, q1b, fitb, resb.success, kb))
    pd.DataFrame(beta_rows).sort_values("gravity_beta").to_csv(
        OUT / "gravity_beta_sensitivity.csv", index=False
    )

    sensitivity = [
        {
            "treated_cost": TREATED_COST,
            "LTR": None,
            "NR": None,
            "NVTR": None,
            "sim_delta_q_250_500m": mean_sim_dq(q_fixed),
            "n_od_paths": int(len(paths_p)),
            "primary": True,
        }
    ]
    skip_cost_aon = "--skip-cost-aon" in sys.argv
    if skip_cost_aon:
        print("skipping extra cost-factor AON; copying prior x10/x1000 rows", flush=True)
        old_cost = OUT / "cost_factor_sensitivity.csv"
        if old_cost.exists():
            prev = pd.read_csv(old_cost)
            for _, row in prev.iterrows():
                if bool(row.get("primary", False)):
                    continue
                sensitivity.append(
                    {
                        "treated_cost": float(row["treated_cost"]),
                        "LTR": float(row["LTR"]) if pd.notna(row["LTR"]) else None,
                        "NR": float(row["NR"]) if pd.notna(row["NR"]) else None,
                        "NVTR": float(row["NVTR"]) if pd.notna(row["NVTR"]) else None,
                        "sim_delta_q_250_500m": float(row["sim_delta_q_250_500m"]),
                        "n_od_paths": int(row["n_od_paths"]),
                        "primary": False,
                    }
                )
    else:
        for factor in (10.0, 1000.0):
            print("sensitivity cost x", factor, flush=True)
            G_s = penalise_treated(G, factor)
            _dist_s, paths_s = od_paths(G_s, zone_nodes, uv_to_i)
            q_s = assign(T_pre, paths_s, len(edges))
            vkt_s = float((q_s * length / 1000).sum())
            de_s = decompose(vkt_pre, vkt_s, d_axis, length, q_pre, q_s)
            sensitivity.append(
                {
                    "treated_cost": factor,
                    "LTR": de_s["LTR"],
                    "NR": de_s["NR"],
                    "NVTR": de_s["NVTR"],
                    "sim_delta_q_250_500m": mean_sim_dq(q_s),
                    "n_od_paths": int(len(paths_s)),
                    "primary": False,
                }
            )

    decomp_fixed = decompose(vkt_pre, vkt_fixed, d_axis, length, q_pre, q_fixed)
    decomp_fixed["scenario"] = "simulated_demand_fixed"
    decomp = pd.DataFrame([decomp_fixed])
    decomp.to_csv(OUT / "vkt_decomposition.csv", index=False)
    sensitivity[0]["LTR"] = decomp_fixed["LTR"]
    sensitivity[0]["NR"] = decomp_fixed["NR"]
    sensitivity[0]["NVTR"] = decomp_fixed["NVTR"]
    pd.DataFrame(sensitivity).to_csv(OUT / "cost_factor_sensitivity.csv", index=False)

    rings = []
    prev = -1.0
    for r in RINGS:
        m = (d_axis > prev) & (d_axis <= r)
        rings.append(
            {
                "ring_m": r,
                "ring_label": f"{int(max(prev, 0))}-{int(r)} m",
                "vkt_pre": float((q_pre[m] * length[m] / 1000).sum()),
                "vkt_fixed": float((q_fixed[m] * length[m] / 1000).sum()),
                "delta_vkt_fixed": float(((q_fixed - q_pre)[m] * length[m] / 1000).sum()),
            }
        )
        prev = r
    rings_df = pd.DataFrame(rings)
    rings_df.to_csv(OUT / "vkt_by_network_ring.csv", index=False)
    fp_fx = footprint(rings_df, "delta_vkt_fixed")
    print("footprint demand-fixed", fp_fx, flush=True)
    print(decomp.to_string(index=False), flush=True)

    st = st.copy()
    st["q_assigned_pre"] = q_pre[se]
    st["q_assigned_fixed"] = q_fixed[se]
    st["delta_q_simulated_fixed"] = st["q_assigned_fixed"] - st["q_assigned_pre"]
    st["delta_q_residual"] = st["delta_q"] - st["delta_q_simulated_fixed"]
    st.to_csv(OUT / "count_fit_stations.csv", index=False)

    order = [
        "on_or_immediate",
        "0_250m",
        "250_500m",
        "500_1000m",
        "1_2km",
        "control_gt2km",
    ]
    resid_rows = []
    for b in order:
        sub = st.loc[st["did_bin"] == b]
        if sub.empty:
            continue
        resid_rows.append(
            {
                "did_bin": b,
                "n": int(len(sub)),
                "obs_delta_q": round(float(sub["delta_q"].mean()), 1),
                "sim_fixed_delta_q": round(float(sub["delta_q_simulated_fixed"].mean()), 1),
                "residual_obs_minus_sim": round(float(sub["delta_q_residual"].mean()), 1),
            }
        )
    resid = pd.DataFrame(resid_rows)
    resid.to_csv(OUT / "observed_vs_simulated_delta_q.csv", index=False)
    print(resid.to_string(index=False), flush=True)

    meta = {
        "status": "v1.0_principal_centrelines; simulated_demand_fixed_primary; elastic_od_not_identified",
        "assignment_version": "v1.0",
        "prior": "gravity_padro_2022_barri_beta2",
        "count_window": "incremental_2022h1_vs_2024_25",
        "system_boundary_m": BUFFER_M,
        "treated_proxy": "principal_centrelines_injected_plus_osm_aligned_cost_x100",
        "principal_undirected_km": 4.85,
        "inject": inj,
        "pre_fit": pre_fit,
        "gravity_k": k,
        "n_zones": int(len(zones)),
        "n_od_paths_pre": int(len(paths)),
        "n_od_paths_post": int(len(paths_p)),
        "n_stations": int(len(st)),
        "treated_edge_km": round(float(length[treated].sum() / 1000), 3),
        "vkt_pre": vkt_pre,
        "vkt_fixed": vkt_fixed,
        "footprint_fixed": fp_fx,
        "cost_factor_sensitivity": sensitivity,
        "gravity_beta_sensitivity": beta_rows,
        "emef_used": False,
        "elastic_od_refit": False,
    }
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    plot_decomp([decomp_fixed], FIG / "ltr_nr_nvtr.png")
    plot_rings(
        rings_df.rename(columns={"delta_vkt_fixed": "delta_vkt"}),
        FIG / "dvkt_by_ring_fixed.png",
    )
    plot_fit(
        q_pre[se],
        q_pre_obs,
        FIG / "count_fit_pre.png",
        "Count fit pre (2022 H1); assigned vs observed",
    )
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    x = np.arange(len(resid))
    ax.axhline(0, color="#333", lw=0.8)
    ax.bar(x - 0.18, resid["obs_delta_q"], 0.36, label="observed dQ", color="#1d3557")
    ax.bar(
        x + 0.18,
        resid["sim_fixed_delta_q"],
        0.36,
        label="simulated demand-fixed dQ",
        color="#e07a5f",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(resid["did_bin"], rotation=20, ha="right")
    ax.set_ylabel("mean dQ (vehicles / working day)")
    ax.set_title("Observed count change vs demand-fixed reroute (not VKT)")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "observed_vs_simulated_dq.png", dpi=160)
    plt.close(fig)
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
