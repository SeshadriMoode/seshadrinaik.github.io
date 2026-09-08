# The geography of access after a permanent mid-grid cut: Barcelona’s Eixos Verds

**Article type:** Original research article

**Target journal:** *Journal of Transport Geography* (Elsevier, ISSN 0966-6923)

---

## Title page

**Seshadri Naik Moode**<sup>a,*</sup>

<sup>a</sup> Barcelona Innovative Transportation (BIT), Universitat Politècnica de Catalunya – BarcelonaTech (UPC), Jordi Girona 1–3, 08034 Barcelona, Spain

<sup>*</sup> Corresponding author. E-mail: seshadri.naik.moode@upc.edu. ORCID: 0000-0002-9651-7535

---

## Abstract

Closing a street to through traffic is not the same as sacrificing access. This article estimates the change in residential opportunity accessibility after a counterfactual through-movement recode of Barcelona’s first permanent Eixos Verds: 4.85 km of as-built green axes on the Cerdà grid. Travel times are simulated free-flow shortest paths on one OpenStreetMap extract. Accessibility is cumulative opportunity to 2022 census-section population, checked with Hansen gravity. Two post-car graphs bound the recode (treated-edge time ×100, and treated edges removed); a third slows nearby parallels by 20%.

For 1,052 off-axis origins the median 15-minute car loss is −0.81% under ×100 and −0.18% when treated edges are dropped. Nobody gains. The 15-minute map darkens the urban edge; Hansen ranks nearby neighbourhoods. On this grid the recode barely moves citywide car opportunity to other residents. The geographical object is incidence of that small change.

**Keywords:** accessibility; cumulative opportunity; Hansen; road-space reallocation; Eixos Verds; Barcelona; 15-minute city; equity

---

## 1. Introduction

When a city removes through-movement from a street, two questions arrive together and are then confused. Did traffic fall? And did people lose access to the rest of the city? Point counts can speak to the first. They cannot speak to the second. A loop records vehicles, not opportunities reached. A short extra detour on a redundant grid can leave 15-minute catchments almost intact while still rearranging who sits on the last minute of an isochrone. Treating a local volume drop as an accessibility result is a category error — the gap this article fills.

Accessibility is the ease of reaching valued destinations (Hansen, 1959; Geurs and van Wee, 2004; Páez et al., 2012). It is a geographical quantity: it lives at origins, decays with travel time or cost, and is uneven across the city (Kwan, 1998; Neutens, 2015). Road-space reallocation, low-traffic neighbourhoods and superblocks are usually evaluated on counts, speeds, or health (Cairns et al., 1998, 2002; Nello-Deakin, 2022; Thomas and Aldred, 2024; Mueller et al., 2020). The 15-minute-city vocabulary (Moreno et al., 2021) has made access politically salient, but it has not produced a standard pre/post account of *car* opportunity after a *permanent* mid-grid cut. Cities still need to know whether closing a street to through traffic closed the city to the people who live on it, and to the people who do not.

Barcelona’s first Eixos Verds (green axes) are a clean test. In 2022–23 the city converted a tactical layout into a permanent forced-turn geometry: Consell de Cent from Vilamarí to Passeig de Sant Joan, short stretches of Girona, Rocafort and Comte Borrell, and four squares at the crossings — 4.85 km of as-built principal centreline. Through-movement on those axes was designed out. Nello-Deakin (2022) already showed that tactical versions of nearby streets could cut local average daily traffic. That local-volume result is taken as given and is not re-estimated. This article asks a different question, on the permanent geometry: how does opportunity accessibility change, and who bears the change?

The contribution is not a prettier isochrone around Consell de Cent, and it is not a city-mean delay of a few seconds. Those would fail as geography. The contribution is a labelled pre/post accessibility account on a citywide network-distance graph:

1. Simulated origin–destination travel time, car and walk;
2. Estimated cumulative-opportunity accessibility at every census section;
3. Incidence of that change by network distance and neighbourhood.

Traffic counts, vehicle-kilometres and evaporative demand are outside the objects. Jobs and transit timetables are not in the files used here; opportunities are 2022 resident population. Household disposable income per capita (2022) is joined only for incidence. Walk access is reported as a level. Walk *change* is zero until a green-axis speed-up is written as a stated scenario.

