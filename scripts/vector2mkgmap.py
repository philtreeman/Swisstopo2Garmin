#!/usr/bin/env python3
"""swissTLM3D (Shapefile, LV95) -> OSM-XML fuer mkgmap (SwissTOPO Vector).

Die Objekte bekommen eigene Tags (tlm_layer, tlm_type, ...), die der mkgmap-Style
in mkgmap/vector/style/ auf Garmin-Typen abbildet. Zusaetzlich wird aus den Gebaeuden ein
Siedlungsgebiet (tlm_layer=siedlung) abgeleitet: Union der um 14 m vergroesserten Gebaeude.

  python3 vector2mkgmap.py --shp DIR --bbox W S E N --out DIR [--tile-km 20]

--bbox in WGS84. Mit --tile-km wird in Kacheln gearbeitet (Speicher); ein Objekt
landet nur in der Kachel, in der sein Repraesentationspunkt liegt (keine Duplikate).

Routing (--routing, zusammen mit --wgs-tile; Kachelliste mit --print-grid-wgs): die Kachel ist ein Rechteck in WGS84, dessen
Kanten auf Vielfachen von 2048 Garmin-Einheiten liegen. Linien und Flaechen werden nur grob (auf die Kachel plus RAND_ROUTING m)
zugeschnitten; das <bounds>-Element sagt mkgmap das genaue Rechteck, mkgmap schneidet dort zu und schreibt die
Begrenzungsknoten (NOD3), ueber die das Geraet von Kachel zu Kachel routet. Strassen teilen an gleichen Koordinaten (LV95 auf
cm gerundet) einen gemeinsamen Knoten, damit Kreuzungen im Routing-Netz verbunden sind. Siehe README, Abschnitt «Routing».
"""
import argparse, math, os, re, sys
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
    ("STEHENDES_GEWAESSER", "see", {"WSTAND_WE": "schwank"}), ("NUTZUNGSAREAL", "areal", {}),
    ("VERKEHRSAREAL", "vareal", {}), ("FREIZEITAREAL", "freizeit", {}),
    ("GEBAEUDE_FOOTPRINT_OST", "gebaeude", {}), ("GEBAEUDE_FOOTPRINT_WEST", "gebaeude", {}),
    ("STRASSE", "strasse", {"WANDERWEGE": "hiking", "BELAGSART": "belag", "KUNSTBAUTE": "kunst", "STUFE": "stufe", "VERKEHRSBD": "vbed"}),
    ("FLIESSGEWAESSER", "fluss", {"STUFE": "stufe", "VERLAUF": "verlauf"}),
    ("EISENBAHN", "bahn", {"KUNSTBAUTE": "kunst", "STUFE": "stufe", "ZAHNRADBAH": "zahnrad", "ANSCHLUSSG": "anschlussg", "VERKEHRSMI": "verkehrsmi"}),
    ("UEBRIGE_BAHN", "ubahn", {"AUSSER_BET": "ausser"}), ("MAUER", "mauer", {}),
    ("SIEDLUNGSNAME", "ort", {"EINWOHNERK": "einwk"}),
    ("NAME_PKT", "namepkt", {"HOEHE": "hoehe"}), ("EINZELOBJEKT", "eo", {}),
    ("GELAENDENAME", "gelaende", {}), ("FLURNAME", "flur", {}), ("GEBIETSNAME", "gebiet", {}),
    ("VERBAUUNG", "verbauung", {}),
    # Ebenen, die erst mit der Legenden-Fassung dazukamen (2026-11-24)
    ("LEITUNG", "leitung", {}), ("STAUBAUTE", "staubaute", {}), ("SPORTBAUTE_LIN", "sportlin", {}), ("SPORTBAUTE_PLY", "sportply", {}),
    ("VERKEHRSBAUTE_PLY", "vbauteply", {}), ("VERKEHRSBAUTE_LIN", "vbautelin", {}), ("SCHUTZGEBIET", "natpark", {}),
    ("VERSORGUNGSBAUTE_PKT", "wpkt", {}), ("SCHIFFFAHRT", "schiff", {}), ("STRASSENINFO", "sinfo", {}),
]
# Objektarten, die gar nicht erst geschrieben werden (nicht in der Zeichenerklaerung oder zu viele)
NUR = {   # Ebene (Suffix) -> erlaubte Objektarten
    "NUTZUNGSAREAL": {"Reben", "Obstanlage", "Baumschule", "Friedhof", "Schrebergartenareal", "Oeffentliches Parkareal", "Deponieareal", "Spitalareal"},
    "VERKEHRSAREAL": {"Heliport"},
    "STAUBAUTE": {"Staumauer", "Staudamm", "Wehr"},
    "VERKEHRSBAUTE_PLY": {"Hartbelagpiste", "Graspiste", "Rollfeld Hartbelag", "Rollfeld Gras"},
    "VERSORGUNGSBAUTE_PKT": {"Windturbine", "Antenne klein", "Antenne gross"},
    "STRASSENINFO": {"Durchfahrtssperre", "Raststaette", "Verladestation"},
    "BODENBEDECKUNG_OST": None, "BODENBEDECKUNG_WEST": None,
}
NUR_ARTEN_BB = None
# nur in der Variante edge: Ebenen, die in fenix ganz wegfallen (kleines Display, wenig Speicher)
NUR_EDGE = ("FLURNAME", "GELAENDENAME", "GEBIETSNAME", "EINZELOBJEKT", "SPORTBAUTE_LIN", "SPORTBAUTE_PLY", "VERKEHRSBAUTE_LIN",
            "VERSORGUNGSBAUTE_PKT", "SCHIFFFAHRT", "STRASSENINFO", "SCHUTZGEBIET")
