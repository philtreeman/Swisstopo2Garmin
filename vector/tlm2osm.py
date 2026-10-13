#!/usr/bin/env python3
"""swissTLM3D (Shapefile, LV95) -> OSM-XML fuer mkgmap.

Die Objekte bekommen eigene Tags (tlm_layer, tlm_type, ...), die der mkgmap-Style
in vector/style/ auf Garmin-Typen abbildet.

  python3 tlm2osm.py --shp DIR --bbox W S E N --out DIR [--tile-km 20]

--bbox in WGS84. Mit --tile-km wird in Kacheln gearbeitet (Speicher); ein Objekt
landet nur in der Kachel, in der sein Repraesentationspunkt liegt (keine Duplikate).
"""
import argparse, math, os, sys
from xml.sax.saxutils import quoteattr
import pyogrio, shapely
from shapely import transform as _t
from pyproj import Transformer

TO_WGS = Transformer.from_crs(2056, 4326, always_xy=True)
FROM_WGS = Transformer.from_crs(4326, 2056, always_xy=True)

# (Shapefile-Suffix, Ebene, Felder die als Tags uebernommen werden)
LAYERS = [
    ("BODENBEDECKUNG_OST", "bb", {}), ("BODENBEDECKUNG_WEST", "bb", {}),
    ("STEHENDES_GEWAESSER", "see", {}), ("NUTZUNGSAREAL", "areal", {}),
    ("VERKEHRSAREAL", "vareal", {}),
    ("GEBAEUDE_FOOTPRINT_OST", "gebaeude", {}), ("GEBAEUDE_FOOTPRINT_WEST", "gebaeude", {}),
    ("STRASSE", "strasse", {"WANDERWEGE": "hiking", "BELAGSART": "belag", "KUNSTBAUTE": "kunst", "STUFE": "stufe"}),
    ("FLIESSGEWAESSER", "fluss", {"STUFE": "stufe"}),
    ("EISENBAHN", "bahn", {"KUNSTBAUTE": "kunst", "STUFE": "stufe", "ZAHNRADBAH": "zahnrad"}),
    ("UEBRIGE_BAHN", "ubahn", {}), ("MAUER", "mauer", {}),
    ("HALTESTELLE", "halt", {}), ("SIEDLUNGSNAME", "ort", {"EINWOHNERK": "einw"}),
    ("NAME_PKT", "namepkt", {"HOEHE": "hoehe"}), ("EINZELOBJEKT", "eo", {}),
    ("GELAENDENAME", "gelaende", {}), ("FLURNAME", "flur", {}),
]


class Writer:
    def __init__(self, path):
        self.path = path
        self.nodes, self.ways, self.rels = open(path + ".n", "w"), open(path + ".w", "w"), open(path + ".r", "w")
        self.nid = self.wid = self.rid = 0

    def _tags(self, tags):
        return "".join(f"<tag k={quoteattr(k)} v={quoteattr(str(v))}/>" for k, v in tags.items() if v is not None and str(v) not in ("", "k_W", "nan", "None"))

    def node(self, x, y, tags=None):
        self.nid -= 1
        t = self._tags(tags) if tags else ""
        self.nodes.write(f'<node id="{self.nid}" lat="{y:.7f}" lon="{x:.7f}" version="1">{t}</node>\n' if t else f'<node id="{self.nid}" lat="{y:.7f}" lon="{x:.7f}" version="1"/>\n')
        return self.nid

    def way(self, coords, tags, closed=False):
        ids = [self.node(x, y) for x, y in coords]
        if closed:
            ids[-1] = ids[0]
        self.wid -= 1
        refs = "".join(f'<nd ref="{i}"/>' for i in ids)
        self.ways.write(f'<way id="{self.wid}" version="1">{refs}{self._tags(tags) if tags else ""}</way>\n')
        return self.wid

    def close(self):
        for f in (self.nodes, self.ways, self.rels):
            f.close()
        with open(self.path, "w") as out:
            out.write('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="tlm2osm">\n')
            for ext in (".n", ".w", ".r"):
                with open(self.path + ext) as f:
                    for line in f:
                        out.write(line)
                os.remove(self.path + ext)
            out.write("</osm>\n")


