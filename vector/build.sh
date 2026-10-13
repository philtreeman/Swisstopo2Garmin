#!/bin/bash
# build.sh <osm-dateien...> -> gmapsupp.img in build_out/
set -e
V=/home/user/Swisstopo2Garmin/vector
rm -rf build_out && mkdir build_out
java -Xmx6g -jar mkgmap-r4924/mkgmap.jar --style-file=$V/style --output-dir=build_out \
  --family-id=3900 --product-id=1 --family-name="swisstopo-style" --series-name="swisstopo-style" \
  --description="swisstopo-style" --mapname=63900001 --code-page=1252 --gmapsupp \
  --draw-priority=20 --remove-short-arcs --reduce-point-density=3 --reduce-point-density-polygon=4 \
  --min-size-polygon=8 --keep-going "$@" $V/typ/swisstopo.txt 2>&1 | grep -v JAVA_TOOL
ls -la build_out
