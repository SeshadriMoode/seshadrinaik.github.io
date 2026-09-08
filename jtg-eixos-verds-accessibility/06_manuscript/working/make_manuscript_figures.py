"""Manuscript maps that the first draft did not have.

Fig1 study area; Fig2 15-min catchments for two origins;
Hansen choropleth (tight colour scale).
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, Patch, Polygon as MplPoly, Rectangle
from pyproj import Transformer
from shapely import wkt
from shapely.geometry import LineString, box, shape
from shapely.ops import linemerge, transform as shp_transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
ACC = ROOT / "04_accessibility" / "working"
INP = ROOT / "02_inventory" / "input"
NET = ROOT / "03_network" / "working"
FIG = ROOT / "06_manuscript" / "figures"
INC = ROOT / "05_incidence" / "working"

sys.path.insert(0, str(ROOT / "05_incidence" / "working"))
from make_incidence import (  # noqa: E402
    CORAL,
    GRAY,
    NAVY,
    TO_UTM,
    _patches,
    _style,
    load_axes_utm,
    load_sections,
)

NEAR_SECCIO = 2138  # Nova Esquerra, ~157 m off-axis
FAR_SECCIO = 8111  # Ciutat Meridiana
CAR15 = 15 * 60.0

AXIS_LABELS = {
    "consell_de_cent": "Consell de Cent",
    "girona": "Girona",
    "rocafort": "Rocafort",
    "borrell": "Comte Borrell",
}
AXIS_OSM_NAME = {
    "consell_de_cent": "Carrer del Consell de Cent",
    "girona": "Carrer de Girona",
    "rocafort": "Carrer de Rocafort",
    "borrell": "Carrer del Comte Borrell",
}
# Inventory centreline is a schematic chord; Consell sits up to ~47 m off OSM.
AXIS_OSM_BUFFER_M = {
    "consell_de_cent": 45.0,
    "girona": 25.0,
    "rocafort": 20.0,
    "borrell": 20.0,
}
GRID_HIGHWAYS = {
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "living_street",
    "pedestrian",
    "cycleway",
    "tertiary_link",
    "secondary_link",
}
TO_WGS = Transformer.from_crs(25831, 4326, always_xy=True)
_OSM_CACHE = None
_OSM_AXES_MAP = None


def load_graph(name: str) -> nx.DiGraph:
    with (NET / name).open("rb") as f:
        return pickle.load(f)


def section_node(snaps: pd.DataFrame, seccio: int):
    row = snaps.loc[snaps.seccio == seccio].iloc[0]
    if not bool(row.snapped):
        raise RuntimeError(f"{seccio} not snapped")
    return (float(row.node_x), float(row.node_y)), row


def catchment(G: nx.DiGraph, origin, snaps: pd.DataFrame, cutoff_s: float) -> pd.Series:
    dist = nx.single_source_dijkstra_path_length(G, origin, cutoff=cutoff_s, weight="time")
    times = []
    for seccio, node, snapped in zip(snaps.seccio, snaps.node, snaps.snapped):
        if seccio == snaps.loc[snaps.node == origin, "seccio"].iloc[0]:
            times.append(0.0)
            continue
        if (not snapped) or node is None:
            times.append(np.nan)
            continue
        t = dist.get(node)
        times.append(np.nan if t is None else float(t))
    return pd.Series(times, index=snaps.index)


def load_osm() -> dict:
    global _OSM_CACHE
    if _OSM_CACHE is None:
        _OSM_CACHE = json.loads((NET / "osm_highways_barcelona.json").read_text(encoding="utf-8"))
    return _OSM_CACHE


def _wgs_bbox(minx, miny, maxx, maxy, pad_m=80.0):
    corners = [
        TO_WGS.transform(minx - pad_m, miny - pad_m),
        TO_WGS.transform(minx - pad_m, maxy + pad_m),
        TO_WGS.transform(maxx + pad_m, miny - pad_m),
        TO_WGS.transform(maxx + pad_m, maxy + pad_m),
    ]
    lons = [c[0] for c in corners]
    lats = [c[1] for c in corners]
    return min(lons), min(lats), max(lons), max(lats)


def _way_in_wgs_bbox(geom: list, bbox) -> bool:
    west, south, east, north = bbox
    lons = [p["lon"] for p in geom]
    lats = [p["lat"] for p in geom]
    return not (max(lons) < west or min(lons) > east or max(lats) < south or min(lats) > north)


def _way_utm(geom: list) -> LineString:
    return LineString([TO_UTM.transform(p["lon"], p["lat"]) for p in geom])


def _iter_lines(geom):
    if geom is None or geom.is_empty:
        return
    if geom.geom_type == "LineString":
        yield geom
    elif geom.geom_type == "MultiLineString":
        yield from geom.geoms
    elif geom.geom_type == "GeometryCollection":
        for part in geom.geoms:
            yield from _iter_lines(part)


def _longest_line(geom):
    lines = list(_iter_lines(geom))
    if not lines:
        return None
    merged = linemerge(lines)
    if merged.geom_type == "LineString":
        return merged
    return max(merged.geoms, key=lambda ln: ln.length)


def osm_axis_geoms(axis_lines):
    """Actual OSM roadway geometries for the phase-1 named streets."""
    osm = load_osm()
    prefer = ("living_street", "residential", "unclassified", "tertiary")
    fill = ("pedestrian",)
    out = {}
    for key, inv in axis_lines:
        want = AXIS_OSM_NAME[key]
        bbox = _wgs_bbox(*inv.bounds, pad_m=150.0)
        max_d = AXIS_OSM_BUFFER_M[key]
        core, extra = [], []
        for el in osm["elements"]:
            tags = el.get("tags") or {}
            hw = tags.get("highway")
            if tags.get("name") != want or hw not in prefer + fill:
                continue
            geom = el.get("geometry") or []
            if len(geom) < 2 or not _way_in_wgs_bbox(geom, bbox):
                continue
            ln = _way_utm(geom)
            mid = ln.interpolate(0.5, normalized=True)
            if mid.distance(inv) > max_d:
                continue
            if hw in prefer:
                core.append(ln)
            else:
                extra.append(ln)
        parts = list(core)
        if parts:
            covered = unary_union(core).buffer(8.0)
            for ln in extra:
                if not covered.contains(ln.interpolate(0.5, normalized=True)):
                    parts.append(ln)
        else:
            parts = extra
        out[key] = unary_union(parts) if parts else inv
    return out


def load_osm_axes_map():
    """Phase-1 OSM roadways for map overlays (not the schematic inventory chord)."""
    global _OSM_AXES_MAP
    if _OSM_AXES_MAP is None:
        fc = json.loads((INP / "phase1_principal.geojson").read_text(encoding="utf-8"))
        axis_lines = []
        for feat in fc["features"]:
            ln = shp_transform(lambda x, y, z=None: TO_UTM.transform(x, y), shape(feat["geometry"]))
            axis_lines.append((feat["properties"]["axis"], ln))
        geoms = osm_axis_geoms(axis_lines)
        clipped = []
        for key, inv in axis_lines:
            geom = geoms[key]
            hit = geom.intersection(inv.buffer(AXIS_OSM_BUFFER_M[key]))
            clipped.append(geom if hit.is_empty else hit)
        _OSM_AXES_MAP = unary_union(clipped)
    return _OSM_AXES_MAP


def draw_osm_grid(ax, clip, lw=0.45, z=3):
    osm = load_osm()
    bbox = _wgs_bbox(*clip.bounds, pad_m=40.0)
    segs = []
    for el in osm["elements"]:
        tags = el.get("tags") or {}
        if tags.get("highway") not in GRID_HIGHWAYS:
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2 or not _way_in_wgs_bbox(geom, bbox):
            continue
        ln = _way_utm(geom)
        if not ln.intersects(clip):
            continue
        hit = ln.intersection(clip)
        for part in _iter_lines(hit):
            xs, ys = part.xy
            segs.append(np.column_stack([xs, ys]))
    if segs:
        ax.add_collection(
            LineCollection(segs, colors="#8a8a8a", linewidths=lw, zorder=z, capstyle="round")
        )


def draw_osm_grid_near_axes(ax, axes, pad=450.0, lw=0.3, z=3):
    minx, miny, maxx, maxy = axes.bounds
    draw_osm_grid(ax, box(minx - pad, miny - pad, maxx + pad, maxy + pad), lw=lw, z=z)


def draw_linework(ax, geom, lw=1.8, z=5, color=CORAL):
    for ln in _iter_lines(geom):
        ax.plot(
            *ln.xy,
            color=color,
            lw=lw,
            zorder=z,
            solid_capstyle="round",
            solid_joinstyle="round",
            marker="None",
        )


def draw_axes(ax, axes, lw=1.8, z=5):
    draw_linework(ax, axes, lw=lw, z=z)


def scale_bar(ax, x, y, length_m=2000.0, label="2 km"):
    ax.plot([x, x + length_m], [y, y], color="k", lw=1.8, zorder=8)
    ax.plot([x, x], [y - 80, y + 80], color="k", lw=1.2, zorder=8)
    ax.plot([x + length_m, x + length_m], [y - 80, y + 80], color="k", lw=1.2, zorder=8)
    ax.text(x + length_m / 2, y + 140, label, ha="center", va="bottom", fontsize=8)


def north_arrow(ax, x, y, size=700):
    ax.add_patch(
        FancyArrow(
            x,
            y,
            0,
            size,
            width=size * 0.12,
            head_width=size * 0.38,
            head_length=size * 0.28,
            length_includes_head=True,
            facecolor="k",
            edgecolor="k",
            zorder=8,
        )
    )
    ax.text(x, y + size + 120, "N", ha="center", va="bottom", fontsize=9, fontweight="bold")


def fig_study_area(g: pd.DataFrame, axes) -> dict:
    """Citywide locator (a) and zoomed phase-1 axes with street names (b)."""
    fc = json.loads((INP / "phase1_principal.geojson").read_text(encoding="utf-8"))
    axis_lines = []
    for feat in fc["features"]:
        ln = shp_transform(lambda x, y, z=None: TO_UTM.transform(x, y), shape(feat["geometry"]))
        axis_lines.append((feat["properties"]["axis"], ln))
    osm_axes = osm_axis_geoms(axis_lines)
    axes_map = unary_union(list(osm_axes.values()))

    districts = []
    for name, sub in g.groupby("nom_districte"):
        geom = unary_union(sub.geom.tolist())
        districts.append((name, geom, geom.centroid))

    minx, miny, maxx, maxy = axes_map.bounds
    pad = 620.0
    zx0, zy0, zx1, zy1 = minx - pad, miny - pad, maxx + pad, maxy + pad

    fig, axs = plt.subplots(1, 2, figsize=(11.0, 6.0))
    ax_city, ax_zoom = axs
    cmap_d = plt.cm.Greys
    n = max(len(districts), 1)

    def paint_districts(ax, clip=None):
        for i, (name, geom, _) in enumerate(sorted(districts, key=lambda t: t[0])):
            gdraw = geom if clip is None else geom.intersection(clip)
            if gdraw.is_empty:
                continue
            rings = [gdraw] if gdraw.geom_type == "Polygon" else [
                p for p in gdraw.geoms if p.geom_type == "Polygon"
            ]
            patches = [MplPoly(np.array(p.exterior.coords), closed=True) for p in rings]
            if not patches:
                continue
            coll = PatchCollection(
                patches,
                facecolor=cmap_d(0.12 + 0.45 * (i / n)),
                edgecolor="#555555",
                linewidths=0.35,
            )
            ax.add_collection(coll)

    paint_districts(ax_city)
    draw_linework(ax_city, axes_map, lw=2.0)
    ax_city.add_patch(
        Rectangle(
            (zx0, zy0),
            zx1 - zx0,
            zy1 - zy0,
            fill=False,
            edgecolor=CORAL,
            lw=1.15,
            linestyle=(0, (4, 2)),
            zorder=6,
        )
    )
    wanted = {
        "Eixample",
        "Ciutat Vella",
        "Nou Barris",
        "Sant Andreu",
        "Sants-Montjuïc",
        "Sarrià-Sant Gervasi",
        "Horta-Guinardó",
        "Les Corts",
        "Gràcia",
        "Sant Martí",
    }
    for name, geom, c in districts:
        if name not in wanted:
            continue
        ax_city.text(c.x, c.y, name, ha="center", va="center", fontsize=6.5, color="#222222", zorder=6)
    cminx, cminy, cmaxx, cmaxy = unary_union(g.geom.tolist()).bounds
    ax_city.set_xlim(cminx - 400, cmaxx + 400)
    ax_city.set_ylim(cminy - 400, cmaxy + 400)
    ax_city.set_aspect("equal")
    ax_city.axis("off")
    ax_city.set_title("(a) Municipality")
    scale_bar(ax_city, cminx + 400, cminy + 200)
    north_arrow(ax_city, cmaxx - 900, cminy + 400, size=700)
    handles = [
        Line2D([0], [0], color=CORAL, lw=2.0, label="As-built principal (4.85 km)"),
        Line2D([0], [0], color=CORAL, lw=1.15, linestyle=(0, (4, 2)), label="Extent of (b)"),
        Patch(facecolor=cmap_d(0.35), edgecolor="#555", label="Districts"),
    ]
    ax_city.legend(handles=handles, loc="upper left", frameon=False, fontsize=7.5)

    clip = box(zx0, zy0, zx1, zy1)
    in_zoom = g.loc[g.geom.map(lambda p: p.intersects(clip))]
    if len(in_zoom):
        rings = []
        for geom in in_zoom.geom:
            polys = [geom] if geom.geom_type == "Polygon" else [
                p for p in geom.geoms if p.geom_type == "Polygon"
            ]
            rings.extend(MplPoly(np.array(p.exterior.coords), closed=True) for p in polys)
        ax_zoom.add_collection(
            PatchCollection(rings, facecolor="#efeae0", edgecolor="none", linewidths=0)
        )
    draw_osm_grid(ax_zoom, clip)
    draw_linework(ax_zoom, axes_map, lw=2.2, z=6)
    label_side = {
        "consell_de_cent": 1.0,
        "girona": 1.0,
        "rocafort": -1.0,
        "borrell": -1.0,
    }
    label_along = {
        "consell_de_cent": 0.62,
        "girona": 0.42,
        "rocafort": 0.52,
        "borrell": 0.48,
    }
    for key, inv in axis_lines:
        ln = _longest_line(osm_axes[key]) or inv
        t = float(label_along.get(key, 0.5))
        mid = ln.interpolate(t, normalized=True)
        p0 = ln.interpolate(max(t - 0.12, 0.0), normalized=True)
        p1 = ln.interpolate(min(t + 0.12, 1.0), normalized=True)
        dx, dy = p1.x - p0.x, p1.y - p0.y
        nrm = (dx * dx + dy * dy) ** 0.5 or 1.0
        ux, uy = dx / nrm, dy / nrm
        px, py = -uy, ux
        ang = np.degrees(np.arctan2(uy, ux))
        if ang > 90:
            ang -= 180
        elif ang < -90:
            ang += 180
        side = label_side.get(key, 1.0)
        dist = 170.0 if key == "consell_de_cent" else 150.0
        ax_zoom.text(
            mid.x + side * dist * px,
            mid.y + side * dist * py,
            AXIS_LABELS.get(key, key),
            rotation=ang,
            ha="center",
            va="center",
            fontsize=8.5,
            color=CORAL,
            fontweight="bold",
            zorder=8,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.9),
        )
    ax_zoom.set_xlim(zx0, zx1)
    ax_zoom.set_ylim(zy0, zy1)
    ax_zoom.set_aspect("equal")
    ax_zoom.axis("off")
    ax_zoom.set_title("(b) Phase-1 axes on the Cerdà grid")
    scale_bar(ax_zoom, zx0 + 80, zy0 + 70, length_m=500.0, label="500 m")
    fig.subplots_adjust(wspace=0.04)
    fig.savefig(FIG / "Fig1_study_area.png")
    plt.close(fig)
    return {"n_districts": len(districts), "zoom_m": [zx0, zy0, zx1, zy1]}


def fig_hansen_map(g: pd.DataFrame, axes) -> None:
    off = g.loc[g.off_axis, "pct_H"]
    vmin = float(np.nanpercentile(off, 5))
    vmax = 0.0
    fig, ax = plt.subplots(figsize=(7.2, 8.4))
    offg = g.loc[g.off_axis]
    on = g.loc[g.on_axis]
    miss = g.loc[~g.snapped]
    cmap = plt.cm.Oranges_r
    coll = _patches(offg.geom.tolist(), offg.pct_H.tolist(), cmap, vmin, vmax)
    ax.add_collection(coll)
    if len(on):
        ax.add_collection(_patches(on.geom.tolist(), [0] * len(on), cmap, vmin, vmax, hatch=True))
    if len(miss):
        ax.add_collection(_patches(miss.geom.tolist(), [0] * len(miss), cmap, vmin, vmax, facecolor="#eeeeee"))
    draw_osm_grid_near_axes(ax, axes, pad=380.0, lw=0.28, z=4)
    draw_axes(ax, axes)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Off-axis Hansen accessibility change (β = 0.05 / min)")
    cbar = fig.colorbar(coll, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("\% change in Hansen car accessibility")
    handles = [
        Line2D([0], [0], color=CORAL, lw=1.6, label="Phase-1 axes (4.85 km)"),
        Patch(facecolor="#bdbdbd", hatch="///", edgecolor="#333", label="Local-egress snaps"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)
    fig.savefig(FIG / "Fig5_hansen_map.png")
    plt.close(fig)


def one_catchment_panel(ax, g, axes, origin_xy, both, lost, title, grid_clip=None):
    rest = g.loc[~g.seccio.isin(both) & ~g.seccio.isin(lost)]
    if len(rest):
        ax.add_collection(
            _patches(rest.geom.tolist(), [0] * len(rest), None, 0, 1, facecolor="#e9ecef")
        )
    both_g = g.loc[g.seccio.isin(both)]
    lost_g = g.loc[g.seccio.isin(lost)]
    if len(both_g):
        ax.add_collection(
            _patches(both_g.geom.tolist(), [0] * len(both_g), None, 0, 1, facecolor="#1d6a7a")
        )
    if len(lost_g):
        lost_rings = []
        for geom in lost_g.geom:
            polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
            lost_rings.extend(MplPoly(np.array(p.exterior.coords), closed=True) for p in polys)
        ax.add_collection(
            PatchCollection(
                lost_rings,
                facecolor="#e63946",
                edgecolor="#111111",
                linewidths=1.15,
                zorder=4,
            )
        )
        ax.plot(
            [p.centroid.x for p in lost_g.geom],
            [p.centroid.y for p in lost_g.geom],
            marker="o",
            linestyle="none",
            markersize=9,
            markerfacecolor="#e63946",
            markeredgecolor="#111111",
            markeredgewidth=1.1,
            zorder=7,
        )
    if grid_clip is not None:
        draw_osm_grid(ax, grid_clip, lw=0.28, z=3)
    else:
        draw_osm_grid_near_axes(ax, axes, pad=380.0, lw=0.28, z=3)
    draw_axes(ax, axes, lw=2.0)
    ax.plot(
        origin_xy[0],
        origin_xy[1],
        marker="o",
        color="#f4f1ea",
        markeredgecolor=NAVY,
        markeredgewidth=1.6,
        markersize=11,
        zorder=8,
    )
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)


def fig_isochrones(g: pd.DataFrame, axes) -> dict:
    snap_path = NET / "sections_snapped_car_egress.csv"
    if not snap_path.exists():
        snap_path = NET / "sections_snapped_car.csv"
    snaps = pd.read_csv(snap_path)
    snaps["node"] = [
        None if not bool(s) else (float(x), float(y))
        for s, x, y in zip(snaps.snapped, snaps.node_x, snaps.node_y)
    ]
    print("loading car graphs", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    stats = {}
    fig, axs = plt.subplots(1, 2, figsize=(11.2, 6.4))
    for ax, seccio, panel in zip(axs, [NEAR_SECCIO, FAR_SECCIO], ["a", "b"]):
        origin, row = section_node(snaps, seccio)
        t_pre = catchment(G_pre, origin, snaps, CAR15)
        t_post = catchment(G_post, origin, snaps, CAR15)
        in_pre = snaps.loc[np.isfinite(t_pre) & (t_pre <= CAR15), "seccio"]
        in_post = snaps.loc[np.isfinite(t_post) & (t_post <= CAR15), "seccio"]
        both = set(in_pre) & set(in_post)
        lost = set(in_pre) - set(in_post)
        gained = set(in_post) - set(in_pre)
        pop_lost = float(g.loc[g.seccio.isin(lost), "pop"].sum())
        pop_pre = float(g.loc[g.seccio.isin(in_pre), "pop"].sum())
        stats[int(seccio)] = {
            "barri": str(row.nom_barri),
            "district": str(row.nom_districte),
            "pop_origin": float(row["pop"]),
            "n_pre": int(len(in_pre)),
            "n_lost": int(len(lost)),
            "n_gained": int(len(gained)),
            "pop_pre": pop_pre,
            "pop_lost": pop_lost,
            "pct_lost": 100.0 * pop_lost / pop_pre if pop_pre else np.nan,
            "d_axis_m": float(row.d_axis_m),
        }
        title = (
            f"({panel}) Section {seccio}, {row.nom_barri}\n"
            f"{int(len(lost))} sections / {pop_lost:,.0f} people leave the 15-min catchment"
        )
        grid_clip = None
        if seccio == NEAR_SECCIO:
            buf = 4500
            grid_clip = box(origin[0] - buf, origin[1] - buf, origin[0] + buf, origin[1] + buf)
        one_catchment_panel(ax, g, axes, origin, both, lost, title, grid_clip=grid_clip)
        # zoom: near origin tight, far origin citywide
        if seccio == NEAR_SECCIO:
            ax.set_xlim(origin[0] - buf, origin[0] + buf)
            ax.set_ylim(origin[1] - buf, origin[1] + buf)
        else:
            minx, miny, maxx, maxy = unary_union(g.geom.tolist()).bounds
            ax.set_xlim(minx - 300, maxx + 300)
            ax.set_ylim(miny - 300, maxy + 300)
    handles = [
        Patch(facecolor="#1d6a7a", edgecolor="#333", label="Still reachable in 15 min after the cut"),
        Patch(facecolor="#e63946", edgecolor="#111", label="In pre 15-min catchment only (lost)"),
        Patch(facecolor="#e9ecef", edgecolor="#333", label="Outside both 15-min catchments"),
        Line2D([0], [0], color=CORAL, lw=1.6, label="Phase-1 axes"),
        Line2D(
            [0],
            [0],
            marker="o",
            color="#f4f1ea",
            markeredgecolor=NAVY,
            lw=0,
            markersize=8,
            label="Origin centroid snap",
        ),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.subplots_adjust(bottom=0.14, wspace=0.04)
    fig.savefig(FIG / "Fig2_isochrones.png")
    plt.close(fig)
    return stats


def copy_incidence_maps() -> None:
    src_dir = ROOT / "05_incidence" / "figures"
    copies = {
        "fig_offaxis_pct_car15.png": "Fig1_offaxis_car15.png",
        "fig_scatter_distance.png": "Fig2_scatter_distance.png",
        "fig_onaxis_x100.png": "Fig3_onaxis_x100.png",
        "fig_barri_hansen.png": "Fig4_barri_hansen.png",
        "fig_income_quintiles.png": "Fig5_income_quintiles.png",
        "fig_offaxis_pct_drop.png": "FigS1_offaxis_drop.png",
        "fig_barri_top12.png": "FigS2_barri_x100.png",
    }
    for src_name, dst_name in copies.items():
        src = src_dir / src_name
        if src.exists():
            (FIG / dst_name).write_bytes(src.read_bytes())


def main():
    _style()
    FIG.mkdir(parents=True, exist_ok=True)
    g = load_sections()
    axes_inv = load_axes_utm()
    print("osm axes for maps", flush=True)
    axes_map = load_osm_axes_map()
    print("study area", flush=True)
    meta = {"study": fig_study_area(g, axes_inv)}
    print("hansen map", flush=True)
    fig_hansen_map(g, axes_map)
    print("isochrones", flush=True)
    meta["isochrones"] = fig_isochrones(g, axes_map)
    copy_incidence_maps()
    (FIG / "extra_figure_stats.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
