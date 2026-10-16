# Vektor-Basiskarte ganze Schweiz

`swisstopo_basiskarte_schweiz.img` (190 MB, Family-ID 3900) aus swissTLM3D 2026-02: Strassen nach Klassen, Wege, Wanderwege, Wald, Fels, Geröll, Gewässer, Bahn, Gebäude, Siedlungs-, Gelände- und Flurnamen. Darstellung an der Landeskarte 1:25'000 orientiert. **Ohne Höhenlinien und Schummerung.** Auf keinem Gerät geprüft.

Gebaut mit `scripts/build_basiskarte.sh` (234 Kacheln à 20 × 20 km, davon 148 mit Inhalt, in einer Datei zusammengeführt).

## Wegen der Grösse in Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei, deshalb liegt die Karte in drei Teilen (2 × 90 MiB, 1 × 0,9 MiB). Zusammensetzen:

```
cat swisstopo_basiskarte_schweiz.img.part_* > swisstopo_basiskarte_schweiz.img
sha256sum -c SHA256SUMS            # Linux;  Mac: shasum -a 256 -c SHA256SUMS
```
Die Prüfsumme in `SHA256SUMS` gehört zur zusammengesetzten Datei. Danach nach `Garmin/` auf das Gerät kopieren. Der Platz auf dem Gerät muss für 190 MB reichen.

Die Overlays (`../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietary».
