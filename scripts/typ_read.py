#!/usr/bin/env python3
"""Liest eine von make_vector_typ.py erzeugte TYP-Textdatei (Linien, Flaechen, Punkte, Zeichenreihenfolge) fuer die Vorschau."""
import re


def _hex(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def read(path):
    txt = open(path, encoding="latin1").read()
    out = {"polygon": {}, "line": {}, "point": {}, "order": [], "lineorder": []}
    for m in re.finditer(r"\[(_\w+)\]\n(.*?)\[end\]", txt, re.S):
        kind, body = m.group(1), m.group(2).split("\n")
        if kind == "_drawOrder":
            out["order"] = [l.split("=")[1].split(",")[0].lower() for l in body if l.startswith("Type=")]
            continue
        if kind not in ("_polygon", "_line", "_point"): continue
        d = {}; i = 0
        while i < len(body):
            l = body[i]
            mm = re.match(r'(Day)?Xpm="(\d+) (\d+) (\d+) (\d+)"', l)
            if mm:
                w, h, n, cpp = map(int, mm.groups()[1:])
                cols = {}
                for j in range(n):
                    k, _, c = re.match(r'"(.) c (\S+)"', body[i + 1 + j]).groups()[0], None, re.match(r'"(.) c (\S+)"', body[i + 1 + j]).group(2)
                    cols[re.match(r'"(.) c (\S+)"', body[i + 1 + j]).group(1)] = None if c == "none" else _hex(c)
                rows = [body[i + 1 + n + j].strip('"') for j in range(h)]
                d.update(w=w, h=h, cols=cols, rows=rows, keys=[re.match(r'"(.) c', body[i + 1 + j]).group(1) for j in range(n)])
                i += 1 + n + h; continue
            if "=" in l:
                k, v = l.split("=", 1); d[k] = v
            i += 1
        t = d["Type"].lower()
        out[kind[1:]][t] = d
        if kind == "_line": out["lineorder"].append(t)
    return out
