# From traffic evaporation to network adaptation: quantifying the mobility footprint of urban road-space reallocation

**Article type:** Original research article (empirically-oriented contribution)

**Target journal:** *Journal of Urban Mobility* (Elsevier, ISSN 2667-0917)

---

## Title page

**Seshadri Naik Moode**<sup>a,*</sup>

<sup>a</sup> Barcelona Innovative Transportation (BIT), Universitat Politècnica de Catalunya – BarcelonaTech (UPC), Jordi Girona 1–3, 08034 Barcelona, Spain

<sup>*</sup> Corresponding author. E-mail: seshadri.naik.moode@upc.edu. ORCID: 0000-0002-9651-7535

---

## Abstract

When a city permanently removes road space, nearby counts record a local traffic reduction, not whether vehicle-kilometres travelled (VKT) left the motorised network. This article studies Barcelona’s first permanent Eixos Verds (2022–23). Exposure is undirected network distance; the outcome is working-day mean average daily traffic. A count-constrained assignment tests a demand-fixed reroute inside a 3.5 km graph.

Relative to January–July 2022, on- and immediately adjacent stations change by +79 vehicles per working day (SE 760) versus stations more than 2 km away; the 250–500 m bin is −212 (SE 544). The 2018–19 versus 2024–25 nearby drop is the 2020 arterial programme, not phase 1. Simulated demand-fixed assignment would cut 39,597 veh-km/day within 40 m (on-axis public loops 4066 and 4067 are dark after 2022, so that local cut is not counted), add 46,906 veh-km elsewhere (order-of-magnitude), and put a +1,700 veh/day surge 250–500 m away. Observed change there is −758. One-for-one redistribution on the instrumented network is rejected. Citywide net VKT is not identified. The contribution is the labelled split of local traffic reduction, redistribution and net vehicle-travel reduction.

**Keywords:** road-space reallocation; vehicle-kilometres travelled; traffic redistribution; network assignment; difference-in-differences; Eixos Verds; Barcelona; mobility footprint

---

## 1. Introduction

Cities that take a general-traffic lane, close a through-route, or turn a junction into a square are usually asked one question in public: did the cars just go next door? The monitoring that follows is almost always a set of point counts. Those counts can show that volume fell on the treated street, and they can show whether adjacent streets rose. They cannot show whether *vehicle travel* fell. Volume at a loop is not VKT. A short, intense local drop can coexist with longer detours, with trips leaving the car, or with both. Treating the local drop as a network result is an accounting error — a methodological gap this study addresses. In what follows, **traffic evaporation** is that count residual: volume that left a treated street and was not recovered on neighbouring loops (Cairns et al., 2002). It is not, by itself, trip suppression or mode shift. Those are two of several behaviours that can produce the residual; route change, retiming, destination change and leakage outside a stated graph are the others. Point counts cannot split them.

Call the drop on and immediately next to the treated links **local traffic reduction** (LTR). Call extra vehicle-kilometres on other links **redistribution** (NR). Their difference, inside a stated system boundary, is **net vehicle-travel reduction** (NVTR). Let \(B\) be the 3.5 km motorised graph around the phase-1 centrelines, and let \(L \subset B\) be the links whose undirected network distance to those centrelines is at most 40 m. Then

\[
\mathrm{NVTR}_{B} = \mathrm{LTR}_{L} - \mathrm{NR}_{B\setminus L} = -\Delta\mathrm{VKT}_{B}.
\]

The identity is defined only inside \(B\). Vehicle-kilometres that leave \(B\), leave the car, or leave the modelled working day are observationally equivalent from inside this graph: they all reduce \(\Delta\mathrm{VKT}_{B}\) relative to a demand-fixed reroute. If NR equals LTR, travel was moved inside \(B\). If NR is smaller, some travel left the motorised network or left the boundary. If NR is larger, detours added kilometres and network VKT rose even while local counts fell. The identity is not a behavioural model. It is the minimum a city needs before it claims that a street redesign reduced mobility by car. The sign is the claim: a **positive** \(\mathrm{NVTR}_{B}\) means vehicle-km inside \(B\) fell; a **negative** \(\mathrm{NVTR}_{B}\) means detours added more kilometres than the local cut removed. Simulated demand-fixed \(\mathrm{NVTR}_{B}=-7{,}309\) veh-km/day is that second case (NR > LTR). It is labelled simulated and is not a measured citywide saving.

The literature already shows that local volumes often fall when road space is cut, that one-for-one displacement onto the nearest parallel is not a general law, and that travellers adapt on route, time, mode and destination (Cairns et al., 1998, 2002; Chung et al., 2012; Nello-Deakin, 2022; Thomas and Aldred, 2024; Tennøy and Hagen, 2021; Parady et al., 2025). What it has not established is *network VKT* after *permanent* reallocation, nor the *network* distance over which any response is concentrated (Koorey et al., 2025). Section 2 walks that evidence as a matrix: the volume column is full; the VKT column is not. The question is not “did traffic evaporate?” Evaporation is a residual from counts. The question is: when a city permanently removes road space, does it remove vehicle travel, or move that travel elsewhere — and over what network distance?

Barcelona is the test bed, not the contribution. In 2022–23 the city converted the first Eixos Verds from tactical paint into a permanent forced-turn geometry: Consell de Cent from Vilamarí to Passeig de Sant Joan, short stretches of Girona, Rocafort and Comte Borrell, and four pedestrian squares at the crossings. Through-movement on those centrelines was designed out. The same streets had already lost a lane in the May 2020 tactical programme that Nello-Deakin (2022) studied. We take his local-volume result as given and do not re-estimate his eleven-street, 2019-versus-2021, Euclidean-buffer design. Those COVID-window tactical streets are not the sample here. We study the permanent regime, with January–July 2022 (tactical already in place, works not started) versus 2024–25 as the preferred treatment window.

Two empirical steps follow, and they are not interchangeable. First, a distance-bin difference-in-differences (DiD) on working-day mean average daily traffic (MADT), with exposure defined as undirected network distance to the built phase-1 axes, describes how observed volume changes with distance. That step cannot produce LTR, NR, NVTR, or a mobility-footprint radius: counters have no lengths, and bin-mean volume change is not vehicle-kilometres. Second, a count-constrained assignment on the motorised OpenStreetMap graph, with a gravity origin–destination (OD) prior, simulates the demand-fixed reroute and tests it at the same stations. The simulation is labelled simulated. An elastic-OD refit was tried and discarded as an artefact. Without an observed OD (the regional household-survey matrix is not used here), elastic network VKT is not identified.

The results are therefore bounded on purpose. Public MADT after the permanent works does not show a further collapse on crossing streets once 2020 is the baseline, nor a displacement bump at 500 m–1 km that survives sampling error. The demand-fixed model does predict a large surge 250–500 m away; the counters do not. Local through-movement was removed; one-for-one redistribution inside 3.5 km is not supported. A measured citywide NVTR is not claimed.

Section 2 places that claim against the matrix: local volumes, displacement, behaviour, congestion versus mobility, spatial footprint, and the empty VKT column. Section 3 describes phase 1 only. Section 4 sets out data, network distance, the DiD, and the assignment procedure. Section 5 reports the event path, robustness, incremental volume change, the simulated decomposition, and the count rejection. Section 6 states what can and cannot be claimed. Section 7 concludes.

---

## 2. Literature: the volume column is full; the VKT column is not

Table 1 is the evidence matrix. For each study it records what was actually measured, what remains missing, and why a later Euclidean ring around another Superblock would not close the gap. Table 2 restates that matrix as the objects this article takes on. The article is complete for those objects.

**Table 1.** Prior evidence after road-space reallocation.

