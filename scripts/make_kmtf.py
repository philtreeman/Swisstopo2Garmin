#!/usr/bin/env python3
"""Erzeugt ein Garmin-Kartenthema (.kmtf) im Stil der swisstopo-Landeskarte.

  python3 make_kmtf.py <vorlage.kmtf> [weitere-vorlage.kmtf ...] <ausgabe.kmtf>

Die Feldnamen (MPM_*) stammen aus Kartenthemen des Geraets (z. B. Popularity.kmtf); alle Felder der Vorlagen werden uebernommen,
danach werden die Farben fuer Land, Wald, Wasser, Gebaeude, Strassen, Bahn, Hoehenlinien und Beschriftung nach den Farben der
swisstopo-Pixelkarte gesetzt (an der Karte gemessen, Strassen nach der Zeichenerklaerung). Format der Farben: #AARRGGBB, je Feld
primaer/sekundaer fuer Tag und Nacht.
"""
import re, sys
import xml.etree.ElementTree as ET

args = sys.argv[1:]
out = args[-1]
fields = {}
order = []
for path in args[:-1]:
    for st in ET.parse(path).getroot().find("stylelist"):
        f = st.get("field")
        if f not in fields:
            fields[f] = st; order.append(f)

def c(hexrgb):
    return "#ff" + hexrgb.lstrip("#").lower()

# (Feld): (primaer, sekundaer) als RGB; fuer Tag und Nacht gleich
FARBEN = {
    "MPM_LAND_CLR": ("#FEFFED", "#FEFFED"), "MPM_URBAN_LAND_CLR": ("#FEFFED", "#FEFFED"), "MPM_MISC_AREA_CLR": ("#EDEDED", "#EDEDED"),
    "MPM_PARK_CLR": ("#DFF0CC", "#DFF0CC"), "MPM_WOODS_CLR": ("#C8E6B2", "#B4D79B"), "MPM_GRASSLND_CLR": ("#E1F2D3", "#E1F2D3"),
    "MPM_WETLAND_CLR": ("#BFE3EF", "#9CCFE0"), "MPM_BOG_CLR": ("#BFE3EF", "#9CCFE0"), "MPM_FLOATING_BOG": ("#BFE3EF", "#9CCFE0"),
    "MPM_WATER_CLR": ("#D3EEFF", "#7BC5F0"), "MPM_MISC_WATER_AREA_CLR": ("#D3EEFF", "#7BC5F0"), "MPM_SHORELINE_CLR": ("#7BC5F0", "#7BC5F0"),
    "MPM_RIVER_CHNL_CLR": ("#7BC5F0", "#5BB4EA"), "MPM_MISC_WATER_LINE_CLR": ("#7BC5F0", "#5BB4EA"), "MPM_GLACIER_CLR": ("#E6F4FF", "#BFE3F7"),
    "MPM_BUILDING_CLR": ("#222222", "#222222"), "MPM_BUILDING_SHADOW_CLR": ("#222222", "#222222"),
    "MPM_RWY_HSRFC_CLR": ("#E8E8E8", "#B0B0B0"),
    # Strassen: Autobahn orange, Hauptstrassen gelb, uebrige weiss, alle mit schwarzem Rand
    "MPM_INTERSTATE_CLR": ("#F5A700", "#000000"), "MPM_SS_INTERSTATE_CLR": ("#F5A700", "#000000"),
    "MPM_MJR_HWY_CLR": ("#FFD54D", "#000000"), "MPM_MNR_HWY_CLR": ("#FFD54D", "#000000"),
    "MPM_ARTERIAL_CLR": ("#FFFFFF", "#000000"), "MPM_COLLECTOR_CLR": ("#FFFFFF", "#000000"), "MPM_RESIDENTIAL_CLR": ("#FFFFFF", "#000000"),
    "MPM_RAMP_CLR": ("#F5A700", "#000000"), "MPM_UNPAVED_CLR": ("#FFFFFF", "#555555"), "MPM_BRIDGE_CLR": ("#FFFFFF", "#000000"),
    "MPM_TRAIL_CLR": ("#000000", "#000000"), "MPM_CARTO_LINE_CLR": ("#000000", "#000000"), "MPM_MISC_LINE_CLR": ("#000000", "#000000"),
    "MPM_RAILRD_CLR": ("#000000", "#FFFFFF"),
    # Hoehenlinien braun
    "MPM_MJR_CNTR_CLR": ("#A5733A", "#A5733A"), "MPM_INT_CNTR_CLR": ("#B8864F", "#B8864F"), "MPM_MNR_CNTR_CLR": ("#D2A878", "#D2A878"),
    "MPM_ISO0_CLR": ("#D2A878", "#D2A878"), "MPM_ISO1_CLR": ("#D2A878", "#D2A878"), "MPM_ISO2_CLR": ("#B8864F", "#B8864F"),
    "MPM_ISO3_CLR": ("#B8864F", "#B8864F"), "MPM_ISO4_CLR": ("#A5733A", "#A5733A"),
    # Beschriftung: schwarz mit weissem Rand, Gewaesser dunkelblau
    "MPM_MAP_TXT_CLR": ("#000000", "#FFFFFF"), "MPM_HGLT_TXT_CLR": ("#000000", "#FFFFFF"), "MPM_WPT_TXT_CLR": ("#000000", "#FFFFFF"),
    "MPM_RVR_LAKE_TXT_CLR": ("#0A4A8A", "#FFFFFF"), "MPM_LABL_OTLN_CLR": ("#000000", "#FFFFFF"),
}
for f, (p, s) in FARBEN.items():
    if f not in fields:
        st = ET.Element("style", field=f); col = ET.SubElement(st, "color")
        ET.SubElement(col, "primary", day="", night=""); ET.SubElement(col, "secondary", day="", night="")
        fields[f] = st; order.append(f)
    col = fields[f].find("color")
    col.find("primary").set("day", c(p)); col.find("primary").set("night", c(p))
    col.find("secondary").set("day", c(s)); col.find("secondary").set("night", c(s))

root = ET.Element("garmin_map_theme")
md = ET.SubElement(root, "metadata")
ET.SubElement(md, "title").text = "Swisstopo"
ET.SubElement(md, "description").text = "Farben der swisstopo-Landeskarte"
ET.SubElement(md, "category").text = "0"
sl = ET.SubElement(root, "stylelist")
for f in order:
    sl.append(fields[f])
ET.ElementTree(root).write(out, encoding="UTF-8", xml_declaration=True)
print("geschrieben:", out, len(order), "Felder")
