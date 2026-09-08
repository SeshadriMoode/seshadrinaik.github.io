"""Network distance from traffic stations to Eixos Verds phase 1.

Undirected shortest-path length on OSM motorised highways, UTM 31N metres.
This is the exposure object for Paper 1. Euclidean bins are only a fallback.

Scope: OSM extract in a 3.5 km buffer of the axes. Stations outside the graph
are coded gt_3.5km (control). Directed assignment comes later (Step 6).
"""
from __future__ import annotations

import csv
import json
import math
import time
from pathlib import Path

import networkx as nx
import requests
from shapely.geometry import LineString, Point, box, mapping, shape
from shapely.ops import transform, unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "04_geometry" / "working"
AXES = OUT / "phase1_axes.geojson"
STATIONS = OUT / "station_distance_to_phase1.csv"
CACHE = OUT / "osm_highways_phase1_buffer.json"
OUT_CSV = OUT / "station_network_distance_to_phase1.csv"

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
TO_WGS = Transformer.from_crs(25831, 4326, always_xy=True)
OVERPASS = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "network-vkt-rsr-research/0.1"}

BUFFER_M = 3500
SNAP_M = 80
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


def to_utm(geom):
    return transform(lambda x, y, z=None: TO_UTM.transform(x, y), geom)


def load_axes_utm():
    fc = json.loads(AXES.read_text(encoding="utf-8"))
    geoms = [to_utm(shape(f["geometry"])) for f in fc["features"]]
    return unary_union(geoms)


def overpass_bbox(minx, miny, maxx, maxy) -> dict:
    # Overpass: south, west, north, east
    south, west, north, east = miny, minx, maxy, maxx
    q = f"""
    [out:json][timeout:180];
    way["highway"]({south},{west},{north},{east});
    out geom;
    """
    r = requests.get(OVERPASS, params={"data": q}, timeout=180, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def fetch_highways(axes_utm):
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    buf = axes_utm.buffer(BUFFER_M)
    minx, miny, maxx, maxy = buf.bounds
    w, s = TO_WGS.transform(minx, miny)
    e, n = TO_WGS.transform(maxx, maxy)
    time.sleep(5)
    data = overpass_bbox(w, s, e, n)
    CACHE.write_text(json.dumps(data), encoding="utf-8")
    return data


def build_graph(osm: dict, clip_utm) -> nx.Graph:
    G = nx.Graph()
    for el in osm.get("elements", []):
        if el.get("type") != "way":
            continue
        hw = (el.get("tags") or {}).get("highway")
        if hw not in HIGHWAY_OK:
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        coords_utm = [TO_UTM.transform(p["lon"], p["lat"]) for p in geom]
        for (x1, y1), (x2, y2) in zip(coords_utm, coords_utm[1:]):
            p1, p2 = Point(x1, y1), Point(x2, y2)
            if not (clip_utm.contains(p1) or clip_utm.contains(p2) or clip_utm.intersects(LineString([(x1, y1), (x2, y2)]))):
                continue
            n1, n2 = (round(x1, 1), round(y1, 1)), (round(x2, 1), round(y2, 1))
            length = math.hypot(x2 - x1, y2 - y1)
            if length < 0.5:
                continue
            G.add_node(n1, x=n1[0], y=n1[1])
            G.add_node(n2, x=n2[0], y=n2[1])
            if G.has_edge(n1, n2):
                if length < G[n1][n2]["length"]:
                    G[n1][n2]["length"] = length
            else:
                G.add_edge(n1, n2, length=length)
    return G


def snap(G: nx.Graph, x: float, y: float, max_m: float = SNAP_M):
    best, best_d = None, 1e18
    # coarse: iterate nodes (graph is local)
    for n, d in G.nodes(data=True):
        dist = math.hypot(d["x"] - x, d["y"] - y)
        if dist < best_d:
            best, best_d = n, dist
    if best is None or best_d > max_m:
        return None, best_d
    return best, best_d


def _lines(geom):
    if geom.geom_type == "LineString":
        return [geom]
    if geom.geom_type in ("MultiLineString", "GeometryCollection"):
        out = []
        for g in geom.geoms:
            out.extend(_lines(g))
        return out
    return []


def axis_nodes(G: nx.Graph, axes_utm, step_m: float = 10.0, max_m: float = 20.0) -> list:
    """Graph nodes on the treated centrelines, not a Euclidean sausage.

    A 40 m node buffer pulled first-parallel streets (Diputació, etc.) into
    distance 0. Sources are densified axis points snapped to the graph.
    """
    nodes = set()
    for line in _lines(axes_utm):
        n_steps = max(int(line.length / step_m), 1)
        for i in range(n_steps + 1):
            pt = line.interpolate(i / n_steps, normalized=True)
            node, _d = snap(G, pt.x, pt.y, max_m)
            if node is not None:
                nodes.add(node)
    return list(nodes)


def network_bin(d):
    if d is None:
        return "outside_graph_control"
    if d <= 40:
        return "on_or_immediate"
    if d < 250:
        return "0_250m"
    if d < 500:
        return "250_500m"
    if d < 1000:
        return "500_1000m"
    if d < 2000:
        return "1_2km"
    return "gt_2km_control"


def main() -> None:
    axes_utm = load_axes_utm()
    clip = axes_utm.buffer(BUFFER_M)
    osm = fetch_highways(axes_utm)
    G = build_graph(osm, clip)
    print(f"graph nodes={G.number_of_nodes()} edges={G.number_of_edges()}")
    targets = axis_nodes(G, axes_utm)
    print(f"axis-snapped nodes={len(targets)}")
    if not targets:
        raise SystemExit("No graph nodes on the phase-1 axes")

    # multi-source Dijkstra from all axis nodes
    dist_map = nx.multi_source_dijkstra_path_length(G, targets, weight="length")

    rows = list(csv.DictReader(STATIONS.open(encoding="utf-8")))
    out = []
    snap_fail = 0
    for r in rows:
        lon, lat = float(r["lon"]), float(r["lat"])
        x, y = TO_UTM.transform(lon, lat)
        node, snap_d = snap(G, x, y)
        if node is None or node not in dist_map:
            snap_fail += 1
            net_d = None
        else:
            net_d = dist_map[node]
        out.append(
            {
                "station_id": r["station_id"],
                "desc": r["desc"],
                "lon": r["lon"],
                "lat": r["lat"],
                "euclid_m": r["dist_m_nearest_axis"],
                "network_m": "" if net_d is None else round(net_d, 1),
                "snap_m": "" if node is None else round(snap_d, 1),
                "network_bin": network_bin(net_d),
                "euclid_bin": r["distance_bin"],
                "years_with_counts": r["years_with_counts"],
                "distance_metric": "undirected_osm_highway_utm31n",
            }
        )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    from collections import Counter

    print("network bins", dict(Counter(r["network_bin"] for r in out)))
    print("snap failures", snap_fail, "of", len(out))


if __name__ == "__main__":
    main()
