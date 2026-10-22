#!/usr/bin/env python3
"""Erzeugt mkgmap/haltestellen/typ/haltestellen.txt (Family-ID 3918): vier Symbole 12 x 12 (Bus, Bahn, Schiff, uebrige Bahnen)."""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "haltestellen", "typ", "haltestellen.txt")
S = 12


def icon(bg, draw_fn):
    im = Image.new("L", (S, S), 0)        # 0 = Symbol-Hintergrund, 255 = weiss
    d = ImageDraw.Draw(im); draw_fn(d)
    rows = []
    for y in range(S):
        row = ""
        for x in range(S):
            corner = x in (0, S - 1) and y in (0, S - 1)
            row += "2" if corner else "1" if im.getpixel((x, y)) else "3"
        rows.append(row)
    return rows


def bus(d):
    d.rectangle((2, 2, 9, 7), fill=255); d.rectangle((3, 3, 8, 4), fill=0); d.rectangle((2, 8, 3, 9), fill=255); d.rectangle((8, 8, 9, 9), fill=255)

def bahn(d):
    d.rectangle((3, 1, 8, 8), fill=255); d.rectangle((4, 2, 7, 4), fill=0); d.point((4, 6), fill=0); d.point((7, 6), fill=0)
    d.line((2, 10, 4, 8), fill=255); d.line((9, 10, 7, 8), fill=255)

def schiff(d):
    d.polygon([(1, 6), (10, 6), (8, 9), (3, 9)], fill=255); d.rectangle((4, 3, 7, 5), fill=255); d.rectangle((5, 1, 6, 2), fill=255)

def seil(d):
    d.line((1, 2, 10, 2), fill=255); d.line((5, 2, 5, 4), fill=255); d.rectangle((3, 4, 8, 8), fill=255); d.rectangle((4, 5, 7, 6), fill=0)


TYPEN = [("0x10f01", "Haltestelle Bus", "#0079C2", bus), ("0x10f02", "Haltestelle Bahn", "#003F87", bahn),
         ("0x10f03", "Haltestelle Schiff", "#1AA0E8", schiff), ("0x10f04", "Uebrige Bahnen", "#7A4FA0", seil)]
txt = """; -*- coding: cp1252 -*-
; TYP fuer die Haltestellen-Karte (Family-ID 3918), erzeugt von scripts/make_haltestellen_typ.py
[_id]
ProductCode=1
FID=3918
CodePage=1252
[end]
"""
for t, name, bg, fn in TYPEN:
    rows = "\n".join('"' + r + '"' for r in icon(bg, fn))
    txt += f'[_point]\nType={t}\nString1=0x04,{name}\nFontStyle=SmallFont\nCustomColor=Day\nDayCustomColor=#000000\nDayXpm="{S} {S} 3 1"\n"2 c none"\n"1 c #FFFFFF"\n"3 c {bg}"\n{rows}\n[end]\n'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="latin1").write(txt)
print("geschrieben:", os.path.normpath(OUT))
