# Step 1 — Barcelona intervention inventory

Status: longlist v0.1 (dated, sourced, not yet a causal sample)

## Purpose of this step

Build a machine-readable list of road-space reallocations in Barcelona with:

- a unique id
- location
- intervention type
- start and end dates (or best available window)
- capacity change, if known
- permanence (tactical / made-permanent / purpose-built)
- COVID overlap
- a preliminary identification priority
- sources

We are **not** deciding yet which schemes enter the paper.

## Inclusion rule for the longlist

Include a scheme if it **permanently or tactically reduced general-traffic carriageway capacity** inside the municipality of Barcelona (lane removal, modal filter, forced-turn green axis, pedestrianisation, or equivalent).

## Exclude from the longlist (for now)

These may matter later as confounders, but they are not road-space reallocation:

- ZBE / Low Emission Zone (regulatory access, not geometry)
- parking prices, resident-parking zones
- Superilla *plans* that were not built
- one-way or signal changes with no capacity loss, unless they are part of a documented Superilla package

## Identification priority (preliminary)

This is a working label only. Step 3 will override it after the counter audit.

| Code | Meaning | Typical cases |
|---|---|---|
| **A** | Best identification window: permanent, post-COVID, dated, high intensity | Eixos Verds phase 1; Pi i Margall |
| **B** | Permanent, pre-COVID, dated, but fewer open-data years before 2017 | Poblenou 2016; Sant Antoni 2018 |
| **C** | COVID-era tactical set (already studied by Nello-Deakin) | May 2020–Mar 2021 Eixample streets |
| **D** | Early / historical; pre-period counts likely missing | Born 1993; Gràcia 2005–06 |
| **E** | Planned or not yet built | 22@ flexible axes; Sant Antoni 2026 works |
| **F** | Mixed corridor reconstruction (RSR + tunnels/urban design) | Glòries, Meridiana, Via Laietana, Diagonal |

Priority A is the core of a defensible first paper. C is useful as a replication/extension of Nello-Deakin, not as the identification core. F may enter later as robustness or as a separate corridor analysis.

## Important coding rules

1. **Same street, two treatments = two rows.** Consell de Cent, Girona and Rocafort had a 2020 tactical lane cut *and* a 2022–23 permanent green axis.
2. **Works period ≠ treatment start.** For causal analysis we will later need both: works-start (disruption) and opening (new regime).
3. **Pelai is a reverse case.** Tactical extra sidewalk in 2021; later redesign restored more vehicle/loading space. Keep it, but do not mix it with the green-axis set.
4. **Enric Granados was already pedestrian-priority** before Eixos Verds. The 2022–23 project mainly added the square at Consell de Cent. Do not treat the whole street as a new capacity cut.

## What this version still lacks

- Exact chainage (from street X to street Y) for every row
- GIS geometry
- A complete 2014–2019 Superilla package list for Les Corts / Hostafrancs
- Confirmation of which 2020 tactical schemes were later reversed
- Official municipal treatment file (does not appear to exist as open data)

Those are Step 1 refinements and Step 2 inputs, not reasons to stop.

## Next step (only after this longlist is accepted)

Map aforament stations onto these streets and see which rows have pre/post counts.
