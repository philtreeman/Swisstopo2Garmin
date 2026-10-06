# Swisstopo 1:50'000 auf dem Garmin Edge 1040

Raster-Karte als Garmin Custom Maps (.kmz). Nur Edge 1040 (Forerunner 935 hat keine Karten).

## MacBook
    python3 -m pip install pillow
    python3 swisstopo2garmin.py --bbox 7.30 46.85 7.60 47.05 --zoom 15 --out out

`--bbox` = West Süd Ost Nord in Grad (WGS84), Werte z. B. aus bboxfinder.com.
Zoom 15 ≈ 4.8 m/px, Zoom 16 ≈ 2.4 m/px (4x grösser).

## Auf den Edge
1. Edge per USB anschliessen (am Mac ggf. "Android File Transfer" bzw. OpenMTP nutzen).
2. Alle `out/*.kmz` nach `Garmin/CustomMaps/` kopieren.
3. Edge trennen, neu starten. Karte unter Einstellungen > Karte > Kartenübersicht aktivieren.

## Grenzen
- Max. 100 JPEGs je KMZ, je JPEG max. 1024x1024 px (im Skript so gesetzt).
- Ganze Schweiz = mehrere GB, nimm Regionen.
- Custom Maps haben kein Routing.