| Study | Setting | What was done | Local volume | Displacement / network | Network VKT | What is missing |
|---|---|---|---|---|---|---|
| Cairns et al. (1998, 2002) | 11 countries; mixed RSR / capacity cuts | Historical evidence review of highway-capacity reductions | Down generally; “disappearing traffic” | Mixed; neighbouring counts often do not absorb the drop | Limited; inferred from counts, not assigned | Permanent mid-grid cuts; assigned network VKT; labelled demand scenario |
| Chung, Hwang and Bae (2012) | Seoul; Cheonggyecheon expressway removal then street cut | Before/after volumes and speeds; mode adaptation over years | Down then mixed | Adaptation on alternatives; subway rose | Limited | Assigned VKT; not a residential-distributor grid |
| Nello-Deakin (2022) | Barcelona; 11 COVID tactical streets | DiD on public MADT; intervention / adjacent / 500 m Euclidean / city control; 2019 H2 vs 2021 H2 | **−14.8%** vs control | Little average adjacent displacement | None | Network distance; permanent geometry; VKT; assignment. Cited here as given; not re-estimated |
| Thomas and Aldred (2024) | London; 46 LTNs | Interior vs boundary motor-traffic counts | Large interior drop | Little average boundary volume rise | Not calculated (aggregation-sensitive; authors explicit) | Assigned network VKT; LTR/NR/NVTR split |
| Goodman et al. (2023) | London (Lambeth); 2020 LTNs | MOT odometer km matched to parking permits; DiD | Resident driving down | Near-LTN km not up vs control | Resident odometer km (−1.3 km/day DiD) | Assigned *network* VKT; location of extra kilometres on the graph |
| Tennøy and Hagen (2021) | Oslo; Bryn tunnel 4→2 lanes (14 months) | Volumes, congestion, commuter adaptation | Down in tunnel (~−23% daily) | Congestion up on remaining tube and adjacent links | Limited | Network VKT; permanent street redesign |
| Parady et al. (2025) | Tokyo; temporary pedestrianisation | DiD with police counters; 500 / 750 / 1,000 m Euclidean buffers | Small / mixed | No severe surrounding increase (~5% in some specs) | None | Permanent treatment; network (not Euclidean) distance; VKT |
| Koorey et al. (2025) | International; 30 *permanent* RSR cases | Evidence review of measured network-VKT impacts | Mixed; often down on the intervention road | Surrounding-network evidence incomplete | **Insufficient** for net network VKT | The measurement this paper’s procedure is written to supply |
| Matajs et al. (2026) | Lisbon; static vs dynamic RSA | Scenario framework; modelled emissions and health | Modelled | Modelled | Modelled | Causal counts after a built treatment |
| Verlinghieri et al. (2025) | London; LTN boundary roads | Mixed-methods: delay vs what loops count | — | Congestion ≠ volume | None | VKT; delay is not mobility |
| **This study** | **Barcelona; Eixos Verds phase 1 (permanent, 2022–23)** | **Network-distance DiD + count-constrained assignment; demand-fixed LTR/NR/NVTR tested at the same counters** | **Crossing-street ΔQ after 2022 H1; on-axis series dark** | **Demand-fixed surge at 250–500 m rejected by counts** | **Simulated demand-fixed only; elastic NVTR not identified** | **Observed OD (EMEF/ATM); restored on-axis MADT** |

**Table 2.** Objects in this article, relative to Table 1.

| Object | Established in prior work? | Remaining gap | This article |
|---|---|---|---|
| Local ADT after a road-space cut | Yes (Cairns; Nello-Deakin; Thomas and Aldred) | Treating that drop as a network result | Kept as **LTR**, not as NVTR |
| One-for-one adjacent / boundary displacement | Not a general law (Nello-Deakin; Thomas and Aldred; Parady) | Euclidean buffers; tactical or LTN geometry | **Undirected network distance** on the Cerdà grid |
| Permanent vs tactical / temporary | Koorey et al. flag the permanent-VKT hole; most count studies are tactical, COVID, or temporary | Permanent mid-grid forced-turn axes | **Eixos Verds phase 1 only**; 2022 H1 vs 2024–25 |
| Assigned network VKT (LTR / NR / NVTR) | Not established (Koorey et al.); Goodman is resident km; Matajs is modelled | Lengths + stated demand scenario + count test | **Demand-fixed assignment**; NVTR labelled simulated and **rejected** at 250–500 m |
| Mobility-footprint radius | Euclidean rings (Parady); not network-distance abs. ΔVKT | Network distance containing most of abs. ΔVKT | **Simulated**: 95% of abs. ΔVKT inside 500 m; not read from the DiD |
| Elastic / citywide NVTR | Empty | Observed OD | **Not identified** (gravity prior is not EMEF) |

Nello-Deakin (2022) is the closest published study in city and data. His local-volume result on the 2020 tactical streets is taken as given. The present object is network vehicle travel after the later, permanent geometry.

### 2.1 Local traffic reduction is established

Cairns, Hass-Klau and Goodwin (1998) assembled the first large evidence review of highway-capacity reductions. Across bus lanes, pedestrianisations, bridge closures and roadworks, predicted gridlock rarely materialised, and a substantial fraction of the volume that left the treated street could not be found on neighbouring counts. Cairns, Atkins and Goodwin (2002) restated the result as “disappearing traffic”: not a single behaviour, but a bundle of route, time, destination, mode and trip-frequency responses that point counts cannot split. The demand-side counterpart is reduced, or negative induced, travel. SACTRA (1994) and Goodwin (1996) established that adding road capacity generates traffic; removing capacity can suppress trips rather than relocate them (Cairns et al., 1998, 2002). Network theory supplies two reasons why a dense, highly connected grid need not convert a local cut into severe parallel congestion. Braess (1968) showed that adding a link can raise total travel time, so removing one can improve, rather than worsen, system cost. The Downs–Thomson paradox (Downs, 1962; Thomson, 1977) is the public-transport analogue: extra road capacity draws passengers off transit and can slow both; the reverse can hold when road space is taken. Those results are the theoretical status of a demand-fixed detour model: it is a counterfactual in which only routes change, not a prediction of how travellers adapt.

Chung, Hwang and Bae (2012) give the same catalogue for a mega-project: demolition of the Cheonggyecheon expressway in Seoul, then a cut from four lanes to two on the restored street. Speeds fell and volumes rose immediately after works; over years, subway use rose and road trips fell. Travellers adapted. The outcome was still volume and speed, not network VKT.

Two features of that literature matter here. First, the outcome was almost always traffic *volume* at a cordon or a handful of links. VKT, when mentioned, was inferred from those counts, not assigned on a network with a stated OD. Second, many of the canonical cases were temporary closures, town-centre packages, or one-off arterial removals — not a permanent, mid-grid removal of through-movement on a few residential-distributor streets. The behavioural catalogue is still the right one. The measurement is not yet VKT.

### 2.2 One-for-one displacement is not a general law

Nello-Deakin (2022) is the closest published study to this one in city and data. He asked whether traffic evaporated after Barcelona’s May 2020–March 2021 tactical cuts on eleven Eixample streets. Using the same public aforament MADT, comparing the second half of 2019 with the second half of 2021, and classifying stations as intervention, adjacent parallel, 500 m Euclidean buffer, or rest-of-city control, he found about −14.8% on intervention streets relative to the control, a small adjacent increase, and a slight decrease in the wider 500 m ring. VKT was not measured. Network assignment was not attempted. The window is COVID-contaminated. The spatial object is Euclidean.

Those findings stand. The present study uses a later, permanent geometry, undirected network distance, a post-tactical baseline, and an assignment test. Consell de Cent, Girona and Rocafort appear in both papers because they were rebuilt; overlap of streets is not overlap of design.

