#!/usr/bin/env python3
"""Vergleichsbilder: swisstopo-Rasterkarte (WMTS) neben einer eigenen Zeichnung von SwissTOPO Vector (kein Garmin-Rendering).

  python3 compare_vector.py <shp-ordner> <out-prefix> <lon> <lat> <breite_m> [<breite_m> ...]

Je Breite entsteht <out-prefix>_<breite>m.png (links Raster, rechts Vektor). Die Sichtbarkeit richtet sich nach den
`resolution`-Werten in mkgmap/vector/style; welche Ebene das Geraet bei welchem Massstab waehlt, ist ungeprueft und hier
angenommen: 400 m = Ebene 24, bis 1500 m = 22, bis 3000 m = 21, bis 6000 m = 20, darueber 18.
"""
import sys, io, math, urllib.request
import numpy as np, pandas as pd, pyogrio, shapely
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from PIL import Image
from pyproj import Transformer
from vector_palette import *
from vector_patterns import PATTERNS

shp, prefix, lon, lat = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
widths = [float(w) for w in sys.argv[5:]]
PX = 564
cx, cy = Transformer.from_crs(4326, 2056, always_xy=True).transform(lon, lat)
to3857 = Transformer.from_crs(2056, 3857, always_xy=True)


def view_res(w):
    return 24 if w <= 600 else 22 if w <= 1500 else 21 if w <= 3000 else 20 if w <= 6000 else 18


def raster(bb, w):
    x0, y0, x1, y1 = bb
    xs = x0 + (np.arange(PX) + .5) / PX * (x1 - x0)
    ys = y1 - (np.arange(PX) + .5) / PX * (y1 - y0)
    X, Y = np.meshgrid(xs, ys)
    mx, my = to3857.transform(X, Y)
    mpp = w / PX / math.cos(math.radians(lat))               # 3857-Meter pro Pixel
    z = min(18, max(8, int(math.floor(math.log2(40075016.686 / 256 / mpp)))))
    n = 2 ** z; o = 20037508.342789244; ts = 2 * o / n
    px = (mx + o) / ts * 256; py = (o - my) / ts * 256
    tx0, tx1, ty0, ty1 = int(px.min() // 256), int(px.max() // 256), int(py.min() // 256), int(py.max() // 256)
    mos = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            u = f"https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{tx}/{ty}.jpeg"
            mos.paste(Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=60).read())).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    a = np.asarray(mos)
    ix = np.clip((px - tx0 * 256).astype(int), 0, a.shape[1] - 1); iy = np.clip((py - ty0 * 256).astype(int), 0, a.shape[0] - 1)
    return a[iy, ix], z


def read(name, bb):
    out = []
    for suf in ([""] if name in ("STRASSE", "EISENBAHN", "VERBAUUNG", "MAUER", "FLIESSGEWAESSER", "STEHENDES_GEWAESSER", "SIEDLUNGSNAME", "FREIZEITAREAL", "NUTZUNGSAREAL", "VERKEHRSAREAL") else ["_OST", "_WEST"]):
        try:
            out.append(pyogrio.read_dataframe(f"{shp}/swissTLM3D_TLM_{name}{suf}.shp", bbox=bb))
        except Exception:
            pass
    return pd.concat(out) if out else pd.DataFrame(columns=["geometry", "OBJEKTART"])


