# What Paper 1 must contribute

A later intervention, more counters, or finer buffers is **not** a contribution. If the result could be summarised as “traffic also fell around Consell de Cent,” the paper has failed.

We take as already shown:

- Local traffic can fall when road space is cut (Cairns et al.; Nello-Deakin 2022; Thomas & Aldred 2024).
- One-for-one displacement onto parallel streets is not a general law.
- Network VKT after road-space reallocation is still **not** established (NZTA 2025).

## The contribution (this is the filter)

**Novel analysis.** Measure the difference between local traffic reduction and network vehicle travel after a *permanent* reallocation, and how that response is distributed through the road network.

**Novel solution.** A reproducible open-data procedure that turns observed counts plus a count-constrained assignment into three quantities a city can use before it cuts a street:

1. **LTR** — local traffic reduction on / next to the treated links  
2. **NR** — redistribution (extra vehicle-km elsewhere)  
3. **NVTR** — net vehicle-travel reduction inside a stated system boundary  

and a **mobility-footprint radius** (network distance within which most of the measurable response occurs).

That is a method and an accounting identity, not a Superblock case study.

## What does *not* count as novelty

| Tempting output | Why it is not enough |
|---|---|
| 2018–19 vs 2024–25 MADT on Eixample streets | Same object as Nello-Deakin, different dates |
| Six Euclidean rings instead of a 500 m buffer | Incremental GIS, same volume outcome |
| “Traffic fell on Consell de Cent” | He already showed local ADT can fall |
| Another Superilla / liveability / health narrative | Large existing literature |
| An uncalibrated shortest-path cartoon labelled as VKT | Not a solution; it is a guess |

## What every next step has to serve

- **Network distance**, not buffers (exposure object).  
- **VKT decomposition**, not ADT as a proxy for mobility (outcome object).  
- **Assignment with a prior OD and stated demand scenarios**, not “the counters imply evaporation.”  
- **Transparency:** observed / estimated / simulated / inferred stay separate.

If a task does not move one of those, we do not do it in Paper 1.

## Working order (novelty first)

1. Network distance from every traffic station to phase-1 axes. **done**  
2. Distance-bin DiD on \(\Delta Q\) — necessary, not the contribution. **done** (2020 stacking disclosed; incremental 2022 H1 contrast is the permanent-treatment window)  
3. Count-constrained assignment → \(\Delta VKT\) and the LTR / NR / NVTR split — this is the contribution. **v1.0 done** (principal 4.85 km; demand-fixed simulated and rejected by counts at 250–500 m; elastic VKT not identified without EMEF)  
4. Literature matrix in parallel only as far as it frames that gap. **done** (`05_literature/`). Next data input is EMEF / 4066–4067, not a second literature thinning.

No paper draft that leads with local ADT. Euclidean rings are retired as exposure. Bin-mean \(\Delta Q\) is not LTR. Simulated demand-fixed NVTR is not measured NVTR.