Section 2 places accessibility after a cut against the volume literature and the 15-minute-city claim. Section 3 describes phase 1 and the data. Section 4 defines the graphs, the through-movement proxies, and \(A_i(t)\). Section 5 reports corridor times, off-axis accessibility, neighbourhood incidence, and the on-axis caveat. Section 6 states what can be claimed. Section 7 concludes.

---

## 2. Access, not volume, after a street is closed

The volume column after road-space reallocation is full. Local motor traffic often falls; one-for-one displacement onto the nearest parallel is not a general law; travellers adapt on route, time, mode and destination (Cairns et al., 1998, 2002; Nello-Deakin, 2022; Thomas and Aldred, 2024; Tennøy and Hagen, 2021; Parady et al., 2025). Network vehicle-kilometres after *permanent* cuts remain thinly measured (Koorey et al., 2025). None of that is an accessibility result. A count residual called evaporation does not say whether the remaining trips still reach the same opportunities in the same time.

Hansen (1959) defined accessibility as potential for interaction, discounted by impedance. Cumulative opportunity — the mass of destinations inside a time threshold — is the indicator cities now recognise as a “15-minute” catchment (Moreno et al., 2021). It is geographically sharp and statistically brittle: a destination that sits at 14 minutes 50 seconds is in; at 15 minutes 10 seconds it is out. Gravity or Hansen forms avoid the knife-edge (Geurs and van Wee, 2004; Páez et al., 2012). This article uses cumulative opportunity as the primary map because that is the language of the 15-minute city, and Hansen as the check that must reverse any ranking produced only by the cutoff.

Equity here means incidence of \(\Delta A\), not a second welfare theory (Pereira et al., 2017; Neutens, 2015). If a 15-minute map darkens the urban edge while a Hansen map darkens the blocks next to the cut, the geography of the *indicator* has been mistaken for the geography of the *detour*. Handy (2020) warned that accessibility is easy to invoke and easy to mis-measure. Superblock evaluations that report walkability or health gains (Mueller et al., 2020) do not substitute for a pre/post car-opportunity account on the same network. Congestion on a boundary road is not access either (Verlinghieri et al., 2025).

Table 1 states the objects.

**Table 1.** What this article measures, and what it does not.

| Object | Status in this article |
|---|---|
| Simulated shortest-path time \(T_{ij}\) on OSM | **Simulated** |
| Cumulative opportunity \(A_i(t)\) with 2022 padrón | **Estimated** from simulated times |
| Hansen \(A_i\) (\(\beta = 0.05\) per minute) | Robustness, not a second paper |
| Incidence by network distance and *barri* | **Estimated** |
| Traffic counts / vehicle-kilometres | Not used |
| Jobs, GTFS | Not in the files; not invented |
| Household income (2022 RDLpc) | Joined for off-axis quintiles only |
| Invented walk speed-up on the green axes | Not in the primary walk graph |

---

## 3. Case and data

Phase 1 of the Eixos Verds is the treatment. Works ran from 16 August 2022 into spring 2023. The as-built principal centrelines used here, and not rewritten, are Consell de Cent (~3.00 km), Girona (0.75 km), Rocafort (0.60 km) and Comte Borrell (0.50 km): **4.85 km** undirected. The same streets had carried a tactical regime from 2020. This article studies the permanent through-movement cut, not Nello-Deakin’s eleven COVID tactical streets, and does not re-estimate his Euclidean-buffer design.

Origins and destinations are Barcelona’s 1,068 census sections. Opportunities \(O_j\) are 1 January 2022 *padró* population (1,639,981 residents). Neighbourhood (*barri*) and district names are used only to aggregate incidence. One car origin, section 7097 (Montbau, 869 residents), lies 331 m from the nearest motorised node and is dropped from car \(A_i\); it remains in the walk graph.

The street network is OpenStreetMap highways covering the municipal bbox (127,766 ways, retrieved 7 September 2026), clipped to the union of neighbourhood polygons plus 300 m. Car edges follow motorway-through-living-street classes, with OSM `maxspeed` where present and otherwise 80 / 50 / 40 / 30 / 20 km/h by hierarchy. Walk edges are pedestrian-usable ways at 4.5 km/h (steps 2 km/h). Current OSM has already retagged parts of Consell de Cent off the motorised extract. The as-built principal is therefore **injected** onto the car graph (9.84 km directed injected; 12.03 km directed treated), matching the forced-turn geometry rather than today’s pedestrian tag. Dijkstra weight is travel **time**, not length.

