# Step 2 — origins, destinations, network

Status: **usable.** Step 1 is locked. Do not compute ΔA until the pre/post graphs exist (Step 3).

## What we can use now

| Object | File | Status |
|---|---|---|
| Treatment geometry | `input/phase1_principal.geojson` | Copy of Paper 1 as-built principal. **4.85 km. Do not rewrite.** |
| Population (opportunities) | `input/2022_pad_mdbas.csv` | 1,068 census sections; 1,639,981 residents (1 Jan 2022) |
| Section polygons | `input/seccions_censals.json` | Open Data BCN; join to padrón is **1,068 / 1,068** on `Codi_Districte×1000 + seccio` = `Seccio_Censal` |
| Neighbourhoods (incidence) | `input/barris.json` | 73 barris; aggregate ΔA here, do not use as the origin unit |
| Centroids + distance to axes | `working/section_centroids.csv` | Euclidean centroid-to-axis (inventory only; exposure in the paper is **network** distance) |

Coverage of section centroids vs the axes (`working/section_distance_bands.csv`):

| Centroid < | Sections | Population |
|---|---:|---:|
| 250 m | 58 | 89,100 |
| 500 m | 108 | 164,942 |
| 1 km | 246 | 387,698 |
| 2 km | 530 | 820,923 |
| 3.5 km | 827 | 1,279,300 |
| city | 1,068 | 1,639,981 |

## What Paper 1’s graph is not

The sibling OSM extract (`osm_highways_phase1_buffer.json`) is a **3.5 km** clip. Assignment cost is **length**, not minutes. Zones are **53 barris** that snap inside that clip.

That graph cannot host a 15-minute car opportunity measure: 241 census sections (about 361,000 people) sit outside the clip, and 15 minutes at 20 km/h is ~5 km. Reuse from Paper 1 is the **treated-edge rule** (angle ≥ 0.8, midpoint ≤ 15 m, principal injected, cost ×100), not the clip.

The same Overpass dump already contains footway / pedestrian / cycleway / steps. Paper 1 discarded them with `HIGHWAY_OK`. Walk does **not** need a second download if we pull a citywide extract and filter in code.

## Locks for Step 3

1. **Origin / destination unit:** census section, not barri. Barri is only for incidence tables.
2. **Study area:** municipality of Barcelona (all 1,068 sections). Far sections are the control: ΔA should be ~0 there. Do not restrict origins to a sausage around Consell de Cent.
3. **Network:** new OSM extract covering the municipal bbox (≈ 8 km around the axes already contains every section). Filter **car** and **walk** from the same dump.
4. **Time, not length.** Edge time = length / speed. Defaults if OSM `maxspeed` is missing:

   | highway | car km/h |
   |---|---:|
   | motorway | 80 |
   | trunk / primary / secondary | 50 |
   | tertiary | 40 |
   | unclassified / residential | 30 |
   | living_street / service | 20 |

   Walk: **4.5 km/h** on footway, pedestrian, path, living_street, residential, and `foot!=no` service links. Steps: 2 km/h. Do not give treated axes a walk speed-up in the primary run.
5. **Post-car graph:** same through-movement penalty as Paper 1 (treated length ×100). That is an **upper bound** on car ΔT: it also hurts short on-axis trips. Robustness: drop treated edges and snap sections to the nearest untreated node.
6. **Opportunities:** 2022 population. Jobs and income are **not** in this folder yet. Income exists at Open Data BCN (`renda-disponible-llars-bcn`) for Step 5. Workplace counts wait until a file is here; do not mix jobs and population in one table.

## Walk graph (honest)

Primary walk ΔA uses the **same geometry**, no invented green-axis speed-up. If walk access barely moves, that is the result, not a failure. A “walk got faster” claim is a **stated scenario** (recoded treated edges as pedestrian), labelled simulated.

Cycle and GTFS remain out.

## Labels

| Object | Label |
|---|---|
| Pre/post shortest-path \(T_{ij}\) | **simulated** |
| \(A_i(t)\) with padrón opportunities | **estimated** (from simulated times) |
| Traffic counts / LTR / NR / NVTR | **not used** |

## Sources (URLs)

- Seccions censals JSON: `https://opendata-ajuntament.barcelona.cat/data/dataset/808daafa-d9ce-48c0-925a-fa5afdb1ed41/resource/db90a207-d125-4f80-aac5-f9d5d6e648f5/download`
- Padrón 2022: already copied from Paper 1 (`2f6e0561-30f4-44a0-8446-e27442d4754c`)
- Income (not downloaded): https://opendata-ajuntament.barcelona.cat/data/en/dataset/renda-disponible-llars-bcn
