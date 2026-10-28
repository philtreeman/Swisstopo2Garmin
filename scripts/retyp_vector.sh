#!/bin/bash
# Fuegt fertige Kachel-Karten von SwissTOPO Vector (aus <out>/tiles/ eines Builds) mit einer anderen TYP-Datei neu zusammen: Aenderungen am
# Design (Farben, Muster, Linien) brauchen so keinen neuen Kachel-Build, nur wenige Minuten.
#   scripts/retyp_vector.sh <mkgmap.jar> <family-id> <name> <typ-datei|-> <ausgabe.img> <kachel.img>...
#   <typ-datei>  mkgmap/vector/typ/swisstopo_vector_*.txt (Family-ID in der Datei muss zur Family-ID der Kacheln passen) oder '-' ohne TYP
set -e
JAR=$(realpath "$1"); FID=$2; NAME=$3; TYP=$4; OUT=$(realpath -m "$5"); shift 5
D=$(mktemp -d)
TYPARG=(); [ "$TYP" != "-" ] && TYPARG=("$(realpath "$TYP")")
java -Xmx6g -jar "$JAR" --output-dir="$D" --family-id="$FID" --product-id=1 --family-name="$NAME" --series-name="$NAME" \
  --description="$NAME" --code-page=1252 --lower-case --gmapsupp "$@" "${TYPARG[@]}" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
cp "$D/gmapsupp.img" "$OUT"; rm -rf "$D"; ls -la "$OUT"
