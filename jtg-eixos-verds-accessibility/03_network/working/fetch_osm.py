"""Download citywide OSM highways for the accessibility graphs.

Tiles the municipal bbox so Overpass does not time out. Dedupes ways by id.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from pyproj import Transformer
from shapely import wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "02_inventory" / "input"
OUT = ROOT / "03_network" / "working"
CACHE = OUT / "osm_highways_barcelona.json"
META = OUT / "fetch_meta.json"

OVERPASS = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "accessibility-rsr-research/0.1"}
TO_WGS = Transformer.from_crs(25831, 4326, always_xy=True)
PAD_M = 500.0
NX, NY = 2, 2
SLEEP_S = 8


def municipal_wgs_bbox():
    barris = json.loads((INP / "barris.json").read_text(encoding="utf-8"))
    u = unary_union([wkt.loads(b["geometria_etrs89"]) for b in barris])
    minx, miny, maxx, maxy = u.bounds
    minx -= PAD_M
    miny -= PAD_M
    maxx += PAD_M
    maxy += PAD_M
    west, south = TO_WGS.transform(minx, miny)
    east, north = TO_WGS.transform(maxx, maxy)
    return south, west, north, east


def tiles(south, west, north, east):
    dlat = (north - south) / NY
    dlon = (east - west) / NX
    overlap = 0.002
    out = []
    for i in range(NY):
        for j in range(NX):
            s = south + i * dlat - (overlap if i else 0)
            n = south + (i + 1) * dlat + (overlap if i < NY - 1 else 0)
            w = west + j * dlon - (overlap if j else 0)
            e = west + (j + 1) * dlon + (overlap if j < NX - 1 else 0)
            out.append((s, w, n, e))
    return out


def overpass_bbox(south, west, north, east) -> dict:
    q = f"""
    [out:json][timeout:300];
    way["highway"]({south},{west},{north},{east});
    out geom;
    """
    last = None
    for attempt in range(4):
        try:
            r = requests.get(OVERPASS, params={"data": q}, timeout=360, headers=HEADERS)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"Overpass failed for {south, west, north, east}: {last}")


def fetch() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    if CACHE.exists() and CACHE.stat().st_size > 1_000_000:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    south, west, north, east = municipal_wgs_bbox()
    ways = {}
    tile_counts = []
    for k, tile in enumerate(tiles(south, west, north, east), start=1):
        if k > 1:
            time.sleep(SLEEP_S)
        data = overpass_bbox(*tile)
        n = 0
        for el in data.get("elements", []):
            if el.get("type") != "way" or "id" not in el:
                continue
            ways[el["id"]] = el
            n += 1
        tile_counts.append({"tile": k, "bbox": tile, "n_ways_raw": n, "n_ways_unique": len(ways)})
        print(f"tile {k}/4 ways_raw={n} unique={len(ways)}", flush=True)
    payload = {"elements": list(ways.values())}
    CACHE.write_text(json.dumps(payload), encoding="utf-8")
    META.write_text(
        json.dumps(
            {
                "fetched_utc": datetime.now(timezone.utc).isoformat(),
                "bbox_swn_e": [south, west, north, east],
                "n_tiles": NX * NY,
                "n_ways": len(ways),
                "tiles": tile_counts,
                "cache": str(CACHE),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    data = fetch()
    print("ways", len(data["elements"]), "bytes", CACHE.stat().st_size)
