"""Build pre/post car and walk graphs for Eixos Verds phase 1.

Car: Paper 1 treated-edge rule (inject principal, angle >= 0.8, midpoint
<= 15 m) with travel *time* as Dijkstra weight. Post = treated time x100.

Walk: OSM pedestrian-usable ways, 4.5 km/h (steps 2 km/h). No invented
green-axis speed-up. Pre and post are the same graph.

Do not rewrite phase1_principal.geojson.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely import wkt
from shapely.geometry import LineString, Point, shape
from shapely.ops import transform, unary_union
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "02_inventory" / "input"
INV = ROOT / "02_inventory" / "working"
OUT = ROOT / "03_network" / "working"

sys.path.insert(0, str(OUT))
from fetch_osm import fetch  # noqa: E402

AXES = INP / "phase1_principal.geojson"
TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)

TREATED_COST = 100.0
SNAP_SECTION_M = 200.0
MUNI_PAD_M = 300.0
INJECT_SPEED_KMH = 30.0
STITCH_SPEED_KMH = 20.0

CAR_HIGHWAY = {
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

CAR_SPEED = {
    "motorway": 80.0,
    "motorway_link": 50.0,
    "trunk": 50.0,
    "trunk_link": 40.0,
    "primary": 50.0,
    "primary_link": 40.0,
    "secondary": 50.0,
    "secondary_link": 40.0,
    "tertiary": 40.0,
    "tertiary_link": 30.0,
    "unclassified": 30.0,
    "residential": 30.0,
    "living_street": 20.0,
    "service": 20.0,
    "injected_principal": INJECT_SPEED_KMH,
    "stitch": STITCH_SPEED_KMH,
}

WALK_CORE = {"footway", "pedestrian", "path", "steps", "living_street", "corridor"}
WALK_GRID = {
    "residential",
    "unclassified",
    "service",
    "track",
    "cycleway",
    "tertiary",
    "tertiary_link",
    "secondary",
    "secondary_link",
    "primary",
    "primary_link",
}
NO_FOOT = {"no", "private", "discouraged", "use_sidepath"}
NO_MOTOR = {"no", "private", "agricultural", "forestry"}


def to_utm(geom):
    return transform(lambda x, y, z=None: TO_UTM.transform(x, y), geom)


def node_key(x, y):
    return (round(x, 1), round(y, 1))


def parse_maxspeed(tags: dict, default: float) -> float:
    raw = tags.get("maxspeed")
    if not raw:
        return default
    s = str(raw).split(";")[0].strip().lower()
    if s in {"none", "signals", "walk", "variable"}:
        return default
    if s.startswith("es:"):
        return {"urban": 50.0, "living_street": 20.0, "rural": 90.0, "motorway": 120.0}.get(
            s[3:], default
        )
    s = s.replace("km/h", "").replace("kmh", "").strip()
    try:
        v = float(s)
    except ValueError:
        return default
    if 5.0 <= v <= 130.0:
        return v
    return default


def time_s(length_m: float, kmh: float) -> float:
    return float(length_m) / (max(kmh, 1.0) / 3.6)


def load_axes_utm():
    fc = json.loads(AXES.read_text(encoding="utf-8"))
    lines = {f["properties"]["axis"]: to_utm(shape(f["geometry"])) for f in fc["features"]}
    return unary_union(list(lines.values())), lines


def load_muni_clip():
    barris = json.loads((INP / "barris.json").read_text(encoding="utf-8"))
    u = unary_union([wkt.loads(b["geometria_etrs89"]) for b in barris])
    return prep(u.buffer(MUNI_PAD_M)), u.buffer(MUNI_PAD_M)


def edge_along_axis(x1, y1, x2, y2, axes_utm, d_mid: float) -> bool:
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


def walk_ok(tags: dict) -> bool:
    hw = tags.get("highway")
    if not hw or hw in {"motorway", "motorway_link"}:
        return False
    foot = str(tags.get("foot", "")).lower()
    if foot in NO_FOOT:
        return False
    if hw in WALK_CORE or hw in WALK_GRID:
        return True
    return foot in {"yes", "designated"}


def walk_speed(tags: dict) -> float:
    hw = tags.get("highway")
    if hw == "steps":
        return 2.0
    return 4.5


def car_ok(tags: dict) -> bool:
    hw = tags.get("highway")
    if hw not in CAR_HIGHWAY:
        return False
    motor = str(tags.get("motor_vehicle", tags.get("vehicle", ""))).lower()
    if motor in NO_MOTOR:
        return False
    access = str(tags.get("access", "")).lower()
    if access in NO_MOTOR and motor not in {"yes", "designated"}:
        return False
    return True


def add_segment(G, x1, y1, x2, y2, *, axes_utm, clip_p, tags, mode: str):
    p1, p2 = Point(x1, y1), Point(x2, y2)
    if not (clip_p.contains(p1) or clip_p.contains(p2) or clip_p.intersects(LineString([(x1, y1), (x2, y2)]))):
        return
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 0.5:
        return
    n1, n2 = node_key(x1, y1), node_key(x2, y2)
    G.add_node(n1, x=n1[0], y=n1[1])
    G.add_node(n2, x=n2[0], y=n2[1])
    d_axis = float(Point((x1 + x2) / 2.0, (y1 + y2) / 2.0).distance(axes_utm))
    treated = mode == "car" and edge_along_axis(x1, y1, x2, y2, axes_utm, d_axis)
    hw = tags.get("highway")
    if mode == "car":
        kmh = parse_maxspeed(tags, CAR_SPEED.get(hw, 30.0))
        oneway = str(tags.get("oneway", "no")).lower()
        if oneway in {"yes", "true", "1"}:
            dirs = [(n1, n2)]
        elif oneway in {"-1", "reverse"}:
            dirs = [(n2, n1)]
        else:
            dirs = [(n1, n2), (n2, n1)]
    else:
        kmh = walk_speed(tags)
        dirs = [(n1, n2), (n2, n1)]
    t = time_s(length, kmh)
    for u, v in dirs:
        if G.has_edge(u, v) and G[u][v]["time"] <= t:
            continue
        G.add_edge(
            u,
            v,
            length=length,
            time=t,
            speed_kmh=kmh,
            d_axis=d_axis,
            treated=treated,
            highway=hw,
            mode=mode,
        )


def build_graph(osm: dict, clip_p, axes_utm, mode: str) -> nx.DiGraph:
    G = nx.DiGraph()
    for el in osm.get("elements", []):
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        if mode == "car" and not car_ok(tags):
            continue
        if mode == "walk" and not walk_ok(tags):
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        coords = [TO_UTM.transform(p["lon"], p["lat"]) for p in geom]
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            add_segment(G, x1, y1, x2, y2, axes_utm=axes_utm, clip_p=clip_p, tags=tags, mode=mode)
    return G


def inject_principal(G: nx.DiGraph, lines: dict, snap_m: float = 22.0, stitch_m: float = 40.0, step_m: float = 12.0):
    osm_nodes = list(G.nodes())
    n_new = 0
    n_snap = 0
    injected_m = 0.0
    for _name, line in lines.items():
        nseg = max(int(line.length / step_m), 1)
        chain = []
        for i in range(nseg + 1):
            p = line.interpolate(i * line.length / nseg)
            n_osm, _d = nearest_from(G, osm_nodes, p.x, p.y, snap_m)
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
                    t = time_s(conn, STITCH_SPEED_KMH)
                    for u, v in ((n, n_grid), (n_grid, n)):
                        if not G.has_edge(u, v):
                            G.add_edge(
                                u,
                                v,
                                length=conn,
                                time=t,
                                speed_kmh=STITCH_SPEED_KMH,
                                d_axis=0.0,
                                treated=False,
                                highway="stitch",
                                mode="car",
                            )
            chain.append(n)
        for a, b in zip(chain, chain[1:]):
            if a == b:
                continue
            length = math.hypot(a[0] - b[0], a[1] - b[1])
            if length < 0.5:
                continue
            t = time_s(length, INJECT_SPEED_KMH)
            for u, v in ((a, b), (b, a)):
                if G.has_edge(u, v) and G[u][v].get("treated"):
                    continue
                G.add_edge(
                    u,
                    v,
                    length=length,
                    time=t,
                    speed_kmh=INJECT_SPEED_KMH,
                    d_axis=0.0,
                    treated=True,
                    highway="injected_principal",
                    mode="car",
                )
                injected_m += length
    return {
        "n_new_nodes": n_new,
        "n_snapped_vertices": n_snap,
        "injected_directed_km": round(injected_m / 1000.0, 3),
    }


def copy_edge_attrs(G: nx.DiGraph) -> nx.DiGraph:
    H = nx.DiGraph()
    for n, d in G.nodes(data=True):
        H.add_node(n, **d)
    for u, v, d in G.edges(data=True):
        H.add_edge(u, v, **dict(d))
    return H


def penalise_treated(G: nx.DiGraph, factor: float) -> nx.DiGraph:
    H = copy_edge_attrs(G)
    for _u, _v, d in H.edges(data=True):
        if d.get("treated"):
            d["length"] = d["length"] * factor
            d["time"] = d["time"] * factor
    return H


def drop_treated(G: nx.DiGraph) -> nx.DiGraph:
    H = copy_edge_attrs(G)
    H.remove_edges_from([(u, v) for u, v, d in G.edges(data=True) if d.get("treated")])
    return H


def giant(G: nx.DiGraph) -> nx.DiGraph:
    if G.number_of_nodes() == 0:
        return G
    und = G.to_undirected(as_view=True)
    nodes = max(nx.connected_components(und), key=len)
    return G.subgraph(nodes).copy()


def treated_km(G: nx.DiGraph) -> float:
    return sum(d["length"] for _u, _v, d in G.edges(data=True) if d.get("treated")) / 1000.0


def snap_sections(G: nx.DiGraph, sections: pd.DataFrame, max_m: float) -> pd.DataFrame:
    nodes = list(G.nodes())
    xy = np.array([[G.nodes[n]["x"], G.nodes[n]["y"]] for n in nodes])
    tree = cKDTree(xy)
    pts = sections[["x", "y"]].to_numpy()
    dist, idx = tree.query(pts, k=1)
    rows = []
    for i, r in enumerate(sections.itertuples(index=False)):
        d = float(dist[i])
        node = nodes[int(idx[i])] if d <= max_m else None
        rows.append(
            {
                "seccio": int(r.seccio),
                "codi_barri": int(r.codi_barri),
                "nom_barri": r.nom_barri,
                "nom_districte": r.nom_districte,
                "x": float(r.x),
                "y": float(r.y),
                "d_axis_m": float(r.d_axis_m),
                "pop": float(r.pop),
                "node_x": None if node is None else node[0],
                "node_y": None if node is None else node[1],
                "snap_m": round(d, 1),
                "snapped": node is not None,
            }
        )
    return pd.DataFrame(rows)


def dump(G: nx.DiGraph, path: Path) -> None:
    with path.open("wb") as f:
        pickle.dump(G, f, protocol=4)


def node_tuple(row) -> tuple | None:
    if not bool(row.snapped):
        return None
    if hasattr(row, "node") and isinstance(row.node, tuple):
        return row.node
    return (float(row.node_x), float(row.node_y))


def od_minutes(G, src, dst):
    if src is None or dst is None or src not in G or dst not in G:
        return None
    try:
        return nx.shortest_path_length(G, src, dst, weight="time") / 60.0
    except nx.NetworkXNoPath:
        return None


def smoke_test(G_pre, G_post, G_drop, snaps: pd.DataFrame, snaps_drop: pd.DataFrame) -> dict:
    near = snaps.loc[snaps.snapped].nsmallest(1, "d_axis_m").iloc[0]
    far = snaps.loc[snaps.snapped].nlargest(1, "d_axis_m").iloc[0]
    band = snaps.loc[(snaps.snapped) & (snaps.d_axis_m < 150)]
    pair = {}
    if len(band) >= 2:
        src_row = band.nsmallest(1, "x").iloc[0]
        dst_row = band.nlargest(1, "x").iloc[0]
        src, dst = node_tuple(src_row), node_tuple(dst_row)
        t_pre = od_minutes(G_pre, src, dst)
        t_post = od_minutes(G_post, src, dst)
        dsrc = snaps_drop.loc[snaps_drop.seccio == src_row.seccio].iloc[0]
        ddst = snaps_drop.loc[snaps_drop.seccio == dst_row.seccio].iloc[0]
        t_drop = od_minutes(G_drop, node_tuple(dsrc), node_tuple(ddst))
        pair = {
            "src_seccio": int(src_row.seccio),
            "dst_seccio": int(dst_row.seccio),
            "t_pre_min": None if t_pre is None else round(t_pre, 3),
            "t_post_x100_min": None if t_post is None else round(t_post, 3),
            "t_post_drop_min": None if t_drop is None else round(t_drop, 3),
            "dt_x100_min": None if t_pre is None or t_post is None else round(t_post - t_pre, 3),
            "dt_drop_min": None if t_pre is None or t_drop is None else round(t_drop - t_pre, 3),
        }
    return {
        "nearest_axis_seccio": int(near.seccio),
        "nearest_axis_snap_m": float(near.snap_m),
        "farthest_axis_seccio": int(far.seccio),
        "farthest_axis_d_m": float(far.d_axis_m),
        "unsnapped_car": [int(x) for x in snaps.loc[~snaps.snapped, "seccio"]],
        "axis_end_od": pair,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("fetch OSM", flush=True)
    osm = fetch()
    print("ways", len(osm.get("elements", [])), flush=True)
    axes_utm, lines = load_axes_utm()
    clip_p, _clip = load_muni_clip()

    print("build car", flush=True)
    car = build_graph(osm, clip_p, axes_utm, "car")
    inject = inject_principal(car, lines)
    car = giant(car)
    car_post = penalise_treated(car, TREATED_COST)
    car_drop = giant(drop_treated(car))

    print("build walk", flush=True)
    walk = giant(build_graph(osm, clip_p, axes_utm, "walk"))

    sections = pd.read_csv(INV / "section_centroids.csv")
    snaps_car = snap_sections(car, sections, SNAP_SECTION_M)
    snaps_walk = snap_sections(walk, sections, SNAP_SECTION_M)
    snaps_drop = snap_sections(car_drop, sections, SNAP_SECTION_M)
    snaps_car.to_csv(OUT / "sections_snapped_car.csv", index=False)
    snaps_walk.to_csv(OUT / "sections_snapped_walk.csv", index=False)
    snaps_drop.to_csv(OUT / "sections_snapped_car_drop.csv", index=False)

    dump(car, OUT / "car_pre.pkl")
    dump(car_post, OUT / "car_post.pkl")
    dump(car_drop, OUT / "car_post_drop.pkl")
    dump(walk, OUT / "walk.pkl")

    smoke = smoke_test(car, car_post, car_drop, snaps_car, snaps_drop)
    hw_car = Counter(d.get("highway") for _u, _v, d in car.edges(data=True))
    meta = {
        "built_utc": datetime.now(timezone.utc).isoformat(),
        "treated_cost": TREATED_COST,
        "snap_section_m": SNAP_SECTION_M,
        "inject": inject,
        "car_pre": {
            "n_nodes": car.number_of_nodes(),
            "n_edges": car.number_of_edges(),
            "treated_directed_km": round(treated_km(car), 3),
            "highways": dict(hw_car.most_common(15)),
        },
        "car_post_drop": {
            "n_nodes": car_drop.number_of_nodes(),
            "n_edges": car_drop.number_of_edges(),
        },
        "walk": {
            "n_nodes": walk.number_of_nodes(),
            "n_edges": walk.number_of_edges(),
            "note": "pre_equals_post_no_invented_speedup",
        },
        "snap_car": {
            "n": int(len(snaps_car)),
            "n_snapped": int(snaps_car.snapped.sum()),
            "median_snap_m": float(snaps_car.loc[snaps_car.snapped, "snap_m"].median())
            if snaps_car.snapped.any()
            else None,
            "max_snap_m": float(snaps_car.loc[snaps_car.snapped, "snap_m"].max())
            if snaps_car.snapped.any()
            else None,
        },
        "snap_walk": {
            "n": int(len(snaps_walk)),
            "n_snapped": int(snaps_walk.snapped.sum()),
            "median_snap_m": float(snaps_walk.loc[snaps_walk.snapped, "snap_m"].median())
            if snaps_walk.snapped.any()
            else None,
        },
        "snap_car_drop": {
            "n": int(len(snaps_drop)),
            "n_snapped": int(snaps_drop.snapped.sum()),
            "median_snap_m": float(snaps_drop.loc[snaps_drop.snapped, "snap_m"].median())
            if snaps_drop.snapped.any()
            else None,
        },
        "smoke": smoke,
        "labels": {
            "T_ij": "simulated",
            "walk_delta": "zero_by_construction_until_stated_scenario",
        },
    }
    (OUT / "graph_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
