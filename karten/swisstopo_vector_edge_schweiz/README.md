# SwissTOPO Vector Edge, ganze Schweiz

`swisstopo_vector_edge_schweiz.img` (318'267'392 Byte = 304 MiB, Family-ID 3900, Name im Gerätemenü **«SwissTOPO Vector Edge»**) aus swissTLM3D 2026-02 und swissBOUNDARIES3D 2026-01. Gebaut am 2026-11-24 mit `VARIANT=edge GRENZEN=<gpkg> ACHSEN=<gdb> HAUPT=<gdb> KANTONSSCHILDER=<csv> scripts/build_vector.sh` mit `ROUTING=1` (153 Kacheln à 6 × 4 Blöcke ≈ 20 × 19,5 km im WGS84-Raster, Kartennummern 6390NNNN, eine TYP-Datei; Bauzeit 35 Minuten mit 3 Prozessen; MapFailedExceptions 0, NET und NOD in jeder Kachel, Beschriftung «Zürcherstrasse» enthalten). **Darstellung strikt nach der swisstopo-Zeichenerklärung «Landeskarten 1:10 000, 1:25 000 und 1:50 000»** (Strassen, Bahn, Seilbahnen, Gewässer, Wald, Fels, Gletscher, Reben, Gebäude, Grenzen, Punktsymbole; Typnummern und Kompromisse im README der Wurzel, Abschnitt «Darstellung nach der Zeichenerklärung»); die frühere Garmin-Darstellung ist ersetzt. **Auf keinem Gerät geprüft.**

**Routingfähig** (Technik im README der Wurzel, Abschnitt «Routing»): jede Kachel enthält NET und NOD. Strassen, Wege und Autostrassen sind routbar. **Ob das Gerät die Karte routet, ist ungeprüft.** swissTLM3D enthält **keine Einbahnstrassen** (nur richtungsgetrennte Fahrbahnen, Rampen und Kreisel) und **keine Abbiegeverbote**; Fahrverbote sperren nur Motorfahrzeuge, nicht Velo und Fussgänger. Das Auto-Routing kann deshalb gegen Einbahnstrassen führen. Die neu gezeichneten Durchfahrtssperren (rotes Kreuz, nur feinste Stufe) sind nur Darstellung und haben keinen Routing-Einfluss.

Inhalt gegenüber der Fenix-Variante zusätzlich: alle Punktsymbole (Quelle, Brunnen, Wasserversorgung, Gipfelkreuz, Denkmal, Spital, Heliport, Windturbine, Antennen, Lift, Durchfahrtssperre …), schraffierte offene Gebäude, Muster ab Auflösung 21, Berg-, Gewässer-, Flur-, Gelände- und Gebietsnamen, Ortsnamen in Schriftgrösse nach Einwohnerzahl, Landes-, Kantons-, Bezirks-, Gemeinde- und Nationalparkgrenze, Strassenschilder (Nationalstrassen, Hauptstrassen, 264 weitere Hauptstrassen-Nummern), Sport- und Freizeitanlagen, Fähren, Hafenstege. Einzelbäume (grünes Plus 3 × 3), Schutzverbauungen und Treppen erscheinen nur in der feinsten Zoomstufe. Vorschaubilder (Zeichnung aus Stil und TYP-Datei, kein Geräte-Rendering): `../../docs/vergleich/`.

## Wegen der Grösse in vier Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_edge_schweiz.img.part_* > swisstopo_vector_edge_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (305 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
