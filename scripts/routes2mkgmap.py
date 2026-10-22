#!/usr/bin/env python3
"""Routen-/Wegenetze (LV95-GeoPackage) -> OSM-XML fuer mkgmap (Overlay-Karten).

  python3 routes2mkgmap.py --kind wanderwege --gpkg SWISSTLM3D_WANDERWEGE.gpkg --out w.osm [--bbox W S E N]
  python3 routes2mkgmap.py --kind wanderland|veloland|mtb --gpkg wanderland.gpkg --out r.osm [--bbox ...]
  python3 routes2mkgmap.py --kind ski --gpkg ski_routes_2056.gpkg --out s.osm [--bbox ...]

Tags: route_layer=<kind>, route_class=<Kategorie; Wanderwege: weg2|weg1|spur|strasse nach Wegtyp>, name=<Beschriftung>.
Quellen: swisstopo (swissTLM3D Wanderwege, Skirouten), SchweizMobil/ASTRA (Wanderland, Veloland, Mountainbikeland).
"""
import argparse
import numpy as np, pyogrio, shapely
from pyproj import Transformer
from mkgmap_xml_writer import Writer

TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
FROM_WGS = Transformer.from_crs(4326, 2056, always_xy=True)
SKI = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4, 12: 4}


def s(x):
    return x.strip() if isinstance(x, str) and x.strip() else ""


def records(kind, df):
    """liefert (geometrie, klasse, name)"""
    if kind == "wanderwege":
        # keine Farbcodierung nach Wander-/Berg-/Alpinwanderweg: die Linienart folgt dem Wegtyp der swisstopo-Zeichenerklaerung
        typ = {"2m Weg": "weg2", "1m Weg": "weg1", "Markierte Spur": "spur"}
        for r in df.itertuples(index=False):
            yield r.geometry, typ.get(r.objektart, "strasse"), s(r.name) if hasattr(r, "name") else ""
    elif kind in ("wanderland", "veloland", "mtb"):
        seen = set()
        for r in df.itertuples(index=False):
            key = (r.NrR, r.geometry.wkb_hex[:200] if r.geometry is not None else None, round(r.geometry.length) if r.geometry is not None else 0)
            if key in seen:
                continue  # Hin-/Rueckweg identisch
            seen.add(key)
            nr, nm = s(r.NrR), s(r.NameR)
            yield r.geometry, s(r.Typ_TR), (f"{nr} {nm}".strip())
    elif kind == "ski":
        for r in df.itertuples(index=False):
            d = r.difficulty
            cls = SKI.get(int(d), 0) if d == d and d is not None else 0
            nm = next((s(x) for x in (r.name_de, r.name) if s(x)), "")
            if nm.startswith("Keine Routeninfo"):
                nm = ""
            dd = s(r.difficulty_de)
            yield r.geometry, str(cls), f"{nm} {dd}".strip() if nm else ""


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--kind", required=True, choices=["wanderwege", "wanderland", "veloland", "mtb", "ski"])
    a.add_argument("--gpkg", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    a.add_argument("--simplify", type=float, default=2.0)
    o = a.parse_args()
    bb = None
    if o.bbox:
        (x0, y0), (x1, y1) = FROM_WGS.transform(o.bbox[0], o.bbox[1]), FROM_WGS.transform(o.bbox[2], o.bbox[3])
        bb = (x0, y0, x1, y1)
    layer = {"wanderwege": None, "wanderland": "Route", "veloland": "Route", "mtb": "Route", "ski": None}[o.kind]
    if o.kind == "wanderwege":
        layer = "tlm_strassen_strasse"
    mk = {"mtb": "mountainbikeland"}
    df = pyogrio.read_dataframe(o.gpkg, layer=layer, bbox=bb)
    w = Writer(o.out)
    n = 0
    for geom, cls, name in records(o.kind, df):
        if geom is None or geom.is_empty or not cls and o.kind != "ski":
            continue
        g = shapely.force_2d(geom)
        if bb:
            g = g.intersection(shapely.box(*bb))  # lange Routen auf das Gebiet zuschneiden
            if g.is_empty:
                continue
        g = g.simplify(o.simplify, preserve_topology=True)
        tags = {"route_layer": o.kind, "route_class": cls}
        if name:
            tags["name"] = name
        for part in (g.geoms if g.geom_type.startswith("Multi") else [g]):
            if part.geom_type != "LineString" or len(part.coords) < 2:
                continue
            c = np.array(part.coords)
            lon, lat = TO_WGS.transform(c[:, 0], c[:, 1])
            w.way(list(zip(lon, lat)), tags)
        n += 1
    w.close()
    print(f"{o.kind}: {n} Objekte -> {o.out}")


if __name__ == "__main__":
    main()
