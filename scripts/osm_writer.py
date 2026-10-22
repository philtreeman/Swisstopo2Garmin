"""Gemeinsame OSM-XML-Ausgabe fuer die Konverter (vector2osm.py, routes2osm.py).

Schreibt Knoten, Wege und Multipolygon-Relationen in drei Zwischendateien und fuegt sie am Ende
in der von mkgmap erwarteten Reihenfolge (Knoten, Wege, Relationen) zusammen.
"""
import os
from xml.sax.saxutils import quoteattr


class Writer:
    def __init__(self, path):
        self.path = path
        self.nodes, self.ways, self.rels = open(path + ".n", "w"), open(path + ".w", "w"), open(path + ".r", "w")
        self.nid = self.wid = self.rid = 0

    def _tags(self, tags):
        return "".join(f"<tag k={quoteattr(k)} v={quoteattr(str(v))}/>" for k, v in tags.items() if v is not None and str(v) not in ("", "k_W", "nan", "None"))

    def node(self, x, y, tags=None):
        self.nid -= 1
        t = self._tags(tags) if tags else ""
        self.nodes.write(f'<node id="{self.nid}" lat="{y:.7f}" lon="{x:.7f}" version="1">{t}</node>\n' if t else f'<node id="{self.nid}" lat="{y:.7f}" lon="{x:.7f}" version="1"/>\n')
        return self.nid

    def way(self, coords, tags, closed=False):
        ids = [self.node(x, y) for x, y in coords]
        if closed:
            ids[-1] = ids[0]
        self.wid -= 1
        refs = "".join(f'<nd ref="{i}"/>' for i in ids)
        self.ways.write(f'<way id="{self.wid}" version="1">{refs}{self._tags(tags) if tags else ""}</way>\n')
        return self.wid

    def close(self):
        for f in (self.nodes, self.ways, self.rels):
            f.close()
        with open(self.path, "w") as out:
            out.write('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="tlm2osm">\n')
            for ext in (".n", ".w", ".r"):
                with open(self.path + ext) as f:
                    for line in f:
                        out.write(line)
                os.remove(self.path + ext)
            out.write("</osm>\n")


def ring(r):
    c = list(r.coords)
    return [(x, y) for x, y, *_ in c]


def emit_polygon(w, poly, tags):
    outer = w.way(ring(poly.exterior), tags if not poly.interiors else None, closed=True)
    if not poly.interiors:
        return
    inner = [w.way(ring(i), None, closed=True) for i in poly.interiors]
    w.rid -= 1
    members = f'<member type="way" ref="{outer}" role="outer"/>' + "".join(f'<member type="way" ref="{i}" role="inner"/>' for i in inner)
    t = dict(tags); t["type"] = "multipolygon"
    w.rels.write(f'<relation id="{w.rid}" version="1">{members}{w._tags(t)}</relation>\n')
