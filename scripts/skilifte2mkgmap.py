#!/usr/bin/env python3
"""Bahnen Winter (Skilifte, Sessel-, Gondel-, Luftseil-, Standseilbahnen) -> OSM-XML (nur Zwischenformat fuer mkgmap).

Quelle: ch.swisstopo.bahnen-winter (bahnen-winter_2056.gpkg), die im Winter betriebenen Bahnen der Landeskarte mit
Schneesportthemen (swisstopo/SAC, jaehrlich nachgefuehrt; in der Schweiz eine Auswahl aus swissTLM3D).
Tags: lift=skilift|sessel|gondel|luft|stand|andere, name (Bahnname, falls vorhanden).

  python3 skilifte2mkgmap.py <bahnen-winter.gpkg> out.osm [W S E N]
"""
import sys
import pyogrio
import shapely
from pyproj import Transformer
from mkgmap_xml_writer import Writer

ART = {"skilift": "skilift", "chairlift": "sessel", "cable_car": "gondel", "aerial_cableway": "luft",
       "funicular": "stand", "other_transport_type": "andere"}
to_wgs = Transformer.from_crs(2056, 4326, always_xy=True)
df = pyogrio.read_dataframe(sys.argv[1])
bbox = [float(v) for v in sys.argv[3:7]] if len(sys.argv) >= 7 else None
w = Writer(sys.argv[2])
count = {}
for name, art, g in zip(df["name"], df["type"], df.geometry):
    art = ART.get(art, "andere")
    if g is None or g.is_empty:
        continue
    for line in getattr(g, "geoms", [g]):
        xy = shapely.get_coordinates(line)
        if len(xy) < 2:
            continue
        lon, lat = to_wgs.transform(xy[:, 0], xy[:, 1])
        if bbox and (lon.max() < bbox[0] or lon.min() > bbox[2] or lat.max() < bbox[1] or lat.min() > bbox[3]):
            continue
        label = name.strip() if isinstance(name, str) and name.strip() else None
        w.way(list(zip(lon, lat)), {"lift": art, "name": label})
        count[art] = count.get(art, 0) + 1
w.close()
print(sys.argv[2], count)
