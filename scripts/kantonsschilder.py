#!/usr/bin/env python3
"""Strassenschilder der Hauptstrassen A/B/C, die nicht im ASTRA-Hauptstrassennetz stehen (Kantonsstrassen-Nummern wie 279, 288, 566).

Quelle: swissTLM3D, Tabellen STRASSENROUTE (Route mit ROUTENNUMM, OBJEKTART Hauptstrasse A/B/C) und STRASSENROUTE_STRASSE (Verknuepfung
Route -> Strassenstueck per UUID) und die Achsen aus STRASSE. Je Route werden die Stuecke zusammengefuegt und alle 4000 m ein Punkt gesetzt
(wie bei den ASTRA-Schildern, vector2mkgmap.py). Nummern, die schon als ASTRA-Hauptstrassen-Schild (vector_shields.HAUPT) vorkommen, fallen weg.

  python3 kantonsschilder.py <shp-ordner> <out.csv>      -> CSV x,y,nr (LV95); die Nummernliste gehoert in vector_shields.KANTON
"""
import csv, sys
import numpy as np, pyogrio, shapely
import vector_shields

ABSTAND = 4000


def main(shp, out):
    T = f"{shp}/swissTLM3D_TLM_"
    rt = pyogrio.read_dataframe(T + "STRASSENROUTE.dbf", read_geometry=False)
    rt = rt[rt.OBJEKTART.isin(["Hauptstrasse A", "Hauptstrasse B", "Hauptstrasse C"])]
    rt["nr"] = rt.ROUTENNUMM.fillna("").astype(str).str.split(".").str[0]
    rt = rt[rt.nr.str.fullmatch(r"\d+") & ~rt.nr.isin([str(n) for n in vector_shields.HAUPT])]
    lk = pyogrio.read_dataframe(T + "STRASSENROUTE_STRASSE.dbf", read_geometry=False)
    lk = lk[lk.ROUTE_U.isin(set(rt.UUID))].merge(rt[["UUID", "nr"]], left_on="ROUTE_U", right_on="UUID")
    wanted = set(lk.STRASSE_U)
    st = pyogrio.read_dataframe(T + "STRASSE.shp", columns=["UUID"], read_geometry=True)
    st = st[st.UUID.isin(wanted)]
    geom = dict(zip(st.UUID, shapely.force_2d(st.geometry.values)))
    rows, nrs = [], {}
    for nr, grp in lk.groupby("nr"):
        gs = [geom[u] for u in grp.STRASSE_U if u in geom]
        if not gs:
            continue
        for ln in shapely.get_parts(shapely.line_merge(shapely.union_all(gs))):
            if ln.geom_type != "LineString" or ln.length < ABSTAND / 4:
                continue
            for d in np.arange(min(ABSTAND / 2, ln.length / 2), ln.length, ABSTAND):
                p = ln.interpolate(float(d)); rows.append((round(p.x, 1), round(p.y, 1), nr)); nrs[nr] = nrs.get(nr, 0) + 1
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["x", "y", "nr"]); w.writerows(rows)
    print(len(rows), "Schilder,", len(nrs), "Nummern")
    print(sorted(int(n) for n in nrs))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
