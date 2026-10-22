#!/usr/bin/env python3
"""swissTLM3D Haltestellen (HALTESTELLE.shp) -> OSM-XML (Zwischenformat fuer mkgmap), mit Tags poi=halt, art=bus|bahn|schiff|uebrige, name.

  python3 haltestellen2mkgmap.py <shp-ordner> out.osm
"""
import sys
import pyogrio, shapely
from pyproj import Transformer
from mkgmap_xml_writer import Writer

ART = {"Haltestelle Bus": "bus", "Haltestelle Bahn": "bahn", "Haltestelle Schiff": "schiff", "Uebrige Bahnen": "uebrige"}
to_wgs = Transformer.from_crs(2056, 4326, always_xy=True)
df = pyogrio.read_dataframe(f"{sys.argv[1]}/swissTLM3D_TLM_HALTESTELLE.shp")
w = Writer(sys.argv[2])
n = 0
for row in df.itertuples(index=False):
    art = ART.get(row.OBJEKTART)
    g = row.geometry
    if art is None or g is None or g.is_empty:
        continue
    p = shapely.force_2d(g)
    lon, lat = to_wgs.transform(p.x, p.y)
    name = row.NAME.strip() if isinstance(row.NAME, str) and row.NAME.strip() else None
    w.node(lon, lat, {"poi": "halt", "art": art, "name": name}); n += 1
w.close()
print(sys.argv[2], n, "Haltestellen")