Census-section centroids snap to the giant weakly connected component (car median snap 30.8 m, \(n = 1{,}067\); walk 17.5 m, \(n = 1{,}068\)). Exposure for incidence is undirected network distance on the pre-car graph to a treated node. Euclidean distance is diagnostic only.

---

## 4. Method

### 4.1 Through-movement proxies

Let \(G^{\mathrm{pre}}\) be the injected car graph. Two post graphs bound the cut.

- **×100.** Treated edges — OSM links whose midpoint is within 15 m of the principal and whose heading satisfies \(|\cos\theta| \ge 0.8\), plus the injected centreline — have time and length multiplied by 100. This is an **upper bound** on car time loss: it also punishes short on-axis trips that leave a node sitting on a treated edge.
- **Drop-treated.** Treated edges are deleted; sections are **re-snapped** to remaining nodes. Origins that sat only on treated nodes must not keep their pre snap.

Walk pre and post are the same graph. A “walk got faster” claim would require recoding treated edges as a stated pedestrian scenario. That recode is not in the primary run.

### 4.2 Accessibility

At origin \(i\),

\[
A_i(t) = \sum_j O_j \mathbf{1}[T_{ij} \le t],
\]

with \(T_{ii} = 0\) (own-zone population is included). Thresholds: car 15 and 30 minutes; walk 15 minutes. Hansen robustness:

\[
H_i = \sum_j O_j \exp(-\beta T_{ij}), \quad \beta = 0.05~\mathrm{min}^{-1},
\]

truncated at 30 minutes. Percentage change is \(100 \times (A_i^{\mathrm{post}} - A_i^{\mathrm{pre}}) / A_i^{\mathrm{pre}}\). **Off-axis** origins have network distance \(> 0\) (\(n = 1{,}052\)). **On-axis** origins snap onto a treated node (\(n = 15\); 23,479 residents). City **means** of \(\Delta A\) are dominated by those 15 rows and are not quoted as the result.

\(T_{ij}\) is simulated. \(A_i\) is estimated. Neither is observed.

---

## 5. Results

### 5.1 Corridor time

Opposite ends of the axis band (census sections 2136 and 2067, centroids within 150 m of the principal) give simulated car times of 4.173 minutes pre and 4.608 minutes post, under both ×100 and drop-treated: **+0.44 minutes** on a 2.2 km trip. The Cerdà grid already supplies a time-competitive parallel. The penalty binds; the detour is small.

### 5.2 Off-axis opportunity

Table 2 is the city result.

**Table 2.** Off-axis census sections (\(n = 1{,}052\)). Median change in estimated car accessibility. Walk is a level (\(\Delta = 0\) by construction).

| Measure | Median \(\Delta A\) (people) | Median % |
|---|---:|---:|
| Car, 15 min, ×100 | −12,923 | **−0.81** |
| Car, 15 min, drop-treated | −2,874 | **−0.18** |
| Car, 30 min, ×100 | −1,674 | **−0.10** |
| Hansen \(\beta = 0.05\) | −7,004 | **−0.61** |
| Walk, 15 min (level) | 80,632 reachable | \(\Delta = 0\) |

No origin gains car access. The 15-minute ×100 loss is a thin isochrone-edge effect: lengthening the threshold to 30 minutes almost removes it. Hansen, with no hard cutoff, stays near −0.6% and **shrinks** with network distance. Fig. 1 maps 15-minute ×100. Fig. 2 plots both car post graphs against network distance: ×100 steepens toward the edge (correlation −0.79); drop-treated is flat (−0.07).

### 5.3 Incidence by neighbourhood

Table 3 reports district medians among off-axis sections. Drop-treated is **−0.18% in every district** (barri range −0.26% to −0.18%). Under 15-minute ×100, Eixample loses the *least* (−0.60%); Sant Andreu and Nou Barris look worse (−1.13%) because those origins already sit on the 15-minute knife-edge. That ranking is an artefact of the indicator. Hansen places the larger — still sub-1% — losses on nearby barris: Barceloneta (−0.75%), Sant Antoni (−0.72%), Raval and Poble-sec (Fig. 4).

