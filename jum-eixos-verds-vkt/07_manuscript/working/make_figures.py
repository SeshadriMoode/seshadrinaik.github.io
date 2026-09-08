"""Manuscript figures from existing CSVs. No new identification."""
from __future__ import annotations

import io
import json
import math
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle
from PIL import Image
from pyproj import Transformer
from shapely import wkt as shapely_wkt
from shapely.geometry import LineString, MultiLineString, Point, box, shape
from shapely.ops import nearest_points, transform as shp_transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
DID = ROOT / "05_did_delta_q" / "working"
ASN = ROOT / "06_assignment" / "working"
GEO = ROOT / "04_geometry" / "working"
FIG = ROOT / "07_manuscript" / "figures"
SUB = ROOT / "07_manuscript" / "submission" / "figures"
CACHE = ROOT / "07_manuscript" / "working"
FIG.mkdir(parents=True, exist_ok=True)
SUB.mkdir(parents=True, exist_ok=True)
(CACHE / "tiles").mkdir(parents=True, exist_ok=True)

BIN_ORDER = [
    "on_or_immediate",
    "0_250m",
    "250_500m",
    "500_1000m",
    "1_2km",
    "control_gt2km",
]
SHORT = {
    "on_or_immediate": "On /\nimmediate",
    "0_250m": "0–250 m",
    "250_500m": "250–500 m",
    "500_1000m": "500 m–1 km",
    "1_2km": "1–2 km",
    "control_gt2km": ">2 km\n(control)",
}
BIN_COLORS = {
    "on_or_immediate": "#9d0208",
    "0_250m": "#dc2f02",
    "250_500m": "#e09f3e",
    "500_1000m": "#457b9d",
    "1_2km": "#6d6875",
    "gt_2km_control": "#adb5bd",
    "outside_graph_control": "#adb5bd",
    "control_gt2km": "#adb5bd",
}
NAVY = "#1d3557"
CORAL = "#e07a5f"
TEAL = "#2a9d8f"
GOLD = "#e09f3e"
CRIMSON = "#9d0208"
GRAY = "#4a4a4a"

TO_3857 = Transformer.from_crs(4326, 3857, always_xy=True)
TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
UTM_TO_3857 = Transformer.from_crs(25831, 3857, always_xy=True)


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "legend.title_fontsize": 10,
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig, lab_name: str, sub_name: str) -> None:
    for ax in fig.get_axes():
        for lab in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            lab.set_fontname("Times New Roman")
        ax.xaxis.label.set_fontname("Times New Roman")
        ax.yaxis.label.set_fontname("Times New Roman")
        ax.title.set_fontname("Times New Roman")
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                t.set_fontname("Times New Roman")
            if leg.get_title() is not None:
                leg.get_title().set_fontname("Times New Roman")
    fig.savefig(FIG / lab_name)
    fig.savefig(SUB / sub_name)


def _legend(ax, **kwargs):
    kw = dict(frameon=True, fancybox=False, edgecolor="#333333", framealpha=0.95, fontsize=9)
    kw.update(kwargs)
    leg = ax.legend(**kw)
    for t in leg.get_texts():
        t.set_fontfamily("Times New Roman")
    if leg.get_title() is not None:
        leg.get_title().set_fontfamily("Times New Roman")
    return leg


