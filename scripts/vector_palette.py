"""Farben von SwissTOPO Vector nach der swisstopo-Zeichenerklaerung «Landeskarten 1:10 000, 1:25 000 und 1:50 000» (Stand 2026-11-24,
am PDF gemessen). Gemeinsam genutzt von make_vector_typ.py (TYP-Datei) und den Vorschau-Skripten. Es gibt nur noch diese eine Darstellung
(frueher gab es zusaetzlich eine an der Garmin-Vektorkarte gemessene; sie ist ersetzt)."""
BG = "#FEFFED"          # Untergrund
WEISS = "#FFFFFF"
SCHWARZ = "#000000"
WALD = "#CBE5D3"
GRUEN = "#00964E"       # Punkte/Striche von Wald offen, Gebueschwald, Gehoelz, Obstanlage, Baumschule, Reben, Einzelbaum
PARK = "#E1EFE2"        # Park, Freizeitanlage, Sport, Camping, Golf, Friedhof, Schrebergarten, Graspiste
DEPONIE = "#E9D9C4"
WASSER = "#008AD2"      # Gewaesserlinien, Gewaesserbeschriftung
WASSER_FL = "#D4EDFC"   # Seen
WASSER_FLUSS = "#BCE4FA"  # Flussflaechen
WASSER_SCHWANK = "#E9F5FD"  # See mit stark wechselndem Wasserstand (heller)
GLETSCHER = "#FFFFFF"
GLETSCHER_STRICH = "#6EC1EE"   # blaue Eisstruktur-Striche im Gletschermuster (0x10e00)
LEITUNG = "#0789CB"     # Hochspannungsleitung, Spital H
BAHN = "#E3000B"        # Bahn, Klettersteig, Treppe, Seilbahnen
SKILIFT = "#CE7611"
STAUMAUER = "#C8C8C8"
LANDESGRENZE = "#E5007C"; GRENZBAND = "#F5B4D2"   # Landes- und Kantonsgrenze (Linie, Band); Bezirks- und Gemeindegrenze nur Band
NATIONALPARK = "#05A535"; NATIONALPARK_BAND = "#9DCC8F"
# Strassen (Verkehrsbedeutung, VERKEHRSBD)
AUTOBAHN = ("#F7A71F", "#000000"); DURCHGANG = ("#F8C7C8", "#000000"); VERBINDUNG = ("#FFF481", "#000000")
HAUPT = ("#FFFFFF", "#000000"); STRASSE = ("#FFFFFF", "#000000"); NEBEN = ("#FFFFFF", "#000000"); NATUR = "#000000"
KLETTERSTEIG = BAHN; TREPPE = BAHN
GEBAEUDE = "#000000"
# Namen, die aeltere Skripte (preview_vector.py, compare_vector.py) noch benutzen
SIEDLUNG = BG; AREAL = BG; VERKEHR = BG; WASSER_LI = WASSER; SPORT = PARK; FRIEDHOF = PARK; SPORTPLATZ = PARK; GEHOELZ = GRUEN
FEUCHT = WASSER; FELS = BG; FELS_GRAU = BG; GEROELL = BG; FELS_TEXTUR = SCHWARZ; REBEN = GRUEN; REBEN_BG = WEISS
WEG = "#000000"; WEG_FEST = "#000000"; LAWINE = "#000000"; BAUM = GRUEN; GRENZE = LANDESGRENZE; PARK_ = PARK
