#!/usr/bin/env python3
"""Erzeugt mkgmap/skipisten/typ/skipisten.txt (Family-ID 3926, Karte «OSM Skipisten»).

Linien (3 px mit 1 px weissem Rand, Pistenfarben nach europaeischer Konvention):
  0x10f00 blau (novice/easy)   0x10f01 rot (intermediate)   0x10f02 schwarz (advanced/expert)
  0x10f03 orange gestrichelt (freeride/extreme)   0x10f04 grau (Schwierigkeit unbekannt)
  0x10f05 nordic gruen gestrichelt   0x10f06 skitour violett gepunktet   0x10f07 sled braun gestrichelt
  0x10f08-0x10f0c Umriss von Pistenflaechen, 1 px in den Pistenfarben (blau, rot, schwarz, orange, grau)
Flaechen (halbdurchsichtig: Schachbrett aus Farbe und 'none'): 0x10e00-0x10e04 blau, rot, schwarz, orange, grau.
Farbtabelle: die durchsichtige Farbe 'none' steht zuerst, Linienmuster haben Breite 32 (sonst bricht der TYP-Compiler still ab).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "skipisten", "typ", "skipisten.txt")
COL = {"blue": "#0B5CD6", "red": "#E01B1B", "black": "#111111", "orange": "#FF8A00", "grey": "#808080"}
NAMEN = {"blue": "leicht", "red": "mittel", "black": "schwer", "orange": "Freeride", "grey": "unbekannt"}
HALO = "#FFFFFF"


def solid(t, name, col):
    return f'[_line]\nType={t}\nString1=0x04,{name}\nLineWidth=3\nBorderWidth=1\nXpm="0 0 2 0"\n"1 c {col}"\n"2 c {HALO}"\n[end]\n'


def thin(t, name, col):
    return f'[_line]\nType={t}\nString1=0x04,{name}\nLineWidth=1\nXpm="0 0 1 0"\n"1 c {col}"\n[end]\n'


def pattern(t, name, col, on, off):
    """3 px Kern + 1 px weisser Rand oben und unten (5 Zeilen); Strich 'on', Luecke 'off' Pixel; Muster Breite 32"""
    per = on + off
    def row(sym_on, sym_off):
        return "".join(sym_on if (x % per) < on else sym_off for x in range(32))
    rows = [row("2", "3"), row("1", "3"), row("1", "3"), row("1", "3"), row("2", "3")]
    body = "\n".join(f'"{r}"' for r in rows)
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 5 3 1"\n"3 c none"\n"1 c {col}"\n"2 c {HALO}"\n{body}\n[end]\n'


def flaeche(t, name, col):
    rows = "\n".join('"' + "".join("b" if (x + y) % 2 == 0 else "a" for x in range(32)) + '"' for y in range(32))
    return f'[_polygon]\nType={t}\nString1=0x04,Skipiste {name}\nXpm="32 32 2 1"\n"a c none"\n"b c {col}"\n{rows}\n[end]\n'


def main():
    k = list(COL)
    txt = ("; -*- coding: cp1252 -*-\n; TYP fuer die Skipisten-Karte (Family-ID 3926), erzeugt von scripts/make_skipisten_typ.py\n"
           "[_id]\nProductCode=1\nFID=3926\nCodePage=1252\n[end]\n[_drawOrder]\n")
    txt += "".join(f"Type=0x10e0{i},{i + 1}\n" for i in range(5)) + "[end]\n"
    for i, c in enumerate(k[:3]):
        txt += solid(f"0x10f0{i}", f"Piste {NAMEN[c]}", COL[c])
    txt += pattern("0x10f03", "Piste Freeride", COL["orange"], 6, 4)
    txt += solid("0x10f04", "Piste unbekannt", COL["grey"])
    txt += pattern("0x10f05", "Langlaufloipe", "#1E9E3C", 6, 4)
    txt += pattern("0x10f06", "Skitourenroute", "#8E2BB5", 2, 4)
    txt += pattern("0x10f07", "Schlittelbahn", "#8B5A2B", 6, 4)
    txt += "".join(thin(f"0x10f{8 + i:02x}", f"Pistenumriss {NAMEN[c]}", COL[c]) for i, c in enumerate(k))
    txt += "".join(flaeche(f"0x10e0{i}", NAMEN[c], COL[c]) for i, c in enumerate(k))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="cp1252").write(txt)
    print("geschrieben:", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
