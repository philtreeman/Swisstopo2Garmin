# SwissTOPO Vector Fenix, ganze Schweiz

`swisstopo_vector_fenix_schweiz.img` (267 MB, Family-ID 3901, Name im Gerätemenü **«SwissTOPO Vector Fenix»**) aus swissTLM3D 2026-02. Gebaut mit `VARIANT=fenix scripts/build_vector.sh` (234 Kacheln à 20 × 20 km, eine TYP-Datei). Darstellung nach Bildschirmfotos der Garmin-Vektorkarte auf dem Edge 1040; die Muster für Fels und Reben sind aus diesen Fotos übernommen (persönlicher Gebrauch). **Auf keinem Gerät geprüft.**

Reduzierte Variante für die Fenix 5S Plus: Fels einfach grau, keine Namen ausser der Höhe an Gipfeln und Pässen, keine Grenzen, keine Strassenschilder, keine Sportplätze. Einzelbäume, Schutzverbauungen und Treppen erscheinen nur in der feinsten Zoomstufe.

## Wegen der Grösse in drei Teile zerlegt
GitHub erlaubt höchstens 100 MB je Datei. Zusammensetzen:
```
cat swisstopo_vector_fenix_schweiz.img.part_* > swisstopo_vector_fenix_schweiz.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```
Danach nach `Garmin/` auf das Gerät kopieren (267 MB freier Platz nötig). Höhenlinien und Routen-Overlays (`../overlay_hoehenlinien_schweiz/`, `../overlays_schweiz/`) lassen sich darüber legen. Daten: © swisstopo, Lizenz laut STAC «proprietär».
