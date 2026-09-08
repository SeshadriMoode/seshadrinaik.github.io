# Step 4 — simulated times, estimated \(A_i\)

Status: **usable.** Scores are in `working/access_sections.csv`. Do not quote the city **mean** ΔA. Incidence maps are Step 5.

## Labels

| Object | Label |
|---|---|
| \(T_{ij}\) | **simulated** (shortest-path time) |
| \(A_i(t)\) | **estimated** from simulated times × 2022 padrón |
| Own-zone population | included (\(T_{ii}=0\)) |

Primary measure: cumulative opportunity, car **15 min**. Robustness: car 30 min, Hansen \(\beta=0.05\) / min (truncated at 30 min), drop-treated graph. Walk 15 min is a **level**, not a delta (pre = post).

Exposure for bands: **undirected network distance** on `car_pre` to a treated node. Euclidean `d_axis_m` stays diagnostic.

## Headline (off-axis)

1,052 sections are not snapped onto the treated centreline (network distance > 0).

| Measure | Median ΔA (people) | Median % |
|---|---:|---:|
| Car 15 min, ×100 | −12,923 | **−0.81%** |
| Car 15 min, drop-treated | −2,874 | **−0.18%** |
| Car 30 min, ×100 | −1,674 | **−0.10%** |
| Hansen β=0.05 | −7,004 | **−0.61%** |

No origin **gains** car access. The 15-minute cumulative loss is a thin isochrone-edge effect: 30 minutes almost removes it. Hansen (no hard cutoff) stays near −0.6% off-axis and **shrinks** with distance, which the 15-minute bins do not (far bins lose slightly more people at the cutoff). That is a threshold artefact, not a far-network shock.

Walk 15 min: median **80,632** residents reachable. ΔA = 0 by construction.

## On-axis trap (do not lead with this mean)

15 sections (23,479 people) snap onto a treated node (network distance 0). Under ×100, 8 of them lose more than half of 15-minute car opportunity (file `working/on_axis_halved_car15.csv`). Section 2065: −99.7% ×100. That is the proxy punishing **leaving the node**, not a city that lost a million reachable people.

Drop-treated + re-snap repairs most of those (on-axis median −0.31%), but three sections (2065, 2144, 2093) remain badly connected after the edges are deleted. Report them as a local-access caveat, not as the city result.

Citywide **mean** ΔA car 15 ×100 is −25,879 (−1.63%) only because those 15 rows dominate. **Median** citywide is −12,923, the same as off-axis.

## Files

- `working/compute_access.py`
- `working/access_sections.csv` — one row per census section
- `working/access_summary_bands.csv` — network-distance bands plus on/off-axis split
- `working/on_axis_halved_car15.csv`
- `working/access_meta.json`

## Next

Step 5: incidence by **barri** (and income once downloaded). Maps of off-axis % loss; on-axis ×100 shown separately or with the drop-treated overlay. Do not colour the city with the −99% trap as if it were the typical block.
