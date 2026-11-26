#!/usr/bin/env bash
# SHA256SUMS fuer geteilte Karten schreiben: jede Teildatei (*.img.part_*) und
# zusaetzlich die daraus zusammengesetzte ganze IMG (berechnet per cat, ohne sie abzulegen).
# Aufruf: scripts/sha256sums.sh <kartenordner> [<kartenordner> ...]
# Pruefen beim Nutzer:  sha256sum -c --ignore-missing SHA256SUMS
#   (macOS: shasum -a 256 -c --ignore-missing SHA256SUMS)
set -euo pipefail
for dir in "$@"; do
  (
    cd "$dir"
    shopt -s nullglob
    parts=( *.img.part_* )
    [ ${#parts[@]} -gt 0 ] || { echo "keine Teile in $dir" >&2; exit 1; }
    sha256sum "${parts[@]}" > SHA256SUMS.tmp
    for base in $(printf '%s\n' "${parts[@]}" | sed 's/\.part_[a-z]*$//' | sort -u); do
      h=$(cat "$base".part_* | sha256sum | cut -d' ' -f1)
      echo "$h  $base" >> SHA256SUMS.tmp
    done
    mv SHA256SUMS.tmp SHA256SUMS
    sha256sum -c --quiet --ignore-missing SHA256SUMS
    echo "$dir: $(wc -l < SHA256SUMS) Eintraege"
  )
done
