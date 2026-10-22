#!/bin/bash
# Laedt die Zusatzdaten fuer SwissTOPO Vector Edge nach <ordner>:
#   swissBOUNDARIES3D (Grenzen)           -> <ordner>/swissBOUNDARIES3D_1_5_LV95_LN02.gpkg   (GRENZEN=...)
#   ASTRA Nationalstrassenachsen (Schilder) -> <ordner>/n/ch.astra.nationalstrassenachsen.gdb  (ACHSEN=...)
#   ASTRA Hauptstrassennetz (Schilder)      -> <ordner>/h/MainRoads_*.gdb                      (HAUPT=...)
#   scripts/download_vector_zusatz.sh <ordner>
set -e
D=${1:?Zielordner}; mkdir -p "$D"; cd "$D"
B=https://data.geo.admin.ch
curl -sS -o grenzen.zip "$B/ch.swisstopo.swissboundaries3d/swissboundaries3d_2026-01/swissboundaries3d_2026-01_2056_5728.gpkg.zip"
unzip -o -q grenzen.zip
curl -sS -o achsen.zip "$B/ch.astra.nationalstrassenachsen/nationalstrassenachsen/nationalstrassenachsen_2056.gdb.zip"
unzip -o -q achsen.zip -d n
curl -sS -o haupt.zip "$B/ch.astra.hauptstrassennetz/hauptstrassennetz/hauptstrassennetz_2056.gdb.zip"
unzip -o -q haupt.zip -d h
ls -d "$D"/*.gpkg "$D"/n/*.gdb "$D"/h/*.gdb
