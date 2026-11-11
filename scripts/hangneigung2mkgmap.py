#!/usr/bin/env python3
"""swissALTIRegio (10 m) -> Hangneigung als Flaechen (OSM-XML fuer mkgmap), zwei Klassierungen aus derselben Neigung.

  python3 hangneigung2mkgmap.py --grenze swissBOUNDARIES3D.gpkg --print-blocks [--bbox W S E N]
  python3 hangneigung2mkgmap.py --grenze swissBOUNDARIES3D.gpkg --block I J --out-dir DIR [--bbox W S E N]

Ablauf je Block (40 x 40 km im LV95-Raster, Ursprung 2480000/1070000 wie die anderen Karten; ein Block = 2 x 2 der
20-km-Kacheln, damit die Kartennummern 64<FamilyID>NN mit zwei Ziffern reichen):
  1. Hoehenmodell-Ausschnitt (Block + 1 Zelle Rand) direkt aus dem Cloud-Optimized-GeoTIFF lesen (HTTP-Range, nichts gespeichert)
  2. Neigung in Grad nach Horn (3 x 3, wie GDAL gdaldem slope), einmal je Block auf 10 m; fuer eine Karte mit 20-m-Raster
     (Standard: Hangneigung --cell-hang 20, Klassen --cell-klassen 10) das Mittel von 2 x 2 Zellen
  3. ausserhalb Schweiz + Liechtenstein (swissBOUNDARIES3D, plus --puffer Meter) leer
  4. je Karte klassieren, Flecken unter --min-flaeche m2 (mindestens 2 Zellen) in der Nachbarklasse aufgehen lassen
     (rasterio sieve)
  5. Klassenraster -> Polygone (rasterio.features.shapes), als Flaechendeckung gemeinsam vereinfacht
     (shapely.coverage_simplify: Nachbarflaechen behalten die gemeinsame Kante, keine Luecken), Blockrand bleibt exakt
  6. OSM-XML mit Tag hang=<untere Grenze in Grad>; Loecher als Multipolygon-Relation
Ausgabe: DIR/hangneigung.osm (Klassen 10, 20, 25, 30, 35, 40, 45, 50) und DIR/klassen.osm (30, 35, 40, 45, 50).
"""
import argparse, os, sys, time, warnings
import numpy as np, rasterio, shapely, pyogrio
from rasterio.windows import from_bounds
from rasterio.features import shapes, sieve, rasterize
from rasterio.transform import from_origin
from pyproj import Transformer
from mkgmap_xml_writer import Writer, emit_polygon

warnings.filterwarnings("ignore", category=RuntimeWarning)  # NaN ausserhalb des Hoehenmodells
DEM = "https://data.geo.admin.ch/ch.swisstopo.swissaltiregio/swissaltiregio/swissaltiregio_2056_5728.tif"
GRID_X0, GRID_Y0 = 2480000, 1070000
TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
FROM_WGS = Transformer.from_crs(4326, 2056, always_xy=True)
# untere Klassengrenzen in Grad; die Klasse gilt bis zur naechsten Grenze, die letzte nach oben offen
KARTEN = {"hangneigung": [10, 20, 25, 30, 35, 40, 45, 50], "klassen": [30, 35, 40, 45, 50]}


def gebiet(gpkg, puffer):
    df = pyogrio.read_dataframe(gpkg, layer="tlm_landesgebiet", columns=["icc"])
    g = shapely.force_2d(shapely.union_all(df[df["icc"].isin(["CH", "LI"])].geometry.values))
    return shapely.buffer(g, puffer) if puffer else g


def bbox_lv95(bb):
    (x0, y0), (x1, y1) = FROM_WGS.transform(bb[0], bb[1]), FROM_WGS.transform(bb[2], bb[3])
    return shapely.box(x0, y0, x1, y1)


