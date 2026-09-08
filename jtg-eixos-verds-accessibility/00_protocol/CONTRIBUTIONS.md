# What Paper 2 must contribute

A prettier isochrone around Consell de Cent is **not** a contribution. If the result could be summarised as “car travel times rose a little on the green axis,” the paper has failed.

Paper 1 already shows: local volumes can fall; demand-fixed rerouting is **rejected** by nearby counts; network VKT is not identified from MADT alone.

## The contribution (this is the filter)

**Novel analysis.** Measure how a *permanent* through-movement cut changes **access to opportunities** (jobs, schools, or a locked destination set), and **who** bears that change, on a network-distance graph.

**Novel solution.** A transparent pre/post accessibility accounting on the same OSM graph used for the volume study:

1. **ΔT** — simulated shortest-path (or generalised-cost) time by OD pair  
2. **ΔA** — estimated change in opportunity accessibility at origins  
3. **Incidence** — how ΔA is distributed across neighbourhoods (and income if the census file is in this repo)

That is a method for cities that already know volumes can fall and still need to know whether access was sacrificed.

## What does *not* count as novelty

| Tempting output | Why it is not enough |
|---|---|
| “Cars go around the Superblock” | Routing cartoon; Paper 1 already simulated that |
| City-mean ΔT of a few seconds | Hides incidence |
| Walk/cycle isochrones with no pre/post car comparator | Different object, often already in Superilla reports |
| Re-using LTR/NR/NVTR as accessibility | Those are vehicle-km identities, not access |

## Inputs from Paper 1 (read-only)

- `04_geometry/working/phase1_principal.geojson`
- OSM extract and treated-edge penalty used in `06_assignment`
- Do **not** copy DiD tables into this manuscript as new results
