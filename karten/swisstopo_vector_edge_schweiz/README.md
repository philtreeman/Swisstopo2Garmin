# SwissTOPO Vector Edge, ganze Schweiz

`swisstopo_vector_edge_schweiz.img` (272 MB, Family-ID 3900, Name im Gerätemenü **«SwissTOPO Vector Edge»**) aus swissTLM3D 2026-02 und swissBOUNDARIES3D 2026-01. Gebaut mit `VARIANT=edge GRENZEN=<gpkg> ACHSEN=<gdb> HAUPT=<gdb> scripts/build_vector.sh` (234 Kacheln à 20 × 20 km, eine TYP-Datei). Darstellung nach Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040; die Muster für Fels und Reben sind aus diesen Fotos übernommen (persönlicher Gebrauch). **Auf keinem Gerät geprüft.**

Inhalt gegenüber der Fenix-Variante zusätzlich (Details im README der Wurzel): Fels mit Textur, Bergnamen mit Höhe («Säntis 2502»), Gewässer-, Flur- und Geländenamen, Landes-, Kantons- und Gemeindegrenzen (magenta), Strassenschilder der Nationalstrassen und Hauptstrassen, Orts- und Strassennamen, Sportplätze. Einzelbäume, Schutzverbauungen und Treppen erscheinen nur in der feinsten Zoomstufe. Vergleichsbilder (Rasterkarte und Zeichnung der Vektorkarte, kein Geräte-Rendering): `../../docs/vergleich/`.

## Wegen der Grösse in drei Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_edge_schweiz.img.part_* > swisstopo_vector_edge_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (272 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
