# From traffic evaporation to network adaptation

Replication code for the *Journal of Urban Mobility* article:

**From traffic evaporation to network adaptation: quantifying the mobility footprint of urban road-space reallocation**

Seshadri Naik Moode. Under review.

This folder is the volume and vehicle-kilometre pipeline only: Open Data BCN counts, network-distance DiD, and a demand-fixed assignment that labels local traffic reduction, redistribution, and net vehicle-travel reduction after Eixos Verds phase 1 (4.85 km).

Opportunity accessibility is not an object here.

## Layout

| Path | Contents |
|---|---|
| `01_intervention_inventory/` | Dated longlist |
| `02_counter_audit/` | Public MADT coverage |
| `04_geometry/` | Phase-1 axes and network-distance bins |
| `05_did_delta_q/` | Distance-bin DiD |
| `06_assignment/` | Count-constrained assignment, LTR / NR / NVTR |
| `07_manuscript/` | LaTeX source and figure scripts |

## What is not in GitHub

The OSM buffer extract is too large. Rebuild geometry and assignment from the scripts in `04_geometry/working/` and `06_assignment/working/`.

Manuscript PDF: `07_manuscript/latex/build.ps1`.
