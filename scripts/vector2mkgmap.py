#!/usr/bin/env python3
"""swissTLM3D (Shapefile, LV95) -> OSM-XML fuer mkgmap (SwissTOPO Vector).

Die Objekte bekommen eigene Tags (tlm_layer, tlm_type, ...), die der mkgmap-Style
in mkgmap/vector/style/ auf Garmin-Typen abbildet. Zusaetzlich wird aus den Gebaeuden ein
Siedlungsgebiet (tlm_layer=siedlung) abgeleitet: Union der um 14 m vergroesserten Gebaeude.

  python3 vector2mkgmap.py --shp DIR --bbox W S E N --out DIR [--tile-km 20]

--bbox in WGS84. Mit --tile-km wird in Kacheln gearbeitet (Speicher); ein Objekt
landet nur in der Kachel, in der sein Repraesentationspunkt liegt (keine Duplikate).
"""
import argparse, math, os, sys
import numpy as np
import pyogrio, shapely
from shapely import transform as _t
from pyproj import Transformer
from mkgmap_xml_writer import Writer, emit_polygon

TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
FROM_WGS = Transformer.from_crs(4326, 2056, always_xy=True)

# (Shapefile-Suffix, Ebene, Felder die als Tags uebernommen werden)
LAYERS = [
    ("BODENBEDECKUNG_OST", "bb", {}), ("BODENBEDECKUNG_WEST", "bb", {}),
    ("STEHENDES_GEWAESSER", "see", {}), ("NUTZUNGSAREAL", "areal", {}),
    ("VERKEHRSAREAL", "vareal", {}), ("FREIZEITAREAL", "freizeit", {}),
    ("GEBAEUDE_FOOTPRINT_OST", "gebaeude", {}), ("GEBAEUDE_FOOTPRINT_WEST", "gebaeude", {}),
    ("STRASSE", "strasse", {"WANDERWEGE": "hiking", "BELAGSART": "belag", "KUNSTBAUTE": "kunst", "STUFE": "stufe"}),
    ("FLIESSGEWAESSER", "fluss", {"STUFE": "stufe"}),
    ("EISENBAHN", "bahn", {"KUNSTBAUTE": "kunst", "STUFE": "stufe", "ZAHNRADBAH": "zahnrad"}),
    ("UEBRIGE_BAHN", "ubahn", {}), ("MAUER", "mauer", {}),
    ("HALTESTELLE", "halt", {}), ("SIEDLUNGSNAME", "ort", {"EINWOHNERK": "einw"}),
    ("NAME_PKT", "namepkt", {"HOEHE": "hoehe"}), ("EINZELOBJEKT", "eo", {}),
    ("GELAENDENAME", "gelaende", {}), ("FLURNAME", "flur", {}),
    ("VERBAUUNG", "verbauung", {}),
]
# nur mit --trees: rund 11,5 Mio. Einzelbaeume (je ein Punkt); vergroessert die Karte stark
LAYERS_TREES = [("EINZELBAUM_OST", "baum", {}), ("EINZELBAUM_WEST", "baum", {})]


PAD = 80            # Rand (m) um die Kachel, damit das Siedlungsgebiet an Kachelgrenzen nahtlos ist
SIEDLUNG_PUFFER = 14  # Meter um jedes Gebaeude
SIEDLUNG_MIN_FLAECHE = 8000  # m2, kleinere Gruppen (Einzelhaeuser) bekommen keinen Untergrund
POINT_KINDS = ("ort", "namepkt", "gelaende", "flur", "eo", "halt")


def to_wgs(g):
    return _t(g, lambda c: __import__("numpy").column_stack(TO_WGS.transform(c[:, 0], c[:, 1])))


def emit_geom(w, g, kind, tags):
    parts = list(g.geoms) if g.geom_type.startswith("Multi") else [g]
    for part in parts:
        if part.geom_type == "Point":
            w.node(part.x, part.y, tags)
        elif part.geom_type == "LineString":
            if kind in POINT_KINDS:
                pt = part.interpolate(0.5, normalized=True); w.node(pt.x, pt.y, tags)
            else:
                w.way(list(part.coords), tags)
        elif part.geom_type == "Polygon":
            if kind in POINT_KINDS:
                pt = part.representative_point(); w.node(pt.x, pt.y, tags)
            else:
                emit_polygon(w, part, tags)


