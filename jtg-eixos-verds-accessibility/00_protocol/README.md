01_measure/NOTES.md
02_inventory/input/phase1_principal.geojson
02_inventory/NOTES.md
Working title: **Who loses access when a city closes a street to through traffic?**

**This repository is the accessibility article only.** It is a standalone article. Do not mix LTR / NR / NVTR estimation, DiD on MADT, or Nello-Deakin re-estimation into this folder.

Barcelona Eixos Verds phase 1 is the empirical test bed. The scientific object is the **change in place-to-place accessibility** when through-movement is removed on the as-built axes, not the change in traffic volume.

Paper 1 (sibling folder `Network_VKT_Road_Space_Reallocation`) supplies **read-only inputs**: phase-1 geometry (4.85 km principal), the treated-edge rule, and the demand-fixed assignment as a *stated* routing scenario. Do not rewrite `phase1_principal.geojson`. Do not reopen Paper 1 locked numbers.

### Paper 2 scope (locked until we change it here)

1. Define accessibility as a travel-time / generalised-cost opportunity measure on the same OSM network, pre vs post the through-movement cut.
2. Map who gains and who loses access (origins × destinations), not a city-wide average.
3. Keep observed / estimated / simulated / inferred labels separate. A shortest-path ΔT is **simulated**. Census-weighted ΔA is **estimated**. Traffic counts do **not** become accessibility.

Not in Paper 2: network VKT decomposition; evaporative demand; Superblock liveability/health; TR Part B variational inequality; a statistical model of intervention heterogeneity across cities (that is a later, separate article).

Equity is **incidence of ΔA**, not a second paper. Scenarios (further Superilles) wait until the phase-1 accessibility object is estimated.

## Sequence (do not skip)

| Step | Deliverable | Status |
|---|---|---|
| 1 | Lock accessibility definition + journal target | **locked** (`01_measure/NOTES.md`) |
| 2 | Inventory origins, destinations, and network (car; walk/cycle only if OSM supports) | **done** (`02_inventory/NOTES.md`) |
| 3 | Pre/post graph: same through-movement penalty as Paper 1 assignment | **done** (`03_network/NOTES.md`) |
| 4 | Origin–destination travel times and opportunity accessibility | **done** (`04_accessibility/NOTES.md`) |
| 5 | Incidence by neighbourhood / income (distributional map) | **done** (`05_incidence/NOTES.md`; 2022 RDLpc joined) |
| 6 | Standalone manuscript | **full draft** (`06_manuscript/latex/main.tex`, `main.pdf`) |

## Inherited constraints (do not reopen)

- Sample A only: Eixos Verds phase 1 (works 16 Aug 2022 – spring 2023). As-built principal **4.85 km**.
- Consell de Cent ~3.0 km, Girona 0.75, Rocafort 0.60, Comte Borrell 0.50 km, four squares.
- Exposure: **undirected OSM network distance**. Euclidean diagnostic only.
- Cite Nello-Deakin (2022) as given. Do not re-estimate his 11 COVID tactical streets.
- Station 4056 is east of phase 1, not treated. 4066/4067 are dark after 2022; they are not accessibility sensors.
- Do not invent EMEF, mobile-phone OD, or transit GTFS triangulation until those files are in this repo.
- Manuscript voice: original submission, never a rebuttal, never “later papers in a series.”

## Current rule

Full JTG draft is in `06_manuscript/latex/main.tex`. Quote off-axis medians. Income quintiles are in: ×100 looks regressive only because Q1 is farther from the axes; drop-treated is −0.18% in every quintile. Word conversion and cover letter wait for a submission pass.
