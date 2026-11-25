#!/usr/bin/env python3
"""Erzeugt die TYP-Datei fuer SwissTOPO Vector (mkgmap/vector/typ/swisstopo_vector.txt).

Alle Farben, Muster und Symbole folgen der swisstopo-Zeichenerklaerung «Landeskarten 1:10 000, 1:25 000 und 1:50 000»
(Stand 2026-11-24, siehe vector_palette.py). Die Typ-Codes passen zu mkgmap/vector/style/{lines,polygons,points} und den inc/-Dateien.
Die vier Dateien (edge, fenix, edge_swisstopo, fenix_swisstopo) sind bis auf die Family-ID gleich; Unterschiede zwischen Edge und
Fenix (Details, Muster erst in feinen Stufen, keine Punktsymbole) stehen im mkgmap-Style, nicht in der TYP-Datei.

Aufruf: make_vector_typ.py [VARIANTE] [--fid N --out DATEI] [--routing]
  --fid/--out: andere Family-ID (z. B. 3930 fuer den Routing-Test) in eine eigene Datei; die Dateien der bestehenden
  Varianten bleiben unveraendert. --routing: zusaetzlich die unsichtbaren routbaren Linien 0x13/0x16
  (mkgmap/vector/style/inc/routing_lines).
"""
import argparse, os, sys

_a = argparse.ArgumentParser()
_a.add_argument("variant", nargs="?", default="edge", choices=("edge", "fenix", "edge_swisstopo", "fenix_swisstopo"))
_a.add_argument("--fid", type=int, help="Family-ID (Standard: 3900 edge, 3901 fenix)")
_a.add_argument("--out", help="Ausgabedatei (Standard: mkgmap/vector/typ/swisstopo_vector_<variante>.txt)")
_a.add_argument("--routing", action="store_true", help="unsichtbare routbare Linien 0x13 und 0x16 mitschreiben")
_o = _a.parse_args()
VARIANT = _o.variant   # edge, fenix (die *_swisstopo-Namen bleiben als Alias fuer dieselbe Darstellung)
BASIS = VARIANT.split("_")[0]
FID = _o.fid or (3900 if BASIS == "edge" else 3901)
OUT = _o.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "vector", "typ", f"swisstopo_vector_{VARIANT}.txt")

from vector_palette import *  # noqa: F401,F403  (Farben, gemeinsam mit preview_vector.py)
from vector_patterns import PATTERNS
import vector_shields


def solid_poly(t, name, col, extra=""):
    return f'[_polygon]\nType={t}\nString1=0x04,{name}\n{extra}Xpm="0 0 1 0"\n"1 c {col}"\n[end]\n'


def pattern_poly(t):
    name, bg, fg, rows = PATTERNS[t]
    body = "\n".join('"' + r + '"' for r in rows)
    return f'[_polygon]\nType={t}\nString1=0x04,{name}\nXpm="32 32 2 1"\n"b c {bg}"\n"f c {fg}"\n{body}\n[end]\n'


def solid_line(t, name, fill, w, border=None, bw=1, extra=""):
    if border:
        return f'[_line]\nType={t}\nString1=0x04,{name}\n{extra}LineWidth={w}\nBorderWidth={bw}\nXpm="0 0 2 0"\n"1 c {fill}"\n"2 c {border}"\n[end]\n'
    return f'[_line]\nType={t}\nString1=0x04,{name}\n{extra}LineWidth={w}\nXpm="0 0 1 0"\n"1 c {fill}"\n[end]\n'


def dash_line(t, name, col, on, off, h=2):
    """gestrichelte Linie; die durchsichtige Farbe muss zuerst in der Farbtabelle stehen (sonst bricht der TYP-Compiler ab)"""
    row = ("1" * on + "3" * off) * 32
    row = '"' + row[:32] + '"'
    rows = "\n".join([row] * h)
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 {h} 2 1"\n"3 c none"\n"1 c {col}"\n{rows}\n[end]\n'


