#!/usr/bin/env python3
"""Erzeugt die TYP-Dateien der beiden Hangneigungs-Karten:
  mkgmap/hangneigung/typ/hangneigung.txt          Family-ID 3924, Klassen 10-20 ... >50 Grad
  mkgmap/hangneigung/typ/hangneigungsklassen.txt  Family-ID 3925, nur die Lawinenklassen ab 30 Grad

  python3 make_hangneigung_typ.py [--dichte 50|25] [--dichte-flach 50|25]

«Semitransparent»: Garmin-TYP kennt kein Alpha. Jede Flaeche ist deshalb ein 32 x 32-Muster mit zwei Farben, die erste
ist 'none' (durchsichtig, muss in der Farbtabelle zuerst stehen). Dichte 50 = Schachbrett (jeder zweite Pixel farbig),
Dichte 25 = jeder zweite Pixel in jeder zweiten Zeile. Die Basiskarte scheint durch die leeren Pixel.

Farben ab 30 Grad gemessen an der swisstopo-WMTS-Ebene ch.swisstopo.hangneigung-ueber_30 («Hangneigungsklassen ab 30°»,
Raum Davos, Zoom 14; die Klassengrenzen wurden mit der eigenen Neigungsberechnung bestaetigt):
  30-35 #F2E50A gelb, 35-40 #F46F24 orange, 40-45 #DE055B rot, 45-50 #C889BB violett, ab 50 #4B4B4B grau.
Unter 30 Grad (nur Karte Hangneigung, swisstopo hat dafuer keine Ebene): eigene Gruenstufen (ColorBrewer RdYlGn).
Die Typen 0x10e0d-0x10e0f und 0x10e1b-0x10e1f sind in keiner anderen TYP-Datei des Repos belegt.
"""
import argparse, os

KLASSEN = [  # untere Grenze, Typ, Farbe, Bezeichnung
    (10, 0x10e0d, "#A6D96A", "10-20"),
    (20, 0x10e0e, "#66BD63", "20-25"),
    (25, 0x10e0f, "#1A9850", "25-30"),
    (30, 0x10e1b, "#F2E50A", "30-35"),
    (35, 0x10e1c, "#F46F24", "35-40"),
    (40, 0x10e1d, "#DE055B", "40-45"),
    (45, 0x10e1e, "#C889BB", "45-50"),
    (50, 0x10e1f, "#4B4B4B", "ueber 50"),
]
TYPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "hangneigung", "typ")


def muster(dichte):
    """32 Zeilen aus 'a' (durchsichtig) und 'b' (Farbe)"""
    rows = []
    for y in range(32):
        if dichte == 50:
            rows.append("".join("b" if (x + y) % 2 == 0 else "a" for x in range(32)))
        elif dichte == 25:
            rows.append("".join("b" if (x % 2 == 0 and y % 2 == 0) else "a" for x in range(32)))
        else:
            raise ValueError(dichte)
    return rows


def polygon(typ, farbe, name, dichte):
    body = "\n".join(f'"{r}"' for r in muster(dichte))
    return (f'[_polygon]\nType=0x{typ:05x}\nString1=0x04,Hangneigung {name} Grad\n'
            f'Xpm="32 32 2 1"\n"a c none"\n"b c {farbe}"\n{body}\n[end]\n')


def typ(fid, titel, klassen, dichte, dichte_flach):
    txt = (f"; -*- coding: cp1252 -*-\n; TYP fuer {titel} (Family-ID {fid}), erzeugt von scripts/make_hangneigung_typ.py\n"
           f"[_id]\nProductCode=1\nFID={fid}\nCodePage=1252\n[end]\n[_drawOrder]\n")
    txt += "".join(f"Type=0x{t:05x},{n + 1}\n" for n, (_, t, _, _) in enumerate(klassen)) + "[end]\n"
    txt += "".join(polygon(t, f, nm, dichte if g >= 30 else dichte_flach) for g, t, f, nm in klassen)
    return txt


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--dichte", type=int, default=50, choices=(50, 25), help="Musterdichte ab 30 Grad in Prozent")
    a.add_argument("--dichte-flach", type=int, default=25, choices=(50, 25), help="Musterdichte unter 30 Grad")
    o = a.parse_args()
    os.makedirs(TYPDIR, exist_ok=True)
    for fn, fid, titel, kl in (("hangneigung.txt", 3924, "swisstopo Hangneigung", KLASSEN),
                               ("hangneigungsklassen.txt", 3925, "swisstopo Hangneigungsklassen", [k for k in KLASSEN if k[0] >= 30])):
        p = os.path.join(TYPDIR, fn)
        open(p, "w", encoding="cp1252").write(typ(fid, titel, kl, o.dichte, o.dichte_flach))
        print("geschrieben:", os.path.normpath(p))


if __name__ == "__main__":
    main()
