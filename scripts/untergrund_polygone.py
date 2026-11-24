#!/usr/bin/env python3
"""Zieht aus swissTLM3D (TLM_BODENBEDECKUNG) die Flaechen fuer die Farbe der Hoehenlinien nach Untergrund.

  python3 untergrund_polygone.py <TLM-Ordner> <ausgabe.npz>

<TLM-Ordner> enthaelt swissTLM3D_TLM_BODENBEDECKUNG_OST/WEST.shp (LV95, PolygonZ). Ergebnis (WKB, LV95, 2D):
  gletscher       OBJEKTART «Gletscher», vereinigt (1800 Flaechen; nicht «Schneefeld Toteis»: kein Eis-Blau in der Landeskarte)
  fels, fels_b    Felsflaechen NICHT vereinigt, dazu je die Huellen (<art>_bounds, N x 4): «fels» = «Fels» und «Fels locker»,
                  «fels_b» = «Felsbloecke» und «Felsbloecke locker» (getrennt, damit sie sich weglassen lassen)
Die Felspolygone (rund 237'000) werden bewusst nicht landesweit vereinigt (unary_union sprengte zweimal 15 GB Arbeitsspeicher):
hoehenlinien2mkgmap.py laedt je 20-km-Block nur die Polygone der Huelle, schneidet sie je Kachel zu und vereinigt nur diese.
Dauer wenige Minuten. Gelesen wird der Inhalt der Shapefiles nur als Daten.
"""
import sys, numpy as np, shapefile, shapely
from shapely.geometry import shape
from shapely.ops import unary_union

ARTEN = {"Gletscher": "gletscher", "Fels": "fels", "Fels locker": "fels", "Felsbloecke": "fels_b", "Felsbloecke locker": "fels_b"}


def main():
    ordner, aus = sys.argv[1], sys.argv[2]
    teile = {k: [] for k in ("gletscher", "fels", "fels_b")}
    for s in ("OST", "WEST"):
        r = shapefile.Reader(f"{ordner}/swissTLM3D_TLM_BODENBEDECKUNG_{s}")
        arten = [rec[0] for rec in r.records(fields=["OBJEKTART"])]     # erst nur die Attribute, Formen einzeln nachladen
        for i, a in enumerate(arten):
            if a in ARTEN:
                g = shapely.force_2d(shape(r.shape(i).__geo_interface__))
                teile[ARTEN[a]].append(g if g.is_valid else shapely.make_valid(g))
    out = {}
    g = unary_union(teile["gletscher"])          # nur Gletscher landesweit: wenige Flaechen
    gl = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty]
    out["gletscher"] = shapely.to_wkb(np.array(gl, dtype=object))
    print("gletscher", len(gl), "Flaechen", round(sum(p.area for p in gl) / 1e6, 1), "km2")
    for k in ("fels", "fels_b"):
        arr = np.array([p for p in teile[k] if not p.is_empty], dtype=object)
        out[k] = shapely.to_wkb(arr)
        out[k + "_bounds"] = shapely.bounds(arr)
        print(k, len(arr), "Polygone, Summe der Einzelflaechen", round(float(shapely.area(arr).sum()) / 1e6, 1), "km2 (mit Ueberlappung)")
    np.savez_compressed(aus, **out)


if __name__ == "__main__":
    main()
