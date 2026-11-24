# SwissTOPO Vector Fenix, ganze Schweiz

`swisstopo_vector_fenix_schweiz.img` (291'241'984 Byte = 278 MiB, Family-ID 3901, Name im Gerätemenü **«SwissTOPO Vector Fenix»**) aus swissTLM3D 2026-02. Gebaut am 2026-11-24 mit `VARIANT=fenix ROUTING=1 scripts/build_vector.sh` (153 Kacheln à 6 × 4 Blöcke ≈ 20 × 19,5 km im WGS84-Raster, Kartennummern 6391NNNN, eine TYP-Datei; Bauzeit 28 Minuten mit 3 Prozessen; MapFailedExceptions 0, NET und NOD in jeder Kachel). **Darstellung nach der swisstopo-Zeichenerklärung** (gleiche Farben und Symbole wie die Edge-Variante), aber **Details weggelassen statt vereinfachte Stile zu erfinden**; die frühere Garmin-Darstellung ist ersetzt. **Auf keinem Gerät geprüft.**

**Routingfähig** (Technik im README der Wurzel, Abschnitt «Routing»): jede Kachel enthält NET und NOD. Strassen, Wege und Autostrassen sind routbar. **Ob das Gerät die Karte routet, ist ungeprüft**, ebenso ob die Fenix 5S Plus mit der Dateigrösse und den Routing-Profilen zurechtkommt. swissTLM3D enthält **keine Einbahnstrassen** (nur richtungsgetrennte Fahrbahnen, Rampen und Kreisel) und **keine Abbiegeverbote**; Fahrverbote sperren nur Motorfahrzeuge, nicht Velo und Fussgänger.

Reduziert gegenüber der Edge-Variante: keine Gebäudeuntertypen (offene Gebäude wie Gebäude, schwarz), keine Punktsymbole (nur Höhenkoten an Gipfeln und Pässen), Fels, Geröll, Wald offen und Gebüschwald erst ab Auflösung 22, keine Namen ausser der Höhe an Gipfeln und Pässen, keine Grenzen, keine Strassenschilder, keine Sportbauten, Fähren, Hafenstege, Durchfahrtssperren. Enthalten sind Gletscher, Bahn rot, Seilbahnen, Gewässer, Hochspannungsleitung, Staumauern und Flugplatzpisten sowie die Einzelbäume (grünes Plus 3 × 3, eine pro 70-m-Zelle, **in der feinsten Zoomstufe**; wie im Edge ausgedünnt); Schutzverbauungen und Treppen ebenfalls nur in der feinsten Stufe.

## Wegen der Grösse in vier Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_fenix_schweiz.img.part_* > swisstopo_vector_fenix_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (280 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