Thomas and Aldred (2024) compile motor-traffic counts for 46 London low-traffic neighbourhoods installed in 2020–21. Interior roads fall sharply; boundary roads, adjusted for background trends, do not rise one-for-one. They interpret the gap as consistent with evaporation in Cairns’s sense, and they are explicit that they have not calculated overall traffic reduction because aggregation is sensitive to how many interior versus boundary sites are instrumented. That honesty is the right precedent. Interior-versus-boundary volume change is still not NVTR. It is the same object as Nello-Deakin’s, in another city’s filter-and-boundary geometry.

Parady, Chikaraishi and Oyama (2025) test temporary pedestrianisation in central Tokyo with police counters and difference-in-differences, and they vary the impact area at 500, 750 and 1,000 m. They find no severe surrounding volume increase: small, manageable fluctuations (around 5% in some specifications), not a one-for-one transfer onto the next street. The schemes are temporary and the buffers are Euclidean. The displacement result travels; the spatial object does not. This paper’s exposure is undirected network distance on the motorised graph, because in the Cerdà grid a Euclidean “immediate” station can be a first parallel (Passeig de Gràcia–Diputació: 49 m Euclidean, 244 m network).

### 2.3 Volume is not mobility, and congestion is not volume

A local drop of 30 cars can coexist with more vehicle-kilometres if the remaining 70 travel farther. Using average daily traffic as a mobility metric is the accounting error the LTR / NR / NVTR split exists to prevent.

Tennøy and Hagen (2021) document the complementary case. A 14-month cut of the Bryn tunnel in Oslo from four lanes to two, on a link carrying about 70,000 vehicles a day, reduced tunnel volumes (about −23% daily; more in the peak) *and* raised congestion on the remaining tube and adjacent links. Commuters changed route, time and mode; household disruption was limited. Traffic down and delay up can occupy the same intervention. Verlinghieri, Larrington-Spencer, Furlong, Aldred and Goodman (2025) make the same distinction for London LTN boundary roads: what residents mean by congestion is not what a loop counts, and delay shares can move even when mean volume does not. Neither study measures network VKT. Both rule out reading a local volume change as a welfare or mobility result.

### 2.4 The VKT column is still empty

Koorey, Johari, Lieswyn and Gregory (2025), NZ Transport Agency Waka Kotahi research report 724, reviewed measured network-VKT impacts of *permanent* road-space reallocation across 30 cases. The review finds good evidence that volumes and often VKT fall on the intervention road, and only moderate, incomplete evidence on the surrounding network. The authors could not demonstrate systemic effectiveness for net VKT reduction, largely because the evidence is not there: few studies monitor a large enough network, fewer still convert counts to vehicle-kilometres with a stated demand scenario, and almost none separate a demand-fixed reroute from demand change.

Two near-misses confirm the gap rather than fill it. Goodman, Laverty, Furlong and Aldred (2023) match Lambeth parking permits to MOT odometer records and estimate that residents inside 2020 LTNs drove 1.3 km/day less than residents elsewhere in the borough (DiD). That is a rare VKT-like object — person-level distance, not a point count — but it is resident driving, not assigned network VKT, and it does not locate extra kilometres on the graph. Matajs, Baptista, Valença, Moura and Félix (2026) give Lisbon a replicable static-versus-dynamic road-space framework and report scenario emissions and health; the VKT in that paper is modelled, not measured after a treatment.

A new Euclidean ring around another Superblock would not fill the column. Filling it requires lengths, a stated demand scenario, and a count test that can reject the reroute.

### 2.5 Scope

Table 2 is the claim of this article: local reduction kept distinct from network travel; network-distance exposure; a permanent-treatment window; a labelled demand-fixed assignment tested at the same counters. Accessibility, distributional incidence, and a regression of footprint on network topology are outside those objects. They are not estimated.

### 2.6 What this article adds

The contribution is therefore not “Barcelona, later years.” Table 2 is the claim. In short:

1. **Analysis.** The difference between local traffic reduction and network vehicle travel after a *permanent* reallocation, and how that response is distributed through the road network (not a Euclidean buffer).
2. **Solution.** A reproducible open-data procedure that turns observed counts plus a count-constrained assignment into LTR, NR, NVTR, and a mobility-footprint radius (the smallest network distance containing most of |\Delta VKT|), with demand-fixed versus demand-elastic scenarios labelled, and with a count test that can reject the reroute.

---

## 3. Study area and intervention: Eixos Verds phase 1 only

Barcelona’s Eixample is a high-density Cerdà grid. East–west streets such as Consell de Cent, Aragó and València, and north–south streets such as Girona, Rocafort and Comte Borrell, have historically carried through traffic as well as access. From May 2020 the city cut general-traffic space on a set of those streets as tactical urbanism (Nello-Deakin, 2022). From 16 August 2022 it began the first *permanent* green axes: a pedestrian-priority section with trees, a bike path, and a forced-turn rule that removes through-movement. Cars may enter a block; they are designed not to continue along the axis.

Phase 1, the treatment in this paper, is:

- **Consell de Cent**, Vilamarí → Passeig de Sant Joan (about 3.0 km of centreline);
- **Girona**, **Rocafort** and **Comte Borrell**, clipped around their Consell de Cent crossings to the documented phase-1 lengths (about 0.75, 0.60 and 0.50 km);
- **four squares** at Consell de Cent × Rocafort, × Comte Borrell, × Enric Granados and × Girona. Private vehicles cannot cross the squares. Enric Granados itself was already pedestrian-priority and is not coded as a new capacity cut.

Works ran from 16 August 2022 toward a spring 2023 opening (municipal communications targeted March–April 2023, before the municipal elections). We ignore the works months and calendar 2023. The post period is 2024–25.

Fig. 1 maps the four phase-1 axes on an Esri street basemap of central Barcelona — Consell de Cent 3.00 km, Girona 0.75 km, Rocafort 0.60 km, Comte Borrell 0.50 km, total 4.85 km. Stations are coloured by undirected OpenStreetMap network distance; larger markers are in the incremental 2022 H1 versus 2024–25 panel. The brown outline is the Eixample district; the inset locates the frame in the municipality. Panel (b) enlarges the Consell de Cent–Girona junction. On-axis stations 4066 and 4067 are marked with stars; they go dark after 2022. OpenStreetMap sidewalk fragments are not the treatment geometry.

What is *not* treatment:

- The 2020 tactical set, including Aragó, València, Gran Via, Pau Claris, Roger de Llúria, Pelai, Indústria, Ronda Universitat and Plaça Universitat. These are confounders for any 2018–19 versus 2024–25 contrast because they sit near the axes.
- Pi i Margall (a contemporaneous civic axis outside the Eixample grid; public on-street series go dark).
- Poblenou 2016, Sant Antoni 2018, Horta, Glòries, Meridiana, Via Laietana, and planned 22@ / Sant Antoni 2026 schemes.
- Rocafort–Tamarit and Comte Borrell–Campo Sagrado public stations: they continue through 2025 but sit in Sant Antoni / Paral·lel, not on the 2022 Eixample green-axis segments. They are not treated links.
- Consell de Cent–Castillejos (station 4056): about 1.07 km network east of Passeig de Sant Joan, outside phase 1.

On-axis public stations 4066 (Girona–Consell de Cent) and 4067 (Consell de Cent–Bruc) stop after 2022. Treated-pavement LTR is therefore missing from open data. Identification uses the network around the axes — crossing and nearby stations that survived reconstruction — not a dense before/after panel on the rebuilt carriageway.

---

## 4. Data and methods

