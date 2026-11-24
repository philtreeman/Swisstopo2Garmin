#!/usr/bin/env python3
"""Vorschau von SwissTOPO Vector: Flaechen mit Mustern, Linien (auch Muster-Linien wie gestrichelt oder mit Querstrichen) und Punkte, so wie
sie aus Stil (mkgmap/vector/style, ausgewertet mit style_eval.py) und TYP-Datei folgen. Kein Garmin-Rendering: ein Bildpunkt der TYP-Muster
ist ein Bildpunkt der Vorschau, die Reihenfolge und das Mischen der Typen sind angenaehert.

  preview_legende.py <osm> <typ.txt> <out.png> --variant edge|fenix [--mpp 9.6] [--box x0 y0 x1 y1 (LV95)] [--labels]
Die Aufloesung (resolution) folgt aus --mpp: 2.4 m je Bildpunkt = 24, 9.6 = 22, 19 = 21, 38 = 20, 150 = 18.
"""
import argparse, os, re, sys, math
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
import style_eval as SE
import typ_read

TO = Transformer.from_crs(4326, 2056, always_xy=True)


def res_of(mpp):
    for r, m in ((24, 3.5), (22, 14), (21, 28), (20, 70)):
        if mpp <= m: return r
    return 18


def parse_osm(path):
    root = ET.parse(path).getroot()
    nodes = {}
    for n in root.iter("node"):
        nodes[n.get("id")] = (float(n.get("lon")), float(n.get("lat")), {t.get("k"): t.get("v") for t in n.findall("tag")})
    ways = {}
    for w in root.iter("way"):
        ways[w.get("id")] = ([n.get("ref") for n in w.findall("nd")], {t.get("k"): t.get("v") for t in w.findall("tag")})
    rels = []
    for r in root.iter("relation"):
        rels.append(([(m.get("ref"), m.get("role")) for m in r.findall("member")], {t.get("k"): t.get("v") for t in r.findall("tag")}))
    return nodes, ways, rels


def xy(nodes, refs):
    a = np.array([nodes[r][:2] for r in refs if r in nodes])
    if len(a) == 0: return a
    x, y = TO.transform(a[:, 0], a[:, 1])
    return np.column_stack([x, y])


def font(size):
    from matplotlib import font_manager
    return ImageFont.truetype(font_manager.findfont("DejaVu Sans"), size)


def tile_array(d):
    """32 x h Muster -> Array (h, w, 4) RGBA"""
    h, w = d["h"], d["w"]
    a = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(d["rows"]):
        for x, ch in enumerate(row):
            c = d["cols"][ch]
            if c is not None: a[y, x] = (*c, 255)
    return a


