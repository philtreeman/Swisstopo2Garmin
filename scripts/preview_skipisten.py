#!/usr/bin/env python3
"""Vorschaubild «Skipisten»: eigene Zeichnung (PIL) der Skipisten-Karte ueber der swisstopo-Landeskarte Winter (WMTS),
links mit Overlay, rechts ohne. KEIN Geraete-Rendering. Farben und Linienarten aus make_skipisten_typ.py.
  preview_skipisten.py <skipisten.osm> <tiles-ordner> <out.png> [W S E N]
Kacheln (Zoom 15, WMTS ch.swisstopo.pixelkarte-farbe-winter) werden bei Bedarf in <tiles-ordner> geladen."""
import math, os, sys, urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

Z = 15
URL = "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe-winter/default/current/3857/{z}/{x}/{y}.jpeg"
COL = {"blue": (0x0B, 0x5C, 0xD6), "red": (0xE0, 0x1B, 0x1B), "black": (0x11, 0x11, 0x11), "orange": (0xFF, 0x8A, 0x00), "grey": (0x80, 0x80, 0x80)}
NORDIC, SLED = (0x1E, 0x9E, 0x3C), (0x8B, 0x5A, 0x2B)
W = 1300


def wpx(lon, lat):
    n = 2 ** Z * 256
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def font(sz, bold=False):
    import matplotlib
    p = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(p, sz)


def basemap(tdir, w, s, e, n):
    x0, y0 = wpx(w, n); x1, y1 = wpx(e, s)
    tx0, tx1, ty0, ty1 = int(x0 // 256), int(x1 // 256), int(y0 // 256), int(y1 // 256)
    img = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    os.makedirs(tdir, exist_ok=True)
    for x in range(tx0, tx1 + 1):
        for y in range(ty0, ty1 + 1):
            f = os.path.join(tdir, f"{Z}_{x}_{y}.jpg")
            if not os.path.exists(f):
                urllib.request.urlretrieve(URL.format(z=Z, x=x, y=y), f)
            img.paste(Image.open(f).convert("RGB"), ((x - tx0) * 256, (y - ty0) * 256))
    img = img.crop((int(x0 - tx0 * 256), int(y0 - ty0 * 256), int(x1 - tx0 * 256), int(y1 - ty0 * 256)))
    return img, x0, y0, x1 - x0


def load(osm, w, s, e, n):
    nodes, lines, areas, outl = {}, [], [], []
    for _, el in ET.iterparse(osm, events=("end",)):
        if el.tag == "node":
            nodes[el.get("id")] = (float(el.get("lon")), float(el.get("lat")))
        elif el.tag == "way":
            tg = {t.get("k"): t.get("v") for t in el.findall("tag")}
            pts = [nodes[nd.get("ref")] for nd in el.findall("nd") if nd.get("ref") in nodes]
            if len(pts) >= 2 and any(w <= p[0] <= e and s <= p[1] <= n for p in pts):
                if tg.get("piste_area"): areas.append((tg["piste_class"], pts))
                elif tg.get("piste_outline"): outl.append((tg.get("piste_class", "grey"), pts))
                elif tg.get("piste_layer"): lines.append((tg["piste_layer"], tg.get("piste_class"), pts))
            el.clear()
        elif el.tag != "tag" and el.tag != "nd":
            el.clear()
    return lines, areas, outl


def dashes(pts, on, off):
    out, cur, draw, left = [], [pts[0]], True, on
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b); pos = 0
        while d - pos > left:
            pos += left; t = pos / d
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if draw: out.append(cur + [p])
            cur = [p]; draw = not draw; left = on if draw else off
        left -= d - pos
        if draw: cur.append(b)
        else: cur = [b]
    if draw and len(cur) > 1: out.append(cur)
    return out


