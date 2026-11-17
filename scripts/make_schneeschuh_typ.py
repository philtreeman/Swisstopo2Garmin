#!/usr/bin/env python3
"""Erzeugt mkgmap/schneeschuh/typ/schneeschuhrouten.txt (Family-ID 3923).

  0x10f13 Schneeschuhroute: durchgezogen, tuerkisgruen #008A79, 3 px, 1 px weisser Rand.
Farbe und Aufbau gemessen an der swisstopo-WMTS-Ebene ch.swisstopo-karto.schneeschuhrouten (Raum Davos):
#008A79, durchgezogen, mit weissem Rand; Kern 2 px (Zoom 15) bis 4 px (Zoom 16), Rand je 2 px.
Die Skirouten-Overlays sind blau (#0B4FD6, 3915) bzw. nach Schwierigkeit gestrichelt (3916).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "schneeschuh", "typ", "schneeschuhrouten.txt")
txt = """; -*- coding: cp1252 -*-
; TYP fuer die Schneeschuhrouten-Karte (Family-ID 3923), erzeugt von scripts/make_schneeschuh_typ.py
[_id]
ProductCode=1
FID=3923
CodePage=1252
[end]
[_line]
Type=0x10f13
String1=0x04,Schneeschuhroute
LineWidth=3
BorderWidth=1
Xpm="0 0 2 0"
"1 c #008A79"
"2 c #FFFFFF"
[end]
"""
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="latin1").write(txt)
print("geschrieben:", os.path.normpath(OUT))