# Ebenen, deren Objekte als Punkt im Repraesentationspunkt geschrieben werden (statt als Linie/Flaeche)
# nur mit --trees: rund 11,5 Mio. Einzelbaeume (je ein Punkt); vergroessert die Karte stark
LAYERS_TREES = [("EINZELBAUM_OST", "baum", {}), ("EINZELBAUM_WEST", "baum", {})]
# nur mit --routing: zusaetzliche Strassen-Attribute fuer Einbahn, Zugang und Strassenklasse (mkgmap/vector/style/inc/routing_lines).
# VERKEHRSBD (tlm_vbed, Verkehrsbedeutung) steht immer im Strassen-Layer: die Strassenfarbe richtet sich danach.
ROUTING_EXTRA = {"RICHTUNGSG": "richtung", "VERKEHRSBE": "vbeschr", "BEFAHRBARK": "befahrbar"}
RAND_ROUTING = 100   # m: Rand um die WGS84-Kachel beim Vorzuschnitt (mkgmap schneidet dann genau am <bounds>-Rechteck)
GARMIN_BLOCK = 2048 * 360 / 2 ** 24   # Grad: 2048 Garmin-Einheiten (0.0439453125), Raster der Routing-Kacheln wie bei splitter


PAD = 80            # Rand (m) um die Kachel beim Lesen der Shapefiles
POINT_KINDS = ("ort", "namepkt", "gelaende", "flur", "eo", "halt", "gebiet", "wpkt", "sinfo", "hpkt", "ulift")   # Objekte, die als Punkt geschrieben werden


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
NAMENSLOS = ("see", "fluss", "flur", "gelaende", "eo", "ort", "strasse", "halt", "gebiet")   # Ebenen, deren Namen in der Variante fenix wegfallen
GRENZ_ARTEN = {"1": "Landesgrenze", "2": "Kantonsgrenze", "3": "Bezirksgrenze", "4": "Gemeindegrenze"}   # swissBOUNDARIES3D


OHNE_NAME = ("leitung", "staubaute", "sportlin", "sportply", "vbauteply", "vbautelin", "natpark", "wpkt", "schiff", "sinfo", "verbauung")   # Ebenen ohne Beschriftung
SCHILD_ABSTAND = 4000   # m zwischen zwei Strassenschildern einer Nationalstrasse


def schilder(quelle, layer, feld, praefix, box, nur=None):
    """Punkte (x, y, '<praefix><nummer>') entlang der Achsen einer GDB-Ebene im Abstand SCHILD_ABSTAND; die Lage haengt nur
    von der Achse ab, nicht von der Kachel, daher entstehen keine Doppelten an Kachelraendern"""
    import re
    df = pyogrio.read_dataframe(quelle, layer=layer)
    out = []
    for nr, grp in df.groupby(feld):
        nr = str(nr)
        if not re.fullmatch(nur, nr):
            continue
        for ln in shapely.get_parts(shapely.line_merge(shapely.union_all(shapely.force_2d(grp.geometry.values)))):
            if ln.geom_type != "LineString" or ln.length < SCHILD_ABSTAND / 4:
                continue
            for d in np.arange(min(SCHILD_ABSTAND / 2, ln.length / 2), ln.length, SCHILD_ABSTAND):
                p = ln.interpolate(float(d))
                if box.contains(p):
                    out.append((p.x, p.y, praefix + nr.lstrip("N")))
    return out


