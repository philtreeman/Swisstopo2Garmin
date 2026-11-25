#!/usr/bin/env python3
"""Vorschaubild Hoehenlinien nach Untergrund (braun Boden, blau Gletscher, schwarz Fels): eigene Zeichnung (PIL) ueber der grauen swisstopo-Pixelkarte (WMTS), links die 10-m-
Karte (Aufloesung 23), rechts die 20-m-Karte (Aufloesung 22). Typ je Linie aus mkgmap/overlays/style/lines (style_eval.py), Farben und
Breiten aus mkgmap/overlays/typ/hoehenlinien_{10,20}m.txt. KEIN Geraete-Rendering.
  preview_hoehenlinien.py <10m.osm[,weitere.osm]> <tiles-ordner> <out.png> W S E N
Die 20-m-Linien werden aus der 10-m-Datei abgeleitet (Hoehe durch 20 teilbar), wie filter_hoehenlinien.py."""
import math, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import style_eval
from preview_skipisten import wpx, font, Z

HERE = os.path.dirname(os.path.abspath(__file__))
OV = os.path.join(HERE, "..", "mkgmap", "overlays")
URL = "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg"
PW = 760


def typ_farben(name):
    out = {}
    for blk in re.findall(r"\[_line\](.*?)\[end\]", open(os.path.join(OV, "typ", name), encoding="utf-8").read(), re.S):
        t = re.search(r"Type=(0x[0-9a-f]+)", blk).group(1)
        out[t] = (re.search(r'"1 c (#[0-9A-Fa-f]{6})"', blk).group(1), int(re.search(r"LineWidth=(\d+)", blk).group(1)))
    return out


def basemap(tdir, w, s, e, n):
    x0, y0 = wpx(w, n); x1, y1 = wpx(e, s)
    tx0, tx1, ty0, ty1 = int(x0 // 256), int(x1 // 256), int(y0 // 256), int(y1 // 256)
    img = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    os.makedirs(tdir, exist_ok=True)
    for x in range(tx0, tx1 + 1):
        for y in range(ty0, ty1 + 1):
            f = os.path.join(tdir, f"grau_{Z}_{x}_{y}.jpg")
            if not os.path.exists(f):
                urllib.request.urlretrieve(URL.format(z=Z, x=x, y=y), f)
            img.paste(Image.open(f).convert("RGB"), ((x - tx0) * 256, (y - ty0) * 256))
    return img.crop((int(x0 - tx0 * 256), int(y0 - ty0 * 256), int(x1 - tx0 * 256), int(y1 - ty0 * 256))), x0, y0, x1 - x0


def load(osm, w, s, e, n):
    nodes, ways = {}, []
    for _, el in ET.iterparse(osm, events=("end",)):
        if el.tag == "node":
            nodes[el.get("id")] = (float(el.get("lon")), float(el.get("lat")))
        elif el.tag == "way":
            tg = {t.get("k"): t.get("v") for t in el.findall("tag")}
            pts = [nodes[nd.get("ref")] for nd in el.findall("nd") if nd.get("ref") in nodes]
            if len(pts) >= 2 and any(w <= p[0] <= e and s <= p[1] <= n for p in pts):
                ways.append((tg, pts))
            el.clear()
        elif el.tag not in ("tag", "nd"):
            el.clear()
    return ways


def panel(base, x0, y0, sc, ways, rules, farben, res, zwanzig):
    img = base.resize((PW, int(base.height * PW / base.width)), Image.LANCZOS).convert("RGB")
    d = ImageDraw.Draw(img)
    f = font(11, True)
    labels = []
    for tg, pts in ways:
        ele = int(tg["ele"])
        if zwanzig:
            if ele % 20:
                continue
            tg = dict(tg, contour="20" if tg["contour"] == "10" else tg["contour"])
        for t in style_eval.classify(rules, tg, res):
            col, wd = farben[t]
            xy = [((wpx(lo, la)[0] - x0) * PW / sc, (wpx(lo, la)[1] - y0) * PW / sc) for lo, la in pts]
            d.line(xy, fill=col, width=wd)
            if tg["contour"] == "100" and t != "0x10f16":    # Fels: keine Hoehenzahl
                labels.append((xy[len(xy) // 2], str(ele), col))
    for (x, y), txt, col in labels[::6]:
        d.text((x, y), txt, fill=col, font=f, stroke_width=2, stroke_fill=(255, 255, 255))
    return img


def main():
    osm, tdir, out = sys.argv[1:4]
    w, s, e, n = map(float, sys.argv[4:8])
    base, x0, y0, sc = basemap(tdir, w, s, e, n)
    ways = [x for f in osm.split(",") for x in load(f, w, s, e, n)]
    rules = style_eval.load("lines", {}, style=os.path.join(OV, "style"))
    a = panel(base, x0, y0, sc, ways, rules, typ_farben("hoehenlinien_10m.txt"), 23, False)
    b = panel(base, x0, y0, sc, ways, rules, typ_farben("hoehenlinien_20m.txt"), 22, True)
    head = 34
    img = Image.new("RGB", (PW * 2 + 6, a.height + head), "white")
    img.paste(a, (0, head)); img.paste(b, (PW + 6, head))
    d = ImageDraw.Draw(img)
    d.text((6, 8), "Hoehenlinien 10 m (braun Boden, blau Gletscher, schwarz Fels; eigene Zeichnung)", fill="black", font=font(13, True))
    d.text((PW + 12, 8), "Hoehenlinien 20 m", fill="black", font=font(13, True))
    img.save(out)


if __name__ == "__main__":
    main()