# Varianten: edge = mit Namen (Berge mit Hoehe, Gewaesser, Fluren, Gelaende) und Grenzen, fenix = ohne Namen ausser der Hoehe an
# Gipfeln und Paessen (kleines Display, weniger Daten)
VARIANTS = ("edge", "fenix")
NAMENSLOS = ("see", "fluss", "flur", "gelaende", "eo", "ort", "strasse", "halt")   # Ebenen, deren Namen in der Variante fenix wegfallen
GRENZ_ARTEN = {"1": "Landesgrenze", "2": "Kantonsgrenze", "4": "Gemeindegrenze"}   # swissBOUNDARIES3D (3 = Bezirksgrenze, nicht verwendet)


def convert_tile(shp_dir, bb_lv95, out_path, simplify, trees=False, variant="edge", grenzen=None):
    w = Writer(out_path)
    x0, y0, x1, y1 = bb_lv95
    counts = {}
    settle = []  # Gebaeude-Geometrien fuer das Siedlungsgebiet (inkl. Rand)
    for suffix, kind, extra in LAYERS + (LAYERS_TREES if trees else []):
        if variant == "fenix" and suffix in ("FLURNAME", "GELAENDENAME", "FREIZEITAREAL"):   # Sportplaetze nur im Edge
            continue
        p = os.path.join(shp_dir, f"swissTLM3D_TLM_{suffix}.shp")
        if not os.path.exists(p):
            print("fehlt:", p, file=sys.stderr); continue
        rb = (x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD) if kind == "gebaeude" else tuple(bb_lv95)
        df = pyogrio.read_dataframe(p, bbox=rb)
        n = 0
        for row in df.itertuples(index=False):
            g = row.geometry
            if g is None or g.is_empty:
                continue
            g = shapely.force_2d(g)
            if kind == "gebaeude" and getattr(row, "OBJEKTART", None) != "Unterirdisches Gebaeude":
                settle.append(g)
            rp = g.representative_point()
            if not (x0 <= rp.x < x1 and y0 <= rp.y < y1):
                continue  # gehoert zur Nachbarkachel
            tags = {"tlm_layer": kind, "tlm_type": getattr(row, "OBJEKTART", None)}
            name = getattr(row, "NAME", None)
            name = name.strip() if isinstance(name, str) and name.strip() else None
            if kind == "strasse" and not name:           # Strassennamen stehen in STRNAME (NAME hat nur Bruecken u. a.)
                sn = getattr(row, "STRNAME", None)
                name = sn.strip() if isinstance(sn, str) and sn.strip() else None
            if kind == "namepkt":                       # Gipfel, Huegel, Paesse: Edge "Name 2502", Fenix nur "2502"
                h = getattr(row, "HOEHE", None)
                h = str(int(round(float(h)))) if h is not None and str(h) not in ("nan", "") else None
                name = (h if variant == "fenix" else f"{name} {h}" if name and h else name)
            elif variant == "fenix" and kind in NAMENSLOS:
                name = None
            if name:
                tags["name"] = name
            for fld, key in extra.items():
                tags[f"tlm_{key}"] = getattr(row, fld, None)
            if simplify and g.geom_type != "Point":
                g = g.simplify(simplify, preserve_topology=True)
                if g.is_empty:
                    continue
            emit_geom(w, to_wgs(g), kind, tags)
            n += 1
        counts[suffix] = n
    if grenzen and variant == "edge":
        box = shapely.box(x0, y0, x1, y1)
        gdf = pyogrio.read_dataframe(grenzen, layer="tlm_hoheitsgrenze", bbox=tuple(bb_lv95))
        n = 0
        for row in gdf.itertuples(index=False):
            art = GRENZ_ARTEN.get(str(row.objektart))
            g = row.geometry
            if art is None or g is None or g.is_empty:
                continue
            for part in shapely.get_parts(shapely.force_2d(g).intersection(box)):
                if part.geom_type == "LineString" and part.length > 0:
                    emit_geom(w, to_wgs(part.simplify(simplify or 0.1, preserve_topology=True)), "grenze", {"tlm_layer": "grenze", "tlm_type": art}); n += 1
        counts["GRENZEN"] = n
    settle = np.array(settle, dtype=object)
    if len(settle):
        # vektorisiert puffern, vereinigen, kleine Gruppen verwerfen, erst dann vereinfachen (schneller)
        u = shapely.union_all(shapely.buffer(settle, SIEDLUNG_PUFFER, quad_segs=1))
        box = shapely.box(x0, y0, x1, y1)
        k = 0
        for poly in (list(u.geoms) if hasattr(u, "geoms") else [u]):
            if poly.geom_type != "Polygon" or poly.area < SIEDLUNG_MIN_FLAECHE:
                continue
            for q in shapely.get_parts(poly.simplify(6, preserve_topology=True).intersection(box)):
                if q.geom_type == "Polygon" and q.area >= SIEDLUNG_MIN_FLAECHE / 2:
                    emit_geom(w, to_wgs(q), "siedlung", {"tlm_layer": "siedlung", "tlm_type": "Siedlung"}); k += 1
        counts["SIEDLUNG"] = k
    w.close()
    return counts


