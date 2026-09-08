"""Build Eixos Verds phase-1 geometry from OSM and classify traffic stations.

Distance here is Euclidean in ETRS89 UTM 31N (EPSG:25831), labelled as an
interim proxy until network distance is built in a later step.

Phase-1 extents (municipal / press, not the full street):
  Consell de Cent: Vilamarí to Passeig de Sant Joan (~2.8 km)
  Perpendicular axes: clipped to documented approximate lengths around
  the Consell de Cent intersections (Girona ~0.75 km, Rocafort ~0.6 km,
  Comte Borrell ~0.5 km).
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import requests
from shapely.geometry import LineString, MultiLineString, Point, mapping, shape
from shapely.ops import linemerge, nearest_points, transform, unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
RAW_STATIONS = ROOT / "02_counter_audit" / "working" / "stations_master.csv"
OUT = ROOT / "04_geometry" / "working"
OUT.mkdir(parents=True, exist_ok=True)

OVERPASS = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "network-vkt-rsr-research/0.1 (academic; barcelona eixos verds geometry)"}
# Eixample-ish bbox for the four streets
BBOX = "41.370,2.140,41.410,2.190"

# WGS84 <-> ETRS89 / UTM 31N (Barcelona municipal CRS)
TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
TO_WGS = Transformer.from_crs(25831, 4326, always_xy=True)

# Consell de Cent is not consistently named in OSM inside this bbox.
# Phase-1 centreline: documented Vilamarí → Pg. Sant Joan, using
# municipal counter positions on that stretch (lon ascending ≈ Llobregat to Besòs).
CONSELL_CONTROL_WGS84 = [
    (2.14950352907181, 41.3787849800429),  # Vilamarí
    (2.155270123, 41.38319485),  # Comte Borrell
    (2.1580927938814, 41.3859229631157),  # Casanova
    (2.15999405057183, 41.3861943064478),  # Muntaner
    (2.16782623743917, 41.392200590956),  # Pau Claris
    (2.170175343, 41.394429536),  # Bruc
    (2.170492432, 41.395294749),  # Girona
    (2.1747, 41.3973),  # Passeig de Sant Joan (phase-1 eastern end)
]

# Perpendicular streets: keep only the phase-1 length centred on Consell de Cent.
# Distances in metres along a north-west / south-east Cerdà street.
HALF_LEN_M = {
    "girona": 375.0,  # ~0.75 km total
    "rocafort": 300.0,  # ~0.6 km total
    "borrell": 250.0,  # ~0.5 km total
}

QUERIES = {
    "consell_de_cent": [
        'way["name"="Carrer de Consell de Cent"]',
        'way["name:ca"="Carrer de Consell de Cent"]',
    ],
    "girona": [
        'way["name"="Carrer de Girona"]',
        'way["name:ca"="Carrer de Girona"]',
    ],
    "rocafort": [
        'way["name"="Carrer de Rocafort"]',
        'way["name:ca"="Carrer de Rocafort"]',
    ],
    "borrell": [
        'way["name"="Carrer del Comte Borrell"]',
        'way["name"="Carrer de Comte Borrell"]',
        'way["name:ca"="Carrer del Comte Borrell"]',
    ],
}


CACHE = OUT / "osm_perpendiculars_raw.json"


def overpass_perpendiculars() -> dict[str, list[dict]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    time.sleep(8)
    q = f"""
    [out:json][timeout:90];
    (
      way["name"="Carrer de Girona"]({BBOX});
      way["name"="Carrer de Rocafort"]({BBOX});
      way["name"="Carrer del Comte Borrell"]({BBOX});
      way["name"="Carrer de Comte Borrell"]({BBOX});
    );
    out geom;
    """
    r = requests.get(OVERPASS, params={"data": q}, timeout=120, headers=HEADERS)
    r.raise_for_status()
    grouped = {"girona": [], "rocafort": [], "borrell": []}
    for el in r.json().get("elements", []):
        n = ((el.get("tags") or {}).get("name") or "").lower()
        if n == "carrer de girona":
            grouped["girona"].append(el)
        elif "rocafort" in n:
            grouped["rocafort"].append(el)
        elif "borrell" in n:
            grouped["borrell"].append(el)
    CACHE.write_text(json.dumps(grouped), encoding="utf-8")
    return grouped


def ways_to_multiline(elements: list[dict]) -> MultiLineString | None:
    lines = []
    for el in elements:
        if el.get("type") != "way":
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        coords = [(p["lon"], p["lat"]) for p in geom]
        lines.append(LineString(coords))
    if not lines:
        return None
    merged = linemerge(unary_union(lines))
    if merged.geom_type == "LineString":
        return MultiLineString([merged])
    if merged.geom_type == "MultiLineString":
        return merged
    return MultiLineString([g for g in getattr(merged, "geoms", []) if g.length > 0])


def to_utm(geom):
    return transform(lambda x, y, z=None: TO_UTM.transform(x, y), geom)


def to_wgs(geom):
    return transform(lambda x, y, z=None: TO_WGS.transform(x, y), geom)


def clip_bbox(ml: MultiLineString, bbox: dict) -> MultiLineString:
    from shapely.geometry import box

    b = box(bbox["minx"], bbox["miny"], bbox["maxx"], bbox["maxy"])
    clipped = ml.intersection(b)
    if clipped.is_empty:
        return MultiLineString([])
    if clipped.geom_type == "LineString":
        return MultiLineString([clipped])
    if clipped.geom_type == "MultiLineString":
        return clipped
    geoms = [g for g in getattr(clipped, "geoms", []) if g.geom_type in {"LineString", "MultiLineString"}]
    parts = []
    for g in geoms:
        if g.geom_type == "LineString":
            parts.append(g)
        else:
            parts.extend(list(g.geoms))
    return MultiLineString(parts)


def clip_around_intersection(street_wgs: MultiLineString, consell_wgs: MultiLineString, half_m: float) -> MultiLineString:
    """Keep the perpendicular axis within ±half_m of its Consell de Cent crossing."""
    street_u = to_utm(street_wgs)
    consell_u = to_utm(consell_wgs)
    p_street, _p_consell = nearest_points(street_u, consell_u)
    kept = street_u.intersection(p_street.buffer(half_m))
    if kept.is_empty:
        return MultiLineString([])
    if kept.geom_type == "LineString":
        return to_wgs(MultiLineString([kept]))
    if kept.geom_type == "MultiLineString":
        return to_wgs(kept)
    parts = [g for g in getattr(kept, "geoms", []) if g.geom_type == "LineString" and g.length > 5]
    if not parts:
        return MultiLineString([])
    return to_wgs(MultiLineString(parts))


def load_traffic_stations() -> list[dict]:
    rows = []
    with RAW_STATIONS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if str(row["is_traffic"]).lower() not in {"true", "1"}:
                continue
            try:
                lon = float(row["lon"])
                lat = float(row["lat"])
            except (TypeError, ValueError):
                continue
            rows.append({**row, "lon": lon, "lat": lat})
    return rows


def dist_m(point_wgs: Point, axes_wgs) -> float:
    pu = to_utm(point_wgs)
    au = to_utm(axes_wgs)
    return pu.distance(au)


def bin_distance(d: float) -> str:
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


def fc(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    consell = MultiLineString([LineString(CONSELL_CONTROL_WGS84)])
    grouped = overpass_perpendiculars()
    raw_geoms = {}
    for key, els in grouped.items():
        ml = ways_to_multiline(els)
        print(f"{key}: {0 if ml is None else len(getattr(ml, 'geoms', [ml]))} OSM parts")
        if ml is None:
            raise SystemExit(f"No OSM geometry for {key}")
        raw_geoms[key] = ml

    girona = clip_around_intersection(raw_geoms["girona"], consell, HALF_LEN_M["girona"])
    rocafort = clip_around_intersection(raw_geoms["rocafort"], consell, HALF_LEN_M["rocafort"])
    borrell = clip_around_intersection(raw_geoms["borrell"], consell, HALF_LEN_M["borrell"])

    axes = {
        "consell_de_cent": consell,
        "girona": girona,
        "rocafort": rocafort,
        "borrell": borrell,
    }
    union = unary_union([g for g in axes.values() if not g.is_empty])

    features = []
    for name, g in axes.items():
        g_utm = to_utm(g)
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "axis": name,
                    "phase": "eixos_verds_2022_2023",
                    "length_m": round(g_utm.length, 1),
                    "distance_metric": "interim_euclidean_utm31n",
                },
                "geometry": mapping(g),
            }
        )
    (OUT / "phase1_axes.geojson").write_text(json.dumps(fc(features), ensure_ascii=False), encoding="utf-8")

    stations = load_traffic_stations()
    out_rows = []
    counts = {}
    for st in stations:
        pt = Point(st["lon"], st["lat"])
        d = dist_m(pt, union)
        nearest_axis = min(axes.keys(), key=lambda k: dist_m(pt, axes[k]) if not axes[k].is_empty else math.inf)
        d_axis = dist_m(pt, axes[nearest_axis])
        b = bin_distance(d)
        counts[b] = counts.get(b, 0) + 1
        out_rows.append(
            {
                "station_id": st["id"],
                "desc": st["desc"],
                "lon": st["lon"],
                "lat": st["lat"],
                "dist_m_nearest_axis": round(d, 1),
                "nearest_axis": nearest_axis,
                "dist_m_that_axis": round(d_axis, 1),
                "distance_bin": b,
                "years_with_counts": st["years_with_counts"],
                "n_years_with_counts": st["n_years_with_counts"],
                "distance_metric": "euclidean_utm31n_interim",
            }
        )

    with (OUT / "station_distance_to_phase1.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(out_rows, key=lambda r: r["dist_m_nearest_axis"]))

    print("axis lengths (m):")
    for name, g in axes.items():
        print(f"  {name:18} {to_utm(g).length:8.1f}")
    print("station bins:")
    for k in ["on_or_immediate", "0_250m", "250_500m", "500_1000m", "1_2km", "gt_2km_control"]:
        print(f"  {k:18} {counts.get(k, 0)}")
    print(f"traffic stations classified: {len(out_rows)}")


if __name__ == "__main__":
    main()