def draw(w, ax, res):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - w / 2, cy + w / 2
    bb = (x0, y0, x1, y1); pad = (x0 - 80, y0 - 80, x1 + 80, y1 + 80)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off"); ax.set_facecolor(BG)
    on = lambda r: r <= res

    def poly(geoms, col, z):
        for g in geoms:
            if g is None or g.is_empty: continue
            for p in shapely.get_parts(shapely.force_2d(g)):
                if p.geom_type != "Polygon": continue
                v, c = [], []
                for r in [p.exterior] + list(p.interiors):
                    a = np.array(r.coords); v += list(a); c += [Path.MOVETO] + [Path.LINETO] * (len(a) - 2) + [Path.CLOSEPOLY]
                ax.add_patch(PathPatch(Path(v, c), fc=col, ec="none", zorder=z))

    def pat_poly(geoms, typ, z):
        """Flaeche mit dem 32x32-Muster der TYP-Datei, ein Musterpixel = ein Bildschirmpixel (564 px Breite)"""
        _, bg, fg, rows = PATTERNS[typ]
        m = np.array([[c == "f" for c in r] for r in rows])
        rgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
        tile = np.where(m[..., None], rgb(fg), rgb(bg)).astype(np.uint8)
        arr = np.tile(tile, (PX // 32 + 1, PX // 32 + 1, 1))[:PX, :PX]
        for g in geoms:
            if g is None or g.is_empty: continue
            for p in shapely.get_parts(shapely.force_2d(g)):
                if p.geom_type != "Polygon": continue
                v, c = [], []
                for r in [p.exterior] + list(p.interiors):
                    a = np.array(r.coords); v += list(a); c += [Path.MOVETO] + [Path.LINETO] * (len(a) - 2) + [Path.CLOSEPOLY]
                patch = PathPatch(Path(v, c), fc="none", ec="none", transform=ax.transData); ax.add_patch(patch)
                im = ax.imshow(arr, extent=(x0, x1, y0, y1), interpolation="nearest", zorder=z, aspect="equal")
                im.set_clip_path(patch)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)

    def line(geoms, col, px, z, ls="-"):
        for g in geoms:
            if g is None: continue
            for l in shapely.get_parts(shapely.force_2d(g)):
                a = np.array(l.coords); ax.plot(a[:, 0], a[:, 1], color=col, lw=px * 0.72, ls=ls, solid_capstyle="butt", zorder=z)

    def road(df, sel, pal, wd, z):
        g = df[sel].geometry; line(g, pal[1], wd + 2, z); line(g, pal[0], wd, z + .1)

    gdf = read("GEBAEUDE_FOOTPRINT", pad)
    if on(21) and len(gdf):
        u = shapely.union_all(shapely.buffer(shapely.force_2d(gdf.geometry.values), 14, quad_segs=1))
        poly([p for p in shapely.get_parts(u) if p.area >= 8000], SIEDLUNG, 2)
    if on(22): poly(read("NUTZUNGSAREAL", bb).geometry, AREAL, 2); poly(read("FREIZEITAREAL", bb).geometry, SPORT, 3)
    if on(23): poly(read("VERKEHRSAREAL", bb).geometry, VERKEHR, 2)
    b = read("BODENBEDECKUNG", bb); t = b.OBJEKTART
    if on(20): poly(b[t.isin(["Wald", "Wald offen", "Gebueschwald"])].geometry, WALD, 4)
    if on(22): pat_poly(b[t == "Gehoelzflaeche"].geometry, "0x4f", 3)
    if on(21):
        pat_poly(b[t.isin(["Fels", "Fels locker"])].geometry, "0x52", 4); pat_poly(b[t == "Lockergestein"].geometry, "0x53", 4)
    if on(20):
        poly(b[t.isin(["Stehende Gewaesser", "Fliessgewaesser"])].geometry, WASSER_FL, 5); poly(read("STEHENDES_GEWAESSER", bb).geometry, WASSER_FL, 5)
    if on(21):
        f = read("FLIESSGEWAESSER", bb); line(f[(f.OBJEKTART == "Fliessgewaesser") & (f.STUFE == "0")].geometry, WASSER_LI, 1.4, 6)
    s = read("STRASSE", bb); t = s.OBJEKTART
    if on(18): road(s, t == "Autobahn", AUTOBAHN, 6, 12)
    if on(19): road(s, t.isin(["10m Strasse", "8m Strasse"]), HAUPT, 5, 10)
    if on(20): road(s, t == "6m Strasse", STRASSE, 4, 8)
    if on(22):
        nat = s.BELAGSART == "Natur"; big = t.isin(["4m Strasse", "3m Strasse"])
        road(s, big & nat, NATUR, 3, 7)
        road(s, t.isin(["4m Strasse", "3m Strasse", "Verbindung", "Dienstzufahrt", "Zufahrt", "Ausfahrt", "Einfahrt"]) & ~(big & nat), NEBEN, 3, 6)
    if on(22):                                                 # Reben, Obst: Gittermuster
        a = read("NUTZUNGSAREAL", bb); a = a[a.OBJEKTART.isin(["Reben", "Obstanlage"])]
        pat_poly(a.geometry, "0x4e", 3)
    if on(23):                                                 # Wege schwarz nach swisstopo-Legende, kein Farbcode
        line(s[t == "2m Weg"].geometry, SCHWARZ, 2, 6)
        line(s[t == "1m Weg"].geometry, SCHWARZ, 2, 6, ls=(0, (5, 3)))
        line(s[t == "Markierte Spur"].geometry, SCHWARZ, 2, 6, ls=(0, (1, 2)))
    if on(24):                                                 # Treppen rot gepunktet
        k = s[s.KUNSTBAUTE.isin(["Treppe", "Bruecke mit Treppe", "Unterfuehrung mit Treppe"])]
        line(k.geometry, "#E60000", 2.2, 9, ls=(0, (1, 2)))
    e = read("EISENBAHN", bb).geometry
    if on(20): line(e, WEG, 3, 11); line(e, "#FFFFFF", 1, 11.2, ls=(0, (4, 4)))
    if on(24):
        line(read("VERBAUUNG", bb).query("OBJEKTART == 'Schutzverbauung'").geometry, LAWINE, 3, 9)
        for geom in read("EINZELBAUM", bb).geometry:
            p = shapely.force_2d(geom)
            if p is not None and x0 < p.x < x1 and y0 < p.y < y1: ax.plot(p.x, p.y, "o", ms=2.2, color=BAUM, mew=0, zorder=15)
    if on(23): poly(gdf[gdf.OBJEKTART != "Unterirdisches Gebaeude"].geometry, GEBAEUDE, 20)
    for r in read("SIEDLUNGSNAME", bb).itertuples():
        if getattr(r, "OBJEKTART", "") == "Ort" and r.NAME and on(21):
            p = shapely.force_2d(r.geometry).representative_point()
            if x0 < p.x < x1 and y0 < p.y < y1:
                ax.text(p.x, p.y, r.NAME, fontsize=9, ha="center", zorder=30, path_effects=[pe.withStroke(linewidth=3, foreground="white")])


for w in widths:
    bb = (cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2)
    img, z = raster(bb, w)
    fig, axs = plt.subplots(1, 2, figsize=(11.3, 5.9), dpi=100)
    axs[0].imshow(img); axs[0].axis("off"); axs[0].set_title(f"Rasterkarte swisstopo (Kachelstufe {z})", fontsize=10)
    draw(w, axs[1], view_res(w)); axs[1].set_title(f"SwissTOPO Vector, Zeichnung (Ebene {view_res(w)})", fontsize=10)
    fig.suptitle(f"{w:.0f} m Breite   {lat:.4f}N {lon:.4f}E", fontsize=10)
    fig.tight_layout(); fig.savefig(f"{prefix}_{int(w)}m.png"); plt.close(fig); print("ok", f"{prefix}_{int(w)}m.png")