def edge_dots_line(t, name, col, h, on=1, off=2):
    """Tunnel wie auf der Garmin-Karte: nur die beiden Raender der Strasse als feine Punktreihe, die Mitte bleibt durchsichtig"""
    dots = '"' + (("1" * on + "3" * off) * 32)[:32] + '"'
    gap = '"' + "3" * 32 + '"'
    rows = "\n".join([dots] + [gap] * (h - 2) + [dots])
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 {h} 2 1"\n"3 c none"\n"1 c {col}"\n{rows}\n[end]\n'


def gallery_line(t, name, fill, h):
    """Galerie / gedeckte Bruecke (Zeichenerklaerung): Strassenfarbe, schwarze Raender, Querstriche alle 4 Pixel"""
    edge = '"' + "2" * 32 + '"'
    mid = '"' + ("2111" * 8) + '"'
    rows = "\n".join([edge] + [mid] * (h - 2) + [edge])
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 {h} 2 1"\n"1 c {fill}"\n"2 c #000000"\n{rows}\n[end]\n'


def treppe_line():
    """Treppe (Zeichenerklaerung): schwarze Doppellinie mit rot punktierter Mitte"""
    black = '"' + "2" * 32 + '"'
    dots = '"' + ("13" * 16) + '"'
    return f'[_line]\nType=0x10e09\nString1=0x04,Treppe\nXpm="32 3 3 1"\n"3 c none"\n"1 c {TREPPE}"\n"2 c #000000"\n{black}\n{dots}\n{black}\n[end]\n'


def rail_line(t, name):
    a = '"' + "1" * 32 + '"'
    b = '"' + ("1" * 6 + "2" * 6)[:32] + '"'
    b = '"' + (("1" * 6 + "2" * 6) * 3)[:32] + '"'
    return f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 3 2 1"\n"1 c {WEG}"\n"2 c #FFFFFF"\n{a}\n{b}\n{a}\n[end]\n'




def BLAU_NAME(font):
    """Beschriftung von Gewaessern blau (Zeichenerklaerung: Fluesse, Seen, Gletscher in #008AD2)"""
    return f"FontStyle={font}\nCustomColor=Day\nDayCustomColor={WASSER}\n"


def pat_line(t, name, rows, cols, extra=""):
    """Linie aus einem 32 x h-Muster; rows = Zeichenketten (Laenge 32), cols = {Zeichen: Farbe}, die durchsichtige Farbe 'n' steht zuerst"""
    keys = sorted(cols, key=lambda k: (k != "n", k))
    body = "\n".join('"' + r + '"' for r in rows)
    tab = "\n".join(f'"{k} c {"none" if cols[k] is None else cols[k]}"' for k in keys)
    return f'[_line]\nType={t}\nString1=0x04,{name}\n{extra}Xpm="32 {len(rows)} {len(keys)} 1"\n{tab}\n{body}\n[end]\n'


