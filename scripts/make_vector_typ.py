#!/usr/bin/env python3
"""Erzeugt die TYP-Datei fuer SwissTOPO Vector (mkgmap/vector/typ/swisstopo_vector.txt).

Farben und Muster sind an Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040 gemessen
(Untergrund creme, Wald gruen, Gebaeude grau auf grauem Siedlungsgebiet, Wege dunkelgrau gestrichelt).
Die Typ-Codes passen zu mkgmap/vector/style/{lines,polygons}.
"""
import os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "vector", "typ", "swisstopo_vector.txt")

from vector_palette import *  # noqa: F401,F403  (Farben, gemeinsam mit preview_vector.py)


def solid_poly(t, name, col):
    return f'[_polygon]\nType={t}\nString1=0x04,{name}\nXpm="0 0 1 0"\n"1 c {col}"\n[end]\n'


def pattern_poly(t, name, bg, fg, density, run, seed, grid=False):
    """32x32-Muster: Hintergrundfarbe bg, Vordergrund fg als zufaellige kurze Striche (run Pixel) oder Raster"""
    rnd = random.Random(seed)
    g = [["b"] * 32 for _ in range(32)]
    if grid:
        for y in range(32):
            for x in range(32):
                if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                    g[y][x] = "f"
    else:
        for _ in range(int(32 * 32 * density / run)):
            y, x = rnd.randrange(32), rnd.randrange(32)
            for k in range(run):
                g[y][(x + k) % 32] = "f"
    rows = "\n".join('"' + "".join(r) + '"' for r in g)
    return f'[_polygon]\nType={t}\nString1=0x04,{name}\nXpm="32 32 2 1"\n"b c {bg}"\n"f c {fg}"\n{rows}\n[end]\n'


def solid_line(t, name, fill, w, border=None):
    if border:
        return f'[_line]\nType={t}\nString1=0x04,{name}\nLineWidth={w}\nBorderWidth=1\nXpm="0 0 2 0"\n"1 c {fill}"\n"2 c {border}"\n[end]\n'
    return f'[_line]\nType={t}\nString1=0x04,{name}\nLineWidth={w}\nXpm="0 0 1 0"\n"1 c {fill}"\n[end]\n'


def dash_line(t, name, col, on, off, h=2):
    """gestrichelte Linie; die durchsichtige Farbe muss zuerst in der Farbtabelle stehen (sonst bricht der TYP-Compiler ab)"""
    row = ("1" * on + "3" * off) * 32
    row = '"' + row[:32] + '"'
    rows = "\n".join([row] * h)
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 {h} 2 1"\n"3 c none"\n"1 c {col}"\n{rows}\n[end]\n'


def rail_line(t, name):
    a = '"' + "1" * 32 + '"'
    b = '"' + ("1" * 6 + "2" * 6)[:32] + '"'
    b = '"' + (("1" * 6 + "2" * 6) * 3)[:32] + '"'
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 3 2 1"\n"1 c {WEG}"\n"2 c #FFFFFF"\n{a}\n{b}\n{a}\n[end]\n'


hdr = """; -*- coding: cp1252 -*-
; TYP fuer SwissTOPO Vector (Family-ID 3900), erzeugt von scripts/make_vector_typ.py
[_id]
ProductCode=1
FID=3900
CodePage=1252
[end]

[_drawOrder]
Type=0x4b,1
Type=0x01,2
Type=0x0c,2
Type=0x0e,2
Type=0x17,3
Type=0x1a,3
Type=0x19,3
Type=0x4f,3
Type=0x4e,3
Type=0x51,3
Type=0x53,3
Type=0x52,3
Type=0x50,4
Type=0x3f,5
Type=0x10e05,6
[end]

"""

parts = [
    solid_poly("0x4b", "Untergrund", BG),
    solid_poly("0x01", "Siedlung", SIEDLUNG),
    solid_poly("0x0c", "Areal", AREAL),
    solid_poly("0x0e", "Verkehrsareal", VERKEHR),
    solid_poly("0x50", "Wald", WALD),
    pattern_poly("0x4f", "Gehoelz", BG, GEHOELZ, 0.30, 2, 1),
    pattern_poly("0x4e", "Reben, Obst", "#F2F8CC", REBEN, 0, 1, 2, grid=True),
    solid_poly("0x17", "Park", PARK),
    solid_poly("0x1a", "Friedhof", FRIEDHOF),
    solid_poly("0x19", "Sport und Freizeit", SPORT),
    pattern_poly("0x51", "Feuchtgebiet", BG, FEUCHT, 0.22, 3, 3),
    pattern_poly("0x52", "Fels", FELS, FELS_TEXTUR, 0.32, 3, 4),
    pattern_poly("0x53", "Geroell", GEROELL, WEG, 0.08, 1, 5),
    solid_poly("0x3f", "Gewaesser", WASSER_FL),
    solid_poly("0x10e05", "Gebaeude", GEBAEUDE),
    # Strassen: Fuellung plus Rand
    solid_line("0x01", "Autobahn", AUTOBAHN[0], 6, AUTOBAHN[1]),
    solid_line("0x02", "Hauptstrasse", HAUPT[0], 5, HAUPT[1]),
    solid_line("0x04", "Strasse", STRASSE[0], 4, STRASSE[1]),
    solid_line("0x06", "Nebenstrasse", NEBEN[0], 3, NEBEN[1]),
    solid_line("0x07", "Naturstrasse", NATUR[0], 3, NATUR[1]),
    # Wege nach der swisstopo-Zeichenerklaerung: 2 m-Weg durchgezogen, 1 m-Weg gestrichelt, markierte Spur punktiert.
    # Wanderwege sind hier nicht farbig codiert (sie liegen im Overlay).
    solid_line("0x0a", "Weg 2 m", SCHWARZ, 1),
    dash_line("0x10e01", "Weg 1 m", SCHWARZ, 5, 3, h=1),
    dash_line("0x10e08", "Markierte Spur", SCHWARZ, 1, 2, h=1),
    dash_line("0x10e09", "Treppe", "#E60000", 1, 2, h=2),
    solid_line("0x10e06", "Schutzverbauung", LAWINE, 3),
    rail_line("0x14", "Bahn"),
    solid_line("0x18", "Bach", WASSER_LI, 1),
    dash_line("0x10e03", "Trockenrinne", WASSER_LI, 2, 3, h=1),
    solid_line("0x10e04", "Mauer", GEBAEUDE, 1),
    dash_line("0x10e02", "Seilbahn", "#000000", 2, 4, h=1),
]
# Einzelbaum: gruener Punkt 3 x 3 (nur wenn die Karte mit --trees gebaut wird)
parts.append(f'''[_point]
Type=0x10f00
String1=0x04,Einzelbaum
DayXpm="3 3 2 1"
"2 c none"
"1 c {BAUM}"
" 1 "
"111"
" 1 "
[end]
'''.replace('" 1 "','"212"'))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="latin1").write(hdr + "".join(parts))
print("geschrieben:", os.path.normpath(OUT))
