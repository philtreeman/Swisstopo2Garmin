#!/usr/bin/env python3
"""Veraltet. Das Raster-IMG wird mit scripts/build_raster.py gebaut."""
import runpy
import sys
from pathlib import Path

sys.stderr.write(
    "Hinweis: experimente/raster_img_kachel_test.py ist ein Alias. "
    "Bitte scripts/build_raster.py bzw. scripts/build_raster.sh nutzen.\n"
)
runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "build_raster.py"),
               run_name="__main__")
