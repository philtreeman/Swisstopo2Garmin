#!/usr/bin/env python3
"""Leitet aus einer 10-m-Hoehenlinien-Datei (OSM-XML fuer mkgmap, eine Zeile je Knoten/Weg) die 20-m-Variante ab: behaelt nur Linien,
deren Hoehe (Tag ele) durch 20 teilbar ist; contour=10 wird zu contour=20 (Haupthoehenlinien 100 bleiben 100). Nicht mehr
verwendete Knoten werden weggelassen.

  python3 filter_hoehenlinien.py ein.osm aus.osm
"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
ele = re.compile(r'k="ele" v="(\d+)"')
ref = re.compile(r'<nd ref="(-?\d+)"')
keep_lines, used = [], set()
with open(src, encoding="utf8") as f:
    for line in f:
        if line.startswith("<way "):
            e = ele.search(line)
            if e and int(e.group(1)) % 20 == 0:
                keep_lines.append(line.replace('k="contour" v="10"', 'k="contour" v="20"'))
                used.update(ref.findall(line))
node = re.compile(r'<node id="(-?\d+)"')
with open(src, encoding="utf8") as f, open(dst, "w", encoding="utf8") as o:
    for line in f:
        if line.startswith("<node "):
            if node.match(line).group(1) in used:
                o.write(line)
        elif line.startswith("<way ") or line.startswith("<relation") or line.startswith("<member") or line.startswith("</relation"):
            break
        else:
            o.write(line)                       # Kopf (xml, <osm ...>)
    o.writelines(keep_lines)
    o.write("</osm>\n")
