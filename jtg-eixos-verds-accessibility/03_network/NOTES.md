# Step 3 — pre/post graphs

Status: **usable.** Travel time is the Dijkstra weight. Do not compute citywide ΔA until Step 4.

## What was built

Same Overpass dump (127,766 ways, municipal bbox + 500 m), clipped to the union of barris + 300 m.

| Graph | Nodes | Directed edges | File |
|---|---:|---:|---|
| Car pre (principal injected, unpenalised) | 79,893 | 109,238 | `working/car_pre.pkl` |
| Car post (treated time ×100) | same | same | `working/car_post.pkl` |
| Car post robustness (treated edges removed) | 79,646 | 108,507 | `working/car_post_drop.pkl` |
| Walk (pre = post) | 296,711 | 712,786 | `working/walk.pkl` |

Treated-edge rule is Paper 1’s: inject `phase1_principal.geojson`, mark OSM links with midpoint ≤ 15 m and heading |cos θ| ≥ 0.8. Injected **9.84 km** directed; treated **12.03 km** directed (Paper 1 clip had 12.11 km).

Scripts: `working/fetch_osm.py`, `working/build_graphs.py`. OSM cache is gitignored (`osm_highways_barcelona.json`, ~75 MB).

## Time, not length

Edge time = length / speed. OSM `maxspeed` when present; otherwise the Step 2 table. Injected principal = 30 km/h. Walk = 4.5 km/h (steps 2 km/h). Walk graph is **not** sped up on the green axes.

## Snaps (census-section centroids, 200 m)

| Mode | Snapped | Median snap |
|---|---:|---:|
| Car pre | 1,067 / 1,068 | 30.8 m |
| Car drop-treated (re-snapped) | 1,067 / 1,068 | 31.5 m |
| Walk | 1,068 / 1,068 | 17.5 m |

Unsnapped car: section **7097** (Montbau, 869 residents, 331 m to the nearest motorised node). Leave it out of car \(A_i\); do not raise the snap radius to chase Collserola.

## Smoke test (simulated \(T_{ij}\))

Opposite ends of the axis band (sections 2136 → 2067, centroids < 150 m from the axes):

| | minutes |
|---|---:|
| Car pre | 4.173 |
| Car post ×100 | 4.608 |
| Car post drop (re-snap) | 4.608 |

**+0.44 min** on a 2.2 km corridor trip. The Cerdà grid already supplies a time-competitive parallel. The penalty **binds**, but the detour is small.

On-axis *local* trips are where ×100 is an upper bound: 2143 → 2093 is 1.19 min pre, **15.85 min** after ×100, **2.62 min** after drop-and-re-snap. Primary car post remains ×100 (same proxy as Paper 1). Report drop-treated as robustness, with sections **re-snapped** to untreated nodes. Do not reuse pre snap nodes on the drop graph — those nodes can vanish with the treated edges.

Walk ΔA is **zero by construction** until a stated pedestrian recode.

## Labels

Pre/post shortest-path times are **simulated**. Next step estimates \(A_i(15)\) and \(A_i(30)\) from those times and the 2022 padrón.
