#!/usr/bin/env python3
"""Erzeugt mkgmap/skilifte/typ/skilifte.txt (Family-ID 3921): Bahnen im Stil der Landeskarte Winter.

Farben an der Pixelkarte ch.swisstopo.pixelkarte-farbe-winter (Parsenn, Davos) gemessen:
  Luftseil-, Gondel-, Sessel-, Standseilbahn dunkelrot (~#A01F21), Masten/Stationen als Kreise
  Skilift ocker-orange (~#BE9452) mit Querstrichen; hier kraeftiger (#D9861A), damit er auf dem Display auffaellt.
Linienmuster: Breite 32 Pixel (wiederholt sich entlang der Linie), Hoehe = Linienbreite. Nur eine Farbe plus
durchsichtig; die durchsichtige Farbe steht zuerst in der Farbtabelle (sonst scheitert der TYP-Compiler still).
Die Kreise stehen in festen Pixelabstaenden, nicht an den wirklichen Masten (die Masten sind nicht in den Daten).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "skilifte", "typ", "skilifte.txt")
ROT = "#A3191E"      # Seilbahnen
OCKER = "#D9861A"    # Skilift


def pattern(t, name, col, rows):
    assert all(len(r) == 32 for r in rows), name
    body = "\n".join(f'"{r}"' for r in rows)
    return f'''[_line]
Type={t}
String1=0x04,{name}
Xpm="32 {len(rows)} 2 1"
"3 c none"
"1 c {col}"
{body}
[end]
'''


def solid(t, name, col, w):
    return f'''[_line]
Type={t}
String1=0x04,{name}
LineWidth={w}
Xpm="0 0 1 0"
"1 c {col}"
[end]
'''


def rep(seg, n=32):
    return (seg * 32)[:n]


# Skilift: 2 px Linie, alle 8 px ein Querstrich ueber 6 px (Landeskarte: Querstriche = Buegel/Masten)
SKILIFT = [rep("1" + "3" * 7), rep("1" + "3" * 7), rep("1" * 8), rep("1" * 8), rep("1" + "3" * 7), rep("1" + "3" * 7)]
# Sessel- und Gondelbahn: 2 px Linie, alle 16 px ein Kreis (Ring 6 x 6, innen durchsichtig) wie die Masten
RING = ["331133", "313313", "133331", "133331", "313313", "331133"]
LINE6 = ["3" * 10, "3" * 10, "1" * 10, "1" * 10, "3" * 10, "3" * 10]
MAST = [(RING[i] + LINE6[i]) * 2 for i in range(6)]
# Standseilbahn: Doppellinie mit Sprossen (Landeskarte: rote Doppellinie mit Wagen)
STAND = ["1" * 32, rep("1" + "3" * 7), rep("1" + "3" * 7), "1" * 32]

TYPEN = [
    pattern("0x10f00", "Skilift", OCKER, SKILIFT),
    pattern("0x10f01", "Sesselbahn", ROT, MAST),
    pattern("0x10f02", "Gondelbahn", ROT, MAST),
    solid("0x10f03", "Luftseilbahn", ROT, 3),
    pattern("0x10f04", "Standseilbahn", ROT, STAND),
    solid("0x10f05", "Bahn (andere)", ROT, 2),
]
txt = """; -*- coding: cp1252 -*-
; TYP fuer die Skilifte-Karte (Family-ID 3921), erzeugt von scripts/make_skilifte_typ.py
[_id]
ProductCode=1
FID=3921
CodePage=1252
[end]
""" + "".join(TYPEN)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="latin1").write(txt)
print("geschrieben:", os.path.normpath(OUT))