def blocks(area, km):
    s = km * 1000
    x0, y0, x1, y1 = area.bounds
    out = []
    for i in range(int((x0 - GRID_X0) // s), int((x1 - GRID_X0) // s) + 1):
        for j in range(int((y0 - GRID_Y0) // s), int((y1 - GRID_Y0) // s) + 1):
            if area.intersects(shapely.box(GRID_X0 + i * s, GRID_Y0 + j * s, GRID_X0 + (i + 1) * s, GRID_Y0 + (j + 1) * s)):
                out.append((i, j))
    return sorted(out)


def read_dem(src, x0, y0, x1, y1, c):
    for k in range(6):
        try:
            with rasterio.open(src) as r:
                w = from_bounds(x0 - c, y0 - c, x1 + c, y1 + c, r.transform)
                a = r.read(1, window=w, boundless=True, fill_value=r.nodata).astype("float64")
                nd = r.nodata
            break
        except Exception as e:  # Netzfehler: erneut versuchen
            if k == 5:
                raise
            print("Lesefehler, neuer Versuch:", e, file=sys.stderr, flush=True)
            time.sleep(2 ** k)
    a[(a == nd) | (a < -1000) | (a > 9000)] = np.nan
    return a


def slope(a, c):
    """Neigung in Grad nach Horn; Ergebnis ist um eine Zelle je Seite kleiner"""
    z1, z2, z3 = a[:-2, :-2], a[:-2, 1:-1], a[:-2, 2:]
    z4, z6 = a[1:-1, :-2], a[1:-1, 2:]
    z7, z8, z9 = a[2:, :-2], a[2:, 1:-1], a[2:, 2:]
    dx = ((z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)) / (8 * c)
    dy = ((z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)) / (8 * c)
    return np.degrees(np.arctan(np.hypot(dx, dy)))


def polygons(cls, transform, tol, box):
    """Klassenraster -> [(klasse, Polygon)] als gemeinsam vereinfachte Flaechendeckung, auf box zugeschnitten"""
    geoms, vals = [], []
    for g, v in shapes(cls, connectivity=4, transform=transform):
        geoms.append(shapely.geometry.shape(g)); vals.append(int(v))
    if not geoms:
        return []
    geoms = np.array(geoms, dtype=object); vals = np.array(vals)
    if tol > 0:
        geoms = shapely.coverage_simplify(geoms, tol, simplify_boundary=False)
    keep = vals > 0
    out = []
    for g, v in zip(geoms[keep], vals[keep]):
        if not g.is_valid:
            g = shapely.make_valid(g)
        g = shapely.intersection(g, box)
        for p in getattr(g, "geoms", [g]):
            if p.geom_type == "Polygon" and not p.is_empty and p.area > 1:
                out.append((v, p))
    return out


def to_wgs(p):
    def tr(r):
        x, y = np.asarray(r.coords).T[:2]
        return np.column_stack(TO_WGS.transform(x, y))
    return shapely.Polygon(tr(p.exterior), [tr(i) for i in p.interiors])


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--grenze", required=True, help="swissBOUNDARIES3D-GeoPackage (Layer tlm_landesgebiet)")
    a.add_argument("--puffer", type=float, default=1000, help="Meter ueber die Landesgrenze hinaus")
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    a.add_argument("--block-km", type=int, default=40)
    a.add_argument("--print-blocks", action="store_true")
    a.add_argument("--block", nargs=2, type=int, metavar=("I", "J"))
    a.add_argument("--out-dir")
    a.add_argument("--dem", default=DEM, help="Hoehenmodell (Datei oder URL, LV95, 10 m)")
    a.add_argument("--cell-hang", type=int, default=20, choices=(10, 20), help="Rasterweite der Karte Hangneigung in Metern")
    a.add_argument("--cell-klassen", type=int, default=10, choices=(10, 20), help="Rasterweite der Karte Hangneigungsklassen")
    a.add_argument("--min-flaeche", type=float, default=400, help="m2; kleinere Flecken gehen in der Nachbarklasse auf")
    a.add_argument("--simplify", type=float, default=0.6, help="Toleranz als Vielfaches der Rasterweite")
    o = a.parse_args()
    area = gebiet(o.grenze, o.puffer)
    if o.bbox:
        area = area.intersection(bbox_lv95(o.bbox))
    if o.print_blocks:
        for n, (i, j) in enumerate(blocks(area, o.block_km), 1):
            print(i, j, n)
        return
    t0 = time.time()
    s = o.block_km * 1000
    i, j = o.block
    x0, y0 = GRID_X0 + i * s, GRID_Y0 + j * s
    x1, y1 = x0 + s, y0 + s
    box = shapely.box(x0, y0, x1, y1)
    src = o.dem if not o.dem.startswith("http") else "/vsicurl/" + o.dem
    dem = read_dem(src, x0, y0, x1, y1, 10)
    sl10 = slope(dem, 10.0)
    sl20 = None
    os.makedirs(o.out_dir, exist_ok=True)
    for name, grenzen in KARTEN.items():
        cell = o.cell_hang if name == "hangneigung" else o.cell_klassen
        if cell == 20:
            if sl20 is None:
                sl20 = np.nanmean(sl10.reshape(sl10.shape[0] // 2, 2, sl10.shape[1] // 2, 2), axis=(1, 3))
            sl = sl20
        else:
            sl = sl10
        tr = from_origin(x0, y1, cell, cell)
        inside = rasterize([area.intersection(box)], out_shape=sl.shape, transform=tr, fill=0, default_value=1,
                           dtype="uint8").astype(bool)
        cls = np.zeros(sl.shape, dtype="uint8")
        for g in grenzen:
            cls[(sl >= g) & inside] = g
        n_min = max(2, int(round(o.min_flaeche / cell ** 2)))
        cls = sieve(cls, size=n_min, connectivity=4)
        cls[~inside] = 0
        tol = o.simplify * cell
        polys = polygons(cls, tr, tol, box)
        w = Writer(os.path.join(o.out_dir, name + ".osm"))
        nv = 0
        for v, p in polys:
            emit_polygon(w, to_wgs(p), {"hang": v})
            nv += len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors)
        w.close()
        print(f"{name} ({cell} m): Block {i} {j}: {len(polys)} Flaechen, {nv} Punkte, "
              f"{os.path.getsize(w.path)/1e6:.1f} MB OSM, {time.time()-t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
