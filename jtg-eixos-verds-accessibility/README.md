# Residential access after a mid-grid cut

Replication code for the *Journal of Transport Geography* article:

**The geography of residential access after a permanent mid-grid cut: Barcelona’s Eixos Verds**

Seshadri Naik Moode. Under review.

This folder is the accessibility pipeline only: simulated free-flow shortest-path times on one OpenStreetMap extract, cumulative-opportunity and Hansen accessibility to 2022 census-section population, and neighbourhood / income incidence after a through-movement recode of Eixos Verds phase 1 (4.85 km).

Traffic counts, vehicle-kilometres, and assignment are not objects here.

## Layout

| Path | Contents |
|---|---|
| `02_inventory/input/` | Phase-1 centreline, census sections, 2022 padró |
| `03_network/working/` | OSM fetch and pre/post car and walk graphs |
| `04_accessibility/working/` | \(A_i(t)\), Hansen, turns, local egress |
| `05_incidence/working/` | Off-axis maps and tables |
| `06_manuscript/` | LaTeX source and figure scripts |

## What is not in GitHub

NetworkX pickles and the full OSM extract are too large. Rebuild them:

```
python 03_network/working/fetch_osm.py
python 03_network/working/build_graphs.py
python 04_accessibility/working/compute_access.py
python 04_accessibility/working/turn_egress.py
python 05_incidence/working/make_incidence.py
python 06_manuscript/working/make_manuscript_figures.py
```

Manuscript PDF: `06_manuscript/latex/build.ps1`.