def main():
    osm, tdir, out = sys.argv[1:4]
    w, s, e, n = (map(float, sys.argv[4:8]) if len(sys.argv) > 7 else (9.78, 46.79, 9.90, 46.86))
    base, x0, y0, wid = basemap(tdir, w, s, e, n)
    k = W / base.width
    base = base.resize((W, round(base.height * k)), Image.LANCZOS)
    H = base.height
    lines, areas, outl = load(osm, w, s, e, n)
    proj = lambda pts: [((a - x0) * k, (b - y0) * k) for a, b in (wpx(*p) for p in pts)]
    ov = base.convert("RGBA")
    fill = Image.new("RGBA", ov.size, (0, 0, 0, 0)); fd = ImageDraw.Draw(fill)
    for c, pts in areas:
        if len(pts) >= 3: fd.polygon(proj(pts), fill=COL[c] + (110,))
    ov = Image.alpha_composite(ov, fill); d = ImageDraw.Draw(ov)
    for c, pts in outl: d.line(proj(pts), fill=COL.get(c, COL["grey"]), width=1)
    order = {"sled": 0, "nordic": 1, "downhill": 2}
    for lay, c, pts in sorted(lines, key=lambda t: order[t[0]]):
        p = proj(pts)
        if lay == "downhill":
            col = COL.get(c or "grey", COL["grey"]); on, off = (6, 4) if c == "orange" else (None, None)
        else:
            col = NORDIC if lay == "nordic" else SLED; on, off = 6, 4
        segs = [p] if on is None else dashes(p, on, off)
        for sg in segs: d.line(sg, fill=(255, 255, 255), width=5, joint="curve")
        for sg in segs: d.line(sg, fill=col, width=3, joint="curve")
    TOP, BOT = 70, 190
    cv = Image.new("RGB", (2 * W + 30, TOP + H + BOT), (255, 255, 255)); cd = ImageDraw.Draw(cv)
    cv.paste(ov.convert("RGB"), (10, TOP)); cv.paste(base, (W + 20, TOP))
    cd.text((10, 8), "Skipisten (OpenStreetMap): Raum Davos / Parsenn", font=font(26, True), fill=(20, 20, 20))
    cd.text((10, 42), "EIGENE ZEICHNUNG, KEIN GERAETE-RENDERING (Farben und Linienarten wie in der TYP-Datei, Darstellung auf dem Geraet ungeprueft)", font=font(17, True), fill=(180, 0, 0))
    cd.text((10, TOP + H + 4), "Mit Overlay", font=font(18, True), fill=(20, 20, 20))
    cd.text((W + 20, TOP + H + 4), "Landeskarte Winter ohne Overlay (swisstopo, zum Vergleich)", font=font(18, True), fill=(20, 20, 20))
    f = font(16); y = TOP + H + 40
    items = [("blue", "Abfahrt leicht"), ("red", "Abfahrt mittel"), ("black", "Abfahrt schwer"), ("orange", "Freeride (gestrichelt)"), ("grey", "Schwierigkeit unbekannt")]
    x = 10
    for c, t in items:
        on = (6, 4) if c == "orange" else None
        for sg in ([[(x, y + 8), (x + 44, y + 8)]] if on is None else dashes([(x, y + 8), (x + 44, y + 8)], 6, 4)):
            cd.line(sg, fill=(255, 255, 255), width=5); cd.line(sg, fill=COL[c], width=3)
        cd.text((x + 52, y), t, font=f, fill=(20, 20, 20)); x += 52 + int(cd.textlength(t, font=f)) + 28
    y2 = y + 40; x = 10
    for col, t, on in ((NORDIC, "Langlauf (gestrichelt)", 6), (SLED, "Schlitteln (gestrichelt)", 6)):
        for sg in dashes([(x, y2 + 8), (x + 44, y2 + 8)], 6, 4):
            cd.line(sg, fill=(255, 255, 255), width=5); cd.line(sg, fill=col, width=3)
        cd.text((x + 52, y2), t, font=f, fill=(20, 20, 20)); x += 52 + int(cd.textlength(t, font=f)) + 28
    cd.rectangle((x, y2, x + 44, y2 + 16), fill=(190, 205, 235), outline=COL["blue"]); cd.text((x + 52, y2), "Pistenflaeche (halbdurchsichtig, mit Umriss)", font=f, fill=(20, 20, 20))
    cd.text((10, y2 + 40), "Daten: (c) OpenStreetMap-Mitwirkende (ODbL), Auszug OSM France 2026-11-11. Hintergrund: swisstopo Landeskarte Winter (WMTS, Zoom 15).", font=font(14), fill=(80, 80, 80))
    cv.quantize(256, method=Image.MEDIANCUT, dither=Image.NONE).save(out, optimize=True)
    print(out, os.path.getsize(out), cv.size, len(lines), len(areas))


if __name__ == "__main__":
    main()