Table 4 splits the same off-axis sections by 2022 household disposable income per capita. The lowest quintile loses more under 15-minute ×100 (−0.97% versus −0.64% in Q5) because it sits farther from the axes (median 4.3 km versus 1.5 km in Q4). Drop-treated is **−0.18% in every quintile**. Hansen is slightly *larger* in Q5 than in Q1 (Fig. 5). The 15-minute map inherits the geography of income on this grid; it does not show that the cut punished poorer origins.

**Table 4.** Off-axis census sections by 2022 disposable-income quintile (RDLpc).

| Quintile | Median € | Median network distance | ×100 % | Drop % | Hansen % |
|---|---:|---:|---:|---:|---:|
| Q1 lowest | 16,797 | 4.26 km | −0.97 | −0.18 | −0.57 |
| Q2 | 20,438 | 3.08 km | −0.81 | −0.18 | −0.59 |
| Q3 | 22,672 | 2.30 km | −0.81 | −0.18 | −0.59 |
| Q4 | 25,013 | 1.53 km | −0.64 | −0.18 | −0.62 |
| Q5 highest | 29,765 | 2.10 km | −0.64 | −0.18 | −0.64 |

**Table 3.** Median off-axis % change in 15-minute car accessibility, by district.

| District | ×100 | Drop-treated | On-axis sections |
|---|---:|---:|---:|
| Sant Andreu | −1.13 | −0.18 | 0 |
| Nou Barris | −1.13 | −0.18 | 0 |
| Horta-Guinardó | −1.10 | −0.18 | 0 |
| Sant Martí | −0.81 | −0.18 | 0 |
| Gràcia | −0.81 | −0.18 | 0 |
| Sarrià–Sant Gervasi | −0.71 | −0.18 | 0 |
| Ciutat Vella | −0.65 | −0.18 | 0 |
| Sants-Montjuïc | −0.65 | −0.18 | 0 |
| Les Corts | −0.65 | −0.18 | 0 |
| Eixample | −0.60 | −0.18 | 15 |

### 5.4 On-axis caveat

Fifteen sections snap onto the treated centreline, all in Dreta, Nova Esquerra and Antiga Esquerra de l’Eixample. Under ×100, eight lose more than half of 15-minute car opportunity; section 2065 shows −99.7%. That is the proxy trapping the snap node, not a million people becoming unreachable. Drop-treated plus re-snap returns most on-axis medians to about −0.3%; three sections remain poorly connected after the edges are deleted. Fig. 3 maps them on a separate scale. They belong in a local-access footnote, not in the city choropleth.

### 5.5 Walk

Median 15-minute walk opportunity is 80,632 residents. Because the walk graph is not recoded, \(\Delta A_{\mathrm{walk}} = 0\). That is an honest zero, not a finding that walking “stayed the same” in the lived street.

---

## 6. Discussion

On this grid, closing 4.85 km of through-movement does not close the city. Off-axis car opportunity moves by less than one percent under a punitive ×100 proxy and by about two tenths of a percent when the axis is simply taken out of the car graph. The geographical work is then to stop the 15-minute map from being read as a periphery penalty. Cumulative opportunity at a round threshold will always first drop the people who were already far. Hansen and the drop-treated graph both say the detour, such as it is, sits near the cut.

Three limits are binding. Opportunities are residents, not jobs or amenities; a workplace layer would change *levels* of \(A_i\) and might change incidence. Times are free-flow shortest paths, not congested assignment; if the cut created delay on parallels, car \(\Delta A\) would be more negative than reported here. Walk and cycle gains remain unmeasured until a stated recode or a GTFS layer exists. None of those limits licences quoting the city-mean \(\Delta A\), which is an on-axis ×100 artefact, or reading the 15-minute periphery ranking as a poverty penalty.

For practice the implication is narrow and usable. A dense orthogonal grid can absorb a permanent mid-block through-cut with a small simulated loss of car opportunity for almost every census section. Cities that want to know whether they sacrificed access should publish off-axis median \(\Delta A\) under more than one impedance, and should not colour the whole municipality with origins that sit on the closed centreline.

---

## 7. Conclusion

Barcelona’s first permanent green axes remove through traffic on 4.85 km of the Eixample grid. Simulated car travel time along that corridor rises by 0.44 minutes. Estimated 15-minute car accessibility among off-axis sections falls by 0.81% under a ×100 treated-edge penalty and by 0.18% when those edges are dropped. Hansen’s ranking is nearby, not peripheral. The 15-minute city map, used without that check, would have told the opposite geographical story. Access, on this evidence, is not the same object as traffic volume, and it is not sacrificed at city scale by this cut.

