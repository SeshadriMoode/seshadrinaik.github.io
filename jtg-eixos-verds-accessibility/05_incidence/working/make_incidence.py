"""Neighbourhood incidence of estimated car accessibility change.

Off-axis % loss is the city result. On-axis x100 is plotted separately.
Income joins if 05_incidence/input/2022_renda_disponible_llars.csv exists.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon as MplPoly
from shapely import wkt
from shapely.geometry import box, shape
from shapely.ops import transform as shp_transform, unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
ACC = ROOT / "04_accessibility" / "working"
INP = ROOT / "02_inventory" / "input"
OUT = ROOT / "05_incidence" / "working"
FIG = ROOT / "05_incidence" / "figures"
INCOME = ROOT / "05_incidence" / "input" / "2022_renda_disponible_llars.csv"

TO_UTM = Transformer.from_crs(4326, 25831, always_xy=True)
NAVY = "#1d3557"
CORAL = "#e07a5f"
GRAY = "#6c757d"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "figure.dpi": 140,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
        }
    )


def load_axes_utm():
    fc = json.loads((INP / "phase1_principal.geojson").read_text(encoding="utf-8"))
    lines = [shp_transform(lambda x, y, z=None: TO_UTM.transform(x, y), shape(f["geometry"])) for f in fc["features"]]
    return unary_union(lines)


def load_map_axes():
    """OSM named streets for drawing. Inventory centreline stays for analysis snaps."""
    sys.path.insert(0, str(ROOT / "06_manuscript" / "working"))
    from make_manuscript_figures import load_osm_axes_map

    return load_osm_axes_map()


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


def load_sections():
    scores = pd.read_csv(ACC / "access_sections.csv")
    sec = json.loads((INP / "seccions_censals.json").read_text(encoding="utf-8"))
    polys = []
    for s in sec:
        poly = wkt.loads(s["geometria_etrs89"])
        seccio = int(s["codi_districte"]) * 1000 + int(s["codi_seccio_censal"])
        polys.append({"seccio": seccio, "geom": poly})
    g = pd.DataFrame(polys).merge(scores, on="seccio", how="left")
    if "egress_connector" in g.columns:
        g["on_axis"] = g["egress_connector"].fillna(False).astype(bool) & (g["snapped"] == True)
    else:
        g["on_axis"] = (g["d_axis_net_m"] == 0) & (g["snapped"] == True)
    g["off_axis"] = (g["snapped"] == True) & ~g["on_axis"]
    return g


def maybe_income(g: pd.DataFrame) -> pd.DataFrame:
    if not INCOME.exists() or INCOME.stat().st_size < 1000:
        g["renda"] = np.nan
        g["renda_q"] = np.nan
        return g
    inc = pd.read_csv(INCOME)
    cols = {c.lower(): c for c in inc.columns}
    # typical: Any, Codi_Districte, Seccio_Censal, Import_Euros / Index
    seccio_col = None
    for key in cols:
        if "seccio" in key:
            seccio_col = cols[key]
            break
    val_col = None
    for key in cols:
        if any(t in key for t in ("import", "euros", "renda", "index", "rdl")):
            val_col = cols[key]
            break
    if seccio_col is None or val_col is None:
        g["renda"] = np.nan
        g["renda_q"] = np.nan
        return g
    tmp = inc[[seccio_col, val_col]].copy()
    tmp.columns = ["raw_sec", "renda"]
    tmp["renda"] = pd.to_numeric(tmp["renda"], errors="coerce")
    if "codi_districte" in cols or "districte" in cols:
        dcol = cols.get("codi_districte") or cols.get("districte")
        if dcol in inc.columns:
            tmp["seccio"] = inc[dcol].astype(int) * 1000 + tmp["raw_sec"].astype(int) % 1000
        else:
            tmp["seccio"] = tmp["raw_sec"].astype(int)
    else:
        tmp["seccio"] = tmp["raw_sec"].astype(int)
    tmp = tmp.dropna(subset=["renda"]).drop_duplicates("seccio")
    g = g.merge(tmp[["seccio", "renda"]], on="seccio", how="left")
    off = g["off_axis"] & g["renda"].notna()
    g.loc[off, "renda_q"] = pd.qcut(g.loc[off, "renda"], 5, labels=[1, 2, 3, 4, 5])
    return g


def barri_table(g: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (codi, name, dist), sub in g.groupby(["codi_barri", "nom_barri", "nom_districte"]):
        off = sub.loc[sub.off_axis]
        on = sub.loc[sub.on_axis]
        rows.append(
            {
                "codi_barri": int(codi),
                "nom_barri": name,
                "nom_districte": dist,
                "n_sections": int(len(sub)),
                "n_off": int(len(off)),
                "n_on_axis": int(len(on)),
                "n_halved_x100": int((sub.A_car15_post < 0.5 * sub.A_car15_pre).sum()),
                "pop": float(sub["pop"].sum()),
                "pop_off": float(off["pop"].sum()) if len(off) else 0.0,
                "pop_on": float(on["pop"].sum()) if len(on) else 0.0,
                "pct_off_median_x100": float(off.pct_car15.median()) if len(off) else np.nan,
                "pct_off_mean_x100": float(np.average(off.pct_car15, weights=off["pop"])) if len(off) and off["pop"].sum() else np.nan,
                "pct_off_median_drop": float(off.pct_car15_drop.median()) if len(off) else np.nan,
                "pct_off_median_hansen": float(off.pct_H.median()) if len(off) else np.nan,
                "pct_off_median_car30": float(off.pct_car30.median()) if len(off) else np.nan,
                "d_axis_net_median_m": float(sub.d_axis_net_m.median()),
                "renda_off_median": float(off.renda.median()) if off.renda.notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("pct_off_median_x100")


def income_quintiles(g: pd.DataFrame) -> pd.DataFrame:
    off = g.loc[g.off_axis & g.renda_q.notna()].copy()
    if off.empty:
        return pd.DataFrame()
    rows = []
    for q, sub in off.groupby("renda_q", observed=True):
        rows.append(
            {
                "renda_q": int(q),
                "n": int(len(sub)),
                "pop": float(sub["pop"].sum()),
                "renda_median": float(sub.renda.median()),
                "pct_x100_median": float(sub.pct_car15.median()),
                "pct_drop_median": float(sub.pct_car15_drop.median()),
                "pct_hansen_median": float(sub.pct_H.median()),
                "d_axis_net_median_m": float(sub.d_axis_net_m.median()),
            }
        )
    return pd.DataFrame(rows)


def _patches(geoms, values, cmap, vmin, vmax, hatch=False, facecolor=None):
    patches = []
    vals = []
    for geom, val in zip(geoms, values):
        rings = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for poly in rings:
            patches.append(MplPoly(np.array(poly.exterior.coords), closed=True))
            vals.append(val)
    coll = PatchCollection(
        patches,
        cmap=None if facecolor is not None or hatch else cmap,
        match_original=False,
        linewidths=0.15,
        edgecolors="#333333",
        alpha=1.0,
    )
    if hatch:
        coll.set_hatch("///")
        coll.set_facecolor("#bdbdbd")
    elif facecolor is not None:
        coll.set_facecolor(facecolor)
    else:
        coll.set_cmap(cmap)
        coll.set_array(np.array(vals, dtype=float))
        coll.set_clim(vmin, vmax)
    return coll


def map_offaxis(g: pd.DataFrame, axes, col: str, title: str, fname: str, vmin: float, vmax: float) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 8.4))
    off = g.loc[g.off_axis]
    on = g.loc[g.on_axis]
    miss = g.loc[~g.snapped]
    cmap = plt.cm.Blues_r
    coll = _patches(off.geom.tolist(), off[col].tolist(), cmap, vmin, vmax)
    ax.add_collection(coll)
    if len(on):
        ax.add_collection(_patches(on.geom.tolist(), [0] * len(on), cmap, vmin, vmax, hatch=True))
    if len(miss):
        ax.add_collection(_patches(miss.geom.tolist(), [0] * len(miss), cmap, vmin, vmax, facecolor="#eeeeee"))
    sys.path.insert(0, str(ROOT / "06_manuscript" / "working"))
    from make_manuscript_figures import draw_osm_grid_near_axes

    draw_osm_grid_near_axes(ax, axes, pad=380.0, lw=0.28, z=4)
    _draw_axes(ax, axes, lw=1.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title)
    cbar = fig.colorbar(coll, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("% change in 15-min car accessibility")
    handles = [
        Line2D([0], [0], color=CORAL, lw=1.6, label="Phase-1 axes (4.85 km)"),
        Patch(facecolor="#bdbdbd", hatch="///", edgecolor="#333", label="On treated centreline (mapped separately)"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)
    fig.savefig(FIG / fname)
    plt.close(fig)


def _draw_axes(ax, axes, lw=2.0):
    for ln in _iter_lines(axes):
        ax.plot(
            *ln.xy,
            color=CORAL,
            lw=lw,
            zorder=5,
            solid_capstyle="round",
            solid_joinstyle="round",
            marker="None",
        )


def map_onaxis(g: pd.DataFrame, axes, fname: str) -> None:
    on = g.loc[g.on_axis].copy()
    if on.empty:
        return
    minx, miny, maxx, maxy = axes.buffer(800).bounds
    off_near = g.loc[g.off_axis & (g.d_axis_net_m < 800)]
    rest = g.loc[~g.on_axis & ~((g.off_axis) & (g.d_axis_net_m < 800))]
    fig, axs = plt.subplots(1, 2, figsize=(11.0, 5.4))
    sys.path.insert(0, str(ROOT / "06_manuscript" / "working"))
    from make_manuscript_figures import draw_osm_grid

    clip = box(minx, miny, maxx, maxy)

    ax = axs[0]
    if len(rest):
        ax.add_collection(_patches(rest.geom.tolist(), [0] * len(rest), None, 0, 1, facecolor="#f2f2f2"))
    if len(off_near):
        ax.add_collection(_patches(off_near.geom.tolist(), [0] * len(off_near), None, 0, 1, facecolor="#d9d9d9"))
    coll_on = _patches(on.geom.tolist(), on.pct_car15.tolist(), plt.cm.Reds_r, -40, 0)
    ax.add_collection(coll_on)
    draw_osm_grid(ax, clip, lw=0.4, z=3)
    _draw_axes(ax, axes, lw=2.2)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(a) Local-egress snaps, ×100")
    cbar_a = fig.colorbar(coll_on, ax=ax, fraction=0.046, pad=0.02)
    cbar_a.set_label("% change")

    ax = axs[1]
    if len(rest):
        ax.add_collection(_patches(rest.geom.tolist(), [0] * len(rest), None, 0, 1, facecolor="#f2f2f2"))
    if len(on):
        ax.add_collection(_patches(on.geom.tolist(), [0] * len(on), None, 0, 1, hatch=True))
    coll_off = _patches(off_near.geom.tolist(), off_near.pct_car15.tolist(), plt.cm.Blues_r, -2.0, 0)
    ax.add_collection(coll_off)
    draw_osm_grid(ax, clip, lw=0.4, z=3)
    _draw_axes(ax, axes, lw=2.2)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(b) Off-axis within 800 m")
    cbar_b = fig.colorbar(coll_off, ax=ax, fraction=0.046, pad=0.02)
    cbar_b.set_label("% change")

    fig.tight_layout()
    fig.savefig(FIG / fname)
    plt.close(fig)


def scatter_distance(g: pd.DataFrame, fname: str) -> None:
    off = g.loc[g.off_axis]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.scatter(off.d_axis_net_m / 1000.0, off.pct_car15, s=8, c=NAVY, alpha=0.35, label="×100")
    ax.scatter(off.d_axis_net_m / 1000.0, off.pct_car15_drop, s=8, c=CORAL, alpha=0.35, label="Drop-treated")
    if "pct_car15_turn" in off.columns:
        ax.scatter(off.d_axis_net_m / 1000.0, off.pct_car15_turn, s=8, c=GRAY, alpha=0.25, label="15 s turns")
    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_xlabel("Network distance to treated centreline (km)")
    ax.set_ylabel("% change in 15-min car accessibility")
    ax.set_title("Off-axis sections only")
    ax.legend(frameon=False)
    fig.savefig(FIG / fname)
    plt.close(fig)


def bar_barris(bt: pd.DataFrame, fname: str) -> None:
    sub = bt.dropna(subset=["pct_off_median_x100"]).nsmallest(12, "pct_off_median_x100")
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    y = np.arange(len(sub))
    ax.barh(y + 0.18, sub.pct_off_median_x100, height=0.35, color=NAVY, label="×100")
    ax.barh(y - 0.18, sub.pct_off_median_drop, height=0.35, color=CORAL, label="Drop-treated")
    ax.set_yticks(y)
    ax.set_yticklabels(sub.nom_barri)
    ax.invert_yaxis()
    ax.set_xlabel("Median off-axis % change, car 15 min")
    ax.set_title("Twelve neighbourhoods with the largest ×100 loss")
    ax.legend(frameon=False)
    ax.axvline(0, color=GRAY, lw=0.6)
    fig.savefig(FIG / fname)
    plt.close(fig)


def bar_income(iq: pd.DataFrame, fname: str) -> None:
    if iq.empty:
        return
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    x = iq.renda_q.astype(int)
    ax.plot(x, iq.pct_x100_median, marker="o", color=NAVY, label="×100")
    ax.plot(x, iq.pct_drop_median, marker="o", color=CORAL, label="Drop-treated")
    ax.plot(x, iq.pct_hansen_median, marker="s", color=GRAY, label="Hansen β=0.05")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["Q1\nlowest", "Q2", "Q3", "Q4", "Q5\nhighest"])
    ax.set_ylabel("Median off-axis % change, car 15 min / Hansen")
    ax.set_title("Income quintiles (off-axis census sections)")
    ax.legend(frameon=False)
    ax.axhline(0, color=GRAY, lw=0.6)
    fig.savefig(FIG / fname)
    plt.close(fig)


def main():
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    g = maybe_income(load_sections())
    bt = barri_table(g)
    bt.to_csv(OUT / "incidence_barri.csv", index=False)
    dist = (
        bt.groupby("nom_districte", as_index=False)
        .agg(
            n_barris=("codi_barri", "count"),
            n_on_axis=("n_on_axis", "sum"),
            pop=("pop", "sum"),
            pop_off=("pop_off", "sum"),
            pct_off_median_x100=("pct_off_median_x100", "median"),
            pct_off_median_drop=("pct_off_median_drop", "median"),
        )
        .sort_values("pct_off_median_drop")
    )
    dist.to_csv(OUT / "incidence_district.csv", index=False)
    iq = income_quintiles(g)
    if len(iq):
        iq.to_csv(OUT / "incidence_income_quintile.csv", index=False)

    axes = load_map_axes()
    off = g.loc[g.off_axis, "pct_car15"]
    vmin = min(-1.0, float(np.nanmin(off))) if np.isfinite(off).any() else -1.0
    vmax = 0.0
    map_offaxis(
        g,
        axes,
        "pct_car15",
        "Off-axis 15-min car accessibility, ×100 proxy (%)",
        "fig_offaxis_pct_car15.png",
        vmin,
        vmax,
    )
    map_offaxis(
        g,
        axes,
        "pct_car15_drop",
        "Off-axis 15-min car accessibility, drop-treated (%)",
        "fig_offaxis_pct_drop.png",
        max(-0.6, float(np.nanpercentile(g.loc[g.off_axis, "pct_car15_drop"], 5))),
        0.0,
    )
    map_onaxis(g, axes, "fig_onaxis_x100.png")
    scatter_distance(g, "fig_scatter_distance.png")
    bar_barris(bt, "fig_barri_top12.png")
    sub_h = bt.dropna(subset=["pct_off_median_hansen"]).nsmallest(12, "pct_off_median_hansen")
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    y = np.arange(len(sub_h))
    ax.barh(y, sub_h.pct_off_median_hansen, color=NAVY)
    ax.set_yticks(y)
    ax.set_yticklabels(sub_h.nom_barri)
    ax.invert_yaxis()
    ax.set_xlabel("Median off-axis % change, Hansen β=0.05")
    ax.set_title("Twelve neighbourhoods with the largest Hansen loss")
    ax.axvline(0, color=GRAY, lw=0.6)
    fig.savefig(FIG / "fig_barri_hansen.png")
    plt.close(fig)
    bar_income(iq, "fig_income_quintiles.png")

    meta = {
        "income_joined": bool(g.renda.notna().any()),
        "n_barri": int(len(bt)),
        "worst_barri_off_x100": None if bt.pct_off_median_x100.isna().all() else str(bt.dropna(subset=["pct_off_median_x100"]).iloc[0].nom_barri),
        "worst_barri_pct": None if bt.pct_off_median_x100.isna().all() else float(bt.pct_off_median_x100.min()),
        "eixample_on_axis": int(bt.loc[bt.nom_districte.str.contains("Eixample", na=False), "n_on_axis"].sum()),
        "off_axis_pct_x100_p5": float(np.nanpercentile(off, 5)),
        "off_axis_pct_x100_p95": float(np.nanpercentile(off, 95)),
        "corr_pct_x100_distance": float(g.loc[g.off_axis, ["pct_car15", "d_axis_net_m"]].corr().iloc[0, 1]),
        "corr_pct_drop_distance": float(g.loc[g.off_axis, ["pct_car15_drop", "d_axis_net_m"]].corr().iloc[0, 1]),
    }
    if g.renda.notna().any():
        meta["corr_pct_x100_renda_off"] = float(
            g.loc[g.off_axis & g.renda.notna(), ["pct_car15", "renda"]].corr().iloc[0, 1]
        )
    (OUT / "incidence_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(bt.nsmallest(8, "pct_off_median_x100")[["nom_barri", "nom_districte", "n_on_axis", "pct_off_median_x100", "pct_off_median_drop"]].to_string(index=False))
    if len(iq):
        print(iq.to_string(index=False))


if __name__ == "__main__":
    main()