def _prep_bar_ax(ax, ylabel: str) -> None:
    ax.axhline(0, color="#222222", lw=0.8, zorder=1)
    ax.set_ylabel(ylabel, fontname="Times New Roman")
    ax.yaxis.grid(True, ls=":", lw=0.5, color="#b0b0b0", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", which="major", length=3)
    for lab in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
        lab.set_fontname("Times New Roman")


def _xy3857(lon, lat):
    return TO_3857.transform(lon, lat)


# ---------------------------------------------------------------------------
# Basemap tiles (Carto Positron) + vector streets / barris
# ---------------------------------------------------------------------------
def _lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[float, float]:
    n = 2.0**z
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def _tile_nw_lonlat(x: int, y: int, z: int) -> tuple[float, float]:
    n = 2.0**z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def _fetch_esri_mosaic(west: float, south: float, east: float, north: float, zoom: int = 15) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Return RGB array and extent in EPSG:3857. Esri tile scheme is z/y/x."""
    x0, y1 = _lonlat_to_tile(west, north, zoom)
    x1, y0 = _lonlat_to_tile(east, south, zoom)
    xs = range(int(math.floor(x0)), int(math.floor(x1)) + 1)
    ys = range(int(math.floor(y1)), int(math.floor(y0)) + 1)
    tiles = []
    for ty in ys:
        row = []
        for tx in xs:
            cache = CACHE / "tiles" / f"esri_street_{zoom}_{tx}_{ty}.png"
            if not cache.exists():
                url = (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    f"World_Street_Map/MapServer/tile/{zoom}/{ty}/{tx}"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "JUM-manuscript-figures/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    cache.write_bytes(resp.read())
            row.append(np.asarray(Image.open(cache).convert("RGB")))
        tiles.append(np.concatenate(row, axis=1))
    mosaic = np.concatenate(tiles, axis=0)
    lon_w, lat_n = _tile_nw_lonlat(xs.start, ys.start, zoom)
    lon_e, lat_s = _tile_nw_lonlat(xs.stop, ys.stop, zoom)
    x_w, y_n = _xy3857(lon_w, lat_n)
    x_e, y_s = _xy3857(lon_e, lat_s)
    return mosaic, (x_w, x_e, y_s, y_n)


AXIS_OSM_NAMES = {
    "consell_de_cent": {"carrer del consell de cent", "carrer de consell de cent"},
    "girona": {"carrer de girona"},
    "rocafort": {"carrer de rocafort"},
    "borrell": {"carrer del comte borrell", "carrer de comte borrell"},
}
# Carriageway / green-axis tags. Footways are sidewalks and pull the line onto blocks.
DISPLAY_HW = {
    "living_street",
    "pedestrian",
    "residential",
    "primary",
    "secondary",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "cycleway",
}


def _osm_named_axis_ways_3857() -> dict[str, list[tuple[str, LineString]]]:
    osm = json.loads((GEO / "osm_highways_phase1_buffer.json").read_text(encoding="utf-8"))
    out: dict[str, list[tuple[str, LineString]]] = {k: [] for k in AXIS_OSM_NAMES}
    for el in osm.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        tags = el.get("tags") or {}
        hw = tags.get("highway")
        if hw not in DISPLAY_HW:
            continue
        name = (tags.get("name") or tags.get("name:ca") or "").strip().lower()
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 2:
            continue
        geom = LineString([_xy3857(lon, lat) for lon, lat in coords])
        for axis_name, names in AXIS_OSM_NAMES.items():
            if name in names:
                out[axis_name].append((hw, geom))
    return out


def _clip_line_to_corridor(geom: LineString, corridor) -> list[LineString]:
    if geom.is_empty or not geom.intersects(corridor):
        return []
    clipped = geom.intersection(corridor)
    geoms = [clipped] if clipped.geom_type == "LineString" else list(getattr(clipped, "geoms", []))
    return [h for h in geoms if h.geom_type == "LineString" and h.length > 8]


def _display_axis_geoms(
    axis: LineString,
    axis_name: str,
    named: dict[str, list[tuple[str, LineString]]],
) -> list[LineString]:
    """Named OSM street fragments inside the as-built extent. Display only."""
    items = named.get(axis_name) or []
    buf = 70.0 if axis_name == "consell_de_cent" else 48.0
    corridor = axis.buffer(buf)
    rank = (
        "living_street",
        "pedestrian",
        "residential",
        "primary",
        "cycleway",
        "tertiary",
        "unclassified",
        "tertiary_link",
    )
    n = 48
    samples = [axis.interpolate(i / n, normalized=True) for i in range(n + 1)]
    covered = [False] * (n + 1)
    selected = []
    by_hw: dict[str, list[LineString]] = {}
    for hw, g in items:
        by_hw.setdefault(hw, []).append(g)
    for hw in rank:
        geoms = [g for g in by_hw.get(hw, []) if g.intersects(corridor)]
        if not geoms:
            continue
        newly = 0
        for i, p in enumerate(samples):
            if covered[i]:
                continue
            if min(p.distance(g) for g in geoms) <= buf:
                covered[i] = True
                newly += 1
        if newly:
            selected.append(hw)
        if sum(covered) >= 0.88 * (n + 1):
            break
    out: list[LineString] = []
    for hw in selected:
        for g in by_hw.get(hw, []):
            out.extend(_clip_line_to_corridor(g, corridor))
    return out or [axis]


def _load_barris_3857():
    raw = json.loads((ASN / "raw" / "barris.json").read_text(encoding="utf-8"))
    polys = []
    for rec in raw:
        geom = shapely_wkt.loads(rec["geometria_etrs89"])
        geom = shp_transform(lambda x, y, z=None: UTM_TO_3857.transform(x, y), geom)
        polys.append((rec["nom_districte"], rec["nom_barri"], geom))
    return polys


def _load_osm_streets_3857(clip):
    cache = CACHE / "osm_streets_clip_3857.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data
    osm = json.loads((GEO / "osm_highways_phase1_buffer.json").read_text(encoding="utf-8"))
    major = {"motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link", "trunk_link", "primary_link"}
    out = {"major": [], "minor": []}
    minx, miny, maxx, maxy = clip.bounds
    pad = clip.buffer(80)
    for el in osm.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        hw = (el.get("tags") or {}).get("highway")
        if not hw:
            continue
        coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
        if len(coords) < 2:
            continue
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        if max(xs) < minx - 0.01 or min(xs) > maxx + 0.01 or max(ys) < miny - 0.01 or min(ys) > maxy + 0.01:
            continue
        line = LineString([_xy3857(lon, lat) for lon, lat in coords])
        if not pad.intersects(line):
            continue
        clipped = line.intersection(pad)
        geoms = [clipped] if clipped.geom_type == "LineString" else list(getattr(clipped, "geoms", []))
        bucket = "major" if hw in major else "minor"
        for g in geoms:
            if g.geom_type == "LineString" and not g.is_empty:
                out[bucket].append(list(g.coords))
    cache.write_text(json.dumps(out), encoding="utf-8")
    return out


def _north_arrow(ax, x, y, size=180.0) -> None:
    ax.annotate(
        "N",
        xy=(x, y + size * 0.15),
        xytext=(x, y - size),
        ha="center",
        va="bottom",
        fontsize=10,
        fontname="Times New Roman",
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1, mutation_scale=12),
        zorder=8,
    )


def _scale_bar(ax, x, y, length_m=500.0) -> None:
    # 500 m true length at this latitude via UTM, then to Web Mercator.
    lon, lat = Transformer.from_crs(3857, 4326, always_xy=True).transform(x, y)
    ux, uy = TO_UTM.transform(lon, lat)
    x1, y1 = UTM_TO_3857.transform(ux, uy)
    x2, y2 = UTM_TO_3857.transform(ux + length_m, uy)
    ax.plot([x1, x2], [y1, y2], color="black", lw=2.2, solid_capstyle="butt", zorder=8)
    ax.plot([x1, x1], [y1 - 18, y1 + 18], color="black", lw=1.4, zorder=8)
    ax.plot([x2, x2], [y2 - 18, y2 + 18], color="black", lw=1.4, zorder=8)
    ax.text((x1 + x2) / 2, y1 + 40, "500 m", ha="center", va="bottom", fontsize=9, fontname="Times New Roman", zorder=8)


def _format_map_ax(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_color("#333333")


def fig_study_area() -> None:
    fc = json.loads((GEO / "phase1_principal.geojson").read_text(encoding="utf-8"))
    named_ways = _osm_named_axis_ways_3857()
    raw_axes = []
    disp_axes = []
    for f in fc["features"]:
        raw = shp_transform(lambda x, y, z=None: TO_3857.transform(x, y), shape(f["geometry"]))
        name = f["properties"]["axis"]
        length_m = f["properties"]["length_m"]
        raw_axes.append((name, raw, length_m))
        disp_axes.append((name, _display_axis_geoms(raw, name, named_ways), length_m))
    st = pd.read_csv(GEO / "station_network_distance_to_phase1.csv", dtype={"station_id": str})
    inc = pd.read_csv(DID / "station_delta_q_incremental_2022h1.csv", dtype={"station_id": str})
    in_panel = set(inc["station_id"])

    union = unary_union([g for _, g, _ in raw_axes])
    frame = union.buffer(2000)
    minx, miny, maxx, maxy = frame.bounds
    # WGS clip for tiles
    to_wgs = Transformer.from_crs(3857, 4326, always_xy=True)
    west, south = to_wgs.transform(minx, miny)
    east, north = to_wgs.transform(maxx, maxy)

    mosaic, extent = _fetch_esri_mosaic(west, south, east, north, zoom=15)
    barris = _load_barris_3857()

    fig, (ax, zax) = plt.subplots(
        1,
        2,
        figsize=(12.8, 7.35),
        gridspec_kw={"width_ratios": [1.42, 1.0], "wspace": 0.07},
    )
    ax.imshow(mosaic, extent=extent, origin="upper", interpolation="nearest", zorder=0)
    # Layer 1 — Eixample outline only (streets remain visible)
    for dist, _name, geom in barris:
        if dist != "Eixample" or not geom.intersects(frame):
            continue
        g = geom.intersection(frame.buffer(80))
        geoms = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
        for poly in geoms:
            if poly.is_empty:
                continue
            xs, ys = poly.exterior.xy
            ax.fill(xs, ys, facecolor="none", edgecolor="#8d6e4c", lw=1.15, zorder=1)
    # Layer 3 — phase-1 axes
    name_label = {
        "consell_de_cent": "Consell de Cent\n(3.00 km)",
        "girona": "Girona\n(0.75 km)",
        "rocafort": "Rocafort (0.60 km)",
        "borrell": "Comte Borrell\n(0.50 km)",
    }
    offsets = {
        "consell_de_cent": (80, 90),
        "girona": (40, 60),
        "rocafort": (-220, 40),
        "borrell": (30, -80),
    }
    for name, raw, _L in raw_axes:
        for geom in next(gs for n, gs, _ in disp_axes if n == name):
            ax.plot(*geom.xy, color="#1b4332", lw=3.0, zorder=5, solid_capstyle="round", label="_nolegend_")
        mid = raw.interpolate(0.52, normalized=True)
        dx, dy = offsets.get(name, (20, 20))
        ax.annotate(
            name_label.get(name, name),
            xy=(mid.x, mid.y),
            xytext=(mid.x + dx, mid.y + dy),
            fontsize=8,
            fontname="Times New Roman",
            color="#1b4332",
            ha="left",
            va="bottom",
            zorder=7,
            arrowprops=dict(arrowstyle="-", color="#1b4332", lw=0.6),
        )
    # Layer 4 — stations
    labels = {
        "on_or_immediate": "On / immediate (≤40 m)",
        "0_250m": "0–250 m",
        "250_500m": "250–500 m",
        "500_1000m": "500 m–1 km",
        "1_2km": "1–2 km",
        ">2 km / outside graph": ">2 km (control)",
    }
    shown = set()
    for bin_name, color in BIN_COLORS.items():
        if bin_name == "control_gt2km":
            continue
        sub = st.loc[st["network_bin"] == bin_name]
        if sub.empty:
            continue
        xy = np.array([_xy3857(lon, lat) for lon, lat in zip(sub["lon"], sub["lat"])])
        keep = (xy[:, 0] >= minx) & (xy[:, 0] <= maxx) & (xy[:, 1] >= miny) & (xy[:, 1] <= maxy)
        if not keep.any():
            continue
        sub = sub.iloc[np.flatnonzero(keep)]
        xy = xy[keep]
        in_d = sub["station_id"].isin(in_panel).to_numpy()
        key = ">2 km / outside graph" if bin_name in {"gt_2km_control", "outside_graph_control"} else bin_name
        lab = labels.get(key, key) if key not in shown else None
        shown.add(key)
        ax.scatter(
            xy[~in_d, 0],
            xy[~in_d, 1],
            s=12,
            c=color,
            alpha=0.7,
            linewidths=0.3,
            edgecolors="white",
            zorder=6,
            label="_nolegend_",
        )
        ax.scatter(
            xy[in_d, 0],
            xy[in_d, 1],
            s=28,
            c=color,
            alpha=0.95,
            linewidths=0.4,
            edgecolors="white",
            zorder=6,
            label=lab,
        )
    dark = st.loc[st["station_id"].isin(["4066", "4067"])]
    if not dark.empty:
        xy = np.array([_xy3857(lon, lat) for lon, lat in zip(dark["lon"], dark["lat"])])
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=160,
            marker="*",
            facecolors="#ffe566",
            edgecolors="black",
            linewidths=0.7,
            zorder=8,
            label="On-axis 4066 / 4067 (dark after 2022)",
        )

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    _format_map_ax(ax)
    ax.set_title("(a) Study area", fontsize=10, fontname="Times New Roman", pad=4)
    _north_arrow(ax, maxx - 240, maxy - 380, size=200)
    _scale_bar(ax, minx + 220, miny + 180, 500)

    near_bins = {"on_or_immediate", "0_250m", "250_500m"}
    girona_g = next(g for name, g, _L in raw_axes if name == "girona")
    consell_g = next(g for name, g, _L in raw_axes if name == "consell_de_cent")
    focus = girona_g.intersection(consell_g)
    if focus.is_empty:
        focus = girona_g.interpolate(0.35, normalized=True)
    else:
        focus = focus.centroid if hasattr(focus, "centroid") else focus
    zpad = 780.0
    zx0, zy0, zx1, zy1 = (
        focus.x - zpad,
        focus.y - zpad,
        focus.x + zpad,
        focus.y + zpad,
    )
    ax.add_patch(
        Rectangle(
            (zx0, zy0),
            zx1 - zx0,
            zy1 - zy0,
            fill=False,
            edgecolor=CRIMSON,
            lw=1.15,
            linestyle="--",
            zorder=8,
        )
    )

    ins = ax.inset_axes([0.015, 0.72, 0.22, 0.26])
    for dist, _name, geom in barris:
        g = geom
        face = "#d8b48a" if dist == "Eixample" else "#e9ecef"
        if g.geom_type == "Polygon":
            ins.fill(*g.exterior.xy, facecolor=face, edgecolor="#bbbbbb", lw=0.2)
        elif g.geom_type == "MultiPolygon":
            for poly in g.geoms:
                ins.fill(*poly.exterior.xy, facecolor=face, edgecolor="#bbbbbb", lw=0.2)
    ins.add_patch(
        Rectangle((minx, miny), maxx - minx, maxy - miny, fill=False, edgecolor=CRIMSON, lw=1.1)
    )
    ins.set_xticks([])
    ins.set_yticks([])
    ins.set_aspect("equal")
    ins.set_title("Barcelona", fontsize=8, fontname="Times New Roman", pad=2)
    for spine in ins.spines.values():
        spine.set_linewidth(0.5)

    zw, zs = to_wgs.transform(zx0, zy0)
    ze, zn = to_wgs.transform(zx1, zy1)
    zmosaic, zextent = _fetch_esri_mosaic(zw, zs, ze, zn, zoom=17)
    zax.imshow(zmosaic, extent=zextent, origin="upper", interpolation="nearest", zorder=0)
    for _name, geoms, _L in disp_axes:
        for geom in geoms:
            zax.plot(*geom.xy, color="#1b4332", lw=2.4, zorder=5, solid_capstyle="round")
    for bin_name, color in BIN_COLORS.items():
        if bin_name not in near_bins:
            continue
        sub = st.loc[st["network_bin"] == bin_name]
        if sub.empty:
            continue
        xy = np.array([_xy3857(lon, lat) for lon, lat in zip(sub["lon"], sub["lat"])])
        keep = (xy[:, 0] >= zx0) & (xy[:, 0] <= zx1) & (xy[:, 1] >= zy0) & (xy[:, 1] <= zy1)
        if not keep.any():
            continue
        sub = sub.iloc[np.flatnonzero(keep)]
        xy = xy[keep]
        in_d = sub["station_id"].isin(in_panel).to_numpy()
        zax.scatter(
            xy[~in_d, 0],
            xy[~in_d, 1],
            s=22,
            c=color,
            alpha=0.8,
            linewidths=0.3,
            edgecolors="white",
            zorder=6,
        )
        zax.scatter(
            xy[in_d, 0],
            xy[in_d, 1],
            s=48,
            c=color,
            alpha=0.95,
            linewidths=0.45,
            edgecolors="white",
            zorder=6,
        )
    if not dark.empty:
        dxy = np.array([_xy3857(lon, lat) for lon, lat in zip(dark["lon"], dark["lat"])])
        zax.scatter(
            dxy[:, 0],
            dxy[:, 1],
            s=220,
            marker="*",
            facecolors="#ffe566",
            edgecolors="black",
            linewidths=0.8,
            zorder=8,
        )
    zax.set_xlim(zx0, zx1)
    zax.set_ylim(zy0, zy1)
    _format_map_ax(zax)
    zax.set_title(
        "(b) Consell de Cent–Girona, 0–250 m and 250–500 m",
        fontsize=10,
        fontname="Times New Roman",
        pad=4,
    )
    for spine in zax.spines.values():
        spine.set_color(CRIMSON)
        spine.set_linewidth(1.15)
    _scale_bar(zax, zx0 + 70, zy0 + 70, 500)

    handles, _labs = ax.get_legend_handles_labels()
    extra = [
        Line2D([0], [0], color="#1b4332", lw=3.2, label="Phase-1 green axes (4.85 km)"),
        Line2D([0], [0], color="#8d6e4c", lw=1.2, label="Eixample district outline"),
        Line2D([0], [0], color=CRIMSON, lw=1.1, linestyle="--", label="Panel (b) frame"),
    ]
    fig.legend(
        handles=extra + handles,
        loc="lower center",
        ncol=4,
        title="Network distance to phase 1",
        fontsize=7.5,
        title_fontsize=8,
        frameon=True,
        fancybox=False,
        edgecolor="#333333",
        framealpha=0.95,
        borderpad=0.45,
        labelspacing=0.28,
        handlelength=1.6,
        columnspacing=1.1,
        bbox_to_anchor=(0.5, 0.028),
        prop={"family": "Times New Roman", "size": 7.5},
    )
    fig.subplots_adjust(left=0.02, right=0.99, top=0.94, bottom=0.20)
    fig.text(
        0.5,
        0.008,
        "Basemap: Esri World Street Map. Streets © Esri, OpenStreetMap contributors.",
        ha="center",
        va="bottom",
        fontsize=6.5,
        fontname="Times New Roman",
        color="#444444",
    )

    _save(fig, "fig1_study_area.png", "Fig1_study_area.png")
    plt.close()


def fig_incremental_did() -> None:
    df = pd.read_csv(DID / "did_incremental_2022h1.csv")
    df = df.set_index("bin").loc[BIN_ORDER]
    y = df["did_q_vs_control"].to_numpy(float)
    se = df["did_q_se"].to_numpy(float)
    x = np.arange(len(BIN_ORDER))
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    _prep_bar_ax(ax, "DiD versus >2 km control (veh / working day)")
    ax.bar(x[:-1], y[:-1], color=NAVY, width=0.68, zorder=3, label="DiD estimate", edgecolor="white", lw=0.4)
    ax.errorbar(x[:-1], y[:-1], yerr=se[:-1], fmt="none", ecolor="black", capsize=3.5, lw=1.05, zorder=4, label="HC1 standard error")
    ax.scatter([x[-1]], [0], color=GRAY, s=42, zorder=5, label="Control (normalised to 0)")
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[b] for b in BIN_ORDER])
    ax.set_ylim(-2500, 1800)
    _legend(ax, loc="upper right")
    _save(fig, "fig2_incremental_did.png", "Fig4_incremental_did.png")
    plt.close()


def fig_stacking() -> None:
    main = pd.read_csv(DID / "did_two_period.csv").set_index("bin").loc[BIN_ORDER]
    inc = pd.read_csv(DID / "did_incremental_2022h1.csv").set_index("bin").loc[BIN_ORDER]
    drop = pd.read_csv(DID / "did_drop_tac2020.csv").set_index("bin").loc[BIN_ORDER]
    x = np.arange(len(BIN_ORDER) - 1)
    w = 0.26
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    _prep_bar_ax(ax, "DiD versus >2 km control (veh / working day)")
    ax.bar(x - w, main["did_q_vs_control"].iloc[:-1], w, label="Cumulative: 2018–19 vs 2024–25", color=CRIMSON, edgecolor="white", lw=0.3, zorder=3)
    ax.bar(x, drop["did_q_vs_control"].iloc[:-1], w, label="Same, drop 2020 counted streets", color=GOLD, edgecolor="white", lw=0.3, zorder=3)
    ax.bar(x + w, inc["did_q_vs_control"].iloc[:-1], w, label="Incremental: 2022 H1 vs 2024–25 (preferred)", color=NAVY, edgecolor="white", lw=0.3, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[b] for b in BIN_ORDER[:-1]])
    _legend(ax, loc="lower left", fontsize=8)
    _save(fig, "fig3_stacking_disclosure.png", "Fig3_window_comparison.png")
    plt.close()


def fig_obs_vs_sim() -> None:
    df = pd.read_csv(ASN / "observed_vs_simulated_delta_q.csv").set_index("did_bin").loc[BIN_ORDER]
    x = np.arange(len(BIN_ORDER))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7.8, 4.5))
    _prep_bar_ax(ax, r"Mean $\Delta Q$ (veh / working day)")
    ax.bar(x - w / 2, df["obs_delta_q"], w, label="Observed incremental $\Delta Q$", color=NAVY, edgecolor="white", lw=0.3, zorder=3)
    ax.bar(x + w / 2, df["sim_fixed_delta_q"], w, label="Simulated demand-fixed $\Delta Q$", color=CORAL, edgecolor="white", lw=0.3, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[b] for b in BIN_ORDER])
    _legend(ax, loc="upper right")
    _save(fig, "fig4_observed_vs_simulated.png", "Fig7_observed_vs_simulated.png")
    plt.close()


def fig_decomp() -> None:
    row = pd.read_csv(ASN / "vkt_decomposition.csv").iloc[0]
    labels = ["LTR\n(local reduction)", "NR\n(elsewhere)", "NVTR\n= LTR − NR"]
    vals = [float(row["LTR"]), float(row["NR"]), float(row["NVTR"])]
    colors = [NAVY, CORAL, TEAL]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    _prep_bar_ax(ax, "veh-km / working day")
    bars = ax.bar(labels, vals, color=colors, edgecolor="white", lw=0.4, zorder=3, width=0.62)
    for bar, v in zip(bars, vals):
        va = "bottom" if v >= 0 else "top"
        off = 900 if v >= 0 else -900
        ax.text(bar.get_x() + bar.get_width() / 2, v + off, f"{v:,.0f}", ha="center", va=va, fontsize=9, fontname="Times New Roman")
    _legend(
        ax,
        handles=[
            Patch(facecolor=NAVY, edgecolor="white", label="LTR (simulated)"),
            Patch(facecolor=CORAL, edgecolor="white", label="NR (simulated)"),
            Patch(facecolor=TEAL, edgecolor="white", label="NVTR (simulated; not measured)"),
        ],
        loc="upper right",
        fontsize=8,
    )
    _save(fig, "fig5_ltr_nr_nvtr_simulated.png", "Fig5_ltr_nr_nvtr.png")
    plt.close()


def fig_event_study() -> None:
    df = pd.read_csv(DID / "event_year_did.csv")
    periods = ["2018", "2022_h1", "2024", "2025"]
    bins = ["on_or_immediate", "0_250m", "250_500m", "500_1000m"]
    colors = [CRIMSON, GOLD, NAVY, TEAL]
    markers = ["o", "s", "D", "^"]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    _prep_bar_ax(ax, "DiD versus >2 km control (veh / working day)")
    x = np.arange(len(periods))
    for b, c, m in zip(bins, colors, markers):
        sub = df.loc[df["bin"] == b].set_index("period").loc[periods]
        ax.errorbar(
            x,
            sub["did_vs_control"],
            yerr=sub["se"],
            marker=m,
            color=c,
            lw=1.5,
            capsize=3,
            markersize=6,
            zorder=3,
            label=SHORT[b].replace("\n", " "),
        )
    ax.set_xticks(x)
    ax.set_xticklabels(["2018", "2022 H1\n(pre-works)", "2024", "2025"])
    _legend(ax, loc="lower left", title="Network-distance bin")
    _save(fig, "fig7_event_study.png", "Fig2_event_study.png")
    plt.close()


def fig_rings() -> None:
    df = pd.read_csv(ASN / "vkt_by_network_ring.csv")
    colors = [NAVY if v < 0 else CORAL for v in df["delta_vkt_fixed"]]
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    _prep_bar_ax(ax, r"Simulated $\Delta$VKT (veh-km / working day)")
    ax.bar(df["ring_label"], df["delta_vkt_fixed"], color=colors, edgecolor="white", lw=0.4, zorder=3, width=0.7)
    ax.tick_params(axis="x", rotation=18)
    _legend(
        ax,
        handles=[
            Patch(facecolor=NAVY, edgecolor="white", label=r"Local cut ($\Delta$VKT $<$ 0)"),
            Patch(facecolor=CORAL, edgecolor="white", label=r"Added travel ($\Delta$VKT $>$ 0)"),
        ],
        loc="upper right",
    )
    _save(fig, "fig6_dvkt_by_ring_simulated.png", "Fig6_dvkt_by_ring.png")
    plt.close()


if __name__ == "__main__":
    _style()
    fig_study_area()
    fig_incremental_did()
    fig_stacking()
    fig_event_study()
    fig_obs_vs_sim()
    fig_decomp()
    fig_rings()
    print("lab", sorted(p.name for p in FIG.glob("*.png")))
    print("sub", sorted(p.name for p in SUB.glob("*.png")))
