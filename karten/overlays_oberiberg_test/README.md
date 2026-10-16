# Routen-Overlays, Testausschnitt Oberiberg

Dieselben sechs Overlays wie in `../overlays_schweiz/`, aber nur für die Bounding Box `8.50 46.85 9.05 47.21` (WGS84, ca. 40 × 40 km um Oberiberg SZ). Zum schnellen Testen auf der Uhr (je 50–370 KB).

`vorschau.png` ist eine eigene Zeichnung mit den Farben der Overlays über der grauen Landeskarte, kein Rendering vom Gerät.

Neu bauen: `scripts/build_overlays.sh daten/ mkgmap.jar out/ 8.50 46.85 9.05 47.21`
