# SwissTOPO Relief Test Baden (Reliefschattierung auf dem Gerät)

Testkarte mit **eingebettetem Höhenmodell (DEM)**: Geräte, die Reliefschattierung unterstützen, zeichnen den Schattenwurf selbst. Raum Baden–Wettingen–Dättwil (gleiche sechs Kacheln wie `karten/routing_test/`, 388 km²), Edge-Variante von SwissTOPO Vector, routingfähig (`ROUTING=1`), Family-ID **3931**, Kartennummern **6395NNNN** (63952618–63952819), Name im Gerätemenü **«SwissTOPO Relief Test Baden»**. Gebaut am 2026-11-24 mit mkgmap r4924 (`scripts/build_dem_test.sh`, Technik und Daten: `docs/relief.md`). Stil und TYP: Stand des letzten Commits `a2498b6` (Strassenfarben nach VERKEHRSBD).

**Auf keinem Gerät geprüft.** Geprüft ist nur: mkgmap meldet 0 Fehler, und jede der 6 Kachel-Karten enthält eine DEM-Teildatei (FAT-Verzeichnis der IMG: `RGN, NET, NOD, LBL, TRE, DEM`). Ob und wie das Gerät das Relief zeichnet, ist offen.

## Dateien (je eine fertige gmapsupp-IMG mit TYP, nach `Garmin/` kopieren)
| Datei | `--dem-dists` | Grösse | gegenüber ohne DEM |
|---|---|---|---|
| `swisstopo_relief_test_baden_ohne_dem.img` | (kein DEM) | 5'832'704 B (5,8 MB) | Referenz |
| `swisstopo_relief_test_baden_dem3312.img` | 3312 (grob, **eine** Stufe) | 6'025'216 B (6,0 MB) | +192'512 B (+3,3 %) |
| `swisstopo_relief_test_baden_dem1648.img` | 1648 (fein, **eine** Stufe) | 6'345'728 B (6,3 MB) | +513'024 B (+8,8 %) |
| `swisstopo_relief_test_baden_dem3312_mehrstufig.img` | 3312,13248,26496,52992,105984 (**eine je Detailstufe**) | 6'061'056 B (6,1 MB) | +228'352 B (+3,9 %) |
| `swisstopo_relief_test_baden_dem1648_mehrstufig.img` | 1648,6592,13184,26368,52736 | 6'449'152 B (6,4 MB) | +616'448 B (+10,6 %) |

Die DEM-Daten selbst machen 185 kB (3312), 508 kB (1648), 221 kB bzw. 611 kB (mehrstufig) aus; der Rest ist Blockrundung. Die Karte hat fünf Detailstufen (Auflösung 24, 22, 21, 20, 18 Bit). mkgmap-Hilfe: «Für Geräte braucht es je Stufe einen Wert.» Die einstufigen Dateien haben deshalb nur **eine** DEM-Stufe (zusätzlich ist unklar, ob das Gerät sie bei anderen Zoomstufen verwendet); die mehrstufigen Dateien haben fünf. **Zuerst die beiden mehrstufigen Dateien testen**, die einstufigen sind Vergleich und Rückfall.

Höhendaten: swissALTIRegio (10 m, swisstopo) als HGT-Kachel N47E008 mit 1 Bogensekunde (3601 × 3601), Raum nördlich der Landesgrenze (Hochrhein, Südschwarzwald) ebenfalls aus dieser Datei (sie enthält die Randgebiete); am Rand zu viewfinderpanoramas.org überblendet, wo nötig.

## Was zu testen ist
1. Eine Datei nach `Garmin/` kopieren, Gerät neu starten, Karte im Karteninformations-Menü einschalten.
2. Reliefschattierung einschalten: **Edge 1040: Karteneinstellungen → Reliefschattierung** (Menüname je nach Firmware; ungeprüft). Fenix 5S Plus: Menüpunkt und ob das Gerät DEM überhaupt zeichnet, ist **ungeprüft**; Reliefschattierung kam bei Garmin mit den TopoActive-Karten, ob die Fenix 5 Plus mit einer fremden Karte schattiert, ist nicht belegt.
3. Prüfen: Erscheint ein Schattenwurf (Bergflanken, Hügel im Raum Baden, Lägern nördlich)? In welchen Zoomstufen? Gibt es Kanten an den Kachelgrenzen (47,4609° N; 8,2617° E; 8,3496° E)? Liegt die Schattierung unter den Flächen (Wald, Siedlung) oder deckt sie sie zu? Ist die Karte langsamer? Bildschirmfotos erwünscht.
4. Dieselbe Prüfung mit `..._ohne_dem.img` (gleicher Raum, gleiche Nummern) als Gegenprobe.

## Wichtig: nicht zusammen laden
- Die fünf Dateien tragen **dieselbe Family-ID 3931 und dieselben Kartennummern**: immer nur **eine** davon auf dem Gerät (oder die vorherige aus `Garmin/` nehmen), sonst kollidieren sie.
- **Nicht zusammen mit `karten/routing_test/swisstopo_vector_routing_test_baden.img`** (3930, 6394NNNN) und nicht zusammen mit den grossen Karten 3900/3901 aktiv haben: Alle decken denselben Raum ab, das Gerät zeichnet doppelt, und welche Karte routet, ist unklar. Die Nummern kollidieren nicht (3931/6395 gegen 3930/6394), die Überdeckung aber stört. Die Testkarte also in Karteninformationen allein einschalten (Overlays dürfen bleiben).
- Dies ist eine **Testkarte**: Das Relief gilt nur für den Raum Baden. Ausserhalb der sechs Kacheln gibt es weder Karte noch DEM.

## Offene Risiken
- Garmin zeichnet DEM nur auf Geräten mit Reliefschattierung und nur, wenn die Karte am Gerät als Hauptkarte mit DEM erkannt wird; bei mehreren Karten ist unklar, welche das Relief liefert. Ungeprüft.
- Einstufig/mehrstufig und die Werte 3312/1648 sind nach der mkgmap-Hilfe gewählt, nicht am Gerät. Falls nur eine Variante schattiert, bitte melden.
- Hochrechnung auf die ganze Schweiz: `docs/relief.md`.
