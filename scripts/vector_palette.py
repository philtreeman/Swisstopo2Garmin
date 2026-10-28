"""Farben von SwissTOPO Vector (gemessen an Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040).
Gemeinsam genutzt von make_vector_typ.py (TYP-Datei) und preview_vector.py (Vorschau)."""
BG = "#FFFAE6"          # Untergrund
SIEDLUNG = "#EEEEEE"    # Siedlungsgebiet
AREAL = "#E6E6E6"       # Industrie-, Schul-, Spitalareale
VERKEHR = "#DEDEDE"     # Parkplaetze, Verkehrsflaechen
WALD = "#A4D26A"
GEBAEUDE = "#8B898B"
WASSER_FL = "#A8DCFA"   # Seen
WASSER_LI = "#52BAF6"   # Fliessgewaesser
PARK = "#C3E48F"
SPORT = "#B4DC84"
FRIEDHOF = "#CFE8AE"
WEG = "#414041"         # Pfade, Wanderwege (gestrichelt)
WEG_FEST = "#626162"    # Feldwege
GEHOELZ = "#A9DC63"; REBEN = "#FF9900"; REBEN_BG = "#DEFAAC"; FEUCHT = "#7FC8E8"; FELS = "#DEDEDE"; FELS_TEXTUR = "#A4A5A4"; GEROELL = "#EFEDE6"
AUTOBAHN = ("#FF9900", "#734400"); HAUPT = ("#FFCE62", "#B38600"); STRASSE = ("#FFFAFF", "#8B898B")
NEBEN = ("#FFFFFF", "#A4A5A4"); NATUR = ("#F6F2D5", "#C9BE7A")
SCHWARZ = "#414041"      # Wege nach swisstopo-Zeichenerklaerung (2 m-Weg, 1 m-Weg, markierte Spur)
LAWINE = "#734400"       # Schutzverbauungen (Lawinen, Steinschlag), braun
BAUM = "#83B200"         # Einzelbaeume (Punkt)
GRENZE = "#BD008B"        # Landes-, Kantons-, Gemeindegrenzen (magenta, wie auf der Garmin-Karte)
FELS_GRAU = "#D0D0D0"    # Fels ohne Textur (Variante Fenix)
SPORTPLATZ = "#FFCE62"     # Sportplaetze (orange, wie auf der Garmin-Karte)

import os
if os.environ.get("VECTOR_DESIGN") == "swisstopo":   # Variante «swisstopo-Stil»: Farben der Landeskarte statt der Garmin-Karte (an der Pixelkarte gemessen)
    BG = "#FEFFED"; SIEDLUNG = "#FEFFED"; AREAL = "#EDEDED"; VERKEHR = "#E8E8E8"
    WALD = "#C8E6B2"; GEBAEUDE = "#222222"
    WASSER_FL = "#D3EEFF"; WASSER_LI = "#7BC5F0"
    PARK = "#DFF0CC"; SPORT = "#E1F2D3"; FRIEDHOF = "#DDEBCB"; SPORTPLATZ = "#E1F2D3"
    WEG = "#000000"; WEG_FEST = "#333333"; SCHWARZ = "#000000"
    GEHOELZ = "#D9EFC4"; FEUCHT = "#BFE3EF"; FELS = "#CFCFCF"; FELS_GRAU = "#C8C8C8"; GEROELL = "#EFEFE0"
    AUTOBAHN = ("#F5A700", "#000000"); HAUPT = ("#FFFFFF", "#000000"); STRASSE = ("#FFFFFF", "#000000")
    NEBEN = ("#FFFFFF", "#000000"); NATUR = ("#FFFFFF", "#555555")
