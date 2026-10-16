#!/bin/bash
# Laedt die offenen Datensaetze fuer die Overlays von data.geo.admin.ch (ca. 750 MB, Stand der Dateien siehe README).
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
ls -la "$D"/*.gpkg
