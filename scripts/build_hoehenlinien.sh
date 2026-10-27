#!/bin/bash
# Baut zwei Hoehenlinien-Overlays aus swissALTI3D (2 m Raster), je eine eigene .img mit eigener Family-ID:
#   swisstopo_overlay_hoehenlinien_20m.img   Aequidistanz 20 m, Haupthoehenlinie alle 100 m mit Beschriftung  (Family-ID 3920)
#   swisstopo_overlay_hoehenlinien_10m.img   Aequidistanz 10 m, Zwischenlinie 50 m, Haupthoehenlinie 100 m   (Family-ID 3919)
#   scripts/build_hoehenlinien.sh <kachelliste.json> <mkgmap.jar> <out-ordner> [W S E N]
#   <kachelliste.json>  Ergebnis von scripts/swissalti3d_kachelliste.py
#   [W S E N]           optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz
# Umgebungsvariablen: JOBS (parallele Bloecke, Standard 3), SPLIT_MB (Standard 90)
#
# Ablauf:
#   1. hoehenlinien2mkgmap.py --print-blocks   Liste der 20-km-Bloecke (LV95-Raster) mit vorhandenen 1-km-Kacheln
#   2. je Block (parallel, fortsetzbar): swissALTI3D-Kacheln laden (je ca. 1 MB), Hoehenlinien im 10-m-Abstand rechnen -> OSM-XML
#      (Zwischenformat fuer mkgmap) -> mkgmap -> <out>/tiles10/6393NNNN.img; daraus filter_hoehenlinien.py (nur Hoehen durch 20
#      teilbar) -> mkgmap -> <out>/tiles20/6392NNNN.img. Die Hoehendaten werden also nur einmal geladen.
#   3. mkgmap fuegt je Variante alle Block-Karten und die TYP-Datei zusammen
#   4. Ist eine Datei groesser als SPLIT_MB, entstehen Teile <name>.img.part_aa, _ab, ...
# Warum zwei Family-IDs: das Geraet laedt von Karten mit gleicher Family-ID nur eine; wer eine alte Datei auf dem Geraet hat,
# soll sie loeschen (die alte hiess «Hoehenlinien 10 m», Family-ID 3917).
set -e
LIST=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
JOBS=${JOBS:-3}; SPLIT_MB=${SPLIT_MB:-90}
STYLE="$R/mkgmap/overlays/style"; TYPDIR="$R/mkgmap/overlays/typ"
python3 "$S/make_overlay_typ.py" >/dev/null
mkdir -p "$OUT/osm" "$OUT/tiles10" "$OUT/tiles20"
BB=(); [ $# -eq 4 ] && BB=(--bbox "$@")
python3 "$S/hoehenlinien2mkgmap.py" --tiles "$LIST" --print-blocks "${BB[@]}" > "$OUT/bloecke.txt"
echo "$(wc -l < "$OUT/bloecke.txt") Bloecke a 20 km"

compile() {  # compile <osm> <tiles-ordner> <mapname> <family-id> <beschreibung>
  local d="$2/$3"
  mkdir -p "$d"
  java -Xmx3g -jar "$JAR" --style-file="$STYLE" --output-dir="$d" \
    --family-id="$4" --product-id=1 --mapname="$3" --description="$5" --code-page=1252 --lower-case \
    --transparent --draw-priority=30 --remove-short-arcs --keep-going "$1" 2>&1 \
    | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
  cp "$d/$3.img" "$2/$3.img"; rm -rf "$d"
}

work() {  # work i j anzahl
  local i=$1 j=$2 n10 n20 osm osm20
  n10=$(printf "6393%04d" $((i*100+j))); n20=$(printf "6392%04d" $((i*100+j)))
  [ -e "$OUT/tiles10/$n10.done" ] && return 0
  osm="$OUT/osm/$n10.osm"; osm20="$OUT/osm/$n20.osm"
  python3 "$S/hoehenlinien2mkgmap.py" --tiles "$LIST" --block "$i" "$j" --out "$osm" --interval 10 "${BB[@]}" >/dev/null
  if grep -q "<way" "$osm"; then
    compile "$osm" "$OUT/tiles10" "$n10" 3919 "Hoehenlinien 10 m"
    python3 "$S/filter_hoehenlinien.py" "$osm" "$osm20"
    compile "$osm20" "$OUT/tiles20" "$n20" 3920 "Hoehenlinien 20 m"
  fi
  rm -f "$osm" "$osm20"; touch "$OUT/tiles10/$n10.done"
  echo "fertig $n10"
}
export -f work compile; export LIST JAR OUT S STYLE SPLIT_MB; export BB_STR="${BB[*]}"
xargs -P "$JOBS" -L1 bash -c 'BB=($BB_STR); work "$@"' _ < "$OUT/bloecke.txt"

for spec in "10:3919:6393:swisstopo Hoehenlinien 10 m" "20:3920:6392:swisstopo Hoehenlinien 20 m"; do
  IFS=: read iv fid pfx label <<<"$spec"
  mkdir -p "$OUT/final$iv"
  java -Xmx6g -jar "$JAR" --output-dir="$OUT/final$iv" --family-id=$fid --product-id=1 \
    --family-name="$label" --series-name="$label" --description="Hoehenlinien $iv m" \
    --code-page=1252 --lower-case --gmapsupp "$OUT"/tiles$iv/${pfx}*.img "$TYPDIR/hoehenlinien_${iv}m.txt" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
  NAME=swisstopo_overlay_hoehenlinien_${iv}m
  cp "$OUT/final$iv/gmapsupp.img" "$OUT/$NAME.img"
  ls -la "$OUT/$NAME.img"
  if [ "$(stat -c%s "$OUT/$NAME.img")" -gt $((SPLIT_MB*1024*1024)) ]; then
    split -b ${SPLIT_MB}m "$OUT/$NAME.img" "$OUT/$NAME.img.part_"
    ls -la "$OUT"/$NAME.img.part_*
  fi
done
