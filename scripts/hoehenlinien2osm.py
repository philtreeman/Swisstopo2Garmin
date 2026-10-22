#!/usr/bin/env python3
"""swissALTI3D (2 m, GeoTIFF) -> Hoehenlinien als OSM-XML fuer mkgmap.

  python3 hoehenlinien2osm.py --tiles tiles_2m.json --print-blocks [--bbox W S E N]
  python3 hoehenlinien2osm.py --tiles tiles_2m.json --block I J --out block.osm [--interval 10]

Die 1-km-Kacheln werden zu 20-km-Bloecken im LV95-Raster zusammengefasst (gleicher Ursprung wie
SwissTOPO Vector). Je Kachel werden die Hoehenlinien im Abstand --interval (Standard 10 m) mit contourpy berechnet,
mit 2,5 m vereinfacht und mit den Tags contour=<10|50|100> (hoechste passende Stufe) und ele=<Hoehe> geschrieben.
Kachelnamen sind die untere linke Ecke in LV95-km; an den Kachelraendern bleibt eine Luecke von einem Pixel (2 m).
"""
import argparse, io, json, math, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, rasterio, contourpy, shapely
from rasterio.io import MemoryFile
from pyproj import Transformer
from osm_writer import Writer

GRID_X0, GRID_Y0, BLOCK = 2480000, 1070000, 20000
TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
FROM_WGS = Transformer.from_crs(4326, 2056, always_xy=True)


def block_of(key):
    e, n = (int(v) * 1000 for v in key.split("-"))
    return (e - GRID_X0) // BLOCK, (n - GRID_Y0) // BLOCK


def fetch(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return r.read()
        except Exception:
            time.sleep(2 ** i)
    raise RuntimeError("Download fehlgeschlagen: " + url)


def tile_lines(data, interval, tol):
    """liefert [(hoehe, [(x, y), ...]), ...] in LV95"""
    with MemoryFile(data) as mf, mf.open() as r:
        a = r.read(1).astype("float64"); T = r.transform; nodata = r.nodata
    a[(a == nodata) | (a < -1000)] = np.nan
    if np.isnan(a).all():
        return []
    gen = contourpy.contour_generator(z=np.ma.masked_invalid(a), name="serial", line_type=contourpy.LineType.Separate)
    lo, hi = np.nanmin(a), np.nanmax(a)
    out = []
    for lv in range(int(math.ceil(lo / interval)) * interval, int(hi // interval) * interval + 1, interval):
        for l in gen.lines(lv):
            if len(l) < 2:
                continue
            xy = np.column_stack([T.c + (l[:, 0] + 0.5) * T.a, T.f + (l[:, 1] + 0.5) * T.e])
            s = shapely.LineString(xy).simplify(tol, preserve_topology=False)
            if len(s.coords) >= 2:
                out.append((lv, np.asarray(s.coords)))
    return out


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--tiles", required=True)
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    a.add_argument("--print-blocks", action="store_true")
    a.add_argument("--block", nargs=2, type=int, metavar=("I", "J"))
    a.add_argument("--out")
    a.add_argument("--interval", type=int, default=10)
    a.add_argument("--simplify", type=float, default=2.5)
    a.add_argument("--workers", type=int, default=4)
    o = a.parse_args()
    tiles = json.load(open(o.tiles))
    if o.bbox:
        (x0, y0), (x1, y1) = FROM_WGS.transform(o.bbox[0], o.bbox[1]), FROM_WGS.transform(o.bbox[2], o.bbox[3])
        tiles = {k: v for k, v in tiles.items()
                 if x0 - 1000 <= int(k.split("-")[0]) * 1000 <= x1 and y0 - 1000 <= int(k.split("-")[1]) * 1000 <= y1}
    blocks = {}
    for k in tiles:
        blocks.setdefault(block_of(k), []).append(k)
    if o.print_blocks:
        for (i, j), ks in sorted(blocks.items()):
            print(i, j, len(ks))
        return
    keys = blocks[tuple(o.block)]
    w = Writer(o.out)

    def work(k):
        return tile_lines(fetch(tiles[k][1]), o.interval, o.simplify)

    n = 0
    with ThreadPoolExecutor(o.workers) as ex:
        for lines in ex.map(work, keys):
            for lv, xy in lines:
                lon, lat = TO_WGS.transform(xy[:, 0], xy[:, 1])
                tags = {"contour": 100 if lv % 100 == 0 else 50 if lv % 50 == 0 else 10, "ele": lv}
                w.way(list(zip(lon, lat)), tags)
                n += 1
    w.close()
    print(o.out, f"{os.path.getsize(o.out)/1e6:.1f} MB", len(keys), "Kacheln", n, "Linien", flush=True)


if __name__ == "__main__":
    main()
