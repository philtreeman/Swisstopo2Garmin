#!/usr/bin/env python3
"""Erzeugt je Overlay-Karte eine eigene TYP-Datei (typ/<name>.txt) mit eigener Family-ID."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "overlays", "typ")


def solid(t, name, fill, w, border):
    return f'''[_line]
Type={t}
String1=0x04,{name}
LineWidth={w}
BorderWidth=1
Xpm="0 0 2 0"
"1 c {fill}"
"2 c {border}"
[end]
'''


def dash(t, name, col, halo="#FFFFFF"):
    # transparente Farbe muss zuerst in der Farbtabelle stehen (sonst bricht der Compiler ab)
    return f'''[_line]
Type={t}
String1=0x04,{name}
Xpm="32 3 3 1"
"3 c none"
"1 c {col}"
"2 c {halo}"
"22222233222222332222223322222233"
"11111133111111331111113311111133"
"22222233222222332222223322222233"
[end]
'''


def write(name, fid, lines):
    hdr = f"""; -*- coding: cp1252 -*-
; TYP fuer Overlay-Karte {name}
[_id]
ProductCode=1
FID={fid}
CodePage=1252
[end]
"""
    with open(os.path.join(OUT, f"{name}.txt"), "w", encoding="latin1") as f:
        f.write(hdr + "".join(lines))


# Typ-Codes passen zu style/lines. Breiten nach Routenkategorie (national > regional > lokal).
YELLOW, YELLOW_B = "#FFD400", "#9A7B00"
LBLUE, LBLUE_B = "#55B8F7", "#1D6FB8"
ORANGE, ORANGE_B = "#FF8A00", "#A85200"
SKI_BLUE = "#0B4FD6"

write("wanderwege", 3911, [dash("0x10f00", "Wanderweg", "#F2C500"), dash("0x10f01", "Bergwanderweg", "#E60000"), dash("0x10f02", "Alpinwanderweg", "#0050B0")])
write("wanderland", 3912, [solid(t, n, YELLOW, w, YELLOW_B) for t, n, w in [("0x10f03", "Wanderland national", 5), ("0x10f04", "Wanderland regional", 4), ("0x10f05", "Wanderland lokal", 3), ("0x10f06", "Wanderland hindernisfrei", 3)]])
write("veloland", 3913, [solid(t, n, LBLUE, w, LBLUE_B) for t, n, w in [("0x10f07", "Veloland national", 5), ("0x10f08", "Veloland regional", 4), ("0x10f09", "Veloland lokal", 3)]])
write("mountainbike", 3914, [solid(t, n, ORANGE, w, ORANGE_B) for t, n, w in [("0x10f0a", "MTB national", 5), ("0x10f0b", "MTB regional", 4), ("0x10f0c", "MTB lokal", 3)]])
# Skirouten wie auf der Rasterkarte: blau, durchgezogen, duenner weisser Rand
write("skirouten_blau", 3915, [solid(f"0x1100{i}", "Skiroute", SKI_BLUE, 3, "#FFFFFF") for i in range(5)])
# Skirouten nach SAC-Schwierigkeit (bisherige Version)
write("skirouten_schwierigkeit", 3916, [dash("0x11000", "Skiroute", "#8E2BB5"), dash("0x11001", "Skiroute L", "#1E9E3C"), dash("0x11002", "Skiroute WS", "#1C6FD6"), dash("0x11003", "Skiroute ZS", "#F28A00"), dash("0x11004", "Skiroute S", "#D6001C")])
print("TYP-Dateien geschrieben:", sorted(os.listdir(OUT)))