GRID_X0, GRID_Y0 = 2480000, 1070000   # Ursprung des Kachelrasters in LV95
CH_BBOX = (5.90, 45.80, 10.60, 47.90)  # ganze Schweiz, WGS84


def print_grid(bbox, km):
    """Gibt die LV95-Kacheln (i j x0 y0 x1 y1) aus, die die Bounding Box abdecken."""
    step = km * 1000
    x0, y0 = FROM_WGS.transform(bbox[0], bbox[1]); x1, y1 = FROM_WGS.transform(bbox[2], bbox[3])
    for i in range(int((x0 - GRID_X0) // step), int((x1 - GRID_X0) // step) + 1):
        for j in range(int((y0 - GRID_Y0) // step), int((y1 - GRID_Y0) // step) + 1):
            print(i, j, GRID_X0 + i * step, GRID_Y0 + j * step, GRID_X0 + (i + 1) * step, GRID_Y0 + (j + 1) * step)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--shp", help="Ordner mit swissTLM3D_TLM_*.shp")
    a.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), help="WGS84")
    a.add_argument("--out", help="Ausgabeordner (mit --bbox)")
    a.add_argument("--tile-km", type=float, default=0)
    a.add_argument("--simplify", type=float, default=1.5, help="Meter, 0=aus")
    a.add_argument("--print-grid", type=float, metavar="KM",
                   help="Kachelliste (LV95-Raster) fuer --bbox (Standard: ganze Schweiz) ausgeben und beenden")
    a.add_argument("--lv95-tile", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"),
                   help="genau eine Kachel in LV95 konvertieren (mit --out-file)")
    a.add_argument("--out-file")
    a.add_argument("--trees", action="store_true", help="Einzelbaeume als Punkte mitschreiben (gross)")
    a.add_argument("--variant", choices=VARIANTS, default="edge", help="edge: mehr Namen und Grenzen; fenix: nur Hoehenpunkte")
    a.add_argument("--grenzen", help="swissBOUNDARIES3D-GeoPackage (Layer tlm_hoheitsgrenze), nur Variante edge")
    o = a.parse_args()
    if o.print_grid:
        print_grid(o.bbox or CH_BBOX, o.print_grid)
        return
    if o.lv95_tile:
        c = convert_tile(o.shp, tuple(o.lv95_tile), o.out_file, o.simplify, o.trees, o.variant, o.grenzen)
        print(o.out_file, f"{os.path.getsize(o.out_file)/1e6:.1f} MB", sum(c.values()), "Objekte", flush=True)
        return
    os.makedirs(o.out, exist_ok=True)
    x0, y0 = FROM_WGS.transform(o.bbox[0], o.bbox[1]); x1, y1 = FROM_WGS.transform(o.bbox[2], o.bbox[3])
    step = o.tile_km * 1000 if o.tile_km else max(x1 - x0, y1 - y0) + 1
    nx, ny = math.ceil((x1 - x0) / step), math.ceil((y1 - y0) / step)
    for i in range(nx):
        for j in range(ny):
            bb = (x0 + i * step, y0 + j * step, min(x0 + (i + 1) * step, x1), min(y0 + (j + 1) * step, y1))
            path = os.path.join(o.out, f"tlm_{i:02d}_{j:02d}.osm")
            c = convert_tile(o.shp, bb, path, o.simplify, o.trees, o.variant, o.grenzen)
            print(path, f"{os.path.getsize(path)/1e6:.1f} MB", c, flush=True)


if __name__ == "__main__":
    main()
