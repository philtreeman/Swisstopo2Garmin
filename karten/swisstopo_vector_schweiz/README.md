# SwissTOPO Vector, ganze Schweiz

`swisstopo_vector_schweiz.img` (201 MB, Family-ID 3900, Name im Gerätemenü **«SwissTOPO Vector»**) aus swissTLM3D 2026-02. Gebaut mit `scripts/build_vector.sh` (148 Kachel-Karten à 20 × 20 km, eine TYP-Datei). Darstellung nach Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040. Beschreibung der Elemente: Hauptseite des Repos. **Auf keinem Gerät geprüft.**

`vorschau_baden.png` ist eine eigene Zeichnung mit denselben Farben (Raum Baden), kein Rendering vom Gerät.

## Wegen der Grösse in drei Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_schweiz.img.part_* > swisstopo_vector_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (201 MB freier Platz nötig). Die Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietary».
