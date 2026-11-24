#!/usr/bin/env python3
"""Vorschau der Strassendarstellung von SwissTOPO Vector: wertet die echten Stildateien (mkgmap/vector/style/lines und
inc/routing_lines) auf den OSM-Kacheln des Konverters aus und zeichnet die Linientypen mit den Farben der TYP-Datei.
Kein Garmin-Rendering: die Typzuordnung kommt aus einem kleinen eigenen Interpreter der Stilregeln (nur die hier benutzte
Teilmenge von mkgmap-Syntax), die Linienmuster (gestrichelt, Querstriche) sind angenaehert.

  python3 preview_strassen.py <osm-datei> <out.png> [--routing] [--res 22] [--box x0 y0 x1 y1 (LV95)]... [--mpp 3]
Ohne --box wird die ganze Kachel gezeichnet. Mehrere --box ergeben mehrere Bilder nebeneinander (je Box ein Feld).
Die OSM-Datei erzeugt: vector2mkgmap.py --shp <tlm> --routing --wgs-tile W S E N --out-file x.osm  (oder --lv95-tile ... ohne --routing)
"""
import argparse, os, re, sys
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(HERE, "..", "mkgmap", "vector", "style")
sys.path.insert(0, HERE)


# ---------------------------------------------------------------- Stil-Interpreter (Teilmenge der mkgmap-Syntax)
def tokenize(s):
    return re.findall(r"'[^']*'|\"[^\"]*\"|!=|[()&|=\[\]{};]|[^\s()&|=!\[\]{};]+", s)


class P:
    def __init__(self, toks): self.t, self.i = toks, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def nxt(self): v = self.t[self.i]; self.i += 1; return v


def parse_or(p):
    a = parse_and(p)
    while p.peek() == "|":
        p.nxt(); b = parse_and(p); a = ("or", a, b)
    return a


def parse_and(p):
    a = parse_atom(p)
    while p.peek() == "&":
        p.nxt(); b = parse_atom(p); a = ("and", a, b)
    return a


def unq(v): return v[1:-1] if v[0] in "'\"" else v


def parse_atom(p):
    if p.peek() == "(":
        p.nxt(); a = parse_or(p); assert p.nxt() == ")"; return a
    k = unq(p.nxt()); op = p.nxt(); v = unq(p.nxt())
    return ("cmp", k, op, v)


def ev(c, tags):
    if c[0] == "or": return ev(c[1], tags) or ev(c[2], tags)
    if c[0] == "and": return ev(c[1], tags) and ev(c[2], tags)
    _, k, op, v = c
    return (tags.get(k) == v) if op == "=" else (tags.get(k) != v)


def load_rules_joined(routing):
    out = []
    def read(path):
        buf = []; skip = False
        raw = open(path, encoding="utf-8").read().splitlines()
        # Fortsetzungszeilen (eingerueckt) an die vorige Regel haengen
        logical = []
        for ln in raw:
            if ln.startswith((" ", "\t")) and logical and not ln.strip().startswith("#"):
                logical[-1] += " " + ln.strip()
            else:
                logical.append(ln.rstrip())
        for ln in logical:
            ln = ln.strip()
            if not ln or ln.startswith("#"): continue
            if ln.startswith("if ("): skip = not routing; continue
            if ln in ("end;", "end"): skip = False; continue
            if skip: continue
            if ln.startswith("include"):
                read(os.path.join(STYLE, ln.split('"')[1])); continue
            out.append(ln)
    read(os.path.join(STYLE, "lines"))
    parsed = []
    for ln in out:
        if ln.startswith("name=*"): continue
        # Aufbau: <bedingung> [{ actions }] [ [ type ... ] ]
        m = re.match(r"^(.*?)\s*(\{.*\})?\s*(\[.*\])?\s*$", ln)
        cond, act, typ = m.group(1), m.group(2), m.group(3)
        # die Bedingung kann ein '{' / '[' in Anfuehrungszeichen enthalten: hier nicht der Fall
        if not cond:
            continue
        c = parse_or(P(tokenize(cond)))
        acts = []
        if act:
            for a in act.strip("{} ").split(";"):
                a = a.strip()
                if a.startswith("set "):
                    k, v = a[4:].split("=", 1); acts.append((k.strip(), v.strip().strip("'")))
        spec = None
        if typ:
            tk = typ.strip("[] ").split()
            spec = {"type": tk[0], "res": 24, "cont": "continue" in tk, "wa": "with_actions" in tk}
            if "resolution" in tk:
                spec["res"] = int(tk[tk.index("resolution") + 1].split("-")[0])
        parsed.append((c, acts, spec))
    return parsed


