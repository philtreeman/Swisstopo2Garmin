#!/usr/bin/env python3
"""Liest aus einem Bildschirmfoto der Garmin-Karte das Flaechenmuster (Kachel) aus.

  python3 extract_pattern.py bild.png x0 y0 x1 y1 "#BG" "#FG" [maxperiode]

Nur Pixel in den beiden angegebenen Farben zaehlen (alles andere, z. B. Symbole, wird ignoriert). Gesucht wird die kleinste
Periode (px, py), bei der die Pixel einer Kachelposition fast immer gleich sind; die Kachel ist die Mehrheit je Position.
Ausgabe: Periode, Uebereinstimmung und die Kachel als Zeilen aus b/f.
"""
import sys
import numpy as np
from PIL import Image

f, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
h2r = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
bg, fg = h2r(sys.argv[6]), h2r(sys.argv[7])
mp = int(sys.argv[8]) if len(sys.argv) > 8 else 40
im = np.asarray(Image.open(f).convert("RGB"))[y0:y1, x0:x1].astype(int)
isb, isf = (im == bg).all(-1), (im == fg).all(-1)
valid = isb | isf
best = None
for py in range(4, mp + 1):
    for px in range(4, mp + 1):
        votes_f = np.zeros((py, px)); votes_b = np.zeros((py, px))
        ys, xs = np.nonzero(valid)
        np.add.at(votes_f, (ys % py, xs % px), isf[ys, xs]); np.add.at(votes_b, (ys % py, xs % px), isb[ys, xs])
        tot = votes_f + votes_b
        if (tot == 0).any():
            continue
        multi = tot >= 2
        if multi.sum() < 0.2 * tot.size:
            continue
        agree = np.maximum(votes_f, votes_b)[multi].sum() / tot[multi].sum()
        if agree > 0.985 and (best is None or px * py < best[0]):
            best = (px * py, px, py, agree, votes_f > votes_b)
if not best:
    sys.exit("keine Periode gefunden")
_, px, py, agree, tile = best
print(f"Periode {px} x {py}, Uebereinstimmung {agree:.3f}")
for r in tile:
    print("".join("f" if v else "b" for v in r))
