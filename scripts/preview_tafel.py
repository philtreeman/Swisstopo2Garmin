#!/usr/bin/env python3
"""Tafel aller Signaturen von SwissTOPO Vector: je Objektart ein Muster (Linie, Flaeche, Punkt) mit den Tags, die der Konverter schreibt,
ausgewertet mit dem echten Stil (style_eval.py) und der TYP-Datei (preview_legende.py). Optional daneben Ausschnitte der Zeichenerklaerung.
  preview_tafel.py <typ.txt> <out-prefix> --variant edge|fenix [--legende-dir DIR]
Erzeugt <out-prefix>_linien.png, _flaechen.png, _punkte.png (und mit --legende-dir <out-prefix>_vergleich_*.png, Legende links)."""
import argparse, os, sys, tempfile
from PIL import Image, ImageDraw
from pyproj import Transformer
import preview_legende as PL

FROM = Transformer.from_crs(2056, 4326, always_xy=True)
X0, Y0 = 2665000, 1259000

B = dict(tlm_layer="bahn", tlm_type="Normalspur", tlm_kunst="Keine", tlm_anschlussg="Falsch", tlm_verkehrsmi="Bahn")
U = lambda t, **k: dict(tlm_layer="ubahn", tlm_type=t, tlm_ausser="Falsch", **k)
F = lambda t, v="Oberirdisch": dict(tlm_layer="fluss", tlm_type=t, tlm_verlauf=v)
LINIEN = [
    ("Normalspurbahn", B), ("Schmalspurbahn", dict(B, tlm_type="Schmalspur")), ("Kleinbahn", dict(B, tlm_type="Kleinbahn")),
    ("Anschlussgleis", dict(B, tlm_anschlussg="Wahr")), ("Tram", dict(B, tlm_verkehrsmi="Tram")),
    ("Bahn Tunnel", dict(B, tlm_kunst="Tunnel")), ("Bahn Galerie", dict(B, tlm_kunst="Galerie")),
    ("Luftseilbahn", U("Luftseilbahn")), ("Gondelbahn", U("Gondelbahn")), ("Sesselbahn", U("Sesselbahn")),
    ("Transportseilbahn", U("Transportseil")), ("Seilbahn ausser Betrieb", dict(U("Luftseilbahn"), tlm_ausser="Wahr")),
    ("Skilift", U("Skilift")), ("Foerderband", U("Foerderband")),
    ("Bach, Fluss", F("Fliessgewaesser")), ("Wasserfall", F("Fliessgewaesser", "Wasserfall")), ("Suone, Bisse", F("Bisse Suone")),
    ("Druckleitung", F("Druckleitung einfach")), ("Druckstollen", F("Druckstollen", "Unterirdisch bestimmt")), ("Trockenrinne", F("Trockenrinne")),
    ("Gewaesserverbauung", dict(tlm_layer="verbauung", tlm_type="Gewaesserverbauung")), ("Hafensteg", dict(tlm_layer="vbautelin", tlm_type="Hafensteg")),
    ("Faehre", dict(tlm_layer="schiff", tlm_type="Autofaehre")), ("Seeufer", dict(tlm_layer="ufer", tlm_type="Ufer")),
    ("Landesgrenze", dict(tlm_layer="grenze", tlm_type="Landesgrenze")), ("Kantonsgrenze", dict(tlm_layer="grenze", tlm_type="Kantonsgrenze")),
    ("Bezirksgrenze", dict(tlm_layer="grenze", tlm_type="Bezirksgrenze")), ("Gemeindegrenze", dict(tlm_layer="grenze", tlm_type="Gemeindegrenze")),
    ("Nationalparkgrenze", dict(tlm_layer="natpark", tlm_type="Nationalpark")),
    ("Hochspannungsleitung", dict(tlm_layer="leitung", tlm_type="Stromleitung")),
    ("Mauer", dict(tlm_layer="mauer", tlm_type="Mauer")), ("Trockenmauer", dict(tlm_layer="verbauung", tlm_type="Trockenmauer")),
    ("Lawinenverbauung", dict(tlm_layer="verbauung", tlm_type="Schutzverbauung")),
    ("Laufbahn", dict(tlm_layer="sportlin", tlm_type="Laufbahn")), ("Skisprunganlage", dict(tlm_layer="sportlin", tlm_type="Skisprungschanze")),
    ("Rodelbahn", dict(tlm_layer="sportlin", tlm_type="Rodelbahn")), ("Schiessstand", dict(tlm_layer="sportlin", tlm_type="Scheibenstand")),
    ("Umriss (Staumauer, Piste)", dict(tlm_layer="umriss", tlm_type="Staumauer")),
]
BB = lambda t: dict(tlm_layer="bb", tlm_type=t)
FLAECHEN = [
    ("Wald", BB("Wald")), ("Wald offen", BB("Wald offen")), ("Gebueschwald", BB("Gebueschwald")), ("Gehoelz, Hecke", BB("Gehoelzflaeche")),
    ("Obstanlage", dict(tlm_layer="areal", tlm_type="Obstanlage")), ("Baumschule", dict(tlm_layer="areal", tlm_type="Baumschule")),
    ("Reben", dict(tlm_layer="areal", tlm_type="Reben")), ("Feuchtgebiet", BB("Feuchtgebiet")),
    ("Fels", BB("Fels")), ("Felsbloecke", BB("Felsbloecke")), ("Geroell", BB("Lockergestein")), ("Gletscher", BB("Gletscher")),
    ("See", BB("Stehende Gewaesser")), ("Flussflaeche", BB("Fliessgewaesser")),
    ("See, wechselnder Wasserstand", dict(tlm_layer="see", tlm_type="See", tlm_schwank="Wahr")), ("Seeinsel", dict(tlm_layer="see", tlm_type="Seeinsel")),
    ("Park, Freizeit, Camping, Golf", dict(tlm_layer="freizeit", tlm_type="Golfplatzareal")), ("Friedhof", dict(tlm_layer="areal", tlm_type="Friedhof")),
    ("Schrebergarten", dict(tlm_layer="areal", tlm_type="Schrebergartenareal")), ("Deponie", dict(tlm_layer="areal", tlm_type="Deponieareal")),
    ("Gebaeude", dict(tlm_layer="gebaeude", tlm_type="Gebaeude")), ("Kapelle, Turm, Tank", dict(tlm_layer="gebaeude", tlm_type="Lagertank")),
    ("Offenes Gebaeude, Treibhaus", dict(tlm_layer="gebaeude", tlm_type="Treibhaus")),
    ("Staumauer", dict(tlm_layer="staubaute", tlm_type="Staumauer")), ("Staudamm", dict(tlm_layer="staubaute", tlm_type="Staudamm")),
    ("Wehr", dict(tlm_layer="staubaute", tlm_type="Wehr")), ("Flugplatz Hartbelagpiste", dict(tlm_layer="vbauteply", tlm_type="Hartbelagpiste")),
    ("Flugplatz Graspiste", dict(tlm_layer="vbauteply", tlm_type="Graspiste")),
]
PUNKTE = [
    ("Quelle", dict(tlm_layer="eo", tlm_type="Quelle")), ("Brunnen", dict(tlm_layer="eo", tlm_type="Brunnen")),
    ("Wasserversorgung", dict(tlm_layer="eo", tlm_type="Wasserversorgung")), ("Gipfelkreuz, Bildstock", dict(tlm_layer="eo", tlm_type="Gipfelkreuz")),
    ("Denkmal", dict(tlm_layer="eo", tlm_type="Denkmal")), ("Triangulationspyramide", dict(tlm_layer="eo", tlm_type="Triangulationspyramide")),
    ("Hoehle", dict(tlm_layer="eo", tlm_type="Grotte, Hoehle")), ("Spital", dict(tlm_layer="hpkt", tlm_type="Spitalareal")),
    ("Heliport", dict(tlm_layer="hpkt", tlm_type="Heliport")), ("Windturbine", dict(tlm_layer="wpkt", tlm_type="Windturbine")),
    ("Antenne klein", dict(tlm_layer="wpkt", tlm_type="Antenne klein")), ("Antenne gross", dict(tlm_layer="wpkt", tlm_type="Antenne gross")),
    ("Lift", dict(tlm_layer="ulift", tlm_type="Lift")), ("Durchfahrtssperre", dict(tlm_layer="sinfo", tlm_type="Durchfahrtssperre")),
    ("Raststaette", dict(tlm_layer="sinfo", tlm_type="Raststaette")), ("Autoverlad", dict(tlm_layer="sinfo", tlm_type="Verladestation")),
    ("Gipfel mit Hoehe", dict(tlm_layer="namepkt", tlm_type="Gipfel", name="Wildhorn 3250")), ("Pass", dict(tlm_layer="namepkt", tlm_type="Pass", name="Hohtuerli 2778")),
    ("Einzelbaum", dict(tlm_layer="baum", tlm_type="Einzelbaum")),
    ("Ort > 10000", dict(tlm_layer="ort", tlm_type="Ort", tlm_einwk="gross", name="Baden")), ("Ort 100-9999", dict(tlm_layer="ort", tlm_type="Ort", tlm_einwk="mittel", name="Ennetbaden")),
    ("Ort < 100", dict(tlm_layer="ort", tlm_type="Ort", tlm_einwk="klein", name="Chlistalde")), ("Quartier", dict(tlm_layer="ort", tlm_type="Quartier", name="Allmend")),
    ("Grossregion", dict(tlm_layer="gebiet", tlm_type="Grossregion", name="Mittelland")), ("Landschaftsname", dict(tlm_layer="gebiet", tlm_type="Landschaftsname", name="Kientaeli")),
    ("Gebiet", dict(tlm_layer="gebiet", tlm_type="Gebiet", name="Pfyn")), ("Flurname", dict(tlm_layer="flur", tlm_type="Flurname", name="Grundwald")),
    ("Schild Nationalstrasse", dict(tlm_layer="nsr", tlm_type="N1")), ("Schild Hauptstrasse", dict(tlm_layer="hsr", tlm_type="H21")),
    ("Schild Kantonsstrasse", dict(tlm_layer="ksr", tlm_type="K279")),
]
ROW, WID, LAB = 16, 90, 190   # Zeilenhoehe, Musterbreite (m = Pixel bei mpp 1), Platz fuer die Beschriftung


