"""Hansen ranking check at stated decays, on the egress OD times.

Primary map remains beta = 0.05. Does not invent EMEF or jobs.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from compute_access import (
    CAR30,
    csr_time,
    hansen,
    load_graph,
    load_snaps,
    od_times,
    zone_index,
)

ROOT = Path(__file__).resolve().parents[2]
NET = ROOT / "03_network" / "working"
OUT = ROOT / "04_accessibility" / "working"
ON_AXIS = {
    2065, 2067, 2069, 2070, 2071, 2072,
    2091, 2092, 2093, 2096,
    2141, 2143, 2144, 2146, 2147,
}
BETAS = (0.03, 0.05, 0.08, 0.15)


def main():
    scores = pd.read_csv(OUT / "access_sections.csv")
    print("load graphs", flush=True)
    G_pre = load_graph("car_pre.pkl")
    G_post = load_graph("car_post.pkl")
    snaps = load_snaps("sections_snapped_car_egress.csv")
    mat_pre, _, idx_pre = csr_time(G_pre)
    z = zone_index(snaps, idx_pre)
    orig_i = z["gi"].to_numpy()
    pop = z["pop"].to_numpy(dtype=float)
    seccio = z["seccio"].to_numpy()
    dnet = scores.set_index("seccio").loc[seccio, "d_axis_net_m"].to_numpy()
    mask_off = (~pd.Series(seccio).isin(ON_AXIS).to_numpy()) & np.isfinite(dnet)

    print("dijkstra pre/post (30 min)", flush=True)
    t_pre = od_times(mat_pre, orig_i, orig_i, CAR30)
    mat_post, _, _ = csr_time(G_post)
    t_post = od_times(mat_post, orig_i, orig_i, CAR30)
    np.fill_diagonal(t_pre, 0.0)
    np.fill_diagonal(t_post, 0.0)

    out = {}
    for b in BETAS:
        hp = hansen(t_pre, pop, b)
        ho = hansen(t_post, pop, b)
        pct = np.where(hp[mask_off] > 0, 100.0 * (ho[mask_off] - hp[mask_off]) / hp[mask_off], np.nan)
        dA = ho[mask_off] - hp[mask_off]
        corr = float(pd.Series(pct).corr(pd.Series(dnet[mask_off])))
        out[str(b)] = {
            "off_n": int(mask_off.sum()),
            "off_median_pct": round(float(np.nanmedian(pct)), 3),
            "off_median_dA": round(float(np.nanmedian(dA)), 1),
            "corr_pct_distance_off": None if not np.isfinite(corr) else round(corr, 3),
            "n_negative": int(np.nansum(pct < -1e-12)),
        }
        print(b, out[str(b)], flush=True)

    (OUT / "hansen_beta_egress_meta.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", OUT / "hansen_beta_egress_meta.json", flush=True)


if __name__ == "__main__":
    main()