def render(osm, typ_path, out, variant="edge", mpp=9.6, box=None, labels=False, routing=False):
    nodes, ways, rels = parse_osm(osm)
    typ = typ_read.read(typ_path)
    opts = {"mkgmap:option:variant": variant}
    if routing: opts["mkgmap:option:routing"] = "1"
    R = {k: SE.load(k, opts) for k in ("lines", "polygons", "points")}
    res = res_of(mpp)
    # Objekte sammeln
    polys, lines, pts = [], [], []
    inner_ids = set()
    for refs, roles in [(r[0], r[1]) for r in rels]:
        pass
    for members, tags in rels:
        ring = lambda role: [xy(nodes, ways[ref][0]) for ref, ro in members if ro == role and ref in ways]
        inner_ids.update(ref for ref, ro in members)
        for t in SE.classify(R["polygons"], tags, res):
            polys.append((t, ring("outer"), ring("inner"), tags))
    for wid, (refs, tags) in ways.items():
        if wid in inner_ids or not tags: continue
        a = xy(nodes, refs)
        if len(a) < 2: continue
        closed = refs[0] == refs[-1] and len(refs) >= 4
        if closed:
            for t in SE.classify(R["polygons"], tags, res):
                polys.append((t, [a], [], tags))
        for t in SE.classify(R["lines"], tags, res):
            lines.append((t, a, tags))
    for nid, (lon, lat, tags) in nodes.items():
        if not tags: continue
        for t in SE.classify(R["points"], tags, res):
            x, y = TO.transform(lon, lat); pts.append((t, x, y, tags))
    if box is None:
        allp = np.vstack([a for _, a, _ in lines] + [p for _, o, _, _ in polys for p in o])
        box = (*allp.min(0), *allp.max(0))
    x0, y0, x1, y1 = box
    W, H = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    bg = typ["polygon"]["0x4b"]["cols"]["1"] if "0x4b" in typ["polygon"] else (255, 255, 255)
    img = np.zeros((H, W, 3), np.uint8); img[:] = bg
    P = lambda a: [((px - x0) / mpp, (y1 - py) / mpp) for px, py in a]
    # --- Flaechen in Zeichenreihenfolge
    byt = {}
    for t, outer, inner, tags in polys: byt.setdefault(t, []).append((outer, inner))
    order = [t for t in typ["order"] if t in byt] + [t for t in byt if t not in typ["order"]]
    yy, xx = np.mgrid[0:H, 0:W]
    for t in order:
        d = typ["polygon"].get(t)
        if d is None: print("kein TYP fuer Flaeche", t, file=sys.stderr); continue
        m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
        for outer, inner in byt[t]:
            for o in outer:
                if len(o) >= 3: dr.polygon(P(o), fill=255)
            for i in inner:
                if len(i) >= 3: dr.polygon(P(i), fill=0)
        mk = np.array(m) > 0
        if d["w"] == 0:
            img[mk] = d["cols"][d["keys"][0]]
        else:
            tl = tile_array(d)
            px = tl[yy % d["h"], xx % d["w"]]
            sel = mk & (px[..., 3] > 0)
            img[sel] = px[..., :3][sel]
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    # --- Linien (in der Reihenfolge der TYP-Datei)
    lo = {t: i for i, t in enumerate(typ["lineorder"])}
    for t, a, tags in sorted(lines, key=lambda l: -lo.get(l[0], 999)):
        d = typ["line"].get(t)
        if d is None: print("kein TYP fuer Linie", t, file=sys.stderr); continue
        pp = P(a)
        if d["w"] == 0:
            w = int(d.get("LineWidth", 1)); bw = int(d.get("BorderWidth", 0)) if len(d["keys"]) > 1 else 0
            if bw: dr.line(pp, fill=d["cols"][d["keys"][1]], width=w + 2 * bw, joint="curve")
            dr.line(pp, fill=d["cols"][d["keys"][0]], width=w, joint="curve")
        else:
            tl = tile_array(d); h = d["h"]
            pa = np.array(pp)
            seg = np.hypot(*np.diff(pa, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
            if cum[-1] < 1: continue
            s = np.arange(0, cum[-1], 0.5)
            ix = np.searchsorted(cum, s, side="right") - 1; ix = np.clip(ix, 0, len(seg) - 1)
            f = (s - cum[ix]) / np.maximum(seg[ix], 1e-9)
            pos = pa[ix] + (pa[ix + 1] - pa[ix]) * f[:, None]
            tang = (pa[ix + 1] - pa[ix]) / np.maximum(seg[ix], 1e-9)[:, None]
            nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
            col = (np.floor(s)).astype(int) % 32
            for r in range(h):
                off = r - (h - 1) / 2
                q = pos + nrm * off
                c = tl[r, col]
                ok = c[:, 3] > 0
                qx, qy = np.round(q[ok, 0]).astype(int), np.round(q[ok, 1]).astype(int)
                inb = (qx >= 0) & (qx < W) & (qy >= 0) & (qy < H)
                arr = np.array(im)
                arr[qy[inb], qx[inb]] = c[ok][inb][:, :3]
                im = Image.fromarray(arr); dr = ImageDraw.Draw(im)
    # --- Punkte
    fs = {"SmallFont": 9, "NormalFont": 11, "LargeFont": 14}
    placed = []   # belegte Beschriftungsflaechen (einfache Kollisionsvermeidung wie im Geraet)
    # grosse Schrift zuerst, damit sie nicht von kleinen verdraengt wird
    pts.sort(key=lambda p: -fs.get(typ["point"].get(p[0], {}).get("FontStyle"), 0))
    for t, x, y, tags in pts:
        d = typ["point"].get(t)
        if d is None: print("kein TYP fuer Punkt", t, file=sys.stderr); continue
        px, py = (x - x0) / mpp, (y1 - y) / mpp
        if not (0 <= px < W and 0 <= py < H): continue
        tl = tile_array(d)
        if tl[..., 3].any() and d["w"] > 2 or (d["w"] <= 2 and tl[..., 3].any()):
            pil = Image.fromarray(tl, "RGBA"); im.paste(pil, (int(px - d["w"] / 2), int(py - d["h"] / 2)), pil)
        nm = tags.get("name")
        if nm and d.get("FontStyle") in fs and (labels or t in ("0x6616", "0x6615")):
            col = typ_read._hex(d.get("DayCustomColor", "#000000"))
            dr = ImageDraw.Draw(im)
            bb = dr.textbbox((px + d["w"] / 2 + 2, py - 5), nm, font=font(fs[d["FontStyle"]]))
            if any(not (bb[2] < r[0] or bb[0] > r[2] or bb[3] < r[1] or bb[1] > r[3]) for r in placed):
                continue
            placed.append(bb)
            dr.text((px + d["w"] / 2 + 2, py - 5), nm.title() if nm.isupper() else nm, fill=col, font=font(fs[d["FontStyle"]]),
                                              stroke_width=1, stroke_fill=(255, 255, 255))
    im.save(out)
    print("ok", out, f"{W}x{H}", "res", res, len(polys), "Flaechen", len(lines), "Linien", len(pts), "Punkte")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("osm"); ap.add_argument("typ"); ap.add_argument("out")
    ap.add_argument("--variant", default="edge"); ap.add_argument("--mpp", type=float, default=9.6)
    ap.add_argument("--box", nargs=4, type=float); ap.add_argument("--labels", action="store_true"); ap.add_argument("--routing", action="store_true")
    o = ap.parse_args()
    render(o.osm, o.typ, o.out, o.variant, o.mpp, tuple(o.box) if o.box else None, o.labels, o.routing)


if __name__ == "__main__":
    main()
