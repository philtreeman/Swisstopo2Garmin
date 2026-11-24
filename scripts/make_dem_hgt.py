#!/usr/bin/env python3
"""Erzeugt SRTM-HGT-Kacheln (1 x 1 Grad, int16 big-endian, WGS84) aus swissALTIRegio fuer mkgmap --dem (Reliefschattierung).

  scripts/make_dem_hgt.py --out <ordner> [--tiles N47E008 ...] [--all] [--res 1|3] [--dem <datei-oder-url>] [--cache <ordner>]

Quelle: swissALTIRegio (10 m, LV95, Cloud-Optimized GeoTIFF, wie in hangneigung2mkgmap.py). Die Datei deckt ein Rechteck von
2385000-2935000 / 974000-1404000 (LV95) ab, also auch die Randgebiete jenseits der Landesgrenze (dort mit Daten der Nachbarlaender
gefuellt), so dass an der Grenze keine Klippe entsteht. Ausserhalb des Rechtecks (nur bei den Randkacheln, z. B. N45E005) dient
viewfinderpanoramas.org (3", Zip je 6-Grad-Streifen/4-Grad-Zeile, nur gelesen) als Rueckfall; ueber 2 km Breite wird zwischen beiden
Quellen ueberblendet. Wo keine Quelle Daten hat, steht -32768.

  --res 1   3601 x 3601 Punkte (1 Bogensekunde, ca. 26 MB je Kachel; Standard)
  --res 3   1201 x 1201 Punkte (3 Bogensekunden, ca. 2,9 MB je Kachel)
  --all     alle Kacheln N45E005 .. N47E010 (18 Stueck)

Die HGT-Gitter sind punktregistriert (Stuetzstelle = ganze Gradzahl, Zeile 0 = Nordrand). Aus 10 m wird je Zelle der Mittelwert
(GDAL average) gebildet, aus dem 3"-Rueckfall bilinear interpoliert.
Heruntergeladene Daten werden nur gelesen (kein Code daraus ausgefuehrt).
"""
import argparse, os, subprocess, sys, time, zipfile
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.warp import reproject
from pyproj import Transformer
from scipy.ndimage import map_coordinates, distance_transform_edt

DEM = "https://data.geo.admin.ch/ch.swisstopo.swissaltiregio/swissaltiregio/swissaltiregio_2056_5728.tif"
VFP = "https://viewfinderpanoramas.org/dem3/%s.zip"
NODATA = -32768
ALL_TILES = [(la, lo) for la in (45, 46, 47) for lo in range(5, 11)]
BLEND_M = 2000.0   # Ueberblendbreite am Rand der swissALTIRegio-Datei


def name(la, lo):
    return "N%02dE%03d" % (la, lo)