Labels are locked. Observed counts identify volume change (\(\Delta Q\)). The assignment estimates a demand-fixed \(\Delta\)VKT. Elastic NVTR is not identified. Euclidean distance is diagnostic only.

### 4.1 Traffic counts

Barcelona Open Data publishes monthly aforament series (`aforaments-descriptiu` and `aforaments-detall`). The outcome is working-day MADT (`Laborable` / `Codi_tipus_dia = 2`). The open files are monthly; they contain no hour-of-day field, so retiming within the working day is not observed. Weekend and holiday series are unused. Stations are traffic stations (`Trànsit`), not bicycle counters. A station enters a two-period contrast if it has at least six pre months and six post months in that contrast. Counters cannot give network VKT: they have no complete set of link lengths and they do not observe uncounted links.

On-axis stations 4066 and 4067 have no post-2022 working-day series in the open aforament files, and no additional on-axis or crossing loops for the rebuilt pavement are in that release. Local traffic reduction on the rebuilt pedestrian-priority carriageway is therefore simulated from the forced-turn geometry, not observed as a before/after count on those loops. The incremental on/immediate panel is crossing and terminal streets that survived reconstruction. Certainty about *how much* volume left the treated kerb is correspondingly limited; certainty about whether neighbouring counted links absorbed a demand-fixed reroute is not, because that test uses the surviving stations.

### 4.2 Exposure: network distance, not buffers

Each station \(i\) is assigned undirected shortest-path distance \(d_i\) on the OSM motorised graph (motorway through living_street, UTM 31N) to the nearest phase-1 centreline, inside a 3.5 km buffer around the axes. Sources are densified centreline points snapped to the graph (10 m along the axis, 20 m snap). A 40 m node buffer was rejected: it set first-parallel streets to distance zero. Stations snap if they lie within 80 m of the graph; otherwise they are classified as outside-graph control. Directed, capacity-aware assignment is a later object (Section 4.4), not this exposure.

Network length exceeds Euclidean for almost every station that is not on the axis (median about 200 m extra among stations on the graph). Passeig de Gràcia–Diputació is 49 m Euclidean from Consell de Cent but 244 m on the grid: a Euclidean “immediate” station that is a first parallel. Seventy-six stations change bin relative to Euclidean (excluding 57 outside the 3.5 km graph). Rings would have been the wrong exposure.

Bins:

- on / immediately adjacent (≤ 40 m);
- 0–250 m;
- 250–500 m;
- 500 m–1 km;
- 1–2 km;
- \> 2 km, including stations outside the graph (control).

The usable 2018–19 and 2024–25 panel is 8, 22, 37, 47, 71, and 202 stations in those bins (148 \> 2 km on-graph plus 54 outside). The eight immediate stations with pre and post are crossing or terminal streets (Muntaner, Casanova, Pau Claris, Aribau–Diputació, Gran Via–Girona, Villarroel–Aragó, Gran Via–Rocafort, Passeig de Sant Joan–Diputació), not loops on the rebuilt pavement.

### 4.3 Distance-bin DiD on \(\Delta Q\)

Collapsed two-period DiD. For each station with enough months:

\[
\Delta Q_i = \bar Q_{i,\text{post}} - \bar Q_{i,\text{pre}},
\]

\[
\Delta Q_i = \alpha + \sum_{b \neq \text{control}} \beta_b \, 1[\text{bin}_i = b] + \varepsilon_i.
\]

Control is network distance > 2 km. The distance bins are an exposure mapping under spatial interference (Butts, 2023): closer stations are more exposed, and the remainder of the instrumented city is the control. Primary standard errors are HC1. Bartlett spatial HAC at 500 m and 1 km (Conley, 1999) and clustering on counted-street name are reported with the incremental estimates. This estimator describes how observed volume change differs by distance. It does not estimate VKT.

Three time windows are reported; only one belongs to the permanent treatment (Table 3).

**Table 3.** Identification windows.

| Window | Pre | Post | What it identifies | Role in this article |
|---|---|---|---|---|
| Cumulative | 2018–19 | 2024–25 | Change versus pre-COVID, including 2020 tactical cuts near the axes | Disclosure: not phase 1 |
| Drop 2020 counted streets | 2018–19 | 2024–25 | Same, dropping counted 2020 tactical streets that are not the 2022 axes | Robustness of the cumulative window |
| Drop Gran Via only | 2018–19 | 2024–25 | Cumulative, dropping Gran Via stations | Shows Aragó and València are enough |
| **Incremental (preferred)** | **Jan–Jul 2022** | **2024–25** | **Change after the 2020 tactical regime — the permanent works** | **Main volume result** |

Calendar 2020–21 and August 2022–May 2023 are unused. Calendar 2023 is unused. Pre-2018 is unused (COVID plus a short open series). The 2018–19 versus 2024–25 contrast is cumulative and dominated by 2020 Aragó / València / Gran Via. It is disclosed so that it is not mistaken for a phase-1 finding. Percentage change relative to the pre mean is a scale column only; it is not an elasticity and not NVTR.

### 4.4 Count-constrained assignment

Public MADT cannot form \(\sum_a q_a L_a\) over the network. The procedure below is the contribution step. It is not a measurement of network VKT.

1. Build a directed OSM motorised graph in the 3.5 km buffer, then inject the as-built principal centrelines (4.85 km undirected: Consell de Cent 3.00, Girona 0.75, Rocafort 0.60, Comte Borrell 0.50) so that links OSM has retagged off the motorised extract still exist in the *pre* network. Crossing vertices snap to existing OSM nodes; 170 new nodes fill gaps.
2. Snap 53 *barris* (neighbourhood) centroids to the graph; take 2022 *padró* population; form a gravity prior \(T_{ij} \propto P_i P_j / d_{ij}^{2}\).
3. All-or-nothing shortest paths. Scale the gravity prior toward 2022 H1 working-day counts by penalised GLS on log origin and destination factors (λ = 5×10⁴, at most 25 L-BFGS-B iterations). Correlation with counts is 0.59, MAPE 0.69, RMSE 11,421, at 297 snapped stations. The optimiser stops at the iteration cap; origin factors range from −4.45 to 2.82. Seventy of 297 stations (24%) receive assigned flow below 1 veh/day — they are unhit by any used path — and a further 56 have predicted/observed ratio outside [1/3, 3]. Simulated ΔQ magnitudes are therefore order-of-magnitude; the usable assignment result is the sign at 250–500 m.
4. Post network: injected principal edges plus OSM edges *along* those centrelines. An OSM way is treated as along-axis only if its midpoint is within 15 m of the centreline and the absolute cosine of the heading versus the local axis tangent is at least 0.8 (about 37°). Crossing stubs fail that test and remain unpenalised. A 20 m distance buffer around the axis was rejected because it penalised every crossing and allocated reroutes onto the wrong streets. Directed treated length is 12.11 km (both-way injection plus leftover OSM-aligned stubs). Cost ×10, ×100 and ×1,000 produce the same all-or-nothing flows: once the axis is dearer than any grid detour, further penalty does not change paths. Gravity impedance β ∈ {1, 2, 3} is varied on the same pre/post paths as a check that the 250–500 m sign is not an artefact of \(d_{ij}^{-2}\). Public OSM tags do not supply reliable link capacities or signal timings on this extract, so user-equilibrium / BPR assignment is not estimated; all-or-nothing is the demand-fixed limiting case, the most concentrated allocation of leftover flow onto shortest remaining paths. Spreading the same leftover over more parallels could put some of the simulated +1,700 inside the sampling error of the 250–500 m DiD (SE 544). It would not turn a predicted increase into the observed −758 unless trips left \(B\), left the car, or left the modelled working day. The count test is that sign mismatch, not the exact 1,700. Uniform extra-arm node delays of 5, 10 and 80 m are a crude turn-cost proxy on the same OD (Table 11, Panel D).
5. Re-assign the **same** OD → simulated demand-fixed flows.
6. Compare simulated \(\Delta Q\) at snapped stations with **observed** incremental \(\Delta Q\) (2022 H1 versus 2024–25). That comparison is the constraint. An uncalibrated shortest-path cartoon would have stopped at step 5 and called the output VKT.

