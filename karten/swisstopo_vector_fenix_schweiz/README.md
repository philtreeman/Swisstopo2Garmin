# SwissTOPO Vector Fenix, ganze Schweiz

`swisstopo_vector_fenix_schweiz.img` (304'742'400 Byte = 291 MiB, Family-ID 3901, Name im Gerätemenü **«SwissTOPO Vector Fenix»**) aus swissTLM3D 2026-02. Gebaut mit `VARIANT=fenix scripts/build_vector.sh` mit `ROUTING=1` (153 Kacheln à 6 × 4 Blöcke ≈ 20 × 19,5 km im WGS84-Raster, Kartennummern 6391NNNN, eine TYP-Datei; Bauzeit 25 Minuten mit 3 Prozessen). Darstellung nach Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040; die Muster für Fels und Reben sind aus diesen Fotos übernommen (persönlicher Gebrauch). **Auf keinem Gerät geprüft.**

**Routingfähig** (Stand 2026-11-22; Technik im README der Wurzel, Abschnitt «Routing»): jede Kachel enthält NET und NOD. Strassen, Wege und Autostrassen sind routbar, Autostrassen werden jetzt auch gezeichnet (wie Hauptstrassen). **Ob das Gerät die Karte routet, ist ungeprüft**, ebenso ob die Fenix 5S Plus mit der Dateigrösse und den Routing-Profilen zurechtkommt. swissTLM3D enthält **keine Einbahnstrassen** (nur richtungsgetrennte Fahrbahnen, Rampen und Kreisel) und **keine Abbiegeverbote**; Fahrverbote sperren nur Motorfahrzeuge, nicht Velo und Fussgänger.

Reduzierte Variante für die Fenix 5S Plus: Fels einfach grau, keine Namen ausser der Höhe an Gipfeln und Pässen, keine Grenzen, keine Strassenschilder, keine Sportplätze. Einzelbäume, Schutzverbauungen und Treppen erscheinen nur in der feinsten Zoomstufe.

## Wegen der Grösse in vier Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_fenix_schweiz.img.part_* > swisstopo_vector_fenix_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (291 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
