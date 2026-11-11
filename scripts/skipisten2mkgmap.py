#!/usr/bin/env python3
"""OpenStreetMap-Auszug (.osm.pbf) -> OSM-XML fuer mkgmap: Pisten (piste:type=downhill|nordic|skitour|sled).

  python3 skipisten2mkgmap.py --pbf switzerland-latest.osm.pbf --out skipisten.osm [--bbox W S E N]

Daten: OpenStreetMap-Mitwirkende, ODbL (https://www.openstreetmap.org/copyright). Einzige OSM-Quelle im Repo.
Gelesen werden Wege (Linien oder, bei area=yes bzw. geschlossen und piste:type=downhill mit area=yes, Flaechen) und
Multipolygon-Relationen mit piste:type. Tags der Ausgabe:
  piste_layer = downhill | nordic | skitour | sled
  piste_class = blue | red | black | orange | grey   (nur downhill; nach piste:difficulty)
  piste_area=yes  Flaeche (nur downhill),  piste_outline=yes  Umriss derselben Flaeche (als Linie)
  name        = piste:name | name | piste:ref | ref
Es werden keine Zwischenergebnisse der Zaehlung gespeichert; die Zaehlung steht auf stdout.
"""
import argparse
from collections import Counter
import osmium
import shapely
from shapely.geometry import LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union, polygonize
from mkgmap_xml_writer import Writer, emit_polygon

LAYERS = ("downhill", "nordic", "skitour", "sled")
CLASS = {"novice": "blue", "easy": "blue", "intermediate": "red", "advanced": "black", "expert": "black",
         "freeride": "orange", "extreme": "orange"}


def layer_of(tags):
    v = tags.get("piste:type")
    if not v:
        return None
    for p in v.split(";"):
        if p.strip() in LAYERS:
            return p.strip()
    return None


def klass(tags):
    d = (tags.get("piste:difficulty") or "").split(";")[0].strip()
    return d, CLASS.get(d, "grey")


def name_of(tags):
    for k in ("piste:name", "name", "piste:ref", "ref"):
        if tags.get(k):
            return tags[k].strip()
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pbf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    a = ap.parse_args()
    bb = box(*a.bbox) if a.bbox else None

    # Durchgang 1: Relationen (Multipolygone) und Wege mit piste:type
    rels, rel_ways = {}, set()
    for o in osmium.FileProcessor(a.pbf, osmium.osm.RELATION):
        lay = layer_of(o.tags)
        if lay and o.tags.get("type") == "multipolygon":
            tg = {t.k: t.v for t in o.tags}
            rels[o.id] = (tg, [(m.ref, m.role) for m in o.members if m.type == "w"])
            rel_ways.update(m.ref for m in o.members if m.type == "w")
    ways = {}
    for o in osmium.FileProcessor(a.pbf, osmium.osm.WAY):
        tg = {t.k: t.v for t in o.tags}
        if layer_of(o.tags) or o.id in rel_ways:
            ways[o.id] = (tg, [n.ref for n in o.nodes])
    need = {n for _, refs in ways.values() for n in refs}
    # Durchgang 2: Knotenkoordinaten
    xy = {}
    for o in osmium.FileProcessor(a.pbf, osmium.osm.NODE):
        if o.id in need:
            xy[o.id] = (o.location.lon, o.location.lat)
    del need

    def coords(ref):
        return [xy[n] for n in ways[ref][1] if n in xy]

    w = Writer(a.out)
    cnt, written = Counter(), Counter()

    def emit_line(g, tg, lay, cls):
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            if p.is_empty or p.geom_type != "LineString":
                continue
            w.way(list(p.coords), {"piste_layer": lay, "piste_class": cls if lay == "downhill" else None, "name": name_of(tg)})

    def emit_area(g, tg, lay, cls):
        polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        for p in polys:
            if p.is_empty or p.geom_type != "Polygon" or p.area == 0:
                continue
            nm = name_of(tg)
            if lay == "downhill":
                emit_polygon(w, p, {"piste_layer": lay, "piste_class": cls, "piste_area": "yes", "name": nm})
            w.way(list(p.exterior.coords), {"piste_layer": lay, "piste_class": cls if lay == "downhill" else None, "piste_outline": "yes", "name": nm}, closed=True)
            for i in p.interiors:
                w.way(list(i.coords), {"piste_layer": lay, "piste_class": cls if lay == "downhill" else None, "piste_outline": "yes"}, closed=True)

    def handle(g, tg, lay, area):
        d, cls = klass(tg)
        if bb is not None:
            g = g.intersection(bb)
            if g.is_empty:
                return
        cnt[(lay, "Flaeche" if area else "Linie", d or "-")] += 1
        (emit_area if area else emit_line)(g, tg, lay, cls)
        written[lay] += 1

    for wid, (tg, refs) in ways.items():
        lay = layer_of(tg)
        if not lay:
            continue
        c = coords(wid)
        if len(c) < 2:
            continue
        area = tg.get("area") == "yes" and len(c) >= 4 and c[0] == c[-1]
        if area:
            g = Polygon(c)
            if not g.is_valid:
                g = shapely.make_valid(g)
                g = unary_union([p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon"]) if not g.is_empty else g
        else:
            g = LineString(c)
        handle(g, tg, lay, area)
    for rid, (tg, mem) in rels.items():
        lay = layer_of(tg)
        lines = [LineString(coords(r)) for r, _ in mem if r in ways and len(coords(r)) >= 2]
        polys = list(polygonize(unary_union(lines))) if lines else []
        if not polys:
            continue
        g = unary_union(polys)
        # Rollen: innere Ringe herausrechnen
        inner = [LineString(coords(r)) for r, role in mem if role == "inner" and r in ways and len(coords(r)) >= 4]
        for ip in polygonize(unary_union(inner)) if inner else []:
            g = g.difference(ip)
        handle(g, tg, lay, True)
    w.close()
    print("Objekte (Ausgangsdaten, Layer / Art / piste:difficulty):")
    for k, v in sorted(cnt.items()):
        print(f"  {k[0]:9s} {k[1]:8s} {k[2]:14s} {v}")
    print("Je Layer geschrieben:", dict(written))


if __name__ == "__main__":
    main()