Accounting, inside the 3.5 km graph, with local links defined as ≤ 40 m from the axes:

\[
\mathrm{LTR} = -\Delta\mathrm{VKT}_{\text{local}}, \quad
\mathrm{NR} = \Delta\mathrm{VKT}_{\text{elsewhere}}, \quad
\mathrm{NVTR} = \mathrm{LTR} - \mathrm{NR} = -\Delta\mathrm{VKT}_{\text{total}}.
\]

A **mobility-footprint radius** is the smallest ring containing at least 80% of |\Delta VKT|. Under demand-fixed assignment that radius is a property of the simulation. It is not read from the DiD table.

A second OD, refit to 2024–25 counts on the penalised network, was attempted as a demand-elastic scenario. With a 53-zone gravity prior it produced a two-million veh-km increase and count correlation 0.29 — an artefact. It is not published. Elastic network VKT is not identified until an observed OD replaces the gravity prior.

Through-traffic from outside the 3.5 km buffer is aliased into local OD via the count fit. Intra-zonal trips, trucks versus cars, and turning movements are not modelled except for the extra-arm junction-delay checks. Magnitudes of simulated \(\Delta Q\) are order-of-magnitude. The usable assignment result is the *sign* at 250–500 m, tested against counts.

---

## 5. Results

### 5.1 The cumulative window is not phase 1

An unadjusted 2018–19 versus 2024–25 bin table looks like a nearby-volume drop (Table 4; 369 stations). The table is observed \(\Delta Q\). The 0–250 m coefficient is −5,569 vehicles per working day (SE 2,343). That coefficient is Aragó, València and Gran Via — the 2020 bus and bike programme — not Consell de Cent. Three Aragó stations alone lose 26–36 thousand vehicles/day in the cumulative window. Crossing streets on the green axes are mixed (Muntaner up, Pau Claris down because of the 2020 bike lane, Casanova slightly down). The citywide control itself falls by 1,895 (SE 261).

**Table 4.** Cumulative DiD, 2018–19 versus 2024–25, versus \>2 km.

| Bin | n | DiD (veh/day) | SE |
|---|---:|---:|---:|
| On / immediate | 8 | −1,055 | 1,990 |
| 0–250 m | 22 | −5,569 | 2,343 |
| 250–500 m | 37 | −1,434 | 801 |
| 500 m–1 km | 44 | −810 | 860 |
| 1–2 km | 66 | −1,197 | 769 |
| \>2 km (control mean change) | 192 | −1,895 | 261 |

Table 5 and Fig. 2 make the time path numerical. Relative to 2019, the 0–250 m DiD versus the rest of the city is already −4,596 (SE 2,062) in 2022 H1 — before the green-axis works. 2024 and 2025 sit on the same step, not a new one. The on/immediate series is noisy and never a precise extra drop. We will not lead with “traffic fell 19% within 250 m of Consell de Cent.” That sentence is Nello-Deakin’s object with the 2020 arterials still inside the ring.

**Table 5.** Event-study DiD versus 2019, working-day MADT, versus \>2 km.

| Period | On / immediate | 0–250 m | 250–500 m | 500 m–1 km | Control mean vs 2019 |
|---|---:|---:|---:|---:|---:|
| 2018 | +437 (433) | +333 (395) | +421 (257) | +126 (252) | +344 |
| 2022 H1 | −1,290 (1,620) | **−4,596 (2,062)** | −1,244 (678) | −1,469 (570) | −904 |
| 2024 | −793 (2,103) | −5,307 (2,150) | −1,291 (798) | −872 (824) | −1,540 |
| 2025 | −1,741 (2,025) | −6,251 (2,424) | −1,751 (826) | −1,102 (920) | −1,337 |

Fig. 3 plots Table 4 against the drop-2020 and incremental specifications.

After dropping 2020 counted streets that are not the 2022 axes, no inner bin is a precise extra reduction (Table 6). On/immediate changes sign (n = 5). The remaining 1–2 km drop (−1,795, SE 722) is Diagonal / Meridiana / other corridor change, not a 2 km green-axis footprint. Dropping Gran Via alone leaves the 0–250 m coefficient still large (−6,128, SE 2,532): Aragó and València are enough. The incremental window exists because these cumulative robustness checks still mix 2020 into the nearby bins.

**Table 6.** Cumulative-window robustness, 2018–19 versus 2024–25, versus \>2 km.

| Bin | Drop 2020 tactical counted streets | Drop Gran Via only |
|---|---:|---:|
| On / immediate | +870 (1,252), n = 5 | −1,438 (2,461), n = 6 |
| 0–250 m | −1,011 (930), n = 14 | −6,128 (2,532), n = 20 |
| 250–500 m | −239 (715), n = 25 | −1,310 (859), n = 33 |
| 500 m–1 km | +114 (765), n = 38 | −704 (873), n = 42 |
| 1–2 km | −1,795 (722), n = 60 | −1,698 (700), n = 63 |

### 5.2 Incremental \(\Delta Q\): the permanent-treatment window

Table 7 and Fig. 4 are the volume result that belongs to phase 1. Pre is January–July 2022 (tactical geometry in place, permanent works not started). Post is 2024–25. The control marker in Fig. 4 is at zero by construction.

**Table 7.** Incremental DiD, 2022 H1 versus 2024–25, versus \>2 km.

| Bin | n | Pre MADT | Post MADT | Mean \(\Delta Q\) | DiD (veh/day) | SE |
|---|---:|---:|---:|---:|---:|---:|
| On / immediate | 8 | 20,966 | 20,498 | −468 | **+79** | 760 |
| 0–250 m | 20 | 24,080 | 22,091 | −1,989 | **−1,442** | 729 |
| 250–500 m | 33 | 19,362 | 18,604 | −758 | **−212** | 544 |
| 500 m–1 km | 40 | 15,398 | 15,527 | +128 | **+675** | 579 |
| 1–2 km | 66 | 14,459 | 13,733 | −726 | −180 | 524 |
| \>2 km (control) | 182 | 11,510 | 10,964 | −546 | 0 | 151 |

On and next to the axes, public MADT does not show a further drop once the 2020 regime is the baseline. The on/immediate DiD is +79 (SE 760): a crossing-street panel, not the rebuilt pavement. Stations 4066 and 4067 remain dark, so the simulated LTR of 39,597 veh-km/day on links ≤ 40 m is not a counted suppression total on the new pedestrian-priority zones. Missing on-axis MADT does not prevent the displacement test: that test is whether surviving nearby counters rose. The 0–250 m coefficient is about two standard errors and is still pulled by Aragó and Avinguda Roma; it is not LTR on the green-axis carriageway. The +675 at 500 m–1 km is one standard error — not evidence of displacement. The 250–500 m bin, which is where a demand-fixed model will later allocate detoured traffic, is −212 (SE 544) relative to a city that itself fell by 546. Bartlett spatial HAC at 500 m and 1 km and clustering on counted-street name leave that 250–500 m coefficient at −212 (SE 554, 560 and 602). Alternative network-distance bins of 0–200, 200–400 and 400–700 m are all negative (−1,078, −703, −272; HC1). Restricting post to January–July 2024–25, so both windows use the same months, leaves the 250–500 m DiD at −15 (SE 479, n = 29). The nearby non-surge is not an artefact of HC1, of the 250/500 m cut-points, or of comparing a half-year pre with a full-year post.

