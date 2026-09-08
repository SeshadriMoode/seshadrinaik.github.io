# JUM submission checklist

Portal: https://www.editorialmanager.com/urbmob/default.aspx  
Guide (re-check on the day you upload; the live page timed out in drafting): https://www.sciencedirect.com/journal/journal-of-urban-mobility/publish/guide-for-authors

Article type in EM: **Original research** / empirically-oriented contribution (case study is also listed on the journal homepage; pick the closest EM dropdown).

Open access: *Journal of Urban Mobility* is fully OA. Confirm the APC and any UPC / transformative-agreement waiver **before** completing payment screens.

---

## Locked scientific claims (do not change at upload)

- Sample is Eixos Verds phase 1 only. Nello-Deakin (2022) is cited as given; his eleven COVID tactical streets are not re-estimated.
- Preferred window is 2022 H1 versus 2024–25. The 2018–19 versus 2024–25 nearby drop is 2020 arterials, not phase 1.
- Simulated demand-fixed NVTR (−7,309 veh-km/day) is a **rejected counterfactual**, not a measurement.
- Do not lead with ADT on Consell de Cent. Do not convert Table 5 into VKT.

---

## What you must fill or confirm before EM

| Item | Status | Where |
|---|---|---|
| Affiliation (BIT–UPC, Jordi Girona 1–3, 08034 Barcelona) | taken from your other Elsevier papers | title page |
| Corresponding e-mail `seshadri.naik.moode@upc.edu` | taken from those papers | title page / cover letter |
| ORCID `0000-0002-9651-7535` | taken from your CV | title page / cover letter |
| Co-authors | **none listed** | add on the title page *before* upload if this work was jointly supervised |
| Funding | PID2019-105331RB-I00 (J-02653 Platoon); JOAN ORÓ FI AGAUR-2022 FI_B 00597 | manuscript Funding section |
| Acknowledgements | omitted (no extra thanks supplied) | — |
| Competing interests | drafted as none | confirm |
| Ethics | drafted as N/A (open counts) | confirm with UPC if needed |
| Generative-AI declaration | drafted (Cursor used for drafting/editing) | confirm wording against the current Elsevier GFA |
| Suggested reviewers | **not invented** | optional in EM; add people you actually want |
| Graphical abstract | **not produced** | optional in Elsevier; Fig. 5 + Fig. 7 can be combined later if EM asks |
| APC / OA waiver | **not checked** | UPC library / Elsevier agreement |

---

## Files to upload

1. `Moode_JUM_manuscript.docx` — Word file for Editorial Manager (regenerate with `python md_to_docx.py` after any text edit). Source markdown is `Moode_JUM_manuscript.md`.
2. `Moode_JUM_highlights.txt` — separate editable file; filename contains “highlights”.
3. `Moode_JUM_cover_letter.md` — paste into EM or upload as PDF/Word.
4. Figures `Fig1_study_area.png` … `Fig7_observed_vs_simulated.png` (300 dpi), captions from `Moode_JUM_figure_captions.md`.
5. Optional: this checklist is for you, not for the journal.

---

## Elsevier housekeeping (standard; confirm on the live GFA)

- Abstract ≤ 250 words (this draft is written to that bound; re-count after any edit).
- Highlights: 3–5 bullets, **≤ 85 characters including spaces** each.
- Keywords: 6–8 (eight are listed).
- Numbered figures and tables sequential; captions not used as in-figure titles.
- References: author–year, DOIs where they exist.
- Data availability statement present.
- CRediT present.
- Do not paste repository folder trees into the submitted text.

---

## After acceptance (not a blocker)

- Deposit processed tables and scripts in a public archive; replace “available from the corresponding author” with the DOI.
- If Gestió de la Mobilitat restores 4066/4067, that is a revision or a follow-up, not a reason to withhold this submission.
- Elastic NVTR still requires an observed OD (EMEF/ATM). Do not invent it in revision unless the matrix is actually in hand.
