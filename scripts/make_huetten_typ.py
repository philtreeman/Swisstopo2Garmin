#!/usr/bin/env python3
"""Erzeugt mkgmap/huetten/typ/huetten.txt (Family-ID 3922): drei Haussymbole (weisse Wand, schwarzer Rand, farbiges Dach).

  0x10f00 Unterkunft im Winter offen (SAC/swisstopo)   13 x 13, rotes Dach
  0x10f01 Schutzhuette, Clubhuette, Biwak              13 x 13, braunes Dach
  0x10f02 uebrige Huette (Alp-, Ski-, Berghuette ...)   9 x 9,  graues Dach
Pixel: . durchsichtig, K schwarz, R Dach, W weiss. Die durchsichtige Farbe steht zuerst in der Farbtabelle.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "huetten", "typ", "huetten.txt")

GROSS = [
    "......K......",
    ".....KRK.....",
    "....KRRRK....",
    "...KRRRRRK...",
    "..KRRRRRRRK..",
    ".KRRRRRRRRRK.",
    "KKKKKKKKKKKKK",
    ".KWWWWWWWWWK.",
    ".KWWWWWWWWWK.",
    ".KWWWKKKWWWK.",
    ".KWWWKKKWWWK.",
    ".KWWWKKKWWWK.",
    ".KKKKKKKKKKK.",
]
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
; TYP fuer die Huetten-Karte (Family-ID 3922), erzeugt von scripts/make_huetten_typ.py
[_id]
ProductCode=1
FID=3922
CodePage=1252
[end]
""" + point("0x10f00", "Unterkunft (im Winter offen)", GROSS, "#E2231A") \
    + point("0x10f01", "Schutzhütte / Biwak", GROSS, "#8C4A1E") \
    + point("0x10f02", "Hütte", KLEIN, "#6E6E6E")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="latin1").write(txt)
print("geschrieben:", os.path.normpath(OUT))
