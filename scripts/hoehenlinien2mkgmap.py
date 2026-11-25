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
import sys, argparse, io, json, math, os, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, rasterio, contourpy, shapely
from shapely import STRtree
from shapely.geometry import box
from shapely.ops import substring
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
                    out += [(lv, c, k) for k, c in untergrund.split(s, masks, lv, interval)]
                else:
                    out.append((lv, np.asarray(s.coords), None))
    return out


class Hang:
    """Hangneigung (Grad, uint8) aus 1"-HGT-Kacheln (3601 x 3601, int16 big-endian; scripts/make_dem_hgt.py): 3 x 3-Mittel der Hoehe, dann Gradient.
    Kachelweise geladen und zwischengespeichert; abgefragt werden Punkte in WGS84 (nearest)."""
    def __init__(self, ordner):
        self.ordner, self.cache, self.lock = ordner, {}, threading.Lock()

    def kachel(self, lat0, lon0):
        k = (lat0, lon0)
        with self.lock:
            return self._kachel(k)

    def _kachel(self, k):
        lat0, lon0 = k
        if k not in self.cache:
            f = os.path.join(self.ordner, "N%02dE%03d.hgt" % (lat0, lon0))
            if not os.path.exists(f):
                self.cache[k] = None
            else:
                z = np.fromfile(f, ">i2").reshape(3601, 3601).astype("float32")
                z[z < -1000] = np.nan
                zp = np.pad(z, 1, mode="edge")
                with np.errstate(invalid="ignore"):
                    m = sum(zp[i:i + 3601, j:j + 3601] for i in range(3) for j in range(3)) / 9.0   # 3 x 3-Mittel (NaN breitet sich aus)
                mp = np.pad(m, 1, mode="edge")
                dy = (mp[2:, 1:-1] - mp[:-2, 1:-1]) / (2 * 30.87)
                cosl = np.cos(np.radians(lat0 + 1 - np.arange(3601) / 3600.0))[:, None]
                dx = (mp[1:-1, 2:] - mp[1:-1, :-2]) / (2 * 30.87 * cosl)
                sl = np.degrees(np.arctan(np.hypot(dx, dy)))
                self.cache[k] = np.nan_to_num(sl, nan=0.0).clip(0, 90).astype("uint8")
        return self.cache[k]

    def at(self, lon, lat):
        out = np.zeros(len(lon), "uint8")
        lat0, lon0 = np.floor(lat).astype(int), np.floor(lon).astype(int)
        for a, b in {(x, y) for x, y in zip(lat0, lon0)}:
            t = self.kachel(a, b)
            if t is None:
                continue
            m = (lat0 == a) & (lon0 == b)
            r = np.clip(np.rint((a + 1 - lat[m]) * 3600).astype(int), 0, 3600)
            c = np.clip(np.rint((lon[m] - b) * 3600).astype(int), 0, 3600)
            out[m] = t[r, c]
        return out


