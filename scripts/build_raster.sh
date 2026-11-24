#!/usr/bin/env bash
# Baut SwissTOPO2026 Raster.
# Mit Vorlage (TopoCHProV5raster.img): Slot-Ersatz, auf dem Edge geprüft.
# Ohne Vorlage: Standalone-DSKIMG aus Format-Stubben + swisstopo WMTS (gerätlich ungeprüft).
# Siehe README, Abschnitt «SwissTOPO2026 Raster».
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SRC="${1:-${TOPO_SRC:-$ROOT/TopoCHProV5raster.img}}"
PY="${PYTHON:-python3}"
if ! "$PY" -c 'from PIL import Image' 2>/dev/null; then
  echo "Pillow fehlt. Beispiel: $PY -m pip install Pillow" >&2
  exit 1
fi

if [[ -f "$SRC" ]]; then
  echo "Bau mit Vorlage: $SRC"
  exec "$PY" "$ROOT/scripts/build_raster.py" "$SRC"
fi

echo "Keine Vorlage unter $SRC — Standalone-Bau (ohne TopoCHProV5raster.img)."
echo "Braucht: Pillow, Netz zu wmts.geo.admin.ch, Stubben in scripts/_raster_*.bin"
exec "$PY" "$ROOT/scripts/build_raster.py"
