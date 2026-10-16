#!/bin/bash
# Baut ein gmapsupp.img mit 5 einzeln schaltbaren Overlay-Karten:
# Wanderwege, Wanderland, Veloland, Mountainbikeland, Skirouten.
#   routes/build.sh <daten-ordner> <mkgmap.jar> <out-ordner> [W S E N]
# <daten-ordner> enthaelt: SWISSTLM3D_WANDERWEGE.gpkg wanderland.gpkg veloland.gpkg
#                          mountainbikeland.gpkg ski_routes_2056.gpkg
# Ohne Bounding Box: ganze Schweiz (gross; evtl. kachelweise bauen).
set -e
D=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
V=$(cd "$(dirname "$0")/.." && pwd)
BB=(); [ $# -eq 4 ] && BB=(--bbox "$@")
mkdir -p "$OUT/osm" "$OUT/img"
conv() { PYTHONPATH=$V python3 $V/routes2osm.py --kind "$1" --gpkg "$D/$2" --out "$OUT/osm/$1.osm" "${BB[@]}"; }
conv wanderwege SWISSTLM3D_WANDERWEGE.gpkg
conv wanderland wanderland.gpkg
conv veloland veloland.gpkg
conv mtb mountainbikeland.gpkg
conv ski ski_routes_2056.gpkg
cat > "$OUT/args.txt" <<ARGS
style-file=$V/routes/style
family-id=3902
product-id=1
code-page=1252
keep-going
transparent
draw-priority=30
gmapsupp
output-dir=$OUT/img
family-name=swisstopo Routen
series-name=swisstopo Routen
mapname=63902001
description=Wanderwege
input-file=$OUT/osm/wanderwege.osm
mapname=63902002
description=Wanderland Routen
input-file=$OUT/osm/wanderland.osm
mapname=63902003
description=Veloland Routen
input-file=$OUT/osm/veloland.osm
mapname=63902004
description=Mountainbikeland Routen
input-file=$OUT/osm/mtb.osm
mapname=63902005
description=Skirouten
input-file=$OUT/osm/ski.osm
input-file=$V/routes/typ/routes.txt
ARGS
java -Xmx6g -jar "$JAR" -c "$OUT/args.txt"
ls -la "$OUT/img/gmapsupp.img"