_KS_CACHE = {}


def kantonsschilder_punkte(pfad, box):
    """Punkte (x, y, nummer) aus der CSV von scripts/kantonsschilder.py (LV95), die in der Kachel liegen"""
    if pfad not in _KS_CACHE:
        import csv
        with open(pfad, newline="") as f:
            _KS_CACHE[pfad] = [(float(r["x"]), float(r["y"]), r["nr"]) for r in csv.DictReader(f)]
    return [p for p in _KS_CACHE[pfad] if box.contains(shapely.Point(p[0], p[1]))]


def clip_to_box(g, box):
    """Geometrie auf die Kachel zuschneiden (Flaechen bleiben Flaechen, Linien bleiben Linien). Jedes Objekt, das mehrere Kacheln
    beruehrt, wird in jede dieser Kacheln geschrieben, damit sich die Kartenkacheln nicht ueberlappen: das Geraet zeichnet in
    ueberlappenden Bereichen nur eine Kachel, sonst fehlen z. B. Waelder an den Kachelraendern."""
    if g.geom_type in ("Polygon", "MultiPolygon") and not g.is_valid:
        g = shapely.make_valid(g)
    c = shapely.intersection(g, box)
    if c.is_empty:
        return None
    want = ("Polygon",) if g.geom_type in ("Polygon", "MultiPolygon") else ("LineString",)
    parts = [q for q in shapely.get_parts(c) if q.geom_type in want and not q.is_empty]
    if not parts:
        return None
    if want == ("Polygon",):
        return parts[0] if len(parts) == 1 else shapely.MultiPolygon(parts)
    return parts[0] if len(parts) == 1 else shapely.MultiLineString(parts)


BAUM_ZELLE = 70.0   # m: je Zelle (absolutes LV95-Raster) bleibt nur der Baum nahe der Mitte; entspricht etwa der Dichte der Garmin-Karte (ca. 165 Baeume/km2 statt 1300)


def wgs_tile_lv95(wgs):
    """WGS84-Rechteck (W S E N) -> (LV95-Polygon der Kachel, LV95-Huelle mit RAND_ROUTING)"""
    w_, s_, e_, n_ = wgs
    t = np.linspace(0, 1, 21)
    lon = np.concatenate([w_ + (e_ - w_) * t, np.full(21, e_), e_ - (e_ - w_) * t, np.full(21, w_)])
    lat = np.concatenate([np.full(21, s_), s_ + (n_ - s_) * t, np.full(21, n_), n_ - (n_ - s_) * t])
    x, y = FROM_WGS.transform(lon, lat)
    poly = shapely.Polygon(np.column_stack([x, y]))
    return poly, poly.buffer(RAND_ROUTING, join_style="mitre")


GARMIN_UNIT = 360 / 2 ** 24   # Grad: eine Garmin-Kartenkoordinate (24 Bit, ca. 1.7 x 2.4 m)


def von_kante_weg(coords, wgs):
    """Strassen-Stuetzpunkte, die weniger als eine Garmin-Einheit neben einer Kachelkante (irgendeiner im Raster) liegen, um
    1.5 Einheiten von der Kante wegschieben. Sonst rundet mkgmap sie genau auf die Kante; das Stueck in der Nachbarkachel hat
    dann die Laenge 0 und fehlt, und der Begrenzungsknoten hat kein Gegenstueck (keine Verbindung ueber die Kante). Die
    Verschiebung haengt nur von der Koordinate ab, beide Nachbarkacheln verschieben gleich."""
    W, S, E, N = wgs
    dx, dy = E - W, N - S
    out = []
    for lon, lat in coords:
        for v0, d in ((W, dx), (S, dy)):
            v = lon if v0 == W else lat
            g = v0 + round((v - v0) / d) * d
            r = (v - g) / GARMIN_UNIT
            if abs(r) < 1:
                v = g + (1.5 if r >= 0 else -1.5) * GARMIN_UNIT
                if v0 == W:
                    lon = v
                else:
                    lat = v
        out.append((lon, lat))
    return out


