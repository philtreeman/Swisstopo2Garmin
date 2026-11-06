#!/usr/bin/env python3
"""Erzeugt mkgmap/unterkuenfte/typ/unterkuenfte_winter.txt (Family-ID 3922, «swisstopo Unterkuenfte Winter»).

  0x10f00 Unterkunft Winter (ch.swisstopo.unterkuenfte-winter)  13 x 13, roter Ring wie im swisstopo-Viewer
  0x10f01 SAC-Huette, nicht im Winter-Datensatz (swissNAMES3D)    9 x 9,  kleines Haus mit braunem Dach
  0x10f02 uebrige Huette (swissNAMES3D)                           9 x 9,  kleines Haus mit grauem Dach

Roter Ring: Farbe #FF1900, leer (Mitte durchsichtig, das Gebaeude der Grundkarte bleibt sichtbar), wie das Symbol
von ch.swisstopo.unterkuenfte-winter (QGIS-Stil der Quelle: Kreis 4,2 mm, Rand 0,8 mm, Fuellung durchsichtig;
im WMTS bei Zoom 14/15 35 px Durchmesser, Ring 4-5 px). Hier 2 px rot mit 1 px weissem Rand aussen und innen,
damit der Ring auf Wald und Fels lesbar bleibt.
Pixel: . durchsichtig, K schwarz, R rot/Dach, W weiss. Die durchsichtige Farbe steht zuerst in der Farbtabelle.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "unterkuenfte", "typ", "unterkuenfte_winter.txt")
ROT = "#FF1900"


def ring(n=13, r_aus=6.4, r_rot=5.4, r_in=3.4, r_weiss=2.6):
    """Kreis aus Abstaenden zur Mitte: weiss | rot | weiss | durchsichtig"""
    c = (n - 1) / 2
    rows = []
    for y in range(n):
        s = ""
        for x in range(n):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
            s += "." if d > r_aus else "W" if d > r_rot else "R" if d >= r_in else "W" if d >= r_weiss else "."
        rows.append(s)
    return rows


KLEIN = [
    "....K....",
    "...KRK...",
    "..KRRRK..",
    ".KRRRRRK.",
    "KKKKKKKKK",
    ".KWWWWWK.",
    ".KWWKWWK.",
    ".KWWKWWK.",
    ".KKKKKKK.",
]


def point(t, name, rows, roof):
    w, h = len(rows[0]), len(rows)
    body = "\n".join(f'"{r}"' for r in rows)
    return f'''[_point]
Type={t}
String1=0x04,{name}
FontStyle=SmallFont
CustomColor=Day
DayCustomColor=#000000
DayXpm="{w} {h} 4 1"
". c none"
"K c #000000"
"R c {roof}"
"W c #FFFFFF"
{body}
[end]
'''


txt = """; -*- coding: cp1252 -*-
; TYP fuer die Karte Unterkuenfte Winter (Family-ID 3922), erzeugt von scripts/make_unterkuenfte_typ.py
[_id]
ProductCode=1
FID=3922
CodePage=1252
[end]
""" + point("0x10f00", "Unterkunft (im Winter offen)", ring(), ROT) \
    + point("0x10f01", "SAC-Hütte", KLEIN, "#8C4A1E") \
    + point("0x10f02", "Hütte", KLEIN, "#8C8C8C")
if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="latin1").write(txt)
    print("geschrieben:", os.path.normpath(OUT))
    for r in ring():
        print(r)
