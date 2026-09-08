# Step 3 — Sample and identification (Paper 1)

Status: locked for Paper 1. Phase-1 map check is done (`04_geometry/NOTES.md`). Exposure is network distance.

The audit did not kill the paper. It killed one bad design: **treated-link DiD on Eixos Verds using public on-street counters**. The proper solution is to identify the **network response**, which was the scientific object all along.

## What we will not do

- Treat Consell de Cent / Girona / Pi i Margall public on-street series as a dense before/after panel. They go dark during reconstruction.
- Call `ROCAFORT - TAMARIT` or `COMTE BORRELL - CAMPO SAGRADO` treated links until a map confirms they sit on the 2022–23 phase-1 segments (they currently look like Sant Antoni).
- Pool Gran Via with one-lane streets.
- Mix the 2020 COVID tactical set and the 2022–23 green axes into one treatment dummy.
- Re-do Nello-Deakin (2022): no 11-street tactical sample, no intervention/adjacent/500 m/control design, no “did traffic evaporate?” paper. See `NOT_NELLO_DEAKIN.md`.

## The proper design

### Sample A — primary (post-COVID, permanent)

**Treatment:** Eixos Verds phase 1 (works 16 Aug 2022 – spring 2023): Consell de Cent, Girona, Rocafort, Comte Borrell, and the four squares.

**Outcome:** monthly MADT at traffic stations, collapsed to a working-day series.

**Time:**
- Pre: 2018–2019
- Ignore: 2020–2021 (COVID) and Aug 2022–May 2023 (works)
- Post: 2024–2025

**Exposure, not a binary on-street dummy:**

Each station \(i\) gets network distance \(d_i\) to the nearest phase-1 green axis (undirected OSM shortest path; Euclidean is diagnostic only). See `04_geometry/NOTES.md`.

Estimate distance-bin DiD:

- on / immediately adjacent
- \(<250\,\mathrm{m}\)
- \(250\)–\(500\,\mathrm{m}\)
- \(500\,\mathrm{m}\)–\(1\,\mathrm{km}\)
- \(1\)–\(2\,\mathrm{km}\)
- \(>2\,\mathrm{km}\) (control)

This is the mobility footprint. It uses the stations we actually have: cross-streets and nearby links, which survived, instead of the treated-street loops that were ripped out.

### Sample C — out of Paper 1

The 2020 Eixample tactical streets **are Nello-Deakin’s sample**. Using them as a secondary empirical block, even “with 2024–25 added,” would make Paper 1 the same article. They stay in the literature review only.

### Out of Paper 1

The 2020 tactical set (Nello-Deakin). Born, Gràcia 2005–06, Horta, Pi i Margall (no public post counts), planned 22@ / Sant Antoni 2026, Glòries, Meridiana, Via Laietana. Poblenou 2016 and Sant Antoni 2018 are optional descriptive context, not identification.

## How this still gets us to VKT

Public MADT cannot give \(\sum q_a L_a\) over the whole network.

Proper bounded solution, in this order:

1. **Now (causal paper core):** \(\Delta Q\) by distance bin. That answers “does the local reduction reappear nearby?”
2. **Next (still Paper 1, Step 6):** count-constrained assignment with a prior OD, demand-fixed vs demand-elastic scenarios, to translate the observed \(\Delta Q\) pattern into \(\Delta VKT_{network}\). Until then we do not write as if we measured network VKT from the counters.

The accounting we will defend:

\[
\Delta Q_{\text{treated}} \neq \Delta VKT_{\text{network}}
\]

observed counts identify the first; the assignment model estimates the second, with the limitation stated.

## Data request (does not block starting Sample A)

Ask Gestió de la Mobilitat for 2023–25 series on stations that went dark: **4066, 4067, 4056, 6027, 6028**. If they arrive, treated-link LTR for Consell de Cent / Girona / Pi i Margall becomes a robustness check, not the design.

## Next step only

Gravity prior is in (`06_assignment/`). Replace it with ATM/EMEF when the file arrives. Do not treat simulated demand-fixed NVTR as a measurement.
