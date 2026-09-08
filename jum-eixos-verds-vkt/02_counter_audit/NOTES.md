# Step 2 — Traffic-counter coverage audit

Status: v0.2 (on-street vs cross-street matching)

## Data used

Public Open Data BCN, 2017–2025:

- Station locations: `aforaments-descriptiu`
- Counts: `aforaments-detall` (monthly average daily traffic by day-type, not hourly)

937 unique station ids in the location files. **449 are traffic** (`Trànsit`). The rest are mainly bicycles and other modes.

Files are in `02_counter_audit/raw/`. Tables are in `02_counter_audit/working/`.

## Matching rule

Barcelona labels are `COUNTED STREET - CROSS STREET (direction)`.

- **on_street** = the counted street is the intervention street
- **cross_street** = the intervention street is only the intersecting street (useful for nearby/spillover, not as a treated-link outcome)

The first pass treated every mention of the name as a hit. That wrongly counted Passeig de Manuel Girona as Carrer de Girona, and “sentit Horta” as the Horta Superilla. v0.2 corrects that.

## What Paper 1 can already use

The COVID-era Eixample lane cuts (priority C) are well covered. That is Nello-Deakin’s world, with more years now (through 2025):

| Street | On-street stations with pre (2018–19) and post (2021–22) |
|---|---|
| Aragó | 9–11 |
| València | 7 |
| Gran Via | 16 (wide arterial; do not pool with 1-lane streets) |
| Pau Claris | 3–4 |
| Roger de Llúria | 3 |
| Pelai | 2 |
| Consell de Cent | 2 |
| Girona | 1 |
| Rocafort | 1 |
| Indústria | 1 |

So a replication/extension of the 2020 tactical set is feasible on public MADT.

## The priority-A problem (this is the important result)

The schemes we wanted as the identification core — permanent, post-COVID green axes — have **thin treated-link coverage**, because several on-street counters go silent during reconstruction.

| Scheme | On-street stations | Pre 2018–19 and post 2024–25 | What happened |
|---|---|---|---|
| Consell de Cent | 2 | 1, and only 2025 (gap in 2023–24) | `CONSELL DE CENT - BRUC` stops after 2022. `CONSELL DE CENT - CASTILLEJOS` skips 2023–24. Castillejos may also sit east of the phase-1 stretch. |
| Girona | 1 | 0 | `GIRONA - CONSELL DE CENT` stops after 2022. |
| Rocafort | 1 | 1 | `ROCAFORT - TAMARIT` continues to 2025, but Tamarit is Sant Antoni / south of Gran Via — likely **outside** the 2022–23 Eixample green-axis stretch. |
| Comte Borrell | 1 | 1 | `COMTE BORRELL - CAMPO SAGRADO` continues to 2025, but that is the Paral·lel / Sant Antoni end, not the 2022 Eixample stretch. |
| Pi i Margall | 2 | 0 | Both stations stop after 2022, i.e. when the works start. |

Nearby (cross-street) counters around Consell de Cent are much healthier: 12 matches, 7 with 2018–19 and 2024–25 (Muntaner, Casanova, Pau Claris, Sardenya, Tarragona, etc.).

**Implication for Paper 1:** on public MADT we can identify the **network around** Eixos Verds. We cannot yet claim a dense treated-link panel on the green axes themselves. That is exactly why the spatial-footprint design is the right first paper — and why a request for raw/hourly aforaments still matters.

## Other longlist rows

- **Poblenou 2016:** counters on bounding streets (Badajoz, Pujades), not inside the 3×3. Usable as a boundary/Superilla case; no pre-2016 open counts.
- **Sant Antoni 2018:** some real nearby streets (Floridablanca, Comte Borrell, Ronda Sant Antoni). Mixed with perimeter roads. Usable with care.
- **Horta:** no traffic station on Carrer d’Horta / Fulton / Eivissa in the open files.
- **Hostafrancs:** only Creu Coberta (perimeter arterial), not Rector Triadó / Torre d’en Damians.
- **Gràcia 2005–06 / Born 1993:** no matches. Drop for Paper 1.
- **Via Laietana:** 8 on-street stations, but most lack a clean 2024–25 post window in this extract.
- **Planned 22@ / Sant Antoni 2026:** ignore until built.

## What this audit does not do

- It does not place stations on the actual treated *segment* (chainage). Rocafort–Tamarit and Borrell–Campo Sagrado need a map check before they are called treated links.
- It does not estimate effects.
- It does not lock the causal sample. That is Step 3.

## Practical consequence

Paper 1 is still possible on open data, with a shifted centre of gravity:

1. **Primary identification:** Eixos Verds 2022–23 via nearby/cross-street stations plus the few surviving on-street series, 2018–19 vs 2024–25.
2. **Secondary identification:** 2020 tactical lane cuts, as a COVID-contaminated but well-instrumented set.
3. **Do not** hang the paper on Pi i Margall or on treated-link Consell de Cent / Girona until we get the missing post-reconstruction counts.

If the Ajuntament can release the 2023–25 series for stations 4066, 4067, 4056, 6027 and 6028, priority A becomes much stronger.
