#!/bin/bash
# Baut die Reliefschattierungs-Testkarte «SwissTOPO Relief Test Baden» (Family-ID 3931, Kartennummern 6395NNNN) in fuenf Varianten
# zum Groessenvergleich: ohne DEM, mit --dem-dists=3312 (grob) und 1648 (fein), je einstufig und mehrstufig (ein Wert je Detailstufe). Docs: docs/relief.md
#   scripts/build_dem_test.sh <shp-ordner> <mkgmap.jar> <out-ordner> [hgt-ordner]
#   <shp-ordner>   entpackte swissTLM3D-Shapefiles (wie bei build_vector.sh)
#   [hgt-ordner]   HGT-Kacheln; fehlt N47E008.hgt, wird sie mit scripts/make_dem_hgt.py erzeugt (Standard <out>/hgt)
# Umgebungsvariablen: PYTHON (Interpreter mit rasterio/pyproj/scipy fuer make_dem_hgt.py, Standard python3),
#   HGT_TILES (Standard N47E008), BBOX ("W S E N", Standard Baden), DEM_DISTS_GROB (Standard 3312), DEM_DISTS_FEIN (Standard 1648), DEM_EXTRA (weitere mkgmap-Optionen, z. B. --dem-interpolation=bilinear)
# Technik: ruft build_vector.sh mit DEM=<hgt> und DEM_DISTS auf (seit der Integration in Edge). Das DEM wird je Kachel eingebaut (die Kachel-IMG enthaelt die DEM-Teildatei), das
# spaetere Zusammenfuegen uebernimmt sie unveraendert. Gleiches Kachelraster wie karten/routing_test (ROUTING=1, 2 x 2 Bloecke).
set -e
SHP=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); HGT=$(realpath -m "${4:-$OUT/hgt}")
S=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-python3}
mkdir -p "$OUT" "$HGT"
HGT_TILES=${HGT_TILES:-N47E008}; BBOX=${BBOX:-8.24 47.43 8.37 47.50}   # Baden; fuer eine Gebirgsprobe z. B. HGT_TILES=N46E008 BBOX="8.0 46.55 8.1 46.62"
for t in $HGT_TILES; do [ -f "$HGT/$t.hgt" ] || $PY "$S/make_dem_hgt.py" --out "$HGT" --tiles $t --res 1; done

build() {  # build <variante> <dem-optionen>
  local v=$1; shift
  local dd=$1; shift
  local demenv=(); [ -n "$dd" ] && demenv=(DEM="$HGT" DEM_DISTS="$dd" DEM_EXTRA="$*")
  env "${demenv[@]}" ROUTING=1 ROUTING_BLOECKE="2 2" VARIANT=edge FAMILY_ID=3931 MAP_PREFIX=6395 \
    MAP_LABEL="SwissTOPO Relief Test Baden" OUT_NAME=swisstopo_relief_test_baden_$v SPLIT_MB=1000 \
    bash "$S/build_vector.sh" "$SHP" "$JAR" "$OUT/$v" $BBOX
}
# Mehrstufig: die Karte hat 5 Detailstufen (Aufloesung 24, 22, 21, 20, 18 Bit, style/options); ein Geraet braucht je Stufe einen Wert
# (mkgmap --help). Faktoren 1, 4, 8, 16, 32 auf den feinsten Wert, ab Stufe 2 grob nach dem Beispiel in der mkgmap-Hilfe.
multi() { local f=$1; echo "$f,$((f*4)),$((f*8)),$((f*16)),$((f*32))"; }
G=${DEM_DISTS_GROB:-3312}; F=${DEM_DISTS_FEIN:-1648}
build ohne_dem ""
build dem3312 "$G" $DEM_EXTRA
build dem1648 "$F" $DEM_EXTRA
build dem3312_mehrstufig "$(multi $G)" $DEM_EXTRA
build dem1648_mehrstufig "$(multi $F)" $DEM_EXTRA
ls -l "$OUT"/*/swisstopo_relief_test_baden_*.img
