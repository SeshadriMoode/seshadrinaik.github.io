# Step 1 — accessibility definition (locked)

Object: **change in opportunity accessibility** after Eixos Verds phase 1 through-movement removal. Same 4.85 km as-built axes as Paper 1. Not volumes. Not VKT.

## Primary measure

**Cumulative-opportunity accessibility** at origin \(i\):

\[
A_i(t) = \sum_j O_j \mathbf{1}[T_{ij} \le t]
\]

- \(T_{ij}\): **simulated** shortest-path travel time on OSM (car; walk as second mode).
- \(O_j\): opportunities at destination \(j\). Until a workplace file is in this repo, \(O_j\) = **2022 padrón population** at census section (already in Paper 1 `06_assignment/working/raw/2022_pad_mdbas.csv`). Jobs replace population when they arrive; do not mix the two in one table.
- Thresholds: car **15 and 30 min**; walk **15 min**. One primary map (car 15 min); the others are robustness.

Hansen gravity \(A_i = \sum_j O_j \exp(-\beta T_{ij})\) is the **robustness check**, not a second paper.

## Modes (honest labels)

| Mode | Graph | What a ΔA means |
|---|---|---|
| Car | Paper 1 OSM + same through-movement penalty on phase-1 axes | Simulated loss (or gain) of car access under demand-fixed routing |
| Walk | OSM pedestrian graph; treated axes **not** given an invented speed-up unless we write a stated scenario | Simulated walk access with the *same* geometry; a “walk got faster” claim needs an explicit speed/permission recode |

Cycle and transit wait until a cycle extract / GTFS is in **this** repo. “Multimodal” in the manuscript means car vs walk until those files exist.

## Incidence (equity as a panel, not a third paper)

Report \(\Delta A_i\) by **barri** (Paper 1 `barris.json` / `zones_in_graph.csv`) and by network distance to the axes. Income / vulnerability layers wait until they are downloaded here.

## Journal (locked)

***Journal of Transport Geography***. Different editor from the JUM volume paper. Do not describe this article as “Paper 2 of a series” in the manuscript.

## What we will not compute in Step 1

Maps, isochrones, or ΔT tables. Those wait for Steps 3–4.

## Reusable inputs (read-only from Paper 1)

- `04_geometry/working/phase1_principal.geojson`
- `06_assignment/working/run_assignment.py` (graph + treated-edge penalty)
- `06_assignment/working/raw/2022_pad_mdbas.csv`
- `06_assignment/working/raw/barris.json`
- `06_assignment/working/zones_in_graph.csv`

Do not copy DiD or LTR/NR/NVTR into this manuscript as new results.