def periodic(unit, n=32):
    return (unit * (n // len(unit) + 1))[:n]


def quer_line(t, name, col, h=5, abstand=8):
    """Linie mit Querstrichen (Skilift, Druckleitung): Mittellinie mit senkrechten Strichen alle 'abstand' Pixel"""
    tick = periodic("1" + "n" * (abstand - 1)); full = "1" * 32
    mid = h // 2
    rows = [tick if r != mid else full for r in range(h)]
    return pat_line(t, name, rows, {"n": None, "1": col})


def hdr_text():
    return f"""; -*- coding: cp1252 -*-
; TYP fuer SwissTOPO Vector (Family-ID {FID}), erzeugt von scripts/make_vector_typ.py
[_id]
ProductCode=1
FID={FID}
CodePage=1252
[end]

[_drawOrder]
{chr(10).join(f"Type={t},{lvl}" for t, lvl in DRAW_ORDER)}
[end]

"""


# Zeichenreihenfolge der Flaechen (unten nach oben)
DRAW_ORDER = [("0x4b", 1), ("0x19", 2), ("0x1a", 2), ("0x10e04", 2), ("0x10e06", 2), ("0x4e", 2), ("0x10e08", 2), ("0x10e09", 2),
              ("0x4f", 2), ("0x50", 2), ("0x10e01", 3), ("0x10e02", 3), ("0x51", 3), ("0x53", 3), ("0x52", 3), ("0x10e10", 3), ("0x10e11", 3), ("0x10e00", 3),
              ("0x3f", 4), ("0x10e0f", 4), ("0x10e03", 4), ("0x10e0e", 4),
              ("0x10e0c", 5), ("0x10e0d", 5), ("0x10e07", 5), ("0x10e0b", 5), ("0x10e05", 6), ("0x10e0a", 6)]


def punkt(t, name, art, farben, font=None, farbe=None):
    """Punktsymbol aus Textzeilen; art = Zeilen, farben = {Zeichen: Farbe}, '.' ist durchsichtig (steht zuerst in der Farbtabelle)"""
    cols = {".": None, **farben}
    keys = list(cols)
    idx = {k: str(i + 1) if i < 9 else chr(ord("a") + i - 9) for i, k in enumerate(keys)}
    rows = "\n".join('"' + "".join(idx[c] for c in r) + '"' for r in art)
    tab = "\n".join(f'"{idx[k]} c {"none" if cols[k] is None else cols[k]}"' for k in keys)
    fnt = f"FontStyle={font}\nCustomColor=Day\nDayCustomColor={farbe or '#000000'}\n" if font else ""
    return f'[_point]\nType={t}\nString1=0x04,{name}\n{fnt}DayXpm="{len(art[0])} {len(art)} {len(keys)} 1"\n{tab}\n{rows}\n[end]\n'


def text_punkt(t, name, font, farbe="#000000"):
    return punkt(t, name, ["..", ".."], {"k": farbe}, font, farbe)


K, B, R, G, W, L = SCHWARZ, WASSER, BAHN, GRUEN, WEISS, LEITUNG
parts = [
    # ---------------- Flaechen
    solid_poly("0x4b", "Untergrund", BG),
    solid_poly("0x19", "Park, Freizeit, Sport", PARK),
    pattern_poly("0x1a"), pattern_poly("0x10e04"),
    solid_poly("0x10e06", "Deponie", DEPONIE),
    pattern_poly("0x4e"), pattern_poly("0x10e08"), pattern_poly("0x10e09"), pattern_poly("0x4f"),
    solid_poly("0x50", "Wald", WALD),
    pattern_poly("0x10e01"), pattern_poly("0x10e02"), pattern_poly("0x51"), pattern_poly("0x53"), pattern_poly("0x52"), pattern_poly("0x10e10"), pattern_poly("0x10e11"),
    pattern_poly("0x10e00"),
    solid_poly("0x3f", "See", WASSER_FL, BLAU_NAME("NormalFont")),
    solid_poly("0x10e0f", "See mit wechselndem Wasserstand", WASSER_SCHWANK, BLAU_NAME("NormalFont")),
    solid_poly("0x10e03", "Flussflaeche", WASSER_FLUSS),
    solid_poly("0x10e0e", "Seeinsel", BG),
    solid_poly("0x10e0c", "Flugplatz Hartbelagpiste", WEISS),
    solid_poly("0x10e0d", "Flugplatz Graspiste", PARK),
    solid_poly("0x10e07", "Staumauer", STAUMAUER),
    solid_poly("0x10e0b", "Staudamm", "#E3E3E3"),
    solid_poly("0x10e05", "Gebaeude", GEBAEUDE),
    pattern_poly("0x10e0a"),
    # ---------------- Strassen nach der swisstopo-Zeichenerklaerung (1:25 000): Farbe nach Verkehrsbedeutung (VERKEHRSBD), schwarzer Rand
    solid_line("0x01", "Autobahn, Autostrasse", AUTOBAHN[0], 6, AUTOBAHN[1]),
    solid_line("0x02", "Durchgangsstrasse", DURCHGANG[0], 5, DURCHGANG[1]),
    solid_line("0x03", "Verbindungsstrasse", VERBINDUNG[0], 4, VERBINDUNG[1]),
    solid_line("0x04", "Strasse 6 m", STRASSE[0], 4, STRASSE[1]),
    solid_line("0x05", "Strasse 8 und 10 m", HAUPT[0], 5, HAUPT[1]),
    solid_line("0x06", "Strasse 3 und 4 m", NEBEN[0], 3, NEBEN[1]),
    solid_line("0x07", "Strasse Naturbelag", NATUR, 1),
    # Wege: 2 m-Weg Hartbelag Doppellinie (0x0a), Naturbelag und Steg feine Volllinie (0x0b), 1 m-Weg gestrichelt, markierte Spur punktiert
    solid_line("0x0a", "Weg 2 m Hartbelag", "#FFFFFF", 2, "#000000"),
    solid_line("0x0b", "Weg 2 m Naturbelag, Steg", SCHWARZ, 1),
    dash_line("0x10e01", "Weg 1 m", SCHWARZ, 5, 3, h=2),
    dash_line("0x10e08", "Markierte Spur", SCHWARZ, 1, 2, h=2),
    treppe_line(),
    dash_line("0x10e00", "Klettersteig", KLETTERSTEIG, 4, 4, h=2),
    solid_line("0x10e06", "Schutzverbauung", SCHWARZ, 2),
    # Tunnel: immer schwarz gestrichelt ohne Farbe; Strassen bis 4 m nur eine gestrichelte Linie
    edge_dots_line("0x10e10", "Autobahn im Tunnel", "#000000", 6, 4, 4),
    edge_dots_line("0x10e11", "Strasse 8 und 10 m im Tunnel", "#000000", 5, 4, 4),
    edge_dots_line("0x10e12", "Strasse 6 m im Tunnel", "#000000", 4, 4, 4),
    dash_line("0x10e13", "Strasse 3 und 4 m im Tunnel", "#000000", 4, 4, h=1),
    # Bruecken: Strassenfarbe nach Verkehrsbedeutung, kraeftiger schwarzer Rand (2 px)
    solid_line("0x10e15", "Autobahn auf Bruecke", AUTOBAHN[0], 6, "#000000", 2),
    solid_line("0x10e16", "Strasse 8 und 10 m auf Bruecke", HAUPT[0], 5, "#000000", 2),
    solid_line("0x10e17", "Strasse 6 m auf Bruecke", STRASSE[0], 4, "#000000", 2),
    solid_line("0x10e18", "Strasse 3 und 4 m auf Bruecke", NEBEN[0], 3, "#000000", 2),
    solid_line("0x10e1a", "Durchgangsstrasse auf Bruecke", DURCHGANG[0], 5, "#000000", 2),
    solid_line("0x10e1b", "Verbindungsstrasse auf Bruecke", VERBINDUNG[0], 4, "#000000", 2),
    # Galerien und gedeckte Bruecken: Strassenfarbe, Querstriche
    gallery_line("0x10e1c", "Galerie Durchgangsstrasse", DURCHGANG[0], 7),
    gallery_line("0x10e1d", "Galerie Verbindungsstrasse", VERBINDUNG[0], 6),
    gallery_line("0x10e1e", "Galerie Strasse", STRASSE[0], 6),
    gallery_line("0x10e1f", "Galerie Autobahn, Autostrasse", AUTOBAHN[0], 8),
    # ---------------- Bahn (rot): Normalspur 3 px, Schmalspur 2 px, Anschlussgleis/Tram 1 px, Tunnel gestrichelt 4/3, Galerie mit Kaestchenreihe
    solid_line("0x14", "Normalspurbahn", BAHN, 3),
    solid_line("0x11300", "Schmalspurbahn, Kleinbahn", BAHN, 2),
    solid_line("0x11301", "Anschlussgleis, Tram", BAHN, 1),
    dash_line("0x10e14", "Bahn im Tunnel", BAHN, 4, 3, h=2),
    pat_line("0x11302", "Bahn in Galerie", ["1" * 32] + [periodic("1nnn")] * 3 + ["1" * 32], {"n": None, "1": BAHN}),
    # ---------------- Seilbahnen
    solid_line("0x11303", "Luftseilbahn", BAHN, 2),
    solid_line("0x11304", "Gondelbahn, Sesselbahn", BAHN, 1),
    solid_line("0x11305", "Transportseilbahn, ausser Betrieb", SCHWARZ, 1),
    quer_line("0x11306", "Skilift", SKILIFT, 5, 8),
    pat_line("0x11307", "Foerderband", [periodic("1nnnnnnn"), "1" * 32, periodic("1nnnnnnn")], {"n": None, "1": SCHWARZ}),
    # ---------------- Gewaesser
    solid_line("0x18", "Bach, Fluss, Suone", WASSER, 1, extra=BLAU_NAME("SmallFont")),
    dash_line("0x10e03", "Trockenrinne, Scheibenstand", SCHWARZ, 1, 2, h=1),
    quer_line("0x11308", "Druckleitung", WASSER, 5, 8),
    dash_line("0x11309", "Druckstollen", WASSER, 6, 3, h=1),
    solid_line("0x1130a", "Gewaesserverbauung", WASSER, 1),
    solid_line("0x1130b", "Hafensteg", SCHWARZ, 1),
    dash_line("0x1130c", "Faehre", SCHWARZ, 4, 4, h=1),
    solid_line("0x11315", "Seeufer", WASSER, 1, extra="FontStyle=NoLabel\n"),
    # ---------------- Mauern, Grenzen, Leitungen, Sportbauten
    solid_line("0x10e04", "Mauer", SCHWARZ, 2),
    dash_line("0x1130d", "Trockenmauer", SCHWARZ, 1, 2, h=1),
    solid_line("0x10e0a", "Landesgrenze", LANDESGRENZE, 2, GRENZBAND, 2),
    solid_line("0x10e0b", "Kantonsgrenze", LANDESGRENZE, 1, GRENZBAND, 1),
    solid_line("0x1130e", "Bezirksgrenze", GRENZBAND, 2),
    dash_line("0x10e0c", "Gemeindegrenze", GRENZBAND, 6, 3, h=2),
    solid_line("0x1130f", "Nationalparkgrenze", NATIONALPARK_BAND, 4, NATIONALPARK, 1),
    pat_line("0x11310", "Hochspannungsleitung", [periodic("1" * 9 + "nnn" + "1" + "nnn")] * 2, {"n": None, "1": LEITUNG}),
    solid_line("0x11311", "Umriss, Laufbahn", SCHWARZ, 1),
    pat_line("0x11312", "Skisprunganlage", ["1" * 32, "n" * 32, "1" * 32], {"n": None, "1": SCHWARZ}),
    solid_line("0x11313", "Rodelbahn", SCHWARZ, 2),
    # ---------------- Punkte
    punkt("0x10f00", "Einzelbaum", [".g.", "ggg", ".g."], {"g": GRUEN}),
    punkt("0x11300", "Quelle", [".bbb.", "b....", "b....", "b....", ".bbb."], {"b": B}),
    punkt("0x11301", "Brunnen", [".bbb.", "b...b", "b...b", "b...b", ".bbb."], {"b": B}),
    punkt("0x11302", "Wasserversorgung", ["bbbbb", "b...b", "b.b.b", "b...b", "bbbbb"], {"b": B}),
    punkt("0x11303", "Gipfelkreuz, Bildstock", ["..k..", "kkkkk", "..k..", "..k..", "..k.."], {"k": K}),
    punkt("0x11304", "Denkmal", ["..k..", ".k.k.", "kkkkk", "..k..", ".k.k.", "kkkkk"], {"k": K}),
    punkt("0x11305", "Triangulationspyramide", ["..k..", ".k.k.", "k.k.k", "kkkkk"], {"k": K}),
    punkt("0x11306", "Hoehle", [".kkk.", "k...k", "k...k"], {"k": K}),
    punkt("0x11307", "Spital", ["lllllll", "lwlllwl", "lwlllwl", "lwwwwwl", "lwlllwl", "lwlllwl", "lllllll"], {"l": L, "w": W}),
    punkt("0x11308", "Heliport", ["..kkkkk..", ".kk...kk.", "kk.k.k.kk", "k..k.k..k", "k..kkk..k", "k..k.k..k", "kk.k.k.kk", ".kk...kk.", "..kkkkk.."], {"k": K}),
    punkt("0x11309", "Windturbine", ["k.....k", ".k...k.", "..k.k..", "...k...", "...k...", "...k...", "..kkk.."], {"k": K}),
    punkt("0x1130a", "Lift", ["rrrr", "r..r", "r..r", "rrrr"], {"r": R}),
    punkt("0x1130b", "Durchfahrtssperre", [".r.", "rrr", ".r."], {"r": R}),
    punkt("0x1130c", "Antenne klein", ["kkk", "k.k", "kkk"], {"k": K}),
    punkt("0x1130d", "Antenne gross", [".kkk.", "k...k", "k.k.k", "k...k", ".kkk."], {"k": K}),
    punkt("0x1130e", "Raststaette", ["kkkkkkk", "kwwkwwk", "kwwkwwk", "kwwkwwk", "kwwkwwk", "kwwkwwk", "kkkkkkk"], {"k": K, "w": W}),
    punkt("0x1130f", "Autoverlad", ["rrrrr", "rwwwr", "rwwwr", "rwwwr", "rrrrr"], {"r": R, "w": W}),
]
# Gipfel, Huegel und Paesse (Hoehenkote): schwarzes Kreuz, Name mit Hoehe in kleiner Schrift
for t, name in (("0x6616", "Gipfel und Huegel"), ("0x6615", "Pass")):
    parts.append(punkt(t, name, ["k...k", ".k.k.", "..k..", ".k.k.", "k...k"], {"k": K}, "SmallFont", "#000000"))
# Strassenschilder der Nationalstrassen (Symbole aus vector_shields.py)
parts.append(vector_shields.typ_eintraege())
# Ortsnamen und Flur-/Gebietsnamen: reiner Text (Symbol durchsichtig), schwarz; Schriftgroesse nach Einwohnerzahl bzw. Namensart
for t, name, font in (("0x6600", "Flur- und Gelaendename", "SmallFont"), ("0x0a00", "Ort ab 10000 Einwohner", "LargeFont"),
                      ("0x0b00", "Ort ab 100 Einwohner", "NormalFont"), ("0x0c00", "Ort unter 100 Einwohner", "SmallFont"),
                      ("0x0d00", "Quartier", "NormalFont"), ("0x0e00", "Quartierteil", "SmallFont"),
                      ("0x11310", "Gebietsname", "SmallFont"), ("0x11311", "Landschaftsname", "NormalFont"), ("0x11312", "Grossregion", "LargeFont")):
    parts.append(text_punkt(t, name, font))
if _o.routing:
    # unsichtbare routbare Linien (Unterlage unter Treppen, Tunneln, Bruecken, 1-m-Wegen und markierten Spuren, deren sichtbarer
    # erweiterter Typ in mkgmap nicht routbar ist): 1 Pixel hoch, alle Pixel durchsichtig
    for t, name in (("0x13", "Strasse (Routing)"), ("0x16", "Weg (Routing)")):
        parts.append(f'[_line]\nType={t}\nString1=0x04,{name}\nXpm="32 1 2 1"\n"3 c none"\n"1 c #000000"\n"' + "3" * 32 + '"\n[end]\n')
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, "w", encoding="latin1").write(hdr_text() + "".join(parts))
print("geschrieben:", os.path.normpath(OUT))
