#!/usr/bin/env python3
"""swissALTI3D (2 m, GeoTIFF) -> Hoehenlinien als OSM-XML fuer mkgmap.

  python3 hoehenlinien2mkgmap.py --tiles tiles_2m.json --print-blocks [--bbox W S E N]
  python3 hoehenlinien2mkgmap.py --tiles tiles_2m.json --block I J --out block.osm [--interval 20]

Die 1-km-Kacheln werden zu 20-km-Bloecken im LV95-Raster zusammengefasst (gleicher Ursprung wie
SwissTOPO Vector). Je Kachel werden die Hoehenlinien im Abstand --interval (Standard 20 m) mit contourpy berechnet,
mit 2,5 m vereinfacht und mit den Tags contour=<Intervall|50|100> (100 = Haupthoehenlinie alle 100 m, 50 = Zwischenlinie bei 10 m Intervall) und ele=<Hoehe> geschrieben.
Kachelnamen sind die untere linke Ecke in LV95-km; an den Kachelraendern bleibt eine Luecke von einem Pixel (2 m).

Mit --untergrund <npz> (von untergrund_polygone.py) werden die Linien an den Raendern der Gletscher- und Felsflaechen aufgeteilt
und die Stuecke mit untergrund=gletscher bzw. untergrund=fels getaggt (Landeskarte: Hoehenlinien auf Gletschern blau, auf Fels schwarz, sonst braun;
bei Ueberlappung hat der Gletscher Vorrang). Die Stilregeln dazu stehen in mkgmap/overlays/style/lines.
"""
import argparse, io, json, math, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, rasterio, contourpy, shapely
from shapely import STRtree
from shapely.geometry import box
from rasterio.io import MemoryFile
from pyproj import Transformer
from mkgmap_xml_writer import Writer

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


def tile_lines(data, interval, tol, untergrund=None, bbox=None):
    """liefert [(hoehe, [(x, y), ...], untergrund), ...] in LV95; untergrund = None, "gletscher" oder "fels" (siehe Untergrund)"""
    with MemoryFile(data) as mf, mf.open() as r:
        a = r.read(1).astype("float64"); T = r.transform; nodata = r.nodata
    a[(a == nodata) | (a < -1000)] = np.nan
    if np.isnan(a).all():
        return []
    gen = contourpy.contour_generator(z=np.ma.masked_invalid(a), name="serial", line_type=contourpy.LineType.Separate)
    lo, hi = np.nanmin(a), np.nanmax(a)
    out = []
    masks = untergrund.masks(bbox) if untergrund and bbox else []
    for lv in range(int(math.ceil(lo / interval)) * interval, int(hi // interval) * interval + 1, interval):
        for l in gen.lines(lv):
            if len(l) < 2:
                continue
            xy = np.column_stack([T.c + (l[:, 0] + 0.5) * T.a, T.f + (l[:, 1] + 0.5) * T.e])
            s = shapely.LineString(xy).simplify(tol, preserve_topology=False)
            if len(s.coords) >= 2:
                if masks:
                    out += [(lv, c, k) for k, c in Untergrund.split(s, masks)]
                else:
                    out.append((lv, np.asarray(s.coords), None))
    return out


class Untergrund:
    """Flaechen (LV95) nach Untergrund; trennt Linien einer Kachel an den Flaechenraendern.
    Rangfolge: Gletscher vor Fels (die Linie wird zuerst am Gletscher, der Rest am Fels getrennt).
    Fels wird NIE landesweit vereinigt: pro Block nur die Polygone der Huelle laden, pro Kachel zuschneiden und vereinigen."""
    # (Schluessel im npz, Tag untergrund=...)
    ORDER = (("gletscher", "gletscher"), ("fels", "fels"), ("fels_b", "fels"))

    def __init__(self, npz, region=None, bloecke=True):
        d = np.load(npz, allow_pickle=True)
        self.kinds = []
        for k, tag in self.ORDER:
            if k not in d.files or (k == "fels_b" and not bloecke):
                continue
            idx = None
            if region is not None and k + "_bounds" in d.files:
                b = d[k + "_bounds"]
                idx = np.nonzero((b[:, 2] >= region[0]) & (b[:, 0] <= region[2]) & (b[:, 3] >= region[1]) & (b[:, 1] <= region[3]))[0]
            w = d[k]
            g = shapely.from_wkb(w if idx is None else w[idx])
            self.kinds.append((tag, g, STRtree(g)))

    def masks(self, bbox):
        """je Art die auf die Kachel zugeschnittene, vorbereitete Flaeche"""
        b = box(*bbox)
        out, byTag = [], {}
        for tag, g, tree in self.kinds:
            idx = tree.query(b)
            if len(idx):
                byTag.setdefault(tag, []).append(shapely.intersection(g[idx], b))
        for tag, parts in byTag.items():
            m = shapely.union_all(np.concatenate(parts))
            if not m.is_empty:
                shapely.prepare(m)
                out.append((tag, m))
        return out

    @staticmethod
    def split(line, masks):
        """[(art|None, coords), ...]"""
        res, rest = [], line
        for k, m in masks:
            if rest.is_empty or not m.intersects(rest):
                continue
            res += [(k, g) for g in lines_of(rest.intersection(m))]
            rest = rest.difference(m)
        res += [(None, g) for g in lines_of(rest)]
        return [(k, np.asarray(g.coords)) for k, g in res if g.length > 0.3]


def lines_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    return [x for p in getattr(g, "geoms", []) for x in lines_of(p)]


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--tiles", required=True)
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    a.add_argument("--print-blocks", action="store_true")
    a.add_argument("--block", nargs=2, type=int, metavar=("I", "J"))
    a.add_argument("--out")
    a.add_argument("--interval", type=int, default=20)
    a.add_argument("--simplify", type=float, default=2.5)
    a.add_argument("--untergrund", help="npz von untergrund_polygone.py: Linien an Gletscherraendern trennen")
    a.add_argument("--ohne-bloecke", action="store_true", help="Felsbloecke (Geroell) nicht als Fels behandeln")
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

    ug = None
    if o.untergrund:
        xs = [int(k.split("-")[0]) * 1000 for k in keys]; ys = [int(k.split("-")[1]) * 1000 for k in keys]
        ug = Untergrund(o.untergrund, (min(xs) - 10, min(ys) - 10, max(xs) + 1010, max(ys) + 1010), not o.ohne_bloecke)

    def work(k):
        e, n = (int(v) * 1000 for v in k.split("-"))
        return tile_lines(fetch(tiles[k][1]), o.interval, o.simplify, ug, (e - 5, n - 5, e + 1005, n + 1005))

    n = 0
    with ThreadPoolExecutor(o.workers) as ex:
        for lines in ex.map(work, keys):
            for lv, xy, art in lines:
                lon, lat = TO_WGS.transform(xy[:, 0], xy[:, 1])
                tags = {"contour": 100 if lv % 100 == 0 else 50 if (o.interval <= 10 and lv % 50 == 0) else o.interval, "ele": lv, "untergrund": art}
                w.way(list(zip(lon, lat)), tags)
                n += 1
    w.close()
    print(o.out, f"{os.path.getsize(o.out)/1e6:.1f} MB", len(keys), "Kacheln", n, "Linien", flush=True)


if __name__ == "__main__":
    main()