---

## Funding

This research has been partially funded by the Spanish Ministry of Economy and Competitiveness (Ministerio de Economía y Competitividad, Gobierno de España), Grant ref. PID2019-105331RB-I00, number J-02653 Platoon. Publications and other results are supported by the JOAN ORÓ FI AGAUR-2022 grant num. FI_B 00597 of the Secretariat for Universities and Research of the Department of Research and Universities of the Generalitat de Catalunya and the European Social Fund Plus.

## Ethics statement

This study uses publicly released census-section population, neighbourhood boundaries and OpenStreetMap. No human-subject data were collected. Institutional ethics approval was not required.

## Data availability

Census-section geometries and 2022 *padró* population are from Open Data BCN. The street network is OpenStreetMap. As-built phase-1 centrelines, graphs, accessibility scores and neighbourhood tables are in the accompanying research repository. Traffic counts were not used.

## References

Cairns, S., Atkins, S., Goodwin, P., 2002. Disappearing traffic? The story so far. Proc. Inst. Civ. Eng. Munic. Eng. 151 (1), 13–22.

Cairns, S., Hass-Klau, C., Goodwin, P., 1998. Traffic Impact of Highway Capacity Reductions: Assessment of the Evidence. Landor Publishing, London.

Geurs, K.T., van Wee, B., 2004. Accessibility evaluation of land-use and transport strategies: review and research directions. J. Transp. Geogr. 12 (2), 127–140.

Handy, S., 2020. Is accessibility an idea whose time has finally come? Transp. Res. Part D 83, 102319.

Hansen, W.G., 1959. How accessibility shapes land use. J. Am. Inst. Plann. 25 (2), 73–76.

Koorey, G., Johari, M., Lieswyn, J., Gregory, M., 2025. Evidence Review of Road Space Reallocation: Effect on Network Vehicle-Kilometres-Travelled. NZ Transport Agency Waka Kotahi, Research report 724.

Kwan, M.-P., 1998. Space-time and integral measures of individual accessibility: a comparative analysis using a point-based framework. Geogr. Anal. 30 (3), 191–216.

Moreno, C., Allam, Z., Chabaud, D., Gall, C., Pratlong, F., 2021. Introducing the 15-Minute City: sustainability, resilience and place identity in future post-pandemic cities. Smart Cities 4 (1), 93–111.

Mueller, N., Rojas-Rueda, D., Khreis, H., Cirach, M., Andrés, D., Ballester, J., Bartoll, X., Daher, C., Deluca, A., Echave, C., et al., 2020. Changing the urban design of cities for health: the superblock model. Environ. Int. 134, 105132.

Nello-Deakin, S., 2022. Exploring traffic evaporation: findings from tactical urbanism interventions in Barcelona. Case Stud. Transp. Policy 10, 2430–2442.

Neutens, T., 2015. Accessibility, equity and health care: review and research directions for transport geographers. J. Transp. Geogr. 43, 14–27.

Páez, A., Scott, D.M., Morency, C., 2012. Measuring accessibility: positive and normative implementations of various accessibility indicators. J. Transp. Geogr. 25, 141–153.

Parady, G., Chikaraishi, M., Oyama, Y., 2025. A walker’s paradise ain’t a driver’s hell: evaluating the causal effect of temporary road pedestrianization on traffic conditions of surrounding roads. J. Transp. Geogr. 127, 104269.

Pereira, R.H.M., Schwanen, T., Banister, D., 2017. Distributive justice and equity in transportation. Transp. Rev. 37 (2), 170–191.

Tennøy, A., Hagen, O.H., 2021. Urban main road capacity reduction: adaptations, effects and consequences. Transp. Res. Part D 96, 102848.

Thomas, A., Aldred, R., 2024. Changes in motor traffic in London’s Low Traffic Neighbourhoods and boundary roads. Case Stud. Transp. Policy 15, 101124.

Verlinghieri, E., Larrington-Spencer, H., Furlong, J., Aldred, R., Goodman, A., 2025. Can mixed-methods help us better understand congestion on Low Traffic Neighbourhood boundary roads? J. Transp. Geogr. 128, 104360.
