# Distance-bin DiD on observed ΔQ

Status: **done as the volume step.** This is necessary and **not** the contribution.

Object: working-day MADT (`Laborable` / `Codi_tipus_dia = 2`) at traffic stations, classified by **network distance** to Eixos Verds phase 1.

This step does **not** measure VKT, LTR, NR, NVTR, or a mobility-footprint radius. Those need lengths and count-constrained assignment (Step 6). `did_over_pre_pct` is a scale column only.

## Estimator

Collapsed two-period DiD. For each station with ≥6 pre months and ≥6 post months:

\[
\Delta Q_i = \bar Q_{i,\text{post}} - \bar Q_{i,\text{pre}}
\]

then

\[
\Delta Q_i = \alpha + \sum_{b \neq \text{control}} \beta_b \, 1[\text{bin}_i = b] + \varepsilon_i
\]

Control = network distance > 2 km, including stations outside the 3.5 km graph. HC1 standard errors. 369 stations in the main sample.

Time windows (locked):

| Spec | Pre | Post | What it identifies |
|---|---|---|---|
| Main | 2018–19 | 2024–25 | Cumulative change vs pre-COVID, including 2020 tactical cuts that sit near the axes |
| Incremental | 2022 Jan–Jul | 2024–25 | Change **after** the 2020 tactical regime, i.e. the permanent works |
| Drop 2020 streets | 2018–19 | 2024–25 | Same as main, dropping counted streets from the 2020 tactical set that are **not** the 2022 axes |

2020–21 and Aug 2022–May 2023 are unused. 2023 is unused.

## The result that matters

A naive 2018–19 vs 2024–25 bin table looks like a nearby-volume drop. It is not a phase-1 finding.

**Main (2018–19 vs 2024–25), ΔQ vs >2 km control, vehicles / working day**

| Bin | n | DiD | SE |
|---|---:|---:|---:|
| on / immediate | 8 | −1,055 | 1,990 |
| 0–250 m | 22 | **−5,569** | 2,343 |
| 250–500 m | 37 | −1,434 | 801 |
| 500 m–1 km | 44 | −810 | 860 |
| 1–2 km | 66 | −1,197 | 769 |
| >2 km (control mean change) | 192 | −1,895 | 261 |

The 0–250 m coefficient is Aragó / València / Gran Via (2020 bus and bike lanes), not Consell de Cent. Three Aragó stations alone lose 26–36 thousand vehicles/day. Crossing streets on the green axes are mixed (Muntaner up, Pau Claris down because of the 2020 bike lane, Casanova slightly down).

**After dropping those 2020 counted streets**, no inner bin is a precise extra reduction. On/immediate even changes sign (n = 5). The remaining 1–2 km drop (−1,795, SE 722) is Diagonal / Meridiana / other corridor change, not the green axes. Do not read it as a 2 km footprint.

**Incremental (2022 H1 vs 2024–25)** — this is the contrast that belongs to the permanent treatment:

| Bin | n | DiD | SE |
|---|---:|---:|---:|
| on / immediate | 8 | +79 | 760 |
| 0–250 m | 20 | −1,442 | 729 |
| 250–500 m | 33 | −212 | 544 |
| 500 m–1 km | 40 | +675 | 579 |
| 1–2 km | 66 | −180 | 524 |
| >2 km (control mean change) | 182 | −546 | 151 |

On and next-to the axes, public MADT does not show a further drop once the 2020 regime is the baseline. The 0–250 m incremental coefficient is about two standard errors and is still pulled by Aragó and Av. Roma; it is not LTR on the rebuilt pavement. The +675 at 500 m–1 km is one standard error — not evidence of displacement.

The event path (raw bin means minus 2019) shows the same split: the 0–250 m series is already far below the other bins in 2022 H1, before the green-axis works.

## What this means for the paper

1. Counters still cannot give network VKT. This table is \(\Delta Q\), observed.
2. We will not lead with “traffic fell 19% within 250 m of Consell de Cent.” That sentence is Nello-Deakin’s object with the 2020 arterials still inside the ring.
3. On-axis LTR remains missing in public data (4066, 4067 dark after 2022). Crossing-street LTR is imprecise.
4. Step 6 should take **station-level** \(\Delta Q\) as counts to match, not these bin averages as the shock. The preferred time contrast for the *permanent* axes is the incremental file (`station_delta_q_incremental_2022h1.csv`). The 2018–19 vs 2024–25 file is the cumulative regime.

## Files

- `working/estimate_did.py`
- `working/station_delta_q.csv` — station-level cumulative ΔQ
- `working/station_delta_q_incremental_2022h1.csv` — station-level incremental ΔQ
- `working/did_two_period.csv` / `did_drop_tac2020.csv` / `did_drop_gran_via.csv` / `did_incremental_2022h1.csv`
- `working/event_year_did.csv`, `year_bin_means.csv`
- `figures/did_decay_main.png`, `did_decay_drop_tac2020.png`, `did_decay_incremental_2022h1.png`, `event_path_vs_2019.png`

## Next step only

Count-constrained assignment with a prior OD, demand-fixed vs demand-elastic, using these station ΔQ series as the count targets. Until that exists we do not write LTR / NR / NVTR, and we do not call any of these bars a mobility-footprint radius.
