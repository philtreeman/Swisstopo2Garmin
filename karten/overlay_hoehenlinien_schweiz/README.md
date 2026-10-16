# Höhenlinien-Overlay ganze Schweiz (10 m Äquidistanz)

`swisstopo_overlay_hoehenlinien.img` (167 MB, Family-ID 3917, Name im Gerätemenü «Hoehenlinien 10 m») aus **swissALTI3D** (2 m Raster, neuestes Jahr je Kachel 2019–2026, 43'650 Kacheln). Gebaut mit `scripts/build_hoehenlinien.sh`. Auf keinem Gerät geprüft.

- Äquidistanz **10 m**. Jede 50 m eine stärkere Zwischenlinie, jede 100 m eine Hauptlinie, beide mit Höhenbeschriftung.
- Hellbraun (10 m, 1 px), mittelbraun (50 m, 1 px), dunkelbraun (100 m, 2 px).
- Ist ein Overlay: ohne Basiskarte. Darüber lassen sich Basiskarte und die Routen-Overlays legen.
- Linien sind 1-km-Kachelweise berechnet und mit 2,5 m vereinfacht. An Kachelrändern bleibt eine Lücke von einem Pixel (2 m), das ist nicht sichtbar. Beschriftungen wiederholen sich deshalb etwa alle Kilometer.

`vorschau_baden.png` ist eine eigene Zeichnung der Höhenlinien (dieselben Farben) über einer grauen Landeskarte, kein Rendering vom Gerät.

## Wegen der Grösse in Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_overlay_hoehenlinien.img.part_* > swisstopo_overlay_hoehenlinien.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren. Daten: © swisstopo (swissALTI3D), Lizenz laut STAC «proprietary».
