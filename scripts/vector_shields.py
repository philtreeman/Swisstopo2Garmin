"""Strassenschilder der Nationalstrassen (N1, N2, ...): Zuordnung Nummer -> Garmin-Punkttyp und Symbol (Bitmap).

Die Punkttypen 0x10f01 bis 0x10f19 sind in mkgmap/vector/style/points festgelegt; die Zeilen dort kommen aus
`python3 scripts/vector_shields.py --style` (hier und im Style muessen die Nummern uebereinstimmen).
"""
import re, sys
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

NUMMERN = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 28, 29]
TYPEN = {f"N{n}": 0x10f01 + i for i, n in enumerate(NUMMERN)}
# Hauptstrassen (ASTRA hauptstrassennetz, Feld RoadNumber): erweiterte Punkttypen 0x11100.. (je 32 Untertypen)
HAUPT = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 16, 17, 18, 19, 21, 24, 27, 28, 29, 30, 101, 105, 106, 111, 123, 144, 181, 182, 189, 190,
         201, 203, 206, 212, 213, 219, 226, 295, 320, 332, 371, 374, 388, 398, 399, 405, 416, 417, 433, 447, 448, 462, 470, 505, 560]
TYPEN.update({f"H{n}": 0x11100 + (i // 32) * 0x100 + i % 32 for i, n in enumerate(HAUPT)})


def symbol(text):
    """weisses Schild mit schwarzem Rand und schwarzer Schrift; 'n' = durchsichtig, 'w' = weiss, 'k' = schwarz (Zeilen aus Zeichen)"""
    f = ImageFont.truetype(font_manager.findfont("DejaVu Sans:bold"), 9)
    l, t, r, b = f.getbbox(text)
    w, h = (r - l) + 5, (b - t) + 4
    txt = Image.new("1", (w, h), 0)
    ImageDraw.Draw(txt).text((3 - l, 2 - t), text, font=f, fill=1)
    px = txt.load()
    rows = []
    for y in range(h):
        row = ""
        for x in range(w):
            edge = x in (0, w - 1) or y in (0, h - 1)
            corner = x in (0, w - 1) and y in (0, h - 1)
            row += "n" if corner else "k" if edge or px[x, y] else "w"
        rows.append(row)
    return rows


def typ_eintraege():
    out = []
    for name, t in TYPEN.items():
        rows = symbol(name.lstrip("H"))
        w, h = len(rows[0]), len(rows)
        tab = {"n": "2", "w": "1", "k": "3"}          # durchsichtige Farbe muss zuerst stehen
        body = "\n".join('"' + "".join(tab[c] for c in r) + '"' for r in rows)
        out.append(f'[_point]\nType=0x{t:x}\nString1=0x04,{"Nationalstrasse" if name[0] == "N" else "Hauptstrasse"} {name}\nDayXpm="{w} {h} 3 1"\n"2 c none"\n"1 c #FFFFFF"\n"3 c #000000"\n{body}\n[end]\n')
    return "".join(out)


if __name__ == "__main__":
    if "--style" in sys.argv:
        for name, t in TYPEN.items():
            print(f"tlm_layer={'nsr' if name[0] == 'N' else 'hsr'} & tlm_type={name} [0x{t:x} resolution {21 if name[0] == 'N' else 22}]")
    else:
        print("\n".join(symbol("N13")))
