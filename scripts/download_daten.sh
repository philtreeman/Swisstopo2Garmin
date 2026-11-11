#!/bin/bash
# Laedt die offenen Datensaetze fuer die Overlays von data.geo.admin.ch (ca. 1,9 GB inkl. OSM-Auszug, Stand der Dateien siehe README).
#   scripts/download_daten.sh <ziel-ordner>
set -e
D=$(realpath -m "${1:?Zielordner angeben}"); mkdir -p "$D"; cd "$D"
B=https://data.geo.admin.ch
get() { [ -s "$2" ] || curl -sS -L --fail -o "$2" "$1"; }
# SchweizMobil / ASTRA: Wanderland, Veloland, Mountainbikeland (GeoPackage, LV95)
for c in wanderland veloland mountainbikeland; do get "$B/ch.astra.$c/$c/${c}_2056.gpkg" "$c.gpkg"; done
# swisstopo: Wanderwegnetz swissTLM3D (ZIP mit SWISSTLM3D_WANDERWEGE.gpkg)
get "$B/ch.swisstopo.swisstlm3d-wanderwege/swisstlm3d-wanderwege/swisstlm3d-wanderwege_2056_5728.gpkg.zip" wanderwege.zip
[ -s SWISSTLM3D_WANDERWEGE.gpkg ] || unzip -o -q wanderwege.zip
# swisstopo/SAC: Skirouten (ZIP mit ski_routes_2056.gpkg und ski_network_2056.gpkg)
get "$B/ch.swisstopo-karto.skitouren/skitouren/skitouren_2056.gpkg.zip" skitouren.zip
[ -s ski_routes_2056.gpkg ] || unzip -o -q skitouren.zip
# swisstopo/SAC: Schneeschuhrouten (ZIP mit snowshoe_routes_2056.gpkg und snowshoe_network_2056.gpkg)
get "$B/ch.swisstopo-karto.schneeschuhrouten/schneeschuhrouten/schneeschuhrouten_2056.gpkg.zip" schneeschuhrouten.zip
[ -s snowshoe_routes_2056.gpkg ] || unzip -o -q schneeschuhrouten.zip
# swisstopo/SAC: Bahnen Winter und Unterkuenfte Winter (Landeskarte mit Schneesportthemen) fuer Skilifte und Unterkuenfte Winter
get "$B/ch.swisstopo.bahnen-winter/bahnen-winter/bahnen-winter_2056.gpkg" bahnen-winter_2056.gpkg
get "$B/ch.swisstopo.unterkuenfte-winter/unterkuenfte-winter/unterkuenfte-winter_2056.gpkg" unterkuenfte-winter_2056.gpkg
# swisstopo: swissNAMES3D (Gebaeudenamen und Hoehen fuer Unterkuenfte Winter, ca. 460 MB)
get "$B/ch.swisstopo.swissnames3d/swissnames3d_2026/swissnames3d_2026_2056.gpkg" swissnames3d_2026_2056.gpkg
# OpenStreetMap (nur fuer das Skipisten-Overlay): Auszug Schweiz von OpenStreetMap France (ca. 680 MB; Geofabrik war nicht erreichbar).
# Daten © OpenStreetMap-Mitwirkende, ODbL.
get "https://download.openstreetmap.fr/extracts/europe/switzerland-latest.osm.pbf" switzerland-latest.osm.pbf
ls -la "$D"/*.gpkg "$D"/*.pbf