def ring(r):
    c = list(r.coords)
    return [(x, y) for x, y, *_ in c]


def emit_polygon(w, poly, tags):
    outer = w.way(ring(poly.exterior), tags if not poly.interiors else None, closed=True)
    if not poly.interiors:
        return
    inner = [w.way(ring(i), None, closed=True) for i in poly.interiors]
    w.rid -= 1
    members = f'<member type="way" ref="{outer}" role="outer"/>' + "".join(f'<member type="way" ref="{i}" role="inner"/>' for i in inner)
    t = dict(tags); t["type"] = "multipolygon"
    w.rels.write(f'<relation id="{w.rid}" version="1">{members}{w._tags(t)}</relation>\n')


def convert_tile(shp_dir, bb_lv95, out_path, simplify):
    w = Writer(out_path)
    x0, y0, x1, y1 = bb_lv95
    counts = {}
    for suffix, kind, extra in LAYERS:
        p = os.path.join(shp_dir, f"swissTLM3D_TLM_{suffix}.shp")
        if not os.path.exists(p):
            print("fehlt:", p, file=sys.stderr); continue
        df = pyogrio.read_dataframe(p, bbox=tuple(bb_lv95))
        n = 0
        for row in df.itertuples(index=False):
            g = row.geometry
            if g is None or g.is_empty:
                continue
            g = shapely.force_2d(g)
            rp = g.representative_point()
            if not (x0 <= rp.x < x1 and y0 <= rp.y < y1):
                continue  # gehoert zur Nachbarkachel
            tags = {"tlm_layer": kind, "tlm_type": getattr(row, "OBJEKTART", None)}
            name = getattr(row, "NAME", None)
            if isinstance(name, str) and name.strip():
                tags["name"] = name.strip()
            for fld, key in extra.items():
                tags[f"tlm_{key}"] = getattr(row, fld, None)
            if simplify and g.geom_type != "Point":
                g = g.simplify(simplify, preserve_topology=True)
                if g.is_empty:
                    continue
            g = _t(g, lambda c: __import__("numpy").column_stack(TO_WGS.transform(c[:, 0], c[:, 1])))
            parts = list(g.geoms) if g.geom_type.startswith("Multi") else [g]
            for part in parts:
                if part.geom_type == "Point":
                    w.node(part.x, part.y, tags)
                elif part.geom_type == "LineString":
                    if kind in ("ort", "namepkt", "gelaende", "flur", "eo", "halt"):
                        pt = part.interpolate(0.5, normalized=True); w.node(pt.x, pt.y, tags)
                    else:
                        w.way(list(part.coords), tags)
                elif part.geom_type == "Polygon":
                    if kind in ("ort", "namepkt", "gelaende", "flur", "eo", "halt"):
                        pt = part.representative_point(); w.node(pt.x, pt.y, tags)
                    else:
                        emit_polygon(w, part, tags)
                else:
                    continue
            n += 1
        counts[suffix] = n
    w.close()
    return counts


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--shp", required=True)
    a.add_argument("--bbox", nargs=4, type=float, required=True, metavar=("W", "S", "E", "N"))
    a.add_argument("--out", required=True)
    a.add_argument("--tile-km", type=float, default=0)
    a.add_argument("--simplify", type=float, default=1.5, help="Meter, 0=aus")
    o = a.parse_args()
    os.makedirs(o.out, exist_ok=True)
    x0, y0 = FROM_WGS.transform(o.bbox[0], o.bbox[1]); x1, y1 = FROM_WGS.transform(o.bbox[2], o.bbox[3])
    step = o.tile_km * 1000 if o.tile_km else max(x1 - x0, y1 - y0) + 1
    nx, ny = math.ceil((x1 - x0) / step), math.ceil((y1 - y0) / step)
    for i in range(nx):
        for j in range(ny):
            bb = (x0 + i * step, y0 + j * step, min(x0 + (i + 1) * step, x1), min(y0 + (j + 1) * step, y1))
            path = os.path.join(o.out, f"tlm_{i:02d}_{j:02d}.osm")
            c = convert_tile(o.shp, bb, path, o.simplify)
            print(path, f"{os.path.getsize(path)/1e6:.1f} MB", c, flush=True)


if __name__ == "__main__":
    main()
