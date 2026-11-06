#!/usr/bin/env python3
"""Unterkuenfte Winter (+ Huetten aus swissNAMES3D) -> OSM-XML (nur Zwischenformat fuer mkgmap).
Tags: poi=huette, art=winter|sac|huette, name.

Quellen (beide offen, data.geo.admin.ch):
  1. ch.swisstopo.unterkuenfte-winter (unterkuenfte-winter_2056.gpkg): Unterkuenfte, die im Winter offen sind,
     von swisstopo und SAC fuer die Landeskarte mit Schneesportthemen gepflegt          -> art=winter (alle Punkte)
  2. swissNAMES3D (swissnames3d_<jahr>_2056.gpkg, Layer swissnames3d_pkt), Gebaeudenamen, nur als Ergaenzung:
     - SAC-Huetten, die nicht in 1. stehen (Name enthaelt das Wort «SAC» oder «CAS»,
       Schreibweise der Landeskarte, z. B. «Rottalhuette SAC»)                         -> art=sac
     - uebrige Huetten: Gebaeudenutzung «Schutzhuette», andere Clubhuetten (AACZ, CAI ...),
       Biwaks, Gebaeude mit Huettennamen (Huette, Cabane, Refuge, Capanna, Berghaus ...),
       ohne Forst- und Waldhuetten                                                     -> art=huette
  Vorrang winter > sac > huette: ein Punkt faellt weg, wenn ein Punkt mit Vorrang naeher als 250 m liegt;
  SAC-Punkte aus 2. auch untereinander (gierig). Ein Eigentuemer-Attribut gibt es in keiner Quelle
  (url_sac_* in 1. verweist auf das SAC-Tourenportal, das auch private Huetten und Rifugi fuehrt).
  Die Hoehe kommt aus der Z-Koordinate von swissNAMES3D (fuer 1. vom naechsten Gebaeudenamen bis 250 m)
  und wird an den Namen angehaengt, wie auf der Landeskarte («Kesch-Huette SAC 2623»).

  python3 unterkuenfte2mkgmap.py <unterkuenfte-winter.gpkg> <swissnames3d.gpkg> out.osm [W S E N]
"""
import re
import sys
import numpy as np
import pyogrio
import shapely
from pyproj import Transformer
from mkgmap_xml_writer import Writer

DUP = 250.0   # m
SAC = re.compile(r"\b(?:SAC|CAS)\b")
CLUB = re.compile(r"\b(?:CAI|CAAI|AACB|AACBs|AACZ|ASAC|SAT|OTC|CAF|FAT|UTOE|SOSAT)\b")
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
n_sac = nam.name.str.contains(SAC).values
n_hut = ~n_sac & ~nam.name.str.contains(NICHT).values & (
    nam.name.str.contains(CLUB).values | nam.name.str.contains(BIWAK).values
    | (nam.gebaeudenutzung == "Schutzhuette").values | nam.name.str.contains(HUETTE).values)

wxy = shapely.get_coordinates(win.geometry.values)
nxyz = shapely.get_coordinates(nam.geometry.values, include_z=True)


def near(xy, ref, d=DUP):
    """True je Punkt in xy, wenn ein Punkt aus ref naeher als d liegt"""
    ref = np.asarray(ref).reshape(-1, 2)
    if len(ref) == 0 or len(xy) == 0:
        return np.zeros(len(xy), bool)
    tree = shapely.STRtree(shapely.points(ref))
    idx = tree.query(shapely.points(xy), predicate="dwithin", distance=d)
    hit = np.zeros(len(xy), bool); hit[idx[0]] = True
    return hit


# Hoehe der Winter-Unterkuenfte: naechster swissNAMES3D-Gebaeudename bis 250 m
tree = shapely.STRtree(shapely.points(nxyz[:, :2]))
wi, ni = tree.query_nearest(shapely.points(wxy), max_distance=DUP, all_matches=False)
wz = np.full(len(wxy), np.nan); wz[wi] = nxyz[ni, 2]

pts = [(x, y, z, n, "winter") for (x, y), z, n in zip(wxy, wz, win.name.values)]
kept = [tuple(p) for p in wxy]
for (x, y, z), n in zip(nxyz[n_sac], nam.name.values[n_sac]):   # SAC-Huetten, die nicht im Winter-Datensatz stehen
    if not near(np.array([[x, y]]), kept)[0]:
        kept.append((x, y)); pts.append((x, y, z, n, "sac"))
huette_ok = n_hut & ~near(nxyz[:, :2], kept)
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