def vfp_sheet(la, lo):
    """viewfinderpanoramas-Blatt: Buchstabe je 4 Grad Breite (A ab Aequator), Zahl = UTM-Zone"""
    return "%s%02d" % (chr(ord("A") + la // 4), lo // 6 + 31)


def fetch_vfp(la, lo, cache):
    sheet = vfp_sheet(la, lo)
    z = os.path.join(cache, sheet + ".zip")
    if not os.path.exists(z):
        os.makedirs(cache, exist_ok=True)
        ca = "/root/.ccr/ca-bundle.crt"
        cmd = ["curl", "-sSf", "--retry", "5", "-o", z + ".part", VFP % sheet]
        env = dict(os.environ)
        if os.path.exists(ca):
            env["CURL_CA_BUNDLE"] = ca
        subprocess.run(cmd, check=True, env=env)
        os.rename(z + ".part", z)
    return z


def read_vfp(la, lo, cache):
    """3"-Kachel als float32 (1201 x 1201) oder None; Luecken = nan"""
    try:
        z = fetch_vfp(la, lo, cache)
    except subprocess.CalledProcessError:
        return None
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if n.endswith(name(la, lo) + ".hgt"):
                a = np.frombuffer(zf.read(n), ">i2").astype("float32")
                s = int(round(np.sqrt(a.size)))
                a = a.reshape(s, s)
                a[a == NODATA] = np.nan
                return a
    return None


def resample_vfp(a, n):
    """bilinear von (s x s) auf (n x n), punktregistriert"""
    s = a.shape[0]
    t = np.linspace(0, s - 1, n)
    yy, xx = np.meshgrid(t, t, indexing="ij")
    fill = np.where(np.isnan(a), 0, a)
    m = (~np.isnan(a)).astype("float32")
    v = map_coordinates(fill, [yy, xx], order=1, mode="nearest")
    w = map_coordinates(m, [yy, xx], order=1, mode="nearest")
    out = np.where(w > 0.999, v, np.nan)
    return out.astype("float32")


def read_ch(src, la, lo, n):
    """swissALTIRegio auf das HGT-Gitter; liefert (hoehe, abstand_zum_rand_in_m) mit nan ausserhalb der Datei"""
    res = 1.0 / (n - 1)
    dst_tr = Affine(res, 0, lo - res / 2, 0, -res, la + 1 + res / 2)
    dst = np.full((n, n), np.nan, dtype="float32")
    for k in range(6):
        try:
            with rasterio.open(src) as r:
                reproject(rasterio.band(r, 1), dst, dst_transform=dst_tr, dst_crs="EPSG:4326",
                          src_nodata=r.nodata, dst_nodata=np.nan, resampling=Resampling.average,
                          num_threads=2, init_dest_nodata=True)
                b = r.bounds
            break
        except Exception as e:  # Netzfehler: erneut versuchen
            if k == 5:
                raise
            print("Lesefehler, neuer Versuch:", e, file=sys.stderr, flush=True)
            time.sleep(2 ** k)
    dst[(dst < -1000) | (dst > 9000)] = np.nan
    # Abstand jedes Gitterpunkts zum Rand des Rechtecks (LV95) fuer die Ueberblendung
    t = np.linspace(0, 1, n)
    lons, lats = np.meshgrid(lo + t, la + 1 - t)
    x, y = Transformer.from_crs(4326, 2056, always_xy=True).transform(lons, lats)
    d = np.minimum.reduce([x - b.left, b.right - x, y - b.bottom, b.top - y])
    return dst, d.astype("float32")


def make_tile(la, lo, n, src, cache):
    ch, d = read_ch(src, la, lo, n)
    have_ch = ~np.isnan(ch)
    fb = None
    if not have_ch.all() or (d < BLEND_M).any():
        v = read_vfp(la, lo, cache)
        if v is not None:
            fb = resample_vfp(v, n) if n != v.shape[0] else v
    if fb is None:
        out = ch
    else:
        w = np.clip(d / BLEND_M, 0, 1)
        w[~have_ch] = 0
        chf = np.where(have_ch, ch, 0)
        out = np.where(np.isnan(fb), np.where(have_ch, ch, np.nan), w * chf + (1 - w) * fb)
        out = np.where(have_ch & (w >= 1), ch, out)
    lucken = np.isnan(out)
    h = np.where(lucken, NODATA, np.rint(out)).astype(">i2")
    return h, lucken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tiles", nargs="*", default=[], help="z. B. N47E008")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--res", type=int, choices=(1, 3), default=1)
    ap.add_argument("--dem", default=DEM, help="swissALTIRegio (Datei oder URL, LV95, 10 m)")
    ap.add_argument("--cache", default=None, help="Ordner fuer die viewfinderpanoramas-Zips (Standard: <out>/../vfp_cache)")
    o = ap.parse_args()
    n = 3601 if o.res == 1 else 1201
    src = o.dem if not o.dem.startswith("http") else "/vsicurl/" + o.dem
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CURL_CA_BUNDLE", "/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else "/etc/ssl/certs/ca-certificates.crt")
    os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "5")
    os.environ.setdefault("GDAL_CACHEMAX", "512")
    cache = o.cache or os.path.join(os.path.dirname(os.path.abspath(o.out)), "vfp_cache")
    todo = list(ALL_TILES) if o.all else []
    for t in o.tiles:
        todo.append((int(t[1:3]), int(t[4:7])))
    if not todo:
        ap.error("--tiles oder --all angeben")
    os.makedirs(o.out, exist_ok=True)
    for la, lo in todo:
        f = os.path.join(o.out, name(la, lo) + ".hgt")
        if os.path.exists(f) and os.path.getsize(f) == 2 * n * n:
            print(name(la, lo), "vorhanden")
            continue
        t0 = time.time()
        h, lucken = make_tile(la, lo, n, src, cache)
        h.tofile(f + ".part"); os.rename(f + ".part", f)
        v = h[~lucken]
        print("%s: %dx%d, %.1f s, Hoehe %d..%d m, Luecken %.2f %%" % (
            name(la, lo), n, n, time.time() - t0, v.min() if v.size else 0, v.max() if v.size else 0, 100 * lucken.mean()), flush=True)


if __name__ == "__main__":
    main()
