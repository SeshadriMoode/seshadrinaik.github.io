# Step 5 — incidence

Status: **usable.** Off-axis % loss is the city result. 2022 household disposable income per capita is joined (`input/2022_renda_disponible_llars.csv`, Open Data BCN). Quintiles are **off-axis sections only**.

## How to read the maps

`fig_offaxis_pct_car15.png` is darker at the **periphery**. That is the 15-minute cutoff, not a Superblock that punished Nou Barris. Correlation of off-axis ×100 % loss with network distance is **−0.79**. People who were already at the edge of a 15-minute isochrone fall off it first.

Drop-treated (`fig_offaxis_pct_drop.png`, `fig_scatter_distance.png`) is almost **flat**: every neighbourhood’s median is between **−0.18% and −0.26%**. Correlation with distance **−0.07**.

Hansen reverses the ranking: larger (still < 1%) losses sit on **nearby** barris (Barceloneta, Sant Antoni, Raval, Poble-sec). Correlation of barri Hansen % with distance is **+0.56** (farther = smaller loss).

**Do not** quote the ×100 periphery ranking as an equity result. Income quintiles show why: Q1 sits 4.3 km from the axes; Q4 sits 1.5 km.

## Neighbourhoods

Off-axis median % change in 15-minute car accessibility:

| District | ×100 | Drop-treated | On-axis sections |
|---|---:|---:|---:|
| Sant Andreu | −1.13 | −0.18 | 0 |
| Nou Barris | −1.13 | −0.18 | 0 |
| Horta-Guinardó | −1.10 | −0.18 | 0 |
| Sant Martí | −0.81 | −0.18 | 0 |
| Gràcia | −0.81 | −0.18 | 0 |
| Sarrià–Sant Gervasi | −0.71 | −0.18 | 0 |
| Ciutat Vella | −0.65 | −0.18 | 0 |
| Sants-Montjuïc | −0.65 | −0.18 | 0 |
| Les Corts | −0.65 | −0.18 | 0 |
| Eixample | **−0.60** | −0.18 | **15** |

Across 73 barris, drop-treated medians span only **−0.26% to −0.18%**. ×100 spans **−1.78%** (Tibidabo) to **−0.45%** (Dreta de l’Eixample). Hansen spans **−0.75% to −0.52%**.

All 15 on-axis snaps (23,479 people) are in three Eixample barris: Dreta (6), Nova Esquerra (5), Antiga Esquerra (4). Map them with `fig_onaxis_x100.png`, not with the city choropleth.

## Income (2022 RDLpc, off-axis quintiles)

| Quintile | Median € | Median network km | ×100 % | Drop % | Hansen % |
|---|---:|---:|---:|---:|---:|
| Q1 lowest | 16,797 | 4.26 | −0.97 | −0.18 | −0.57 |
| Q2 | 20,438 | 3.08 | −0.81 | −0.18 | −0.59 |
| Q3 | 22,672 | 2.30 | −0.81 | −0.18 | −0.59 |
| Q4 | 25,013 | 1.53 | −0.64 | −0.18 | −0.62 |
| Q5 highest | 29,765 | 2.10 | −0.64 | −0.18 | −0.64 |

×100 looks mildly regressive because poorer sections are farther from the Eixample axes (corr %×renda = +0.34). Drop-treated is **−0.18% in every quintile**. Hansen is slightly *larger* in Q5 than Q1: the detour sits nearer the cut, which is not the poorest ring. File: `working/incidence_income_quintile.csv`; figure: `figures/fig_income_quintiles.png`.

## Files

- `input/2022_renda_disponible_llars.csv`
- `working/incidence_barri.csv`, `incidence_district.csv`, `incidence_income_quintile.csv`, `incidence_meta.json`
- `figures/fig_offaxis_pct_car15.png` — city, off-axis ×100, on-axis hatched
- `figures/fig_offaxis_pct_drop.png`
- `figures/fig_onaxis_x100.png` — zoom
- `figures/fig_scatter_distance.png`
- `figures/fig_barri_top12.png` — ×100 ranking (periphery; disclose the artefact)
- `figures/fig_barri_hansen.png` — Hansen ranking (nearby)
- `figures/fig_income_quintiles.png`
