#!/bin/bash
# Baut die 6 Routen-Overlays als je eine eigene .img-Datei (eigene Family-ID, eigenes TYP):
#   swisstopo_overlay_wanderwege.img               Wanderwegnetz (swissTLM3D), gelb/rot/blau gestrichelt
#   swisstopo_overlay_wanderland.img               Wanderland-Routen (SchweizMobil), gelb
#   swisstopo_overlay_veloland.img                 Veloland-Routen (SchweizMobil), hellblau
#   swisstopo_overlay_mountainbike.img             Mountainbikeland-Routen (SchweizMobil), orange
#   swisstopo_overlay_skirouten_blau.img           Skirouten, blau durchgezogen (wie Rasterkarte)
#   swisstopo_overlay_skirouten_schwierigkeit.img  Skirouten, nach SAC-Schwierigkeit gefaerbt
#
# Aufruf:  scripts/build_overlays.sh <daten-ordner> <mkgmap.jar> <out-ordner> [W S E N]
#   <daten-ordner>  die GeoPackages aus scripts/download_daten.sh
#   [W S E N]       optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz in 2x2 Kacheln
#
# Ablauf:
#   1. routes2osm.py   GeoPackage (LV95) -> OSM-XML (eigene Tags route_layer/route_class/name), je Kachel
#   2. make_overlay_typ.py  schreibt je Karte eine TYP-Datei (Farben, Linienbreiten, Muster)
#   3. mkgmap          OSM + mkgmap/overlays/style + TYP -> gmapsupp.img, kopiert nach <out>/swisstopo_overlay_<name>.img
# Zwischenstaende (<out>/osm/*.osm) werden wiederverwendet; zum Neuberechnen loeschen.
set -e
D=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd)       # scripts/
R=$(dirname "$S")                      # Repo-Wurzel
STYLE="$R/mkgmap/overlays/style"; TYPDIR="$R/mkgmap/overlays/typ"

# Kacheln: mit Bounding Box eine Kachel; ohne Bounding Box die ganze Schweiz in 2x2 Kacheln
if [ $# -eq 4 ]; then TILES=("$1 $2 $3 $4")
else TILES=("5.90 45.80 8.25 46.85" "8.25 45.80 10.60 46.85" "5.90 46.85 8.25 47.85" "8.25 46.85 10.60 47.85"); fi

mkdir -p "$OUT/osm"
conv() {  # conv <kind> <geopackage>
  local i=0
  for t in "${TILES[@]}"; do
    [ -s "$OUT/osm/$1_$i.osm" ] || python3 "$S/routes2osm.py" --kind "$1" --gpkg "$D/$2" --out "$OUT/osm/$1_$i.osm" --bbox $t
    i=$((i+1))
  done
}
conv wanderwege SWISSTLM3D_WANDERWEGE.gpkg
conv wanderland wanderland.gpkg
conv veloland veloland.gpkg
conv mtb mountainbikeland.gpkg
conv ski ski_routes_2056.gpkg

python3 "$S/make_overlay_typ.py" >/dev/null

# Name : OSM-Praefix : Family-ID : Beschreibung (so heisst die Karte im Geraetemenue)
for spec in "wanderwege:wanderwege:3911:Wanderwege" "wanderland:wanderland:3912:Wanderland Routen" \
            "veloland:veloland:3913:Veloland Routen" "mountainbike:mtb:3914:Mountainbikeland Routen" \
            "skirouten_blau:ski:3915:Skirouten blau" "skirouten_schwierigkeit:ski:3916:Skirouten nach Schwierigkeit"; do
  IFS=: read name osm fid desc <<<"$spec"
  rm -rf "$OUT/img_$name"; mkdir -p "$OUT/img_$name"
  java -Xmx6g -jar "$JAR" --style-file="$STYLE" --output-dir="$OUT/img_$name" \
    --family-id=$fid --product-id=1 --family-name="swisstopo $desc" --series-name="swisstopo $desc" \
    --description="$desc" --mapname=6${fid}001 --code-page=1252 --gmapsupp --keep-going --transparent \
    --draw-priority=30 $(ls "$OUT"/osm/${osm}_*.osm) "$TYPDIR/$name.txt" | grep -E "Exception|SEVERE" || true
  cp "$OUT/img_$name/gmapsupp.img" "$OUT/swisstopo_overlay_$name.img"
done
ls -la "$OUT"/swisstopo_overlay_*.img
