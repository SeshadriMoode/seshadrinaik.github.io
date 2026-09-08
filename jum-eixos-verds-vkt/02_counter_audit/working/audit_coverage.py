"""Step 2: match Barcelona aforament stations to the intervention longlist.

Street matching is name-based on Desc_aforament. Geometry comes later.
This is a coverage audit, not a causal sample.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "02_counter_audit" / "raw"
OUT = ROOT / "02_counter_audit" / "working"
INV = ROOT / "01_intervention_inventory" / "barcelona_interventions.csv"

YEARS = list(range(2017, 2026))


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def norm(s: str) -> str:
    s = strip_accents(str(s)).upper()
    s = s.replace("'", " ").replace("’", " ").replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# Street patterns for on-street (treated-link) matching.
# Each pattern is a regex applied to the normalised station description.
STREET_PATTERNS: dict[str, list[str]] = {
    "BCN-2022-EIX-CONSELLDECENT": [r"\bCONSELL DE CENT\b"],
    "BCN-2020-CONSELLDECENT-TAC": [r"\bCONSELL DE CENT\b"],
    "BCN-2022-EIX-GIRONA": [r"^(GIRONA|C GIRONA|CARRER GIRONA)$"],
    "BCN-2020-GIRONA-TAC": [r"^(GIRONA|C GIRONA|CARRER GIRONA)$"],
    "BCN-2022-EIX-ROCAFORT": [r"\bROCAFORT\b"],
    "BCN-2020-ROCAFORT-TAC": [r"\bROCAFORT\b"],
    "BCN-2022-EIX-BORRELL": [r"\b(COMTE )?BORRELL\b"],
    "BCN-2018-SANTANTONI": [
        r"\b(COMTE )?BORRELL\b",
        r"\bTAMARIT\b",
        r"\bFLORIDABLANCA\b",
        r"\bRONDA SANT ANTONI\b",
        r"\bPG SANT ANTONI\b",
        r"\bPASSEIG SANT ANTONI\b",
    ],
    "BCN-2025-SANTANTONI-DEF": [
        r"\b(COMTE )?BORRELL\b",
        r"\bPARLAMENT\b",
        r"\bALDANA\b",
    ],
    "BCN-2022-PIMARGALL": [r"\bPI I MARGALL\b", r"\bPI MARGALL\b"],
    "BCN-2019-ARAGO-S1": [r"\bARAGO\b"],
    "BCN-2020-ARAGO-S2": [r"\bARAGO\b"],
    "BCN-2020-VALENCIA": [r"\bVALENCIA\b"],
    "BCN-2020-GRANVIA": [r"\bGRAN VIA\b"],
    "BCN-2020-PAUCLARIS": [r"\bPAU CLARIS\b"],
    "BCN-2020-ROGERDELLURIA": [r"\bROGER DE LLURIA\b", r"\bLLURIA\b"],
    "BCN-2020-INDUSTRIA": [r"\bINDUSTRIA\b"],
    "BCN-2020-RONDAUNI": [r"\bRONDA (DE LA )?UNIVERSITAT\b"],
    "BCN-2020-PLUNI": [r"\bPL(ACA)? UNIVERSITAT\b", r"\bPLAZA UNIVERSITAT\b"],
    "BCN-2021-PELAI-TAC": [r"\bPELAI\b"],
    "BCN-2023-PELAI-REVISE": [r"\bPELAI\b"],
    "BCN-2020-CASTILLEJOS-TAC": [r"\bCASTILLEJOS\b"],
    "BCN-2022-VIALAIETANA": [r"\bVIA LAIETANA\b", r"\bLAIETANA\b"],
    "BCN-GLORIES": [r"\bGLORIES\b"],
    "BCN-MERIDIANA": [r"\bMERIDIANA\b"],
    "BCN-2016-POBLENOU": [
        r"\bBADAJOZ\b",
        r"\bPALLARS\b",
        r"\bLLACUNA\b",
        r"\bTANGER\b",
        r"\bPERE IV\b",
        r"\bPUJADES\b",
        r"\bAVILA\b",
        r"\bSANCHO DE AVILA\b",
    ],
    "BCN-2018-HORTA": [
        r"\bCARRER D HORTA\b",
        r"\bC HORTA\b",
        r"^HORTA$",
        r"\bFULTON\b",
        r"\bEIVISSA\b",
        r"\bCAMPOAMOR\b",
        r"\bBAIXADA DE LA COMBINACIO\b",
    ],
    "BCN-2014-HOSTAFRANCS": [
        r"\bRECTOR TRIADO\b",
        r"\bTORRE D EN DAMIANS\b",
        r"\bTORRE DAMIANS\b",
        r"\bERMENGARDA\b",
        r"\bMIQUEL BLEACH\b",
        r"\bSANT NICOLAU\b",
        r"\bCREU COBERTA\b",
    ],
    "BCN-2005-GRACIA-VILA": [r"\bPL(ACA)? (DE LA )?VILA\b", r"\bRIUS I TAULET\b"],
    "BCN-2006-GRACIA-VERDI": [r"\bVERDI\b", r"\bVIRREINA\b", r"\bASTURIES\b"],
    "BCN-1993-BORN": [r"\bPASSEIG DEL BORN\b", r"\bPG DEL BORN\b", r"\bCOMERCIAL\b"],
    "BCN-2025-22AT-AXES": [
        r"\bSANCHO DE AVILA\b",
        r"\bALMOGAVERS\b",
        r"\bPUJADES\b",
        r"\bDOCTOR TRUETA\b",
        r"\bALABA\b",
        r"\bCIUTAT DE GRANADA\b",
        r"\bFLUVIA\b",
        r"\bBOLIVIA\b",
        r"\bCRISTOBAL DE MOURA\b",
        r"\bBADAJOZ\b",
        r"\bPERE IV\b",
    ],
}


def is_traffic(desc_tipus: str) -> bool:
    t = norm(desc_tipus)
    return t in {"TRANSIT", "TRANSITO"} or t.startswith("TRANSIT")


def load_stations() -> dict[str, dict]:
    """Union of station metadata. Prefer later-year description."""
    stations: dict[str, dict] = {}
    for year in YEARS:
        path = RAW / f"{year}_aforament_descripcio.csv"
        if not path.exists():
            continue
        for row in load_csv(path):
            sid = str(row["Id_aforament"]).strip().strip('"')
            stations[sid] = {
                "id": sid,
                "desc": row["Desc_aforament"],
                "desc_norm": norm(row["Desc_aforament"]),
                "tipus": row.get("Desc_tipus_aforament", ""),
                "is_traffic": is_traffic(row.get("Desc_tipus_aforament", "")),
                "n_lanes": row.get("Num_carrils", ""),
                "district": row.get("Codi_districte") or row.get("Codi_Districte", ""),
                "barri": row.get("Codi_Barri") or row.get("Codi_barri", ""),
                "lon": row.get("Longitud", ""),
                "lat": row.get("Latitud", ""),
                "meta_year": year,
            }
    return stations


def load_year_coverage() -> dict[str, set[int]]:
    coverage: dict[str, set[int]] = defaultdict(set)
    months: dict[tuple[str, int], set[int]] = defaultdict(set)
    for year in YEARS:
        path = RAW / f"{year}_aforament_detall_valor.csv"
        if not path.exists():
            continue
        for row in load_csv(path):
            sid = str(row["Id_aforament"]).strip().strip('"')
            coverage[sid].add(year)
            try:
                months[(sid, year)].add(int(row["Mes"]))
            except (KeyError, ValueError):
                pass
    return coverage, months


def split_label(desc: str) -> tuple[str, str]:
    """Station labels are usually COUNTED_STREET - CROSS_STREET (direction)."""
    parts = re.split(r"\s+-\s+", str(desc).strip(), maxsplit=1)
    prim = norm(parts[0])
    sec = norm(parts[1]) if len(parts) > 1 else ""
    sec = re.sub(
        r"\b(SENTIT|ENTRADA|SORTIDA|PUJADA|BAIXADA|CALÇADA|CALÇADA|BESOS|LLOBREGAT|MAR|MUNTANYA|MUNTANAYA)\b.*",
        "",
        sec,
    ).strip()
    return prim, sec


def match_where(desc: str, intervention_id: str) -> str | None:
    prim, sec = split_label(desc)
    for pat in STREET_PATTERNS.get(intervention_id, []):
        if re.search(pat, prim):
            return "on_street"
        if sec and re.search(pat, sec):
            return "cross_street"
    return None


def coverage_flags(years: set[int], pre_years: list[int], post_years: list[int]) -> dict:
    pre = [y for y in pre_years if y in years]
    post = [y for y in post_years if y in years]
    return {
        "n_years": len(years),
        "years": ",".join(str(y) for y in sorted(years)),
        "n_pre": len(pre),
        "n_post": len(post),
        "has_pre_post": int(len(pre) > 0 and len(post) > 0),
        "pre_years": ",".join(str(y) for y in pre),
        "post_years": ",".join(str(y) for y in post),
    }


# Pre/post windows relative to treatment. Works year is treated as contaminated.
WINDOWS = {
    "A": {"pre": [2018, 2019], "post": [2024, 2025]},  # post-COVID permanent
    "B": {"pre": [2017, 2018], "post": [2019, 2021, 2022]},
    "C": {"pre": [2018, 2019], "post": [2021, 2022]},  # COVID tactical
    "D": {"pre": [], "post": [2017, 2018, 2019]},
    "E": {"pre": [2023, 2024, 2025], "post": []},
    "F": {"pre": [2018, 2019], "post": [2024, 2025]},
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    interventions = load_csv(INV)
    stations = load_stations()
    coverage, _months = load_year_coverage()

    # station master
    master_path = OUT / "stations_master.csv"
    with master_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "desc",
                "tipus",
                "is_traffic",
                "n_lanes",
                "district",
                "barri",
                "lon",
                "lat",
                "meta_year",
                "years_with_counts",
                "n_years_with_counts",
            ],
        )
        w.writeheader()
        for sid, st in sorted(stations.items(), key=lambda x: x[0]):
            yrs = sorted(coverage.get(sid, set()))
            w.writerow(
                {
                    **{k: st[k] for k in ["id", "desc", "tipus", "is_traffic", "n_lanes", "district", "barri", "lon", "lat", "meta_year"]},
                    "years_with_counts": ",".join(map(str, yrs)),
                    "n_years_with_counts": len(yrs),
                }
            )

    matches = []
    summary_rows = []

    for inv in interventions:
        iid = inv["id"]
        pri = inv["id_priority"]
        win = WINDOWS.get(pri, WINDOWS["C"])
        hit_stations = []
        for sid, st in stations.items():
            if not st["is_traffic"]:
                continue
            role = match_where(st["desc"], iid)
            if not role:
                continue
            yrs = coverage.get(sid, set())
            flags = coverage_flags(yrs, win["pre"], win["post"])
            hit_stations.append((sid, st, yrs, flags, role))
            matches.append(
                {
                    "intervention_id": iid,
                    "intervention_name": inv["name"],
                    "id_priority": pri,
                    "match_role": role,
                    "station_id": sid,
                    "station_desc": st["desc"],
                    "n_lanes": st["n_lanes"],
                    "lon": st["lon"],
                    "lat": st["lat"],
                    **flags,
                }
            )

        on_st = [x for x in hit_stations if x[4] == "on_street"]
        n_on = len(on_st)
        n_on_prepost = sum(x[3]["has_pre_post"] for x in on_st)
        n = len(hit_stations)
        n_prepost = sum(x[3]["has_pre_post"] for x in hit_stations)
        if n_on_prepost >= 1 and pri in {"A", "B", "C"}:
            usable = "yes_on_street"
        elif n_prepost >= 1 and pri in {"A", "B", "C"}:
            usable = "yes_cross_only"
        elif n >= 1:
            usable = "maybe"
        else:
            usable = "no"
        summary_rows.append(
            {
                "intervention_id": iid,
                "name": inv["name"],
                "id_priority": pri,
                "covid_overlap": inv["covid_overlap"],
                "n_on_street": n_on,
                "n_on_street_pre_post": n_on_prepost,
                "n_any_match": n,
                "n_any_pre_post": n_prepost,
                "on_street_ids": ";".join(x[0] for x in on_st),
                "on_street_descs": " | ".join(x[1]["desc"] for x in on_st),
                "usable_now": usable,
            }
        )

    with (OUT / "intervention_station_matches.csv").open("w", encoding="utf-8", newline="") as f:
        if matches:
            w = csv.DictWriter(f, fieldnames=list(matches[0].keys()))
            w.writeheader()
            w.writerows(matches)

    with (OUT / "intervention_coverage_summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    n_st = len(stations)
    n_tr = sum(1 for s in stations.values() if s["is_traffic"])
    print(f"stations={n_st} traffic={n_tr}")
    print("priority A/B/C with at least one pre+post station:")
    for row in summary_rows:
        if row["id_priority"] in {"A", "B", "C"}:
            print(
                f"  {row['id_priority']} {row['intervention_id']:28} "
                f"on={row['n_on_street']} on_prepost={row['n_on_street_pre_post']} "
                f"any={row['n_any_match']} usable={row['usable_now']}"
            )


if __name__ == "__main__":
    main()
