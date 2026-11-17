#!/usr/bin/env python3
"""Vergleichszeichnung der Hangneigungs-Overlays (eigene Zeichnung, KEIN Rendering vom Geraet).

  python3 preview_hangneigung.py --osm-hang hangneigung.osm [...] --osm-klassen klassen.osm [...] --typ-dir mkgmap/hangneigung/typ \
      --center 9.83 46.80 --zoom 14 --tiles 4 --out vorschau.png [--dichte-test vorschau_dichte.png]

Links: OSM-Zwischendateien (genau das, was mkgmap bekommt), je Bildschirmpixel mit dem 32 x 32-Muster aus der TYP-Datei
gefuellt (durchsichtige Pixel zeigen die graue Landeskarte). Rechts: swisstopo-WMTS-Ebenen ueber derselben Karte
(ch.swisstopo.hangneigung-ueber_30 bzw. ch.swisstopo-karto.hangneigung, mit 60 % Deckkraft wie im Viewer ueblich).
"""
import argparse, io, math, os, re, urllib.request
import xml.etree.ElementTree as ET
import numpy as np, shapely
from PIL import Image, ImageDraw, ImageFont
from rasterio.features import rasterize
from rasterio.transform import Affine

WMTS = "https://wmts.geo.admin.ch/1.0.0/{l}/default/current/3857/{z}/{x}/{y}.{f}"


