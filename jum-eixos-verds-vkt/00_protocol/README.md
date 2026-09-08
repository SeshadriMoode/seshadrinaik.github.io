# From Traffic Evaporation to Network Adaptation

Working title: **From Traffic Evaporation to Network Adaptation: Quantifying the Mobility Footprint of Urban Road-Space Reallocation**

**This repository is Paper 1 only.** Later papers (accessibility, heterogeneity regression, council brief) wait.

Barcelona is the empirical test bed. The scientific object is the difference between local traffic reduction and network vehicle travel.

### Paper 1 scope (locked)

1. Causal effects of road-space reallocation on traffic volumes (treated / nearby / wider network).
2. How that response decays with network distance and over time.
3. How far local traffic reduction becomes redistribution versus net change in network VKT, with demand-fixed vs demand-elastic scenarios made explicit.

The **contribution** is (3), using (1)–(2) as the observed mechanism. See `CONTRIBUTIONS.md`. Distance-bin traffic counts alone are not the paper.

Not in Paper 1: full accessibility, equity, policy scenario testing, or a statistical model of intervention heterogeneity.

## Sequence (do not skip)

We work one step at a time. Do not start the next step until the current deliverable is usable.

| Step | Deliverable | Status |
|---|---|---|
| 1 | Barcelona intervention inventory (dated longlist) | **done (v0.1)** |
| 2 | Traffic-counter coverage audit against the inventory | **done (v0.2)** |
| 3 | Decide which interventions enter the causal sample | **locked** |
| 4 | Lock identification strategy | **locked: distance-bin DiD on Eixos Verds 2022–23; Nello-Deakin sample out** |
| **4b** | Phase-1 geometry + **network** distance bins | **done (exposure locked)** |
| **4c** | Distance-bin DiD on \(\Delta Q\) | **done (volume only; 2020 stacking disclosed)** |
| 5 | Literature matrix (working evidence table) | **v0.1 done** — `05_literature/literature_matrix.md`; Section 2 of the JUM draft walks the empty VKT column |
| 6 | Count-constrained assignment → LTR / NR / NVTR | **v1.0: principal 4.85 km injected; demand-fixed simulated; elastic VKT not identified** |
| **6b** | JUM manuscript (Paper 1) | **draft uses v1.0 + fig1/fig7** (`07_manuscript/JUM_paper_draft.md`) |
| **6c** | Full case study (still Paper 1) | **map + assignment v1.0 done**; next data: EMEF / 4066–4067 (`07_manuscript/CASE_STUDY_V1.md`) |
| 7 | Accessibility / equity / scenarios | later papers |

The TR Part B variational-inequality / evaporation-index article is **paused** and is not this repository.

Step 5 is a working matrix scored on whether each study measures network VKT, not a finished PRISMA. PRISMA can sit on top later; it is not a reason to thin Section 2 again.

## What this paper is (and is not)

This paper answers:

> When a city removes road space, does it remove vehicle travel, or move that travel elsewhere?

It does **not** try to:

- rediscover traffic evaporation
- evaluate Superblocks as an urban-design project
- solve accessibility, equity, emissions, and VKT in one article

First paper = causal traffic effects + spatial footprint + bounded network-VKT decomposition.

## Current rule

**Manuscript drafting** (`07_manuscript/JUM_paper_draft.md`) uses assignment **v1.0**. Demand-fixed reroute is **simulated**; observed counts reject it at 250–500 m. Do not quote −7,309 veh-km as measured NVTR. Do not write LTR/NR/NVTR from the DiD table. Do not lead with local ADT on Consell de Cent.

**TR-B is paused.** Do not build the variational-inequality / evaporation-index paper in this repository.

**EMEF/ATM is still the next data input** for tightening elastic NVTR. On-axis 4066/4067 post counts remain a data request.
