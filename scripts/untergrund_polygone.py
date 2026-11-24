#!/usr/bin/env python3
"""Zieht aus swissTLM3D (TLM_BODENBEDECKUNG) die Gletscherflaechen fuer die blauen Hoehenlinien.

  python3 untergrund_polygone.py <TLM-Ordner> <ausgabe.npz>

<TLM-Ordner> enthaelt swissTLM3D_TLM_BODENBEDECKUNG_OST/WEST.shp (LV95, PolygonZ). Ergebnis: WKB-Feld «gletscher» (LV95, 2D), vereinigt.
Nur OBJEKTART «Gletscher» (nicht «Schneefeld Toteis»: keine Gletscherflaeche, in der Landeskarte kein Eis-Blau). Dauer rund 15 Sekunden.
Felsflaechen (Hoehenlinien schwarz) wurden versucht: die Vereinigung der rund 250'000 Felspolygone sprengte den Arbeitsspeicher (15 GB),
daher nicht umgesetzt. Gelesen wird der Inhalt der Shapefiles nur als Daten.
"""
import sys, numpy as np, shapefile, shapely
from shapely.geometry import shape
from shapely.ops import unary_union


def main():
    ordner, aus = sys.argv[1], sys.argv[2]
    gl = []
    for s in ("OST", "WEST"):
        r = shapefile.Reader(f"{ordner}/swissTLM3D_TLM_BODENBEDECKUNG_{s}")
        arten = [rec[0] for rec in r.records(fields=["OBJEKTART"])]     # erst nur die Attribute, Formen einzeln nachladen
        for i, a in enumerate(arten):
            if a == "Gletscher":
                g = shapely.force_2d(shape(r.shape(i).__geo_interface__))
                gl.append(g if g.is_valid else shapely.make_valid(g))
    g = unary_union(gl)
    teile = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty]
    np.savez_compressed(aus, gletscher=shapely.to_wkb(np.array(teile, dtype=object)))
    print("gletscher", len(teile), "Flaechen", round(sum(p.area for p in teile) / 1e6, 1), "km2")


if __name__ == "__main__":
    main()
