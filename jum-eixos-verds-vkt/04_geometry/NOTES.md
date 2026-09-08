# Phase-1 green-axis geometry and station distances

Status: **network distance is the working exposure.** Euclidean remains only as a diagnostic column.

This is **not** Nello-Deakin’s 11-street / 500 m buffer map. Stations are classified by **undirected shortest-path distance** on the OSM motorised graph to the **2022–23 built Eixos Verds**, not by membership in the 2020 tactical set.

## Treatment geometry

Phase 1 only:

- Consell de Cent, Vilamarí → Passeig de Sant Joan (~3.0 km centreline)
- Girona, Rocafort, Comte Borrell clipped around their Consell de Cent crossings to the documented lengths

Consell de Cent is built from known intersections on that stretch (OSM naming for this street is unreliable in the Eixample extract). Perpendicular streets are OSM ways, clipped.

Files:

- `working/phase1_axes.geojson` — OSM-derived (perpendiculars still include sidewalk fragments; lengths inflated)
- `working/phase1_principal.geojson` — **as-built principal centrelines** used by the study-area map and assignment v1.0 (Consell 3.00 km + Girona 0.75 + Rocafort 0.60 + Borrell 0.50 = 4.85 km)
- `working/station_distance_to_phase1.csv` (Euclidean, diagnostic)
- `working/station_network_distance_to_phase1.csv` (**exposure**)
- `working/osm_highways_phase1_buffer.json` (OSM cache)
- `working/build_network_distance.py`

## How network distance is defined

- Undirected OSM highways (motorway through living_street), UTM 31N, 3.5 km buffer around the axes.
- Sources are **densified centreline points snapped to the graph** (10 m along the axis, 20 m snap). A 40 m node sausage was rejected: it set first-parallel streets to distance 0.
- Station snap ≤ 80 m. Stations outside the graph (all Euclidean > 3.5 km) are `outside_graph_control`.
- Directed, capacity-aware assignment is Step 6, not this object.

## Map check (the audit question)

| Station | Street | Euclid | Network | Verdict |
|---|---|---:|---:|---|
| 4067 | Consell de Cent – Bruc | 0 m | 0 m | On the treated axis. Series stops after 2022. |
| 4066 | Girona – Consell de Cent | 0 m | 0 m | On the treated axis. Series stops after 2022. |
| 4056 | Consell de Cent – Castillejos | 1.03 km | 1.07 km | **Outside** phase 1 (east of Pg. Sant Joan). |
| 3024 | Rocafort – Tamarit | 433 m | 420 m | **Not** the 2022 Rocafort green axis. Sant Antoni / south. |
| 3032 | Comte Borrell – Campo Sagrado | 898 m | 1.13 km | **Not** the 2022 Borrell green axis. Paral·lel / Sant Antoni. |
| 4058 | Pg. de Gràcia – Diputació | 49 m | **244 m** | First parallel, not on-axis. Euclidean would have mis-binned it as immediate. |

Those Sant Antoni / east-of-Sant-Joan stations must not be coded as treated links.

## Why this is not a Euclidean-ring paper

Network length exceeds Euclidean for almost every station that is not on the axis (median ~200 m extra among stations on the graph). Most bin changes are **outward**: a station that looks “close as the crow flies” is farther on the grid. The Pg. de Gràcia–Diputació case is the existence proof that rings would have been the wrong exposure.

76 stations change bin relative to Euclidean (excluding the 57 outside the 3.5 km graph). 41 of those move from 1–2 km into `>2 km` control.

## Usable panel (2018–19 and 2024–25), network bins

| Bin | All traffic stations | With pre and post |
|---|---:|---:|
| on / immediate (≤40 m) | 12 | 8 |
| 0–250 m | 26 | 22 |
| 250–500 m | 44 | 37 |
| 500 m–1 km | 60 | 47 |
| 1–2 km | 85 | 71 |
| >2 km (control) | 165 | 148 |
| outside graph (control) | 57 | 54 |

The eight immediate stations with pre and post are **crossing / terminal streets** (Muntaner, Casanova, Pau Claris, Aribau–Diputació, Gran Via–Girona, Villarroel–Aragó, Gran Via–Rocafort, Pg. Sant Joan–Diputació), not loops on the rebuilt pavement. On-axis series 4066 and 4067 remain dark after 2022.

## What this step is not

Network distance is the **exposure object**. It is not LTR, not NVTR, and not a mobility-footprint radius. Those need count-constrained assignment (Step 6). Do not lead the paper with this table.