def classify(rules, tags, res):
    """Liste der Linientypen eines Objekts (mehrere bei «continue»); Sichtbarkeit: resolution <= res"""
    t = dict(tags); orig = dict(tags); out = []
    for c, acts, spec in rules:
        if not ev(c, t): continue
        for k, v in acts: t[k] = v
        if spec is None: continue
        if spec["res"] >= 0 and spec["res"] <= res:
            out.append(spec["type"].lower())
        if spec["cont"]:
            if not spec["wa"]: t = dict(orig)
            continue
        break
    return out


# ---------------------------------------------------------------- Zeichnen
LEGENDE = [  # (Beschriftung, Tags) je eine waagrechte Linie, so wie sie in der Zeichenerklaerung stehen
    ("Autobahn", dict(tlm_type="Autobahn", tlm_vbed="Hochleistungsstrasse", tlm_kunst="Keine")),
    ("Autostrasse", dict(tlm_type="Autostrasse", tlm_vbed="Hochleistungsstrasse", tlm_kunst="Keine")),
    ("10 m-Strasse", dict(tlm_type="10m Strasse", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Hart")),
    ("6 m-Strasse", dict(tlm_type="6m Strasse", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Hart")),
    ("4 m-Strasse Hartbelag", dict(tlm_type="4m Strasse", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Hart")),
    ("4 m-Strasse Naturbelag", dict(tlm_type="4m Strasse", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Natur")),
    ("2 m-Weg Hartbelag", dict(tlm_type="2m Weg", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Hart")),
    ("2 m-Weg Naturbelag", dict(tlm_type="2m Weg", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Natur")),
    ("1 m-Weg", dict(tlm_type="1m Weg", tlm_vbed="k_W", tlm_kunst="Keine", tlm_belag="Hart")),
    ("Steg", dict(tlm_type="1m Weg", tlm_vbed="k_W", tlm_kunst="Steg", tlm_belag="Hart")),
    ("Markierte Route", dict(tlm_type="Markierte Spur", tlm_vbed="k_W", tlm_kunst="k_W")),
    ("Klettersteig", dict(tlm_type="Klettersteig", tlm_vbed="k_W", tlm_kunst="k_W")),
    ("Treppe", dict(tlm_type="1m Weg", tlm_vbed="k_W", tlm_kunst="Treppe")),
    ("Durchgangsstrasse", dict(tlm_type="6m Strasse", tlm_vbed="Durchgangsstrasse", tlm_kunst="Keine")),
    ("Verbindungsstrasse", dict(tlm_type="6m Strasse", tlm_vbed="Verbindungsstrasse", tlm_kunst="Keine")),
    ("Galerie Durchgang", dict(tlm_type="6m Strasse", tlm_vbed="Durchgangsstrasse", tlm_kunst="Galerie")),
    ("Galerie Verbindung", dict(tlm_type="6m Strasse", tlm_vbed="Verbindungsstrasse", tlm_kunst="Galerie")),
    ("Galerie Strasse", dict(tlm_type="6m Strasse", tlm_vbed="k_W", tlm_kunst="Galerie")),
    ("Galerie Autobahn", dict(tlm_type="Autobahn", tlm_vbed="Hochleistungsstrasse", tlm_kunst="Galerie")),
    ("Bruecke Durchgang", dict(tlm_type="6m Strasse", tlm_vbed="Durchgangsstrasse", tlm_kunst="Bruecke")),
    ("Bruecke Verbindung", dict(tlm_type="6m Strasse", tlm_vbed="Verbindungsstrasse", tlm_kunst="Bruecke")),
    ("Bruecke Strasse", dict(tlm_type="6m Strasse", tlm_vbed="k_W", tlm_kunst="Bruecke")),
    ("Tunnel 10 m", dict(tlm_type="10m Strasse", tlm_vbed="Durchgangsstrasse", tlm_kunst="Tunnel")),
    ("Tunnel 6 m", dict(tlm_type="6m Strasse", tlm_vbed="Verbindungsstrasse", tlm_kunst="Tunnel")),
    ("Tunnel 4 m", dict(tlm_type="4m Strasse", tlm_vbed="k_W", tlm_kunst="Tunnel")),
    ("Tunnel Autobahn", dict(tlm_type="Autobahn", tlm_vbed="Hochleistungsstrasse", tlm_kunst="Tunnel")),
]


def legende_osm(path):
    """Testdatei: je Klasse eine 400 m lange waagrechte Linie bei Baden, Abstand 60 m"""
    to = Transformer.from_crs(2056, 4326, always_xy=True)
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<osm version="0.5" generator="preview_strassen">']
    nid = 1; wid = 100000
    for i, (lab, tg) in enumerate(LEGENDE):
        ids = []
        for dx in (0, 400):
            lon, lat = to.transform(2665000 + dx, 1259000 - 60 * i)
            out.append(f'<node id="{nid}" lat="{lat:.7f}" lon="{lon:.7f}"/>'); ids.append(nid); nid += 1
        t = dict(tg, tlm_layer="strasse", tlm_label=lab)
        out.append(f'<way id="{wid}"><nd ref="{ids[0]}"/><nd ref="{ids[1]}"/>' + "".join(f'<tag k="{k}" v="{v}"/>' for k, v in t.items()) + "</way>"); wid += 1
    out.append("</osm>")
    open(path, "w").write("\n".join(out)); print("geschrieben", path)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("osm"); ap.add_argument("out")
    ap.add_argument("--routing", action="store_true")
    ap.add_argument("--res", type=int, default=22, help="Detailstufe (resolution), 24 = feinste")
    ap.add_argument("--box", nargs=4, type=float, action="append", metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--mpp", type=float, default=3.0, help="Meter je Bildpunkt")
    ap.add_argument("--count", action="store_true", help="nur die Typen je Objektart zaehlen")
    ap.add_argument("--legende-osm", metavar="OSM", help="stattdessen eine OSM-Testdatei mit allen Strassenklassen als gerade Linien schreiben")
    o = ap.parse_args()
    if o.legende_osm:
        return legende_osm(o.legende_osm)
    os.environ.setdefault("VECTOR_DESIGN", "swisstopo")
    from vector_palette import (AUTOBAHN, DURCHGANG, VERBINDUNG, HAUPT, STRASSE, NEBEN, NATUR, SCHWARZ, WEG, BG, GEBAEUDE, WALD,
                                WASSER_LI, KLETTERSTEIG, TREPPE)
    rules = load_rules_joined(o.routing)
    root = ET.parse(o.osm).getroot()
    nodes = {n.get("id"): (float(n.get("lon")), float(n.get("lat"))) for n in root.iter("node")}
    to = Transformer.from_crs(4326, 2056, always_xy=True)
    ways = []
    for w in root.iter("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        pts = [nodes[n.get("ref")] for n in w.findall("nd") if n.get("ref") in nodes]
        if len(pts) < 2: continue
        a = np.array(pts); x, y = to.transform(a[:, 0], a[:, 1])
        ways.append((tags, np.column_stack([x, y])))
    from collections import Counter
    cnt = Counter()
    typed = []
    for tags, xy in ways:
        if tags.get("tlm_layer") not in ("strasse", "bahn", "bahnuebergang"): continue
        ts = classify(rules, tags, o.res)
        for t in ts: cnt[(tags.get("tlm_layer"), tags.get("tlm_type"), tags.get("tlm_vbed"), tags.get("tlm_kunst"), t)] += 1
        typed.append((tags, xy, ts))
    if o.count:
        for k, v in sorted(cnt.items(), key=lambda kv: tuple(str(x) for x in kv[0])): print(v, *k)
        return
    # Typ -> (Zeichner)  breite in Bildpunkten; Reihenfolge = Zeichenreihenfolge (unten nach oben)
    SOLID = {"0x07": (NATUR, 1, None), "0x0b": (SCHWARZ, 1, None),
             "0x06": (NEBEN[0], 3, NEBEN[1]), "0x04": (STRASSE[0], 4, STRASSE[1]), "0x05": (HAUPT[0], 5, HAUPT[1]),
             "0x03": (VERBINDUNG[0], 4, VERBINDUNG[1]), "0x02": (DURCHGANG[0], 5, DURCHGANG[1]), "0x01": (AUTOBAHN[0], 6, AUTOBAHN[1]),
             "0x0a": ("#FFFFFF", 2, "#000000"),
             "0x10e18": (NEBEN[0], 3, "#000000", 2), "0x10e17": (STRASSE[0], 4, "#000000", 2), "0x10e16": (HAUPT[0], 5, "#000000", 2),
             "0x10e1b": (VERBINDUNG[0], 4, "#000000", 2), "0x10e1a": (DURCHGANG[0], 5, "#000000", 2), "0x10e15": (AUTOBAHN[0], 6, "#000000", 2)}
    GAL = {"0x10e1e": (STRASSE[0], 6), "0x10e1d": (VERBINDUNG[0], 6), "0x10e1c": (DURCHGANG[0], 7), "0x10e1f": (AUTOBAHN[0], 8)}
    TUN2 = {"0x10e12": 4, "0x10e11": 5, "0x10e10": 6}
    order = ["0x07", "0x0b", "0x0a", "0x10e01", "0x10e08", "0x06", "0x04", "0x05", "0x03", "0x02", "0x01", "0x10e18", "0x10e17", "0x10e16",
             "0x10e1b", "0x10e1a", "0x10e15", "0x10e1e", "0x10e1d", "0x10e1c", "0x10e1f", "0x10e13", "0x10e12", "0x10e11", "0x10e10", "0x10e09", "0x10e00"]
    boxes = o.box or [list(map(float, (xy := np.vstack([w[1] for w in typed])).min(0)) + list(xy.max(0)))]
    n = len(boxes)
    sizes = [((b[2] - b[0]) / o.mpp, (b[3] - b[1]) / o.mpp) for b in boxes]
    fig = plt.figure(figsize=(sum(s[0] for s in sizes) / 100 + 0.1 * n, max(s[1] for s in sizes) / 100), dpi=100)
    fig.patch.set_facecolor("#FEFFED")
    left = 0.0; tot = sum(s[0] for s in sizes)
    for b, s in zip(boxes, sizes):
        ax = fig.add_axes([left / tot, 0, s[0] / tot, s[1] / max(q[1] for q in sizes)]); left += s[0]
        ax.set_xlim(b[0], b[2]); ax.set_ylim(b[1], b[3]); ax.axis("off"); ax.set_facecolor("#FEFFED")
        lw = lambda px: px * 0.72
        for t in order:
            for tags, xy, ts in typed:
                if t not in ts: continue
                if xy[:, 0].max() < b[0] or xy[:, 0].min() > b[2] or xy[:, 1].max() < b[1] or xy[:, 1].min() > b[3]: continue
                x, y = xy[:, 0], xy[:, 1]
                if t in SOLID:
                    sp = SOLID[t]; fill, w, edge = sp[0], sp[1], sp[2]; bw = sp[3] if len(sp) > 3 else 1
                    if edge: ax.plot(x, y, color=edge, lw=lw(w + 2 * bw), solid_capstyle="butt", zorder=2)
                    ax.plot(x, y, color=fill, lw=lw(w), solid_capstyle="butt", zorder=3)
                elif t in GAL:
                    fill, h = GAL[t]
                    ax.plot(x, y, color="#000000", lw=lw(h), solid_capstyle="butt", zorder=4)
                    ax.plot(x, y, color=fill, lw=lw(h - 2), solid_capstyle="butt", zorder=4.1)
                    ax.plot(x, y, color="#000000", lw=lw(h - 2), ls=(0, (1, 3)), dash_capstyle="butt", zorder=4.2)
                elif t in TUN2:
                    h = TUN2[t]
                    for off in (-1, 1):
                        # Randlinien als Versatz senkrecht zur Linie
                        d = np.gradient(xy, axis=0); nrm = np.column_stack([-d[:, 1], d[:, 0]]); nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
                        q = xy + nrm * off * (h - 1) / 2 * o.mpp
                        ax.plot(q[:, 0], q[:, 1], color="#000000", lw=lw(1), ls=(0, (4, 4)), dash_capstyle="butt", zorder=5)
                elif t == "0x10e13":
                    ax.plot(x, y, color="#000000", lw=lw(1), ls=(0, (4, 4)), dash_capstyle="butt", zorder=5)
                elif t == "0x10e01":
                    ax.plot(x, y, color=SCHWARZ, lw=lw(2), ls=(0, (2.5, 1.5)), dash_capstyle="butt", zorder=3)
                elif t == "0x10e08":
                    ax.plot(x, y, color=SCHWARZ, lw=lw(2), ls=(0, (0.5, 1.5)), dash_capstyle="butt", zorder=3)
                elif t == "0x10e09":
                    ax.plot(x, y, color="#000000", lw=lw(3), solid_capstyle="butt", zorder=6)
                    ax.plot(x, y, color="#FFFFFF", lw=lw(1), solid_capstyle="butt", zorder=6.1)
                    ax.plot(x, y, color=TREPPE, lw=lw(1), ls=(0, (1, 1)), dash_capstyle="butt", zorder=6.2)
                elif t == "0x10e00":
                    ax.plot(x, y, color=KLETTERSTEIG, lw=lw(2), ls=(0, (2, 2)), dash_capstyle="butt", zorder=6)
        for tags, xy, ts in typed:
            if tags.get("tlm_label") and b[0] <= xy[0, 0] <= b[2]:
                ax.text(xy[0, 0] - 15, xy[0, 1], tags["tlm_label"], ha="right", va="center", fontsize=8, zorder=9)
    fig.savefig(o.out, dpi=100, facecolor=fig.get_facecolor())
    print("ok", o.out, len(typed), "Objekte")


if __name__ == "__main__":
    main()