class Untergrund:
    """Flaechen (LV95) nach Untergrund; trennt Linien einer Kachel an den Flaechenraendern.
    Rangfolge: Gletscher vor Fels (die Linie wird zuerst am Gletscher, der Rest am Fels getrennt).
    Fels wird NIE landesweit vereinigt: pro Block nur die Polygone der Huelle laden, pro Kachel zuschneiden und vereinigen."""
    # (Schluessel im npz, Tag untergrund=...)
    ORDER = (("gletscher", "gletscher"), ("fels", "fels"), ("fels_b", "fels"))

    def __init__(self, npz, region=None, bloecke=True, glaettung=(15.0, 7.0, 5000.0), min_stueck=30.0, hang=None, steil=(40, 50, 60), steil_luecke=30.0, steil_rest=50.0):
        """glaettung = (d, simplify, Mindestflaeche) in m / m^2 fuer Fels; d = 0: ungeglaettet. min_stueck: Linienstuecke darunter erben den Untergrund der Nachbarn"""
        self.d, self.simp, self.minfl = glaettung
        self.min_stueck = min_stueck
        self.hang, self.steil, self.steil_luecke, self.steil_rest = hang, steil, steil_luecke, steil_rest
        self.stat = {"fels": 0.0, "fels_weg": 0.0, "braun": 0.0, "braun_steil": 0.0}
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

    def smooth(self, m):
        """Closing (buffer +d, -d) schliesst Luecken und Zacken, Inseln und Loecher unter der Mindestflaeche weg, dann vereinfachen"""
        d = self.d
        m = m.buffer(d, 4).buffer(-d, 4)
        polys = [p for p in getattr(m, "geoms", [m]) if p.geom_type == "Polygon" and p.area >= self.minfl]
        polys = [shapely.Polygon(p.exterior, [r for r in p.interiors if shapely.Polygon(r).area >= self.minfl]) for p in polys]
        if not polys:
            return shapely.Polygon()
        return shapely.union_all(polys).simplify(self.simp, preserve_topology=True)

    def masks(self, bbox):
        """je Art die auf die Kachel zugeschnittene, vorbereitete Flaeche. Fels wird mit Rand (2 d + 20 m) zugeschnitten, geglaettet
        und erst dann auf die Kachel gekuerzt, damit an den Kachelraendern keine Glaettungsartefakte entstehen."""
        b = box(*bbox)
        out, byTag = [], {}
        pad = 2 * self.d + 20 if self.d else 0
        bw = box(bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
        for tag, g, tree in self.kinds:
            glatt = tag == "fels" and self.d > 0
            idx = tree.query(bw if glatt else b)
            if len(idx):
                byTag.setdefault(tag, []).append(shapely.intersection(g[idx], bw if glatt else b))
        for tag, parts in byTag.items():
            m = shapely.union_all(np.concatenate(parts))
            if tag == "fels" and self.d > 0 and not m.is_empty:
                m = self.smooth(m).intersection(b)
            if not m.is_empty:
                shapely.prepare(m)
                out.append((tag, m))
        return out

    def split(self, line, masks, lv=0, interval=20):
        """[(art|None, coords), ...]; Stuecke unter min_stueck erben den Untergrund des laengsten Nachbarn am Ende, gleiche Nachbarn werden wieder zusammengefuegt"""
        res, rest = [], line
        for k, m in masks:
            if rest.is_empty or not m.intersects(rest):
                continue
            res += [[k, g] for g in lines_of(rest.intersection(m))]
            rest = rest.difference(m)
        res += [[None, g] for g in lines_of(rest)]
        res = [r for r in res if r[1].length > 0.3]
        if self.min_stueck and len(res) > 1:
            for r in sorted(res, key=lambda r: r[1].length):
                if r[1].length >= self.min_stueck:
                    break
                ends = [shapely.Point(r[1].coords[0]), shapely.Point(r[1].coords[-1])]
                nb = [o for o in res if o is not r and any(o[1].distance(e) < 1.0 for e in ends)]
                if nb:
                    r[0] = max(nb, key=lambda o: o[1].length)[0]
            by = {}
            for k, g in res:
                by.setdefault(k, []).append(g)
            res = [[k, g] for k, gs in by.items() for g in lines_of(shapely.line_merge(shapely.MultiLineString(gs)) if len(gs) > 1 else gs[0])]
        out = []
        for k, g in res:
            if k == "fels" and self.hang is not None:
                out += [("fels", x) for x in self.ausduennen(g, lv, interval)]
            else:
                if k is None and self.hang is not None and self.stat_braun:
                    self.stat["braun"] += g.length
                    self.stat["braun_steil"] += self.steil_laenge(g, self.schwelle(lv, interval))
                out.append((k, g))
        return [(k, np.asarray(g.coords)) for k, g in out if g.length > 0.3]

    stat_braun = False

    def schwelle(self, lv, interval):
        return self.steil[2] if lv % 100 == 0 else self.steil[1] if (lv % 50 == 0 and interval <= 10) else self.steil[0]

    def proben(self, g, schritt=15.0):
        L = g.length
        d = np.unique(np.append(np.arange(0, L, schritt), L))
        pts = shapely.line_interpolate_point(g, d)
        xy = shapely.get_coordinates(pts)
        lon, lat = TO_WGS.transform(xy[:, 0], xy[:, 1])
        return d, self.hang.at(np.asarray(lon), np.asarray(lat))

    def steil_laenge(self, g, thr):
        d, sl = self.proben(g)
        return float(np.sum(np.diff(d) * (sl[:-1] > thr)))

    def ausduennen(self, g, lv, interval):
        """Fels: Teilstuecke mit Hangneigung > Schwelle (Intervall 40, 50 m 50, 100 m 60 Grad) entfernen; Luecken unter steil_luecke
        zwischen steilen Stuecken werden mit entfernt (Hysterese), uebrig bleibende Reststuecke unter steil_rest ebenfalls."""
        L = g.length
        self.stat["fels"] += L
        thr = self.schwelle(lv, interval)
        d, sl = self.proben(g)
        steil = sl > thr
        if not steil.any():
            return [g]
        # Intervalle [d_i, d_i+1] zwischen steilen Proben als steil: Probe i steil -> Stueck davor und danach
        st = np.zeros(len(d) - 1, bool)
        st |= steil[:-1] | steil[1:]
        runs = []                       # (von, bis) in m der steilen Abschnitte
        i = 0
        while i < len(st):
            if st[i]:
                j = i
                while j + 1 < len(st) and st[j + 1]:
                    j += 1
                runs.append([d[i], d[j + 1]]); i = j + 1
            else:
                i += 1
        merged = []
        for r in runs:
            if merged and r[0] - merged[-1][1] < self.steil_luecke:
                merged[-1][1] = r[1]
            else:
                merged.append(r)
        keep, pos = [], 0.0
        for a, b in merged:
            if a - pos >= self.steil_rest:
                keep.append((pos, a))
            pos = b
        if L - pos >= self.steil_rest:
            keep.append((pos, L))
        out = [substring(g, a, b) for a, b in keep]
        out = [x for x in out if not x.is_empty and x.geom_type == "LineString"]
        self.stat["fels_weg"] += L - sum(x.length for x in out)
        return out


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
    a.add_argument("--fels-d", type=float, default=15.0, help="Glaettung der Felsflaechen: Closing buffer(+d).buffer(-d) in m (0 = aus)")
    a.add_argument("--fels-simplify", type=float, default=7.0, help="Vereinfachung der Felsflaechen in m")
    a.add_argument("--fels-minflaeche", type=float, default=5000.0, help="Felsinseln und -loecher unter dieser Flaeche (m2) fallen weg")
    a.add_argument("--min-stueck", type=float, default=30.0, help="Linienstuecke darunter (m) erben den Untergrund der Nachbarn")
    a.add_argument("--hgt", help="Ordner mit 1\"-HGT-Kacheln (make_dem_hgt.py): Hoehenlinien auf steilem Fels weglassen")
    a.add_argument("--steil", default="40,50,60", help="Schwellen Hangneigung in Grad fuer Intervall-, 50-m- und 100-m-Linien auf Fels")
    a.add_argument("--steil-luecke", type=float, default=30.0, help="Luecken (m) zwischen steilen Abschnitten schliessen")
    a.add_argument("--steil-rest", type=float, default=50.0, help="Reststuecke (m) unter diesem Wert entfernen")
    a.add_argument("--stat-braun", action="store_true", help="Statistik: Laenge steiler braunen Linien (nur Messung)")
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
        ug = Untergrund(o.untergrund, (min(xs) - 10, min(ys) - 10, max(xs) + 1010, max(ys) + 1010), not o.ohne_bloecke,
                        (o.fels_d, o.fels_simplify, o.fels_minflaeche), o.min_stueck,
                        Hang(o.hgt) if o.hgt else None, tuple(float(x) for x in o.steil.split(",")), o.steil_luecke, o.steil_rest)
        ug.stat_braun = o.stat_braun

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
    if ug:
        print("STAT", o.out, {k: round(v) for k, v in ug.stat.items()}, file=sys.stderr, flush=True)
    print(o.out, f"{os.path.getsize(o.out)/1e6:.1f} MB", len(keys), "Kacheln", n, "Linien", flush=True)


if __name__ == "__main__":
    main()
