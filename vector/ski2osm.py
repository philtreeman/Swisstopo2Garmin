#!/usr/bin/env python3
"""swisstopo Skirouten (GeoPackage, LV95) -> OSM-XML fuer mkgmap (Overlay-Karte).

  python3 ski2osm.py --gpkg ski_routes_2056.gpkg --out ski.osm [--sources swisstopo_sac,...]

Schwierigkeitsklassen (SAC): 0 unbekannt, 1 L/L+, 2 WS-/WS/WS+, 3 ZS-/ZS/ZS+, 4 S-/S/S+/SS
"""
import argparse, math
import numpy as np, pyogrio, shapely
from pyproj import Transformer
from tlm2osm import Writer

TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
CLASS = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4, 12: 4}


def label(r):
    name = next((x.strip() for x in (r.name_de, r.name) if isinstance(x, str) and x.strip()), "")
    if not name or name.startswith("Keine Routeninfo"):
        return None
    d = getattr(r, "difficulty_de", None)
    d = d if isinstance(d, str) and d else ""
    return f"{name} {d}".strip()


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--gpkg", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--sources", default="", help="Komma-Liste, z. B. swisstopo_sac (leer = alle)")
    a.add_argument("--simplify", type=float, default=2.0)
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), help="WGS84, nur Routen in diesem Gebiet")
    o = a.parse_args()
    bb = None
    if o.bbox:
        f = Transformer.from_crs(4326, 2056, always_xy=True)
        (x0, y0), (x1, y1) = f.transform(o.bbox[0], o.bbox[1]), f.transform(o.bbox[2], o.bbox[3])
        bb = (x0, y0, x1, y1)
    df = pyogrio.read_dataframe(o.gpkg, bbox=bb)
    if o.sources:
        df = df[df.source.isin(o.sources.split(","))]
    w = Writer(o.out)
    n = 0
    for r in df.itertuples(index=False):
        g = r.geometry
        if g is None or g.is_empty:
            continue
        g = shapely.force_2d(g).simplify(o.simplify, preserve_topology=True)
        diff = r.difficulty
        cls = CLASS.get(int(diff), 0) if diff == diff and diff is not None else 0
        tags = {"ski_class": cls, "ski_source": r.source}
        lab = label(r)
        if lab:
            tags["name"] = lab
        for part in (g.geoms if g.geom_type.startswith("Multi") else [g]):
            if part.geom_type != "LineString" or len(part.coords) < 2:
                continue
            c = np.array(part.coords)
            lon, lat = TO_WGS.transform(c[:, 0], c[:, 1])
            w.way(list(zip(lon, lat)), tags)
        n += 1
    w.close()
    print(f"{n} Routen -> {o.out}")


if __name__ == "__main__":
    main()
