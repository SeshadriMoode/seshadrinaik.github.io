"""As-built phase-1 principal centrelines (not OSM sidewalk sausage).

Consell de Cent: control-point line already in phase1_axes.geojson (~3.0 km).
Perpendiculars: documented half-length through the Consell crossing, oriented
by PCA of the clipped OSM geometry so sidewalk spaghetti does not inflate length.

Target undirected length: ~3.0 + 0.75 + 0.60 + 0.50 = 4.85 km.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString, mapping, shape
from shapely.ops import nearest_points, transform

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "04_geometry" / "working"
AXES = OUT / "phase1_axes.geojson"

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
TO_WGS = Transformer.from_crs(25831, 4326, always_xy=True)

# Same documented clips as build_phase1_axes.py
HALF_LEN_M = {
    "girona": 375.0,
    "rocafort": 300.0,
    "borrell": 250.0,
}


def to_utm(geom):
    return transform(lambda x, y, z=None: TO_UTM.transform(x, y), geom)


def to_wgs(geom):
    return transform(lambda x, y, z=None: TO_WGS.transform(x, y), geom)


def coords_xy(geom):
    if geom.geom_type == "LineString":
        return list(geom.coords)
    out = []
    for g in getattr(geom, "geoms", []):
        out.extend(coords_xy(g))
    return out


def pca_axis(geom_utm) -> np.ndarray:
    xy = np.array(coords_xy(geom_utm), dtype=float)
    xy = xy - xy.mean(axis=0)
    _, _, vh = np.linalg.svd(xy, full_matrices=False)
    vec = vh[0]
    n = float(np.linalg.norm(vec)) or 1.0
    return vec / n


def perp_centreline(consell_utm, feat_utm, half_m: float) -> LineString:
    inter = nearest_points(consell_utm, feat_utm.centroid)[0]
    vec = pca_axis(feat_utm)
    p0 = (inter.x - vec[0] * half_m, inter.y - vec[1] * half_m)
    p1 = (inter.x + vec[0] * half_m, inter.y + vec[1] * half_m)
    return LineString([p0, p1])


def main() -> None:
    fc = json.loads(AXES.read_text(encoding="utf-8"))
    by_name = {f["properties"]["axis"]: shape(f["geometry"]) for f in fc["features"]}
    consell = to_utm(by_name["consell_de_cent"])
    if consell.geom_type == "MultiLineString":
        consell = max(consell.geoms, key=lambda g: g.length)

    lines = {"consell_de_cent": consell}
    for name, half in HALF_LEN_M.items():
        lines[name] = perp_centreline(consell, to_utm(by_name[name]), half)

    features = []
    print("principal centreline lengths (m, UTM):")
    total = 0.0
    for name, g in lines.items():
        total += g.length
        print(f"  {name:18} {g.length:8.1f}")
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "axis": name,
                    "phase": "eixos_verds_2022_2023",
                    "length_m": round(g.length, 1),
                    "kind": "principal_as_built",
                },
                "geometry": mapping(to_wgs(g)),
            }
        )
    print(f"  {'TOTAL':18} {total:8.1f}")
    out = {"type": "FeatureCollection", "features": features}
    dest = OUT / "phase1_principal.geojson"
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("wrote", dest)


if __name__ == "__main__":
    main()
