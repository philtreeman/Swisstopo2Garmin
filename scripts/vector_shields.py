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
# Hauptstrassen A/B/C aus swissTLM3D STRASSENROUTE (Kantonsstrassen-Nummern, z. B. 279, 288, 566), soweit nicht schon im ASTRA-Netz;
# Liste und Punkte erzeugt scripts/kantonsschilder.py; Punkttypen 0x11400.. (je 32 Untertypen)
KANTON = [9, 12, 14, 15, 20, 22, 23, 25, 26, 102, 103, 104, 109, 110, 112, 113, 114, 115, 116, 121, 122, 124, 125, 126, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 168, 169, 170, 171, 172, 173, 174, 177, 178, 179, 180, 183, 185, 186, 188, 191, 192, 193, 202, 204, 205, 207, 208, 210, 211, 220, 221, 222, 223, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 285, 286, 287, 288, 289, 290, 291, 292, 293, 296, 297, 298, 299, 305, 307, 308, 309, 310, 311, 312, 313, 314, 317, 318, 322, 323, 324, 329, 330, 331, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 352, 353, 354, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 375, 376, 377, 378, 381, 382, 383, 386, 387, 389, 390, 391, 392, 393, 394, 395, 396, 397, 401, 402, 404, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 418, 421, 422, 426, 427, 428, 429, 430, 431, 432, 434, 435, 437, 441, 444, 445, 446, 449, 450, 451, 453, 454, 458, 459, 463, 465, 466, 467, 468, 469, 471, 472, 473, 474, 507, 509, 536, 541, 556, 558, 559, 561, 566, 567]
TYPEN.update({f"K{n}": 0x11400 + (i // 32) * 0x100 + i % 32 for i, n in enumerate(KANTON)})


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
        rows = symbol(name.lstrip("HK"))
        w, h = len(rows[0]), len(rows)
        tab = {"n": "2", "w": "1", "k": "3"}          # durchsichtige Farbe muss zuerst stehen
        body = "\n".join('"' + "".join(tab[c] for c in r) + '"' for r in rows)
        out.append(f'[_point]\nType=0x{t:x}\nString1=0x04,{"Nationalstrasse" if name[0] == "N" else "Hauptstrasse"} {name}\nDayXpm="{w} {h} 3 1"\n"2 c none"\n"1 c #FFFFFF"\n"3 c #000000"\n{body}\n[end]\n')
    return "".join(out)


if __name__ == "__main__":
    if "--style" in sys.argv:
        for name, t in TYPEN.items():
            print(f"tlm_layer={ {'N': 'nsr', 'H': 'hsr', 'K': 'ksr'}[name[0]] } & tlm_type={name} [0x{t:x} resolution {21 if name[0] == 'N' else 22}]")
    else:
        print("\n".join(symbol("N13")))