def tile_xy(lon, lat, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def mosaic(layer, fmt, z, x0, y0, nt):
    im = Image.new("RGBA", (256 * nt, 256 * nt), (0, 0, 0, 0))
    for dx in range(nt):
        for dy in range(nt):
            d = urllib.request.urlopen(WMTS.format(l=layer, z=z, x=x0 + dx, y=y0 + dy, f=fmt), timeout=60).read()
            im.paste(Image.open(io.BytesIO(d)).convert("RGBA"), (256 * dx, 256 * dy))
    return np.asarray(im).astype(float) / 255


def read_osm(paths):
    """-> [(hang, Polygon in lon/lat)]"""
    out = []
    for p in paths:
        nodes, ways = {}, {}
        root = ET.parse(p).getroot()
        for e in root:
            if e.tag == "node":
                nodes[e.get("id")] = (float(e.get("lon")), float(e.get("lat")))
            elif e.tag == "way":
                c = [nodes[n.get("ref")] for n in e.findall("nd")]
                t = {x.get("k"): x.get("v") for x in e.findall("tag")}
                ways[e.get("id")] = c
                if "hang" in t:
                    out.append((int(t["hang"]), shapely.Polygon(c)))
            elif e.tag == "relation":
                t = {x.get("k"): x.get("v") for x in e.findall("tag")}
                m = e.findall("member")
                outer = [ways[x.get("ref")] for x in m if x.get("role") == "outer"]
                inner = [ways[x.get("ref")] for x in m if x.get("role") == "inner"]
                out.append((int(t["hang"]), shapely.Polygon(outer[0], inner)))
    return out


def read_typ(path):
    """Typ-Datei -> {Farbe: Muster (32 x 32 bool)} in der Reihenfolge der Klassen"""
    txt = open(path, encoding="cp1252").read()
    res = []
    for blk in re.findall(r"\[_polygon\](.*?)\[end\]", txt, re.S):
        col = re.search(r'"b c (#[0-9A-Fa-f]{6})"', blk).group(1)
        rows = re.findall(r'^"([ab]{32})"$', blk, re.M)
        res.append((col, np.array([[c == "b" for c in r] for r in rows])))
    return res


def draw_own(base, polys, typ, grenzen, z, x0, y0, nt):
    n = 2 ** z
    size = 256 * nt
    def to_px(p):
        def tr(r):
            lon, lat = np.asarray(r.coords).T
            x = ((lon + 180) / 360 * n - x0) * 256
            y = ((1 - np.arcsinh(np.tan(np.radians(lat))) / np.pi) / 2 * n - y0) * 256
            return np.column_stack([x, y])
        return shapely.Polygon(tr(p.exterior), [tr(i) for i in p.interiors])
    idx = {g: k + 1 for k, g in enumerate(grenzen)}
    shp = [(to_px(p), idx[v]) for v, p in polys if v in idx]
    cls = rasterize(shp, out_shape=(size, size), transform=Affine.identity(), fill=0, dtype="uint8") if shp else np.zeros((size, size), "uint8")
    img = base[:, :, :3].copy()
    yy, xx = np.mgrid[0:size, 0:size]
    for k, (col, pat) in enumerate(typ, 1):
        m = (cls == k) & pat[yy % 32, xx % 32]
        img[m] = [int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return img


def over(base, layer, alpha=0.6):
    a = layer[:, :, 3:4] * alpha
    return base[:, :, :3] * (1 - a) + layer[:, :, :3] * a


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--osm-hang", nargs="+", required=True)
    a.add_argument("--osm-klassen", nargs="+", required=True)
    a.add_argument("--typ-dir", required=True)
    a.add_argument("--center", nargs=2, type=float, default=(9.83, 46.80))
    a.add_argument("--zoom", type=int, default=14)
    a.add_argument("--tiles", type=int, default=4)
    a.add_argument("--out", required=True)
    a.add_argument("--titel", default="Raum Davos")
    o = a.parse_args()
    z, nt = o.zoom, o.tiles
    cx, cy = tile_xy(*o.center, z)
    x0, y0 = int(cx - nt / 2), int(cy - nt / 2)
    base = mosaic("ch.swisstopo.pixelkarte-grau", "jpeg", z, x0, y0, nt)
    wk = mosaic("ch.swisstopo.hangneigung-ueber_30", "png", z, x0, y0, nt)
    wh = mosaic("ch.swisstopo-karto.hangneigung", "png", z, x0, y0, nt)
    hang, kl = read_osm(o.osm_hang), read_osm(o.osm_klassen)
    th = read_typ(os.path.join(o.typ_dir, "hangneigung.txt"))
    tk = read_typ(os.path.join(o.typ_dir, "hangneigungsklassen.txt"))
    own_h = draw_own(base, hang, th, [10, 20, 25, 30, 35, 40, 45, 50], z, x0, y0, nt)
    own_k = draw_own(base, kl, tk, [30, 35, 40, 45, 50], z, x0, y0, nt)
    panels = [(own_k, "Eigene Zeichnung: swisstopo Hangneigungsklassen (3925)\nMuster 1:1 je Pixel, kein Geraete-Rendering"),
              (over(base, wk), "swisstopo WMTS ch.swisstopo.hangneigung-ueber_30\n(Hangneigungsklassen ab 30°, 60 % Deckkraft)"),
              (own_h, "Eigene Zeichnung: swisstopo Hangneigung (3924)\nMuster 1:1 je Pixel, kein Geraete-Rendering"),
              (over(base, wh), "swisstopo WMTS ch.swisstopo-karto.hangneigung\n(Hangneigung ab 30°, einfarbig, 60 % Deckkraft)")]
    leg = [("10-20°", "#A6D96A"), ("20-25°", "#66BD63"), ("25-30°", "#1A9850"), ("30-35°", "#F2E50A"), ("35-40°", "#F46F24"),
           ("40-45°", "#DE055B"), ("45-50°", "#C889BB"), (">50°", "#4B4B4B")]
    # Bilder 1:1 (ein Kartenpixel = ein Bildpixel), damit das Muster nicht durch Skalieren verfaelscht wird
    size = 256 * nt
    pad, head, foot = 12, 64, 40
    W, H = 2 * size + 3 * pad, 2 * (size + head) + pad + foot + 30
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f = ImageFont.load_default(size=15); fb = ImageFont.load_default(size=17)
    d.text((pad, 6), f"{o.titel}, Web-Mercator-Zoom {z}, 1 Kartenpixel = 1 Bildpixel. Links eigene Zeichnung (KEIN Geraete-Rendering), "
           "rechts swisstopo-WMTS; Hintergrund swisstopo Landeskarte grau", fill="black", font=f)
    for k, (im, t) in enumerate(panels):
        x, y = pad + (k % 2) * (size + pad), 30 + (k // 2) * (size + head)
        for n, line in enumerate(t.split("\n")):
            d.text((x, y + 4 + n * 18), line, fill="black", font=f)
        img.paste(Image.fromarray((np.clip(im, 0, 1) * 255).astype("uint8")), (x, y + head - 20))
    x = pad
    for t, c in leg:
        d.rectangle((x, H - foot, x + 18, H - foot + 18), fill=c); d.text((x + 24, H - foot), t, fill="black", font=fb)
        x += 110
    img.save(o.out, optimize=True)
    print("geschrieben:", o.out)


if __name__ == "__main__":
    main()
