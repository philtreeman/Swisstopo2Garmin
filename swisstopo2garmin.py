#!/usr/bin/env python3
"""Swisstopo Landeskarte 1:50'000 -> Garmin Custom Maps (.kmz) fuer Edge 1040.

Beispiel (Region Bern, ca. 25x25 km):
  python3 swisstopo2garmin.py --bbox 7.30 46.85 7.60 47.05 --zoom 15 --out out
Dann die *.kmz nach  <Edge>/Garmin/CustomMaps/  kopieren.
"""
import argparse, io, math, os, time, zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

LAYER = "ch.swisstopo.pixelkarte-farbe-pk50.noscale"  # 1:50'000
URL = "https://wmts.geo.admin.ch/1.0.0/{layer}/default/current/3857/{z}/{x}/{y}.jpeg"
R = 6378137.0
ORIGIN = math.pi * R

def ll2tile(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return int(x), int(y)

def tile2ll(x, y, z):
    n = 2 ** z
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat

def fetch(args):
    layer, z, x, y = args
    for i in range(4):
        try:
            with urllib.request.urlopen(URL.format(layer=layer, z=z, x=x, y=y), timeout=30) as r:
                return (x, y), Image.open(io.BytesIO(r.read())).convert("RGB")
        except Exception:
            time.sleep(2 ** i)
    return (x, y), Image.new("RGB", (256, 256), "white")

def kml(name, boxes):
    s = ['<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
         f"<name>{name}</name>"]
    for i, (fn, n, s_, e, w, order, lod) in enumerate(boxes):
        region = (f"<Region><LatLonAltBox><north>{n:.7f}</north><south>{s_:.7f}</south>"
                  f"<east>{e:.7f}</east><west>{w:.7f}</west></LatLonAltBox>"
                  f"<Lod><minLodPixels>{lod}</minLodPixels><maxLodPixels>-1</maxLodPixels></Lod></Region>") if lod else ""
        s.append(f"<GroundOverlay><name>{i}</name>{region}<drawOrder>{order}</drawOrder>"
                 f"<Icon><href>{fn}</href></Icon><LatLonBox><north>{n:.7f}</north>"
                 f"<south>{s_:.7f}</south><east>{e:.7f}</east><west>{w:.7f}</west></LatLonBox></GroundOverlay>")
    s.append("</Document></kml>")
    return "".join(s)

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--bbox", nargs=4, type=float, required=True, metavar=("W", "S", "E", "N"))
    a.add_argument("--zoom", type=int, default=15, help="WMTS-Zoom (15 ~ 4.8 m/px, 16 ~ 2.4 m/px)")
    a.add_argument("--out", default="out")
    a.add_argument("--chunk", type=int, default=4, help="Kacheln pro Seite je JPEG (4 -> 1024px, Garmin-Max)")
    a.add_argument("--per-kmz", type=int, default=100, help="max. JPEGs pro KMZ (Garmin-Limit 100)")
    a.add_argument("--quality", type=int, default=75)
    a.add_argument("--layer", default=LAYER)
    a.add_argument("--overview-layer", help="zweite, groebere Karte (z. B. 1:50k) darunter legen")
    a.add_argument("--overview-zoom", type=int, default=14)
    a.add_argument("--lod", type=int, default=0, help="Detailkarte erst ab dieser Bildschirmgroesse (px) zeigen, 0=aus")
    o = a.parse_args()
    os.makedirs(o.out, exist_ok=True)
    w, s, e, n = o.bbox
    c = o.chunk
    jobs = []  # (layer, zoom, cx, cy, drawOrder, lod)
    layers = ([(o.overview_layer, o.overview_zoom, 10, 0)] if o.overview_layer else []) + [(o.layer, o.zoom, 50, o.lod)]
    for layer, z, order, lod in layers:
        x0, y0 = ll2tile(w, n, z); x1, y1 = ll2tile(e, s, z)
        x0 -= x0 % c; y0 -= y0 % c
        jobs += [(layer, z, cx, cy, order, lod) for cy in range(y0, y1 + 1, c) for cx in range(x0, x1 + 1, c)]
    print(f"{len(jobs)} JPEGs, {math.ceil(len(jobs)/o.per_kmz)} KMZ")
    for k in range(0, len(jobs), o.per_kmz):
        idx = k // o.per_kmz + 1
        boxes, files = [], []
        for layer, z, cx, cy, order, lod in jobs[k:k + o.per_kmz]:
            tj = [(layer, z, cx + i, cy + j) for j in range(c) for i in range(c)]
            with ThreadPoolExecutor(8) as ex:
                tiles = dict(ex.map(fetch, tj))
            img = Image.new("RGB", (256 * c, 256 * c))
            for (tx, ty), t in tiles.items():
                img.paste(t, ((tx - cx) * 256, (ty - cy) * 256))
            fn = f"t_{z}_{cx}_{cy}.jpg"
            buf = io.BytesIO(); img.save(buf, "JPEG", quality=o.quality, optimize=True)
            files.append((fn, buf.getvalue()))
            west, north = tile2ll(cx, cy, z); east, south = tile2ll(cx + c, cy + c, z)
            boxes.append((fn, north, south, east, west, order, lod))
        path = os.path.join(o.out, f"swisstopo_{idx:02d}.kmz")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zf:
            zf.writestr("doc.kml", kml(f"swisstopo_{idx:02d}", boxes))
            for fn, data in files:
                zf.writestr(fn, data)
        print(path, f"{os.path.getsize(path)/1e6:.1f} MB")

if __name__ == "__main__":
    main()
