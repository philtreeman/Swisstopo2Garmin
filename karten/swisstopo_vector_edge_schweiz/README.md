# SwissTOPO Vector Edge, ganze Schweiz

`swisstopo_vector_edge_schweiz.img` (323'764'224 Byte = 309 MiB, Family-ID 3900, Name im Gerätemenü **«SwissTOPO Vector Edge»**) aus swissTLM3D 2026-02 und swissBOUNDARIES3D 2026-01. Gebaut mit `VARIANT=edge GRENZEN=<gpkg> ACHSEN=<gdb> HAUPT=<gdb> scripts/build_vector.sh` mit `ROUTING=1` (153 Kacheln à 6 × 4 Blöcke ≈ 20 × 19,5 km im WGS84-Raster, Kartennummern 6390NNNN, eine TYP-Datei; Bauzeit 22 Minuten mit 3 Prozessen). Darstellung nach Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040; die Muster für Fels und Reben sind aus diesen Fotos übernommen (persönlicher Gebrauch). **Auf keinem Gerät geprüft.**

**Routingfähig** (Stand 2026-11-22; Technik im README der Wurzel, Abschnitt «Routing»): jede Kachel enthält NET und NOD. Strassen, Wege und Autostrassen sind routbar, Autostrassen werden jetzt auch gezeichnet (wie Hauptstrassen). **Ob das Gerät die Karte routet, ist ungeprüft** (nur die kleine Testkarte `../routing_test/` war als Vorstufe gedacht, auch sie ist ungeprüft). swissTLM3D enthält **keine Einbahnstrassen** (nur richtungsgetrennte Fahrbahnen, Rampen und Kreisel) und **keine Abbiegeverbote**; Fahrverbote sperren nur Motorfahrzeuge, nicht Velo und Fussgänger. Das Auto-Routing kann deshalb gegen Einbahnstrassen führen.

Inhalt gegenüber der Fenix-Variante zusätzlich (Details im README der Wurzel): Fels mit Textur, Bergnamen mit Höhe («Säntis 2502»), Gewässer-, Flur- und Geländenamen, Landes-, Kantons- und Gemeindegrenzen (magenta), Strassenschilder der Nationalstrassen und Hauptstrassen, Orts- und Strassennamen, Sportplätze. Einzelbäume, Schutzverbauungen und Treppen erscheinen nur in der feinsten Zoomstufe. Vergleichsbilder (Rasterkarte und Zeichnung der Vektorkarte, kein Geräte-Rendering): `../../docs/vergleich/`.

## Wegen der Grösse in vier Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_edge_schweiz.img.part_* > swisstopo_vector_edge_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (310 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