def einw_klasse(v):
    """EINWOHNERK (Klassen wie «2'000 bis 9'999», «< 20», «> 100'000») -> gross (ab 10'000), mittel (ab 100), klein"""
    try:
        n = int(re.sub(r"\D", "", str(v).split(" bis")[0]))
    except ValueError:
        return "klein"
    return "gross" if n >= 10000 else "mittel" if n >= 100 else "klein"


UFER_MIN = 150.0   # m: kuerzere Seeufer (Teiche) bekommen keine Uferlinie
# Flaechen, deren Umriss zusaetzlich als schwarze Linie gezeichnet wird (Zeichenerklaerung: Staumauer, Sportplatz, Flugplatzpiste)
UMRISS = {"staubaute": {"Staumauer", "Staudamm"}, "sportply": {"Sportplatz"}, "vbauteply": None}


def linien_in(g, box):
    """Linienteile von g innerhalb der Kachel"""
    c = shapely.intersection(g, box)
    return [q for q in shapely.get_parts(c) if q.geom_type == "LineString" and q.length > 0]


def convert_tile(shp_dir, bb_lv95, out_path, simplify, trees=False, variant="edge", grenzen=None, achsen=None, haupt=None,
                 routing=False, wgs=None, kantonsschilder=None):
    """routing=True: wgs=(W, S, E, N) ist die Kachel; Objekte werden nur grob zugeschnitten, mkgmap schneidet am <bounds>-Rechteck"""
    if routing:
        exact, tbox = wgs_tile_lv95(wgs)
        bb_lv95 = tbox.bounds
        w = Writer(out_path, bounds=wgs)
        wW, wS, wE, wN = wgs
        def in_tile(px, py):   # Punkte gehoeren zu genau einer Kachel (Test in WGS84, halboffen)
            lo, la = TO_WGS.transform(px, py)
            return wW <= lo < wE and wS <= la < wN
    else:
        w = Writer(out_path)
        tbox = shapely.box(*bb_lv95)
        def in_tile(px, py):
            return x0 <= px < x1 and y0 <= py < y1
    x0, y0, x1, y1 = bb_lv95
    counts = {}
    baeume = {}                       # Zelle -> (Abstand zur Zellenmitte, Punkt)
    for suffix, kind, extra in LAYERS + (LAYERS_TREES if trees else []):
        if variant == "fenix" and suffix in NUR_EDGE:
            continue
        p = os.path.join(shp_dir, f"swissTLM3D_TLM_{suffix}.shp")
        if not os.path.exists(p):
            print("fehlt:", p, file=sys.stderr); continue
        rb = tuple(bb_lv95)
        erlaubt = NUR.get(suffix)
        where = "OBJEKTART IN (" + ",".join("'" + a + "'" for a in sorted(erlaubt)) + ")" if erlaubt else None
        df = pyogrio.read_dataframe(p, bbox=rb, where=where)
        if routing and kind == "strasse":
            extra = dict(extra, **ROUTING_EXTRA)
        n = 0
        for row in df.itertuples(index=False):
            g = row.geometry
            if g is None or g.is_empty:
                continue
            g = shapely.force_2d(g)
            obj = getattr(row, "OBJEKTART", None)
            if kind == "baum":
                if in_tile(g.x, g.y):
                    c = (int(g.x // BAUM_ZELLE), int(g.y // BAUM_ZELLE))
                    d = (g.x % BAUM_ZELLE - BAUM_ZELLE / 2) ** 2 + (g.y % BAUM_ZELLE - BAUM_ZELLE / 2) ** 2
                    if c not in baeume or d < baeume[c][0]:
                        baeume[c] = (d, g)
                continue
            if variant == "fenix" and kind == "verbauung" and obj == "Gewaesserverbauung":
                continue
            # --- Sonderfaelle: Punkte aus Flaechen/Linien, Seen
            pt_kind = None
            if (kind == "areal" and obj == "Spitalareal") or (kind == "vareal" and obj == "Heliport"):
                if variant == "fenix":
                    continue
                pt_kind = "hpkt"
            elif kind == "ubahn" and obj == "Lift":
                pt_kind = "ulift"
            if pt_kind:
                rp = g.representative_point() if g.geom_type != "LineString" else g.interpolate(0.5, normalized=True)
                if in_tile(rp.x, rp.y):
                    emit_geom(w, to_wgs(rp), pt_kind, {"tlm_layer": pt_kind, "tlm_type": obj}); n += 1
                continue
            if kind == "see":
                ring = g.geom_type == "LineString" and g.is_closed and len(g.coords) >= 4
                if obj == "See":
                    if g.length >= UFER_MIN:
                        for q in linien_in(g, tbox):
                            emit_geom(w, to_wgs(q.simplify(simplify or 0.1, preserve_topology=True)), "ufer", {"tlm_layer": "ufer", "tlm_type": "Ufer"}); n += 1
                if ring and (obj == "Seeinsel" or (obj == "See" and str(getattr(row, "WSTAND_WE", "")) == "Wahr")):
                    c = clip_to_box(shapely.Polygon(g), tbox)
                    if c is not None:
                        tg = {"tlm_layer": "see", "tlm_type": obj}
                        if obj == "See":
                            tg["tlm_schwank"] = "Wahr"
                        emit_geom(w, to_wgs(c), kind, tg); n += 1
                continue
            if kind == "natpark":
                for q in linien_in(g.boundary, tbox):
                    emit_geom(w, to_wgs(q.simplify(simplify or 0.1, preserve_topology=True)), kind, {"tlm_layer": "natpark", "tlm_type": obj}); n += 1
                continue
            if kind in UMRISS and (UMRISS[kind] is None or obj in UMRISS[kind]) and g.geom_type in ("Polygon", "MultiPolygon"):
                for q in linien_in(g.boundary, tbox):
                    emit_geom(w, to_wgs(q), "umriss", {"tlm_layer": "umriss", "tlm_type": obj}); n += 1
            if kind in POINT_KINDS or g.geom_type == "Point":
                rp = g.representative_point()
                if not in_tile(rp.x, rp.y):
                    continue  # Punkte gehoeren zu genau einer Kachel
            elif routing and kind == "strasse":
                # Strassen im Routing-Build nicht zuschneiden: beide Nachbarkacheln muessen exakt dieselbe Geometrie haben,
                # sonst rundet mkgmap den Schnittpunkt an der Kachelkante verschieden und die Begrenzungsknoten passen nicht
                if not g.intersects(tbox):
                    continue
            else:
                g = clip_to_box(g, tbox)
                if g is None:
                    continue
            tags = {"tlm_layer": kind, "tlm_type": obj}
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
            if kind in OHNE_NAME:
                name = None
            if name:
                tags["name"] = name
            for fld, key in extra.items():
                v = getattr(row, fld, None)
                tags[f"tlm_{key}"] = einw_klasse(v) if key == "einwk" else v
            if simplify and g.geom_type != "Point":
                g = g.simplify(simplify, preserve_topology=True)   # behaelt Anfangs- und Endpunkte (dort liegen die Kreuzungen)
                if g.is_empty:
                    continue
            if routing and kind == "strasse":
                # auf cm runden, dann gemeinsame Knoten: swissTLM3D teilt Strassen an jeder Kreuzung mit exakt gleichem Endpunkt
                g = _t(g, lambda c: np.round(c, 2))
                for part in shapely.get_parts(to_wgs(g)):
                    w.way(von_kante_weg(part.coords, wgs), tags, share=True)
                n += 1
                continue
            emit_geom(w, to_wgs(g), kind, tags)
            n += 1
        counts[suffix] = n
    for _, pt in baeume.values():
        emit_geom(w, to_wgs(pt), "baum", {"tlm_layer": "baum", "tlm_type": "Einzelbaum"})
    counts["BAEUME"] = len(baeume)
    if grenzen and variant == "edge":
        box = tbox
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
    if variant == "edge" and (achsen or haupt or kantonsschilder):
        box = exact if routing else tbox
        pts = []
        if achsen:
            pts += [(x, y, "nsr", nr) for x, y, nr in schilder(achsen, "Stammachsen", "Strassennummer", "N", box, r"N\d+")]
        if haupt:
            pts += [(x, y, "hsr", nr) for x, y, nr in schilder(haupt, "MainRoads_RoadSegment", "RoadNumber", "H", box, r"\d+")]
        if kantonsschilder:
            pts += [(x, y, "ksr", "K" + nr) for x, y, nr in kantonsschilder_punkte(kantonsschilder, box)]
        for x, y, lay, nr in pts:
            emit_geom(w, to_wgs(shapely.Point(x, y)), lay, {"tlm_layer": lay, "tlm_type": nr})
        counts["SCHILDER"] = len(pts)
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


def print_grid_wgs(bbox, bx, by):
    """Routing-Kacheln (i j W S E N) in WGS84: bx x by Bloecke zu 2048 Garmin-Einheiten, Ursprung auf dem Blockraster.
    6 x 4 Bloecke sind etwa 20 x 19.5 km. NNNN = i*100+j wie beim LV95-Raster."""
    ox, oy = math.floor(CH_BBOX[0] / GARMIN_BLOCK), math.floor(CH_BBOX[1] / GARMIN_BLOCK)   # Rasterursprung (Bloecke)
    def idx(v, o, b):
        return int((v / GARMIN_BLOCK - o) // b)
    for i in range(idx(bbox[0], ox, bx), idx(bbox[2], ox, bx) + 1):
        for j in range(idx(bbox[1], oy, by), idx(bbox[3], oy, by) + 1):
            W, E = (ox + i * bx) * GARMIN_BLOCK, (ox + (i + 1) * bx) * GARMIN_BLOCK
            S, N = (oy + j * by) * GARMIN_BLOCK, (oy + (j + 1) * by) * GARMIN_BLOCK
            print(i, j, repr(W), repr(S), repr(E), repr(N))


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
    a.add_argument("--routing", action="store_true",
                   help="routingfaehige Ausgabe: gemeinsame Strassenknoten, Strassenattribute, <bounds> (braucht --wgs-tile)")
    a.add_argument("--wgs-tile", nargs=4, type=float, metavar=("W", "S", "E", "N"),
                   help="eine Routing-Kachel in WGS84 konvertieren (mit --routing und --out-file)")
    a.add_argument("--print-grid-wgs", nargs=2, type=int, metavar=("BX", "BY"),
                   help="Routing-Kachelliste (WGS84, BX x BY Bloecke zu 2048 Garmin-Einheiten) fuer --bbox ausgeben und beenden")
    a.add_argument("--trees", action="store_true", help="Einzelbaeume als Punkte mitschreiben (gross)")
    a.add_argument("--variant", choices=VARIANTS, default="edge", help="edge: mehr Namen und Grenzen; fenix: nur Hoehenpunkte")
    a.add_argument("--achsen", help="ASTRA-Nationalstrassenachsen (GDB, Layer Stammachsen) fuer die Schilder, nur Variante edge")
    a.add_argument("--haupt", help="ASTRA-Hauptstrassennetz (GDB, Layer MainRoads_RoadSegment) fuer die Schilder, nur Variante edge")
    a.add_argument("--kantonsschilder", help="CSV (x,y,nr) der Strassenschilder der uebrigen Hauptstrassen (scripts/kantonsschilder.py), nur Variante edge")
    a.add_argument("--grenzen", help="swissBOUNDARIES3D-GeoPackage (Layer tlm_hoheitsgrenze), nur Variante edge")
    o = a.parse_args()
    if o.print_grid:
        print_grid(o.bbox or CH_BBOX, o.print_grid)
        return
    if o.print_grid_wgs:
        print_grid_wgs(o.bbox or CH_BBOX, *o.print_grid_wgs)
        return
    if o.wgs_tile:
        if not o.routing:
            a.error("--wgs-tile nur zusammen mit --routing")
        c = convert_tile(o.shp, None, o.out_file, o.simplify, o.trees, o.variant, o.grenzen, o.achsen, o.haupt, routing=True, wgs=tuple(o.wgs_tile), kantonsschilder=o.kantonsschilder)
        print(o.out_file, f"{os.path.getsize(o.out_file)/1e6:.1f} MB", sum(c.values()), "Objekte", flush=True)
        return
    if o.lv95_tile:
        c = convert_tile(o.shp, tuple(o.lv95_tile), o.out_file, o.simplify, o.trees, o.variant, o.grenzen, o.achsen, o.haupt, kantonsschilder=o.kantonsschilder)
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
            c = convert_tile(o.shp, bb, path, o.simplify, o.trees, o.variant, o.grenzen, o.achsen, o.haupt, kantonsschilder=o.kantonsschilder)
            print(path, f"{os.path.getsize(path)/1e6:.1f} MB", c, flush=True)


if __name__ == "__main__":
    main()