Table 7 is the spatial pattern of observed volume change that the assignment has to match. It is neither a measure of evaporation nor a conversion of bin means into NVTR.

### 5.3 Simulated demand-fixed LTR / NR / NVTR

If every trip stays on the network and only routes change, the assignment inside the 3.5 km graph produces Table 8 and Fig. 5.

**Table 8.** Simulated demand-fixed decomposition, 3.5 km graph (veh-km / working day).

| Quantity | Value | Label |
|---|---:|---|
| LTR (reduction on links ≤ 40 m from the axes) | 39,597 | simulated |
| NR (change on all other links in the graph) | +46,906 | simulated |
| NVTR = LTR − NR | **−7,309** | simulated; not measured |
| Pre network VKT | 6,881,281 | simulated |
| Post network VKT | 6,888,590 | simulated |

Network VKT would *rise* by about 0.1%. Detours are longer than the cut. Table 9 and Fig. 6 locate that extra travel: 95% of |\Delta VKT| is inside 500 m of the axes. The 250–500 m ring is where most of the extra vehicle-kilometres land (+25,922); 40–250 m also gains (+16,539). The 500 m figure is a simulated mobility-footprint radius under demand-fixed routing. It is not an observed radius from Table 7.

**Table 9.** Simulated demand-fixed \(\Delta\)VKT by network ring (veh-km / working day).

| Ring | \(\Delta\)VKT |
|---|---:|
| 0–40 m | −39,597 |
| 40–250 m | +16,539 |
| 250–500 m | +25,922 |
| 500 m–1 km | +3,883 |
| 1–2 km | +562 |
| 2–3.5 km | 0 |

Simulated ΔVKT is exactly zero on links 2–3.5 km from the axes. On this OSM extract, NVTR inside 2 km therefore equals NVTR inside the 3.5 km boundary: enlarging \(B\) cannot add simulated load that is not already on the graph. A 4–5 km extract is not used. Observed mean ΔQ beyond 2 km is −546 (Table 7) and −640 at the snapped assignment stations (Table 10). That citywide decline is the control, not a split of leakage versus suppression.

These numbers are the demand-fixed counterfactual. They are not a measured NVTR.

### 5.4 The constraint: observed counts reject that counterfactual

Table 10 and Fig. 7 compare mean incremental \(\Delta Q\) at snapped stations with the demand-fixed prediction.

**Table 10.** Observed incremental \(\Delta Q\) versus simulated demand-fixed \(\Delta Q\) (veh / working day).

| Bin | n | Observed | Simulated demand-fixed | Residual (obs − sim) |
|---|---:|---:|---:|---:|
| On / immediate | 8 | −468 | **−354** | −114 |
| 0–250 m | 20 | −1,989 | −2,453 | +464 |
| 250–500 m | 33 | −758 | **+1,700** | **−2,458** |
| 500 m–1 km | 40 | +128 | +131 | −3 |
| 1–2 km | 66 | −726 | −118 | −608 |
| \>2 km | 130 | −640 | 0 | −640 |
| Obs. mean vs +1,700 | 33 | −758 | +1,700 | t = −4.67 |

Demand-fixed says the missing through-traffic should show up on counted links 250–500 m away (+1,700). Those links track the rest of the city (−758 observed, versus −640 beyond 2 km), not a reroute surge. Net of the citywide residual that a fixed-OD model cannot see, the 250–500 m gap is still about −1,800 vehicles/day. The extra 46,906 veh-km in the simulation did not appear on the instrumented network. With the as-built centrelines on the graph, the immediate bin now has the right *sign* (−354 simulated, −468 observed): flow leaves the treated links. The rejection is the nearby surge, not the local drop. At those 33 stations the observed mean ΔQ is −758 (SD 3,025, SE 527). Against the simulated constant +1,700, t = −4.67 (p < 0.001). That test is of the count residual, not of NVTR. A DiD of +1,700 with the observed HC1 standard error (544) would be detected at 88% power (two-sided, α = 0.05): the panel is not too noisy to have seen the surge.

The gravity prior, scaled only by a median factor, correlates 0.16 with pre-period counts. Penalised GLS at λ = 5×10⁴ raises that to 0.59 (MAPE 0.69, RMSE 11,421, n = 297) and stops at the iteration cap. Simulated \(\Delta Q\) magnitudes are order-of-magnitude. The **sign** at 250–500 m is the usable result: a demand-fixed model must put extra volume there, and the counters do not.

That sign is a property of the grid under fixed demand, not of the poorly fitted prior. Removing through-movement on a Cerdà street forces remaining OD pairs onto next-shortest paths; those paths are first parallels and streets in the 250–500 m ring. Gravity impedance β changes how many short versus long trips the prior contains. It does not reverse that topological loading. Cost factors ×10, ×100 and ×1,000 already produce identical all-or-nothing paths (Table 11). Refitting origins and destinations at β = 1 and β = 3 on those same paths leaves simulated \(\Delta Q\) at 250–500 m at +2,408 and +1,452 (primary β = 2: +1,700). A gravity-only scale, GLS at λ ∈ {5×10³, 5×10⁴, 5×10⁵}, and 80 optimiser iterations all keep that simulated change positive (+2,014 to +1,283; Table 11, Panel D). Observed \(\Delta Q\) there remains −758. Weak spatial fit can distort how large the simulated surge is. It does not create the surge, and it does not explain why the counters fail to show one.

Uniform junction delays rewrite the *pre* graph. An 80 m extra-arm delay already removes the axes from all 2,307 all-or-nothing paths before the policy penalty, so it is not a post-treatment check. Delays of 5 m and 10 m leave 26 and 24 OD pairs on the axes; the leftover reroute does not reproduce the length-only +1,700 loading at the counted 250–500 m stations (simulated ΔQ −780 and +2). Cost factors ×10–×1,000, which isolate the forced-turn without emptying the pre network, leave the +1,700 unchanged. Turn penalties can move simulated leftover flow across rings. They do not produce a counted nearby surge.

Putting the missing Consell de Cent centreline back on the graph multiplies *both* LTR and NR; NVTR stays a ~0.1% rise (Table 11). The immediate-bin simulation changes sign, from an OSM-stub artefact (+658) to a local drop (−354). The 250–500 m rejection does not.

Table 11 collects the assignment specification and the geometry and impedance checks. Assignment rows are simulated except the observed \(\Delta Q\) line.

**Table 11.** Assignment specification and geometry robustness.

*Panel A. Count-constrained assignment (as-built 4.85 km).*

| Item | Value | Label |
|---|---|---|
| Zones | 53 *barris* | gravity prior \(T_{ij} \propto P_i P_j / d_{ij}^{2}\) |
| Count-fit stations | 297 | 2022 H1 working-day MADT |
| Correlation / MAPE / RMSE | 0.59 / 0.69 / 11,421 | penalised GLS on gravity prior |
| GLS (λ = 5×10⁴, ≤ 25 iter.) | stopped at iteration cap; 70/297 stations unhit | magnitudes order-of-magnitude |
| Origin / dest. log-factors | [−4.45, 2.82] / [−3.50, 1.94] | 53 zones; 2,307 OD pairs |
| Treated-cost ×10, ×100, ×1,000 | identical AON paths | once the axis is dearer than any grid detour |
| Elastic OD refit | discarded (corr. 0.29) | not identified |
| Simulated footprint (80% of abs. ΔVKT) | 500 m (94.8% at 500 m) | simulation property, not DiD |

