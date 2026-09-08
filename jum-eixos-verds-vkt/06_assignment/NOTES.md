# Count-constrained assignment (Step 6)

Status: **v1.0 — as-built principal centrelines on the graph. Elastic network VKT is not identified.**

v0.1 is archived in `working/v0.1/`. Do not mix those numbers with v1.0.

Labels:

| Object | Status |
|---|---|
| Station \(\Delta Q\) | **observed** (incremental 2022 H1 vs 2024–25) |
| Demand-fixed LTR / NR / NVTR | **simulated** (gravity OD, AON, principal centrelines injected, cost ×100) |
| Elastic OD / second VKT total | **not identified** with the open gravity prior |
| ATM/EMEF prior | **not used** |

## What changed from v0.1

OSM had retagged parts of Consell de Cent off the motorised extract, so v0.1 only penalised 2.58 km of leftover aligned edges. v1.0 injects the as-built principal centrelines from `04_geometry/working/phase1_principal.geojson` (4.85 km undirected). Crossing vertices snap to OSM nodes; 170 new nodes fill gaps. Directed treated length is 12.11 km (both-way injection 9.84 km plus OSM-aligned stubs).

Cost ×10, ×100 and ×1,000 produce **identical** AON flows. Once the axis is dearer than any Cerdà-grid detour, further penalty does not matter. That saturation is disclosed, not a three-scenario result.

## Simulated demand-fixed (inside the 3.5 km graph)

| | veh-km / working day |
|---|---:|
| LTR (reduction on links ≤ 40 m from the axes) | 39,597 |
| NR (change on all other links in the graph) | +46,906 |
| NVTR = LTR − NR | **−7,309** |

Network VKT **rises** by about 0.1%. 95% of |\Delta VKT| is inside 500 m. **Do not quote −7,309 as measured NVTR.**

With the axis actually on the graph, immediate counted links now fall in the simulation (−354), matching the sign of the observed −468. v0.1 had put +658 there because the missing centreline dumped the local drop onto the wrong stubs.

## The constraint: observed counts still reject one-for-one reroute

| Bin | n | Observed | Simulated demand-fixed | Residual |
|---|---:|---:|---:|---:|
| on / immediate | 8 | −468 | −354 | −114 |
| 0–250 m | 20 | −1,989 | −2,453 | +464 |
| 250–500 m | 33 | −758 | **+1,700** | **−2,458** |
| 500 m–1 km | 40 | +128 | +131 | −3 |
| 1–2 km | 66 | −726 | −118 | −608 |
| >2 km | 130 | −640 | 0 | −640 |

## Impedance sensitivity (v1.0, same AON paths)

Gravity $\beta \in \{1,2,3\}$, Furness refit, **same** pre/post shortest paths. Do **not** quote the NVTR column.

| β | Pre-fit corr / MAPE | Sim. ΔQ 250–500 m | Sign | Observed |
|---|---:|---:|---|---:|
| 1 | 0.61 / 0.68 | **+2,408** | positive | −758 |
| 2 (primary) | 0.59 / 0.69 | **+1,700** | positive | −758 |
| 3 | 0.54 / 0.72 | **+1,452** | positive | −758 |

Furness did not converge at any β. File: `working/gravity_beta_sensitivity.csv`.

## Files

- `working/run_assignment.py`
- `working/phase1` inputs via `04_geometry/working/phase1_principal.geojson`
- `working/vkt_decomposition.csv`
- `working/vkt_by_network_ring.csv`
- `working/observed_vs_simulated_delta_q.csv`
- `working/cost_factor_sensitivity.csv`
- `working/gravity_beta_sensitivity.csv`
- `working/run_meta.json`
- `working/v0.1/` — previous run

## Next

Replace the gravity prior with ATM/EMEF. Until then we do not tighten the elastic NVTR number.
