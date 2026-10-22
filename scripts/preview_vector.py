#!/usr/bin/env python3
"""Vorschau-Zeichnung von SwissTOPO Vector (gleiche Farben wie die TYP-Datei, kein Garmin-Rendering).

  python3 preview_vector.py <shp-ordner> out.png [lon lat [breite_m]]      (Standard: Baden, 700 m)
Zeichnet Untergrund, Siedlungsgebiet, Wald, Gewaesser, Strassen, Wege, Bahn und Gebaeude aus den swissTLM3D-Shapefiles.
"""
import sys, numpy as np, pyogrio, shapely
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from pyproj import Transformer
from vector_palette import *

shp, out = sys.argv[1], sys.argv[2]
lon, lat = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (8.3185, 47.4815)
size = float(sys.argv[5]) if len(sys.argv) > 5 else 700.0
cx, cy = Transformer.from_crs(4326, 2056, always_xy=True).transform(lon, lat)
x0, y0, x1, y1 = cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2
bb = (x0, y0, x1, y1)
rd = lambda n, b=bb: pyogrio.read_dataframe(f"{shp}/swissTLM3D_TLM_{n}.shp", bbox=b)
fig = plt.figure(figsize=(5.64, 5.64), dpi=100); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis("off"); fig.patch.set_facecolor(BG)
mpp = size / 564.0  # Meter pro Pixel


def poly(geoms, col, z):
    for g in geoms:
        if g is None or g.is_empty:
            continue
        for p in shapely.get_parts(shapely.force_2d(g)):
            if p.geom_type != "Polygon":
                continue
            v, c = [], []
            for r in [p.exterior] + list(p.interiors):
                a = np.array(r.coords); v += list(a); c += [Path.MOVETO] + [Path.LINETO] * (len(a) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(v, c), fc=col, ec="none", zorder=z))


def line(geoms, col, px, z, ls="-"):
    for g in geoms:
        if g is None:
            continue
        for l in shapely.get_parts(shapely.force_2d(g)):
            a = np.array(l.coords); ax.plot(a[:, 0], a[:, 1], color=col, lw=px * 0.72, ls=ls, solid_capstyle="butt", zorder=z)


def road(df, sel, pal, w, z):
    g = df[sel].geometry
    line(g, pal[1], w + 2, z); line(g, pal[0], w, z + 0.1)


PAD = (x1 - x0) * 0.2
geb = pd = None
gdf = pyogrio.read_dataframe(f"{shp}/swissTLM3D_TLM_GEBAEUDE_FOOTPRINT_OST.shp", bbox=(x0 - 80, y0 - 80, x1 + 80, y1 + 80))
u = shapely.union_all(shapely.buffer(shapely.force_2d(gdf.geometry.values), 14, quad_segs=1))
poly([p for p in shapely.get_parts(u) if p.area >= 8000], SIEDLUNG, 2)
for n in ("NUTZUNGSAREAL",):
    poly(rd(n).geometry, AREAL, 2)
poly(rd("VERKEHRSAREAL").geometry, VERKEHR, 2)
poly(rd("FREIZEITAREAL").geometry, SPORT, 3)
b = rd("BODENBEDECKUNG_OST")
poly(b[b.OBJEKTART.isin(["Wald", "Wald offen", "Gebueschwald"])].geometry, WALD, 4)
poly(b[b.OBJEKTART == "Gehoelzflaeche"].geometry, "#D9EDA8", 3)
poly(b[b.OBJEKTART.isin(["Fels", "Fels locker"])].geometry, FELS, 4)
poly(b[b.OBJEKTART == "Lockergestein"].geometry, GEROELL, 4)
poly(b[b.OBJEKTART.isin(["Stehende Gewaesser", "Fliessgewaesser"])].geometry, WASSER_FL, 5)
poly(rd("STEHENDES_GEWAESSER").geometry, WASSER_FL, 5)
f = rd("FLIESSGEWAESSER"); line(f[(f.OBJEKTART == "Fliessgewaesser") & (f.STUFE == "0")].geometry, WASSER_LI, 1.4, 6)
s = rd("STRASSE"); t = s.OBJEKTART
road(s, t == "Autobahn", AUTOBAHN, 6, 12)
road(s, t.isin(["10m Strasse", "8m Strasse"]), HAUPT, 5, 10)
road(s, t == "6m Strasse", STRASSE, 4, 8)
nat = s.BELAGSART == "Natur"
road(s, t.isin(["4m Strasse", "3m Strasse"]) & nat, NATUR, 3, 7)
road(s, t.isin(["4m Strasse", "3m Strasse", "Verbindung", "Dienstzufahrt", "Zufahrt", "Ausfahrt", "Einfahrt", "Platz"]) & ~(t.isin(["4m Strasse", "3m Strasse"]) & nat), NEBEN, 3, 6)
w = t.isin(["1m Weg", "2m Weg"])
line(s[(t == "2m Weg") & s.WANDERWEGE.isna()].geometry, WEG_FEST, 1.4, 6)
line(s[w & s.WANDERWEGE.notna()].geometry, WEG, 2, 6, ls=(0, (3, 2)))
line(s[(t == "1m Weg") & s.WANDERWEGE.isna()].geometry, WEG, 1.4, 6, ls=(0, (3, 3)))
e = rd("EISENBAHN").geometry; line(e, WEG, 3, 11); line(e, "#FFFFFF", 1, 11.2, ls=(0, (4, 4)))
poly(gdf[gdf.OBJEKTART != "Unterirdisches Gebaeude"].geometry, GEBAEUDE, 20)
for r in rd("SIEDLUNGSNAME").itertuples():
    if r.OBJEKTART == "Ort" and r.NAME:
        p = shapely.force_2d(r.geometry).representative_point()
        if x0 < p.x < x1 and y0 < p.y < y1:
            ax.text(p.x, p.y, r.NAME, fontsize=9, ha="center", zorder=30, color="#000000",
                    path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=3, foreground="white")])
fig.savefig(out, dpi=100); print("ok", out)