*Panel B. Leftover OSM stubs versus as-built principal centrelines.*

| | OSM stubs (2.58 km) | As-built principal (4.85 km, injected) |
|---|---:|---:|
| Directed treated km | 2.58 | 12.11 |
| LTR (veh-km/day) | 8,666 | 39,597 |
| NR (veh-km/day) | +15,725 | +46,906 |
| NVTR (veh-km/day) | −7,059 | −7,309 |
| Simulated \(\Delta Q\), on / immediate | +658 | −354 |
| Simulated \(\Delta Q\), 250–500 m | +3,624 | +1,700 |
| Observed \(\Delta Q\), 250–500 m | −758 | −758 |
| Pre-fit correlation | 0.56 | 0.59 |

*Panel C. Gravity impedance β on the same pre/post paths (sign check, not a new NVTR).*

| Gravity β | Pre-fit corr. / MAPE | Sim. \(\Delta Q\) at 250–500 m |
|---|---|---|
| 1 | 0.61 / 0.68 | **+2,408** (positive) |
| 2 (primary) | 0.59 / 0.69 | **+1,700** (positive) |
| 3 | 0.54 / 0.72 | **+1,452** (positive) |
| Observed \(\Delta Q\), 250–500 m | — | −758 |

*Panel D. Count-fit and junction delay (sign at 250–500 m; not a new NVTR).*

| Count-fit | Pre-fit corr. / MAPE | Sim. \(\Delta Q\) at 250–500 m |
|---|---|---|
| Gravity + median scale only | 0.16 / 1.56 | **+2,014** (positive) |
| GLS λ = 5×10³, 25 iter. | 0.59 / 0.69 | **+1,739** (positive) |
| GLS λ = 5×10⁴, 25 iter. (primary) | 0.59 / 0.69 | **+1,700** (positive) |
| GLS λ = 5×10⁵, 25 iter. | 0.58 / 0.69 | **+1,810** (positive) |
| GLS λ = 5×10⁴, 80 iter. | 0.62 / 0.66 | **+1,283** (positive) |
| Junction delay 5 m/arm | 0.53 / 0.74 | −780 (26 OD pairs on-axis in pre) |
| Junction delay 10 m/arm | 0.52 / 0.80 | +2 (24 OD pairs on-axis in pre) |
| Junction delay 80 m/arm | 0.46 / 0.99 | 0 (axes unused in pre) |
| Observed \(\Delta Q\), 250–500 m | — | −758 |

Neither NVTR is a measurement.

That is the LTR ≠ NVTR statement that can be defended without treating NVTR as measured:

- Local through-movement on the axes is removed (by design; on-axis counts are still dark).
- If demand were fixed and remaining trips took shortest-distance paths, nearby counted links should have risen. They did not.
- Therefore the demand-fixed NVTR (−7,309) is not what happened on the instrumented 3.5 km network. Some combination of trip suppression, mode shift, destination change, retiming, and leakage outside \(B\) absorbed the flow. Those channels cannot be split with the data used here. Absence of a 250–500 m surge is not a measurement of evaporation.

---

## 6. Discussion

### 6.1 Interpretation

Phase 1 is a forced-turn geometry plus four squares. Public on-axis series 4066 and 4067 cease after reconstruction, so LTR on the rebuilt pedestrian-priority carriageway comes from the assignment (39,597 veh-km/day on links ≤ 40 m), not from a post-rebuild loop. The displacement test uses stations that continued to report.

A length-only demand-fixed assignment on that geometry predicts a large positive \(\Delta Q\) at 250–500 m. Observed \(\Delta Q\) there follows the city, not the simulation. The incremental DiD at 500 m–1 km (+675, SE 579) is within one standard error of zero. Crossing-street on/immediate \(\Delta Q\) is indistinguishable from the control (+79, SE 760). Localized adjacent displacement on the instrumented 3.5 km network is therefore not the observed pattern.

Even under the rejected demand-fixed run, local VKT falls by 39,597 veh-km while network VKT would rise. Table 7 and Table 8 are different objects.

The demand-fixed model allows only rerouting. Disappearing traffic is a bundle of route, time, destination, mode and trip-frequency responses (Cairns, Atkins and Goodwin, 2002); reduced demand is the capacity-removal counterpart of induced travel (SACTRA, 1994; Goodwin, 1996). On a dense grid, removing a link need not produce severe parallel congestion (Braess, 1968; Downs, 1962; Thomson, 1977). Tennøy and Hagen (2021) document the empirical analogue: remaining-link volumes fell while congestion rose, and travellers changed route, time and mode. The Barcelona counts are consistent with that catalogue. They do not split the residual into suppression, mode shift, retiming, destination change or leakage beyond \(B\). Leakage here includes macro-rerouting onto the Ronda Litoral or Ronda de Dalt: those ring roads sit outside the 3.5 km graph, so a trip that leaves \(B\) for a Ronda is observationally equivalent, from inside this assignment, to a trip that left the car. Widening \(B\) until it contains the Rondes would be a different system boundary and a different paper. Simulated ΔVKT is already zero in the 2–3.5 km ring on the present extract, so leftover flow is not sitting in that outer ring waiting to be counted.

The 2018–19 versus 2024–25 nearby drop is the 2020 arterial programme (Aragó, València, Gran Via). The incremental window isolates phase 1 from that earlier cut. Low-emission-zone rules and metropolitan transit fares in 2022–25 apply across the municipality. The >2 km control differences those common shocks to the extent they load the Eixample and the rest of the city equally. A more central bite than the control would pull nearby DiD down; it would not, by itself, produce the demand-fixed +1,700 at 250–500 m.

### 6.2 Scope of the estimates

Citywide elastic NVTR is not identified. The gravity prior is not a household-survey matrix; the penalised GLS adjustment hits the iteration cap and leaves 70 of 297 stations unhit; a second OD refit to 2024–25 counts was an artefact; and \(B\) is a 3.5 km graph, not the metropolitan system. Simulated −7,309 is the demand-fixed counterfactual that the counts reject: network VKT inside \(B\) would *rise* because detours are longer than the cut. Simulated ΔVKT is zero in the 2–3.5 km ring, so leftover flow that left \(B\) is not recovered by widening the present extract. Observed decline beyond 2 km (−546 mean ΔQ) is consistent with a citywide drop and does not separate leakage from suppression, retiming or mode shift. Whether that leftover is true evaporation or VKT pushed onto the Rondes is exactly the unidentified object.

On-axis LTR is likewise simulated. Stations 4066 and 4067 remain empty in 2023–25. Station 4056 reappears in 2025 from May, 1.07 km network east of phase 1, and is not treated-pavement LTR.

### 6.3 Monitoring

Before it cuts a street, a city can: (i) instrument the network by **network distance**, not a 500 m circle; (ii) keep a **pre-works baseline after any earlier tactical regime**, so that paint and concrete are not pooled; (iii) report LTR, NR and NVTR from an assignment with a **stated demand scenario**, and show the count residual; (iv) treat a demand-fixed NVTR that the counts contradict as a rejected counterfactual, not as a headline saving. Health, retail and accessibility remain outside the present objects.

### 6.4 Limitations

