#!/usr/bin/env python3
"""Huetten (Punkte) -> OSM-XML (nur Zwischenformat fuer mkgmap), Tags poi=huette, art=winter|schutz|huette, name.

Quellen (beide offen, data.geo.admin.ch):
  1. ch.swisstopo.unterkuenfte-winter (unterkuenfte-winter_2056.gpkg): Unterkuenfte, die im Winter offen sind,
     von swisstopo und SAC fuer die Landeskarte mit Schneesportthemen gepflegt              -> art=winter
  2. swissNAMES3D (swissnames3d_<jahr>_2056.gpkg, Layer swissnames3d_pkt), Gebaeudenamen:
     - Gebaeudenutzung «Schutzhuette», Clubhuetten (SAC/CAS/CAI/AACB ...) und Biwaks       -> art=schutz
     - uebrige Gebaeude mit Huettennamen (Huette, Cabane, Refuge, Capanna, Berghaus ...)   -> art=huette
       (ohne Forst- und Waldhuetten)
  Punkte aus 2., die naeher als 250 m an einem Punkt einer hoeheren Art liegen, werden weggelassen (Doppel).
  Die Hoehe kommt aus der Z-Koordinate von swissNAMES3D (fuer Winter-Unterkuenfte vom naechsten Gebaeudenamen
  bis 250 m) und wird an den Namen angehaengt, wie auf der Landeskarte («Keschhuette SAC 2632»).

  python3 huetten2mkgmap.py <unterkuenfte-winter.gpkg> <swissnames3d.gpkg> out.osm [W S E N]
"""
import re
import sys
import numpy as np
import pyogrio
import shapely
from pyproj import Transformer
from mkgmap_xml_writer import Writer

DUP = 250.0   # m
CLUB = re.compile(r"\b(?:SAC|CAS|CAI|AACB|AACZ|AACBe|ASAC|SAT|OTC|CAF|FAT|UTOE|SOSAT)\b")
BIWAK = re.compile(r"(?i)biwak|bivacco|bivouac|bivacc")
HUETTE = re.compile(r"(?i)h[uü]tt|hitt|h[oö]tt|huette|cabane|capanna|chamanna|chamonna|refuge|rifugio|baita|berghaus|skihaus|"
                    r"ski-?haus|clubhaus|naturfreundehaus|ferienhaus|alpbeizli|buvette d'alpage")
NICHT = re.compile(r"(?i)forst|forestièr|waldh[uü]tt")   # Forst- und Waldhuetten im Flachland/Jura weglassen

to_wgs = Transformer.from_crs(2056, 4326, always_xy=True)
win_path, names_path, out = sys.argv[1:4]
bbox = [float(v) for v in sys.argv[4:8]] if len(sys.argv) >= 8 else None

win = pyogrio.read_dataframe(win_path)
nam = pyogrio.read_dataframe(names_path, layer="swissnames3d_pkt",
                             where="objektart IN ('Gebaeude', 'Offenes Gebaeude')")
nam = nam[nam.name.notna()]
club = nam.name.str.contains(CLUB) | nam.name.str.contains(BIWAK) | (nam.gebaeudenutzung == "Schutzhuette")
hut = nam.name.str.contains(HUETTE) & ~nam.name.str.contains(NICHT) & ~club

wxy = shapely.get_coordinates(win.geometry.values)
nxyz = shapely.get_coordinates(nam.geometry.values, include_z=True)


def near(xy, ref, d=DUP):
    """True je Punkt in xy, wenn ein Punkt aus ref naeher als d liegt"""
    if len(ref) == 0:
        return np.zeros(len(xy), bool)
    tree = shapely.STRtree(shapely.points(ref))
    idx = tree.query(shapely.points(xy), predicate="dwithin", distance=d)
    hit = np.zeros(len(xy), bool); hit[idx[0]] = True
    return hit


# Hoehe der Winter-Unterkuenfte: naechster swissNAMES3D-Gebaeudename bis 250 m
tree = shapely.STRtree(shapely.points(nxyz[:, :2]))
wi, ni = tree.query_nearest(shapely.points(wxy), max_distance=DUP, all_matches=False)
wz = np.full(len(wxy), np.nan); wz[wi] = nxyz[ni, 2]

cm, hm = club.values, hut.values
schutz_ok = cm & ~near(nxyz[:, :2], wxy)
huette_ok = hm & ~near(nxyz[:, :2], np.vstack([wxy, nxyz[schutz_ok, :2]]))

pts = [(x, y, z, n, "winter") for (x, y), z, n in zip(wxy, wz, win.name)]
pts += [(x, y, z, n, "schutz") for (x, y, z), n in zip(nxyz[schutz_ok], nam.name.values[schutz_ok])]
pts += [(x, y, z, n, "huette") for (x, y, z), n in zip(nxyz[huette_ok], nam.name.values[huette_ok])]

w = Writer(out)
count = {}
for x, y, z, name, art in pts:
    lon, lat = to_wgs.transform(x, y)
    if bbox and not (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
        continue
    label = name.strip() if isinstance(name, str) and name.strip() else None
    if label and np.isfinite(z) and z > 0:
        label = f"{label} {int(round(z))}"
    w.node(lon, lat, {"poi": "huette", "art": art, "name": label})
    count[art] = count.get(art, 0) + 1
w.close()
print(out, count)