def osm(items, kind, path):
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<osm version="0.6">']
    n = [0]; wid = [100000]
    def node(x, y, tags=None):
        n[0] += 1; lon, lat = FROM.transform(x, y)
        t = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in (tags or {}).items())
        out.append(f'<node id="{n[0]}" lat="{lat:.7f}" lon="{lon:.7f}">{t}</node>' if t else f'<node id="{n[0]}" lat="{lat:.7f}" lon="{lon:.7f}"/>'); return n[0]
    ways = []
    for i, (lab, tags) in enumerate(items):
        y = Y0 - i * ROW
        if kind == "linie":
            a, b = node(X0, y), node(X0 + WID, y); ways.append(([a, b], tags))
        elif kind == "flaeche":
            ids = [node(X0, y + 6), node(X0 + WID, y + 6), node(X0 + WID, y - 6), node(X0, y - 6)]; ways.append((ids + [ids[0]], tags))
        else:
            node(X0 + 20, y, tags)
    for ids, tags in ways:
        wid[0] += 1
        out.append(f'<way id="{wid[0]}">' + "".join(f'<nd ref="{i}"/>' for i in ids) + "".join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items()) + "</way>")
    out.append("</osm>"); open(path, "w").write("\n".join(out))


def sheet(items, kind, typ, variant, outpng):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.osm"); osm(items, kind, p)
        box = (X0 - LAB, Y0 - len(items) * ROW + ROW / 2, X0 + WID + 30, Y0 + ROW / 2)
        PL.render(p, typ, outpng, variant, 1.0, box, labels=True)
    im = Image.open(outpng).convert("RGB"); dr = ImageDraw.Draw(im); f = PL.font(11)
    for i, (lab, _) in enumerate(items):
        dr.text((6, i * ROW + 2), lab, fill=(0, 0, 0), font=f)
    im.save(outpng); return im


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("typ"); ap.add_argument("prefix"); ap.add_argument("--variant", default="edge"); ap.add_argument("--legende-dir")
    o = ap.parse_args()
    ims = {}
    for kind, items, name in (("linie", LINIEN, "linien"), ("flaeche", FLAECHEN, "flaechen"), ("punkt", PUNKTE, "punkte")):
        ims[name] = sheet(items, kind, o.typ, o.variant, f"{o.prefix}_{name}.png")
    if o.legende_dir:
        crops = {"linien": ["c02R0.png", "c03R1.png", "c03L0.png"], "flaechen": ["c03R0.png", "c04L0.png", "c04L1.png", "c03L1.png"],
                 "punkte": ["c03L0.png", "c02R1.png", "c03L1.png"]}
        Hh = 1000
        for name, files in crops.items():
            right = ims[name]; k = max(1, Hh // right.height)
            right = right.resize((right.width * k, right.height * k), Image.NEAREST)
            left = [Image.open(os.path.join(o.legende_dir, f)).convert("RGB") for f in files]
            left = [l.resize((int(l.width * Hh / l.height), Hh)) for l in left]
            Wl = sum(l.width for l in left)
            sheetim = Image.new("RGB", (Wl + 30 + right.width, max(Hh, right.height)), (255, 255, 255))
            x = 0
            for l in left: sheetim.paste(l, (x, 0)); x += l.width
            sheetim.paste(right, (Wl + 30, 0))
            sheetim.save(f"{o.prefix}_vergleich_{name}.png")
    print("ok")


if __name__ == "__main__":
    main()