No observed OD: public EMEF is corona-level. Dark on-axis stations 4066 and 4067 (and 6027, 6028) after 2022, so treated-pavement LTR is simulated rather than counted; no further on-axis loops are in the open release. Treated geometry is the as-built 4.85 km; directed treated length (12.11 km) still double-counts some parallel OSM stubs. The gravity prior, after penalised GLS, fits counts at correlation 0.59, with 24% of stations unhit; simulated \(\Delta Q\) magnitudes are order-of-magnitude, while the 250–500 m sign stays positive across β, λ, iteration cap and a median-scale-only prior. Open aforaments are monthly working-day MADT, so peak-hour retiming is not observed. Link capacities and signal timings are not in the OSM extract, so equilibrium assignment is not estimated. Uniform extra-arm delays of 5–80 m are a proxy, not an observed turn penalty; 80 m already empties the axes in the pre network. Manual Pla de Mobilitat Urbana counts are not in the open aforament release used here and are not substituted for 4066 and 4067. The literature review is organised around the volume-versus-VKT distinction that structures the research question.

---

## 7. Conclusion

Road-space reallocation is advocated, and contested, as a change in how much people drive. The data cities actually collect are how many vehicles pass a point. This paper keeps those objects apart for Barcelona’s first permanent green axes.

On public working-day MADT, the large nearby drop between 2018–19 and 2024–25 is the 2020 arterial programme, not Eixos Verds phase 1. Relative to 2022 H1, crossing and nearby stations do not show a further local collapse or a precise displacement bump. A simulated, order-of-magnitude demand-fixed assignment on the as-built 4.85 km of phase-1 centreline would have produced 39,597 veh-km/day of local reduction, 46,906 veh-km of extra travel elsewhere, a small rise in network VKT, and a surge at 250–500 m. The counters reject that surge. Local through-movement was designed out; one-for-one redistribution inside 3.5 km is not what happened on the instrumented streets. That finding is a lack of localized adjacent displacement. It is not a measured net reduction in citywide vehicle travel. Leftover flow may have shifted to other modes, other hours, other destinations, or links outside the 3.5 km graph.

Net vehicle travel for the city is still unmeasured. Until an observed origin–destination matrix is on the graph, NVTR remains a labelled scenario, not a statistic. The mobility-footprint procedure — network distance, a clean incremental window, and a count-constrained split of LTR, NR and NVTR — is the result that travels. The next data input tightens the number. It does not change the question.

---

## CRediT authorship contribution statement

**Seshadri Naik Moode:** Conceptualization; Methodology; Software; Formal analysis; Validation; Visualization; Writing – original draft; Writing – review & editing.

---

## Declaration of competing interest

The author declares that he has no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

---

## Funding

This research has been partially funded by the Spanish Ministry of Economy and Competitiveness (Ministerio de Economía y Competitividad, Gobierno de España), Grant ref. PID2019-105331RB-I00, number J-02653 Platoon. Publications and other results are supported by the JOAN ORÓ FI AGAUR-2022 grant num. FI_B 00597 of the Secretariat for Universities and Research of the Department of Research and Universities of the Generalitat de Catalunya and the European Social Fund Plus.

---

## Ethics statement

This study uses publicly released traffic-count series, neighbourhood boundaries and census population. No human-subject data were collected. Institutional ethics approval was not required.

---

## Data availability

Traffic counts are from Ajuntament de Barcelona Open Data (datasets *aforaments-descriptiu* and *aforaments-detall*; monthly working-day MADT extracts for 2017–2025). Neighbourhood (*barris*) boundaries and 2022 *padró* population are from the same portal. The street network is OpenStreetMap motorised highways. The ATM/EMEF origin–destination matrix was not used.

Processed station-level panels, difference-in-differences tables, assignment outputs and the Python scripts that reproduce all numbered tables and figures are available from the corresponding author and will be deposited in an open repository upon acceptance.

---

## Declaration of generative AI in scientific writing

During the preparation of this work the author used language-model assistance (Cursor) in order to draft and edit the manuscript. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the publication.

---

## References

Cairns, S., Atkins, S., Goodwin, P., 2002. Disappearing traffic? The story so far. *Proceedings of the Institution of Civil Engineers — Municipal Engineer* 151 (1), 13–22.

Butts, K., 2023. Difference-in-differences with spatial spillovers. arXiv:2105.03737.

Cairns, S., Hass-Klau, C., Goodwin, P., 1998. *Traffic Impact of Highway Capacity Reductions: Assessment of the Evidence*. Landor Publishing, London.

Chung, J.H., Hwang, K.Y., Bae, Y.K., 2012. The loss of road capacity and self-compliance: Lessons from the Cheonggyecheon stream restoration. *Transport Policy* 21, 165–178. https://doi.org/10.1016/j.tranpol.2012.01.009

Conley, T.G., 1999. GMM estimation with cross sectional dependence. *Journal of Econometrics* 92 (1), 1–45. https://doi.org/10.1016/S0304-4076(98)00084-0

Goodman, A., Laverty, A.A., Furlong, J., Aldred, R., 2023. The impact of 2020 Low Traffic Neighbourhoods on levels of car/van driving among residents: Findings from Lambeth, London, UK. *Findings*. https://doi.org/10.32866/001c.75470

Koorey, G., Johari, M., Lieswyn, J., Gregory, M., 2025. *Evidence Review of Road Space Reallocation: Effect on Network Vehicle-Kilometres-Travelled*. NZ Transport Agency Waka Kotahi research report 724. ViaStrada Ltd. https://www.nzta.govt.nz/resources/research/reports/724

Matajs, C.R., Baptista, P., Valença, G., Moura, F., Félix, R., 2026. How does road space allocation affect the environment and health? An evaluation framework for dynamic and static urban interventions. *Journal of Transport & Health* 49, 102316. https://doi.org/10.1016/j.jth.2026.102316

Nello-Deakin, S., 2022. Exploring traffic evaporation: Findings from tactical urbanism interventions in Barcelona. *Case Studies on Transport Policy* 10, 2430–2442. https://doi.org/10.1016/j.cstp.2022.11.003

Parady, G., Chikaraishi, M., Oyama, Y., 2025. A walker’s paradise ain’t a driver’s hell: Evaluating the causal effect of temporary road pedestrianization on traffic conditions of surrounding roads. *Journal of Transport Geography* 127, 104269. https://doi.org/10.1016/j.jtrangeo.2025.104269

Tennøy, A., Hagen, O.H., 2021. Urban main road capacity reduction: Adaptations, effects and consequences. *Transportation Research Part D* 96, 102848. https://doi.org/10.1016/j.trd.2021.102848

Thomas, A., Aldred, R., 2024. Changes in motor traffic in London’s Low Traffic Neighbourhoods and boundary roads. *Case Studies on Transport Policy* 15, 101124. https://doi.org/10.1016/j.cstp.2023.101124

Verlinghieri, E., Larrington-Spencer, H., Furlong, J., Aldred, R., Goodman, A., 2025. Can mixed-methods help us better understand congestion on Low Traffic Neighbourhood boundary roads? *Journal of Transport Geography* 128, 104360. https://doi.org/10.1016/j.jtrangeo.2025.104360

---

## Figure captions

**Fig. 1.** Phase-1 green axes (4.85 km) and public traffic stations by undirected network distance. (a) Study area. (b) Consell de Cent–Girona. Basemap: Esri World Street Map.

**Fig. 2.** Event-study DiD versus 2019, working-day MADT, by network-distance bin versus stations more than 2 km from the axes. Error bars: HC1.

**Fig. 3.** DiD versus >2 km under three windows: 2018–19 vs 2024–25; the same without counted 2020 tactical streets; and 2022 H1 vs 2024–25.

**Fig. 4.** Incremental DiD, 2022 H1 versus 2024–25, versus the >2 km control. Error bars: HC1.

**Fig. 5.** Simulated demand-fixed LTR, NR and NVTR, 3.5 km graph.

**Fig. 6.** Simulated demand-fixed \(\Delta\)VKT by network ring.

**Fig. 7.** Observed incremental mean \(\Delta Q\) versus simulated demand-fixed \(\Delta Q\) at snapped stations.
