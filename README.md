# swisstopo → Garmin: SwissTOPO Vector, Höhenlinien und Routen-Overlays

Dieses Repo baut aus offenen Bundesdaten Vektorkarten für Garmin-Geräte (`.img`):

- **SwissTOPO Vector Edge / Fenix** (`swisstopo_vector_edge_schweiz.img`, `swisstopo_vector_fenix_schweiz.img`): die Basiskarten der ganzen Schweiz aus swissTLM3D, zwei Varianten (Edge mit allen Details, Namen, Grenzen und Schildern; Fenix mit denselben Farben und Symbolen, aber reduziert), Darstellung nach der swisstopo-Zeichenerklärung.
- **Reliefschattierung (DEM)** ist in der Edge-Karte eingebettet (fein, mehrstufig; Edge 1040 getestet am Testausschnitt Baden; am Gerät unter Karteneinstellungen → Reliefschattierung einschalten). Die Fenix-Karte hat keins. Quelle: swissALTIRegio (swisstopo), am Landesrand viewfinderpanoramas.org (J. de Ferranti); siehe `docs/relief.md`.
- **Höhenlinien** (10 m und 20 m) und **Routen-Overlays** (Wanderwege, Wanderland, Veloland, Mountainbikeland, Skirouten): je eine **eigene Karte** mit eigener Family-ID, die auf eine Basiskarte gelegt wird (SwissTOPO Vector, die Garmin-Karte oder OpenTopoMap).
- **Hangneigung** und **Hangneigungsklassen** (ab 30°, wie swisstopo «Hangneigung über 30°»): zwei semitransparente Flächen-Overlays aus swissALTIRegio (10 m), siehe Abschnitt [Hangneigungs-Overlays](#hangneigungs-overlays).

**Teststand:**
- **Garmin Edge 1040: geprüft, funktioniert.** Der Nutzer hat Overlays für Skirouten, Wanderwege und Fahrradrouten aufs Gerät geladen. Mehrere `.img`-Dateien nebeneinander werden also geladen. Welche der beiden Fahrradkarten (Veloland, Mountainbike) einzeln geprüft wurde, ist nicht festgehalten.
- **Garmin Fenix 5S Plus: Test offen.** Ob die Uhr mehrere `.img` nebeneinander lädt und wie die Linien auf dem kleinen Display aussehen, ist ungeprüft.

Die Overlays:

| Datei | Inhalt | Darstellung |
|---|---|---|
| `swisstopo_overlay_wanderwege.img` | Wanderwegnetz der Schweiz (swissTLM3D, Stand 2026-07) | schwarz, nicht farbig codiert; Linienart nach Wegtyp wie in der swisstopo-Zeichenerklärung (2-m-Weg durchgezogen, 1-m-Weg gestrichelt, markierte Spur punktiert) |
| `swisstopo_overlay_wanderland.img` | Wanderland-Routen (SchweizMobil) | gelb |
| `swisstopo_overlay_veloland.img` | Veloland-Routen (SchweizMobil) | hellblau |
| `swisstopo_overlay_mountainbike.img` | Mountainbikeland-Routen (SchweizMobil) | orange |
| `swisstopo_overlay_skirouten_blau.img` | Skirouten (swisstopo/SAC u. a.) | blau, durchgezogen, weisser Rand (wie auf der Rasterkarte) |
| `swisstopo_overlay_skirouten_schwierigkeit.img` | gleiche Skirouten | gestrichelt, nach SAC-Schwierigkeit: grün L, blau WS, orange ZS, rot S, violett unbekannt |
| `swisstopo_overlay_skilifte.img` | Bahnen, die im Winter fahren (`ch.swisstopo.bahnen-winter`, wie Landeskarte Winter): Skilifte, Sessel-, Gondel-, Luftseil-, Standseilbahnen | wie Landeskarte Winter: Skilift ocker-orange mit Querstrichen, Sessel-/Gondelbahn dunkelrot mit Kreisen (Masten, in festem Abstand), Luftseilbahn dunkelrot 3 px, Standseilbahn rote Doppellinie mit Sprossen; Name erst in den feinen Zoomstufen |
| `swisstopo_overlay_unterkuenfte_winter.img` | Unterkünfte Winter (`ch.swisstopo.unterkuenfte-winter`, swisstopo/SAC), ergänzt um Hütten aus swissNAMES3D | roter Ring (13 px, `#FF1900`, innen leer, weisser Rand) wie im swisstopo-Viewer, schon weit herausgezoomt, Name mit Höhe ab mittlerer Zoomstufe («Kesch-Hütte SAC 2623»); nur in der feinsten Stufe zusätzlich kleine Häuser: braun = SAC-Hütte ausserhalb des Winter-Datensatzes, grau = übrige Hütte |
| `swisstopo_overlay_schneeschuhrouten.img` | Schneeschuhrouten (`ch.swisstopo-karto.schneeschuhrouten`, swisstopo/SAC und Winterwanderwege VS) | türkisgrün `#008A79`, durchgezogen, weisser Rand (wie swisstopo); Name mit WT-Schwierigkeit in der feinsten Stufe |
| `swisstopo_overlay_skipisten.img` | **OpenStreetMap** (nicht swisstopo): Pisten `piste:type=downhill` (9'158 Linien, 919 Flächen), Langlauf `nordic` (5'348), Schlitteln `sled` (610); Skitouren (`piste:type=skitour`) bewusst nicht enthalten, dafür die Skirouten-Overlays (Family-ID 3915/3916); Auszug OpenStreetMap France vom 2026-11-11 | Abfahrt blau (novice/easy), rot (intermediate), schwarz (advanced/expert), orange gestrichelt (freeride/extreme), grau (unbekannt); 3 px mit 1 px weissem Rand; Langlauf grün gestrichelt, Schlitteln braun gestrichelt; Pistenflächen halbdurchsichtig (Schachbrett) mit 1-px-Umriss; Name ab der feinen Zoomstufe; Menü «OSM Skipisten» |
| `swisstopo_overlay_hoehenlinien.img` | Höhenlinien, Äquidistanz 20 m (swissALTI3D 2 m) | hellbraun; alle 100 m dunkler und stärker, mit Höhenangabe |
| `swisstopo_overlay_hangneigung.img` | Hangneigung in 8 Stufen ab 10° (swissALTIRegio 10 m, Klassen auf 20-m-Raster) | semitransparent (Punktmuster): 10–20° hellgrün, 20–25° grün, 25–30° dunkelgrün (je 25 % der Pixel), ab 30° wie die Klassen-Karte (50 %); unter 10° leer |
| `swisstopo_overlay_hangneigungsklassen.img` | Lawinen-Hangneigungsklassen ab 30° wie `ch.swisstopo.hangneigung-ueber_30` (10-m-Raster) | semitransparent (Schachbrett, 50 % der Pixel): 30–35° gelb `#F2E50A`, 35–40° orange `#F46F24`, 40–45° rot `#DE055B`, 45–50° violett `#C889BB`, über 50° grau `#4B4B4B` (Farben an der WMTS-Ebene gemessen) |

Die Routen von SchweizMobil tragen «Nummer Name» als Beschriftung (z. B. «1 Via Alpina»), die Skirouten «Name Schwierigkeit». Bei Wanderland, Veloland und Mountainbikeland sind die Linien nach national (breit), regional und lokal gestuft.

Fertige Dateien liegen im Ordner `karten/` (siehe unten).

![Vorschau Oberiberg](karten/overlays_oberiberg_test/vorschau.png)

*Vorschau: eigene Zeichnung mit denselben Farben über einer grauen Landeskarte, kein Rendering vom Gerät.*

## Fertige Karten (`karten/`)

| Ordner | Inhalt | Grösse |
|---|---|---|
| `karten/overlay_hoehenlinien_schweiz/` | Höhenlinien 10 m und 20 m, ganze Schweiz, je in 2 Teilen (zusammensetzen mit `cat`, siehe README im Ordner) | 168 MB und 109 MB |
| `karten/swisstopo_vector_edge_schweiz/` | **SwissTOPO Vector Edge**, ganze Schweiz, in 5 Teilen, routingfähig, **mit Reliefschattierung (DEM)** (zusammensetzen mit `cat`, siehe README im Ordner) | 415 MiB (434'896'896 Byte, 5 Teile, mit Reliefschattierung) |
| `karten/swisstopo_vector_fenix_schweiz/` | **SwissTOPO Vector Fenix**, ganze Schweiz, in 4 Teilen, routingfähig | 278 MiB (291'209'216 Byte) |
| `karten/overlays_schweiz/` | alle Overlays einzeln, ganze Schweiz (Routen, Haltestellen, Winter, Skipisten, Hangneigung) | 137 MB, davon Hangneigung 75 MB und Hangneigungsklassen 45 MB |
| `karten/overlays_oberiberg_test/` | alle 6 Overlays, Testausschnitt Oberiberg SZ (ca. 40 × 40 km) plus `vorschau.png` | 0,8 MB |
| `karten/relief_test/` | Reliefschattierung-Testkarte Baden (Family-ID 3931, fünf DEM-Varianten); ersetzt durch das DEM in der Edge-Karte, nützlich für den Fenix-Test | 6 MB je Datei |
| `karten/routing_test/` | **SwissTOPO Vector Routing Test** (Family-ID 3930): Edge-Variante als routingfähige Karte, Raum Baden–Wettingen–Dättwil, mit Testanleitung (siehe [Routing](#routing-status-test)) | 5,8 MB |

Installation: gewünschte `.img` nach `Garmin/` auf das Gerät kopieren (USB), neu starten, unter Einstellungen → Karte aktivieren. Eine vorhandene `gmapsupp.img` nicht überschreiben.

## Datenquellen

Alle Daten ausser den Skipisten (OpenStreetMap, siehe Tabelle) sind offen auf `data.geo.admin.ch` verfügbar (STAC-Collection in Klammern). Die Lizenz steht dort als «proprietary»; die Nutzungsbedingungen von swisstopo bzw. ASTRA/SchweizMobil gelten. Repo daher nicht öffentlich machen, ohne sie geprüft zu haben.

| Ebene | Datensatz | Stand |
|---|---|---|
| Wanderwege | swissTLM3D Wanderwege, Layer `tlm_strassen_strasse` mit Feld `wanderwege` (`ch.swisstopo.swisstlm3d-wanderwege`), 409'276 Abschnitte | 2026-07 |
| Wanderland, Veloland, Mountainbikeland | SchweizMobil, Layer `Route` (`ch.astra.wanderland`, `ch.astra.veloland`, `ch.astra.mountainbikeland`) | 2026-02 |
| Skirouten | `ch.swisstopo-karto.skitouren`, 10'789 Routen: swisstopo/SAC 9'384, Petzl Foundation/Skitourenguru 884, DAV/ÖAV/AVS 439, topo.verlag 82 (Feld `source`) | 2025-12 |
| SwissTOPO Vector | swissTLM3D (`ch.swisstopo.swisstlm3d`), Ausgabe 2026-02 | 2026-02 |
| Skilifte | Bahnen Winter (`ch.swisstopo.bahnen-winter`, swisstopo/SAC, jährlich nachgeführt, in der Schweiz eine Auswahl aus swissTLM3D), 1'805 Bahnen: 840 Skilifte, 361 Sesselbahnen, 137 Gondelbahnen, 193 Luftseilbahnen, 251 Standseilbahnen, 23 andere; inkl. grenznaher Gebiete im Ausland | 2025-11-20 |
| Unterkünfte Winter | `ch.swisstopo.unterkuenfte-winter` (swisstopo/SAC), alle 506 Unterkünfte als roter Ring; dazu aus swissNAMES3D 2026 (`ch.swisstopo.swissnames3d`, Gebäudenamen) 27 SAC-Hütten, die nicht im Winter-Datensatz stehen (Name enthält «SAC» oder «CAS»; ein Eigentümer-Attribut gibt es nicht), und 987 übrige Hütten (Schutzhütten, andere Clubhütten, Biwaks, Name mit Hütte, Cabane, Refuge, Capanna, Berghaus …; ohne Forst-/Waldhütten); Punkte unter 250 m neben einem Punkt mit Vorrang weggelassen | 2025-11-20 / 2026 |
| Schneeschuhrouten | `ch.swisstopo-karto.schneeschuhrouten`, Datei `snowshoe_routes_2056.gpkg`, 2'825 Routen (4'630 km): swisstopo/SAC 2'485, Winterwanderwege Kt. VS 340; 292 mit Name und WT-Schwierigkeit | 2025-12-11 |
| Skipisten | **OpenStreetMap** (Auszug OpenStreetMap France, `https://download.openstreetmap.fr/extracts/europe/switzerland-latest.osm.pbf`, 684 MB, Stand 2026-11-11), Tags `piste:type`, `piste:difficulty`, `piste:name`; Geofabrik war von der Cloud-Umgebung aus nicht erreichbar. **Lizenz ODbL, © OpenStreetMap-Mitwirkende** (<https://www.openstreetmap.org/copyright>); die Namensnennung steht auch in der Karte (`--copyright-message`). Der Auszug ist an der Landesgrenze beschnitten, grenznahe Pisten im Ausland fehlen | 2026-11-11 |
| Höhenlinien | swissALTI3D (`ch.swisstopo.swissalti3d`), 2-m-Raster, neuestes Jahr je 1-km-Kachel | 2019–2026 |
| Hangneigung | swissALTIRegio (`ch.swisstopo.swissaltiregio`), 10-m-Raster, eine Cloud-Optimized-GeoTIFF-Datei (10 GB, es werden nur die Ausschnitte gelesen); begrenzt auf Schweiz + Liechtenstein + 1 km aus swissBOUNDARIES3D (`ch.swisstopo.swissboundaries3d`, Layer `tlm_landesgebiet`) | 2026-05 / 2026-01 |

## Aufbau des Repos

```
README.md                      diese Datei
AGENTS.md                      Kontext für KI-Assistenten (Ziel, Entscheide, Stand)
scripts/                       alle Skripte
  download_daten.sh              lädt die Overlay-Datensätze von data.geo.admin.ch
  build_overlays.sh              baut die 6 Overlay-.img (Hauptskript, siehe unten)
  routes2mkgmap.py                  GeoPackage → OSM-XML für die Routen-Overlays
  make_overlay_typ.py            schreibt die TYP-Dateien (Farben, Breiten, Muster)
  mkgmap_xml_writer.py                  gemeinsame OSM-XML-Ausgabe
  build_skilifte.sh              baut das Skilifte-Overlay (skilifte2mkgmap.py, make_skilifte_typ.py)
  build_unterkuenfte_winter.sh   baut das Overlay Unterkünfte Winter (unterkuenfte2mkgmap.py, make_unterkuenfte_typ.py)
  build_schneeschuhrouten.sh     baut das Schneeschuhrouten-Overlay (routes2mkgmap.py --kind schneeschuh, make_schneeschuh_typ.py)
  build_skipisten.sh             baut das Skipisten-Overlay aus OpenStreetMap (skipisten2mkgmap.py, make_skipisten_typ.py; braucht pyosmium)
  build_hoehenlinien.sh          baut das Höhenlinien-Overlays (10 m und 20 m) aus swissALTI3D
  hoehenlinien2mkgmap.py            swissALTI3D-Kacheln → Höhenlinien als OSM-XML
  swissalti3d_kachelliste.py     listet alle swissALTI3D-Kacheln (neuestes Jahr)
  build_hangneigung.sh           baut die Overlays Hangneigung und Hangneigungsklassen aus swissALTIRegio
  hangneigung2mkgmap.py             Höhenmodell → Neigung → Klassenflächen als OSM-XML
  make_hangneigung_typ.py        schreibt die beiden TYP-Dateien (Farben, Punktmuster)
  preview_hangneigung.py         Vergleichszeichnung gegen die swisstopo-WMTS-Ebenen
  build_vector.sh                baut SwissTOPO Vector (ganze Schweiz oder Region)
  vector2mkgmap.py                  swissTLM3D-Shapefiles → OSM-XML
  make_vector_typ.py             schreibt die TYP-Datei (Farben, Muster, Linien; --fid, --routing für Testkarten)
  vector_palette.py              Farben von SwissTOPO Vector (swisstopo-Zeichenerklärung)
  vector_patterns.py             Flächenmuster, vector_shields.py Strassenschilder, kantonsschilder.py Kantonsstrassen-Nummern
  style_eval.py, typ_read.py     Auswertung von Stil und TYP für die Vorschau
  preview_legende.py             Vorschau mit Mustern, Linien und Punkten; preview_tafel.py: Tafel aller Signaturen
  preview_vector.py              Vorschau-Zeichnung von SwissTOPO Vector
mkgmap/
  overlays/style/                mkgmap-Regeln: Tags → Garmin-Linientypen
  overlays/typ/                  erzeugte TYP-Dateien, eine je Overlay
  vector/style/, typ/            dasselbe für SwissTOPO Vector
karten/                        fertige Karten
experimente/                   Einzelversuche, nicht Teil der Pipeline
```

## Eigene Karten bauen

### Voraussetzungen
- Python 3 mit `pyogrio shapely pyproj numpy` (für die Vorschau zusätzlich `geopandas matplotlib`), z. B. `python3 -m venv venv && venv/bin/pip install pyogrio shapely pyproj numpy geopandas matplotlib`
- Java (getestet mit 21) und **mkgmap** (getestet r4924): <https://www.mkgmap.org.uk/download/mkgmap.html>
- Rund 1 GB Festplatte für die Daten, 15 GB RAM sind komfortabel (die Schweiz wird in 4 Kacheln gebaut)
- Internetzugang zu `data.geo.admin.ch`

### Schritte
```
scripts/download_daten.sh daten/                       # einmalig, ca. 750 MB
scripts/build_overlays.sh daten/ mkgmap/mkgmap.jar out/                      # ganze Schweiz
scripts/build_overlays.sh daten/ mkgmap/mkgmap.jar out/ 8.50 46.85 9.05 47.21   # nur eine Region (W S E N)
```
Ergebnis: `out/swisstopo_overlay_*.img`. Die ganze Schweiz braucht einige Minuten. Bereits berechnete Zwischenstände (`out/osm/`) werden wiederverwendet; zum Neuberechnen löschen.

### Was `build_overlays.sh` tut
Das Skript baut aus den GeoPackages die sechs `.img`-Dateien:

1. **Kacheln festlegen.** Mit Bounding Box eine Kachel, sonst die Schweiz in 2 × 2 Kacheln, damit der Speicher reicht.
2. **Konvertieren** (`routes2mkgmap.py`). Liest je Ebene das GeoPackage, schneidet die Linien auf die Kachel zu, vereinfacht sie (2 m) und schreibt OSM-XML mit den Tags `route_layer` (wanderwege, wanderland, veloland, mtb, ski), `route_class` (z. B. national/regional/lokal, Wanderweg/Berg/Alpin, SAC-Klasse 1–4) und `name`. Hin- und Rückweg identischer SchweizMobil-Routen werden nur einmal geschrieben.
3. **TYP-Dateien schreiben** (`make_overlay_typ.py`). Pro Overlay eine TYP-Datei mit eigener Family-ID: Farben, Linienbreiten, Strichmuster.
4. **mkgmap aufrufen**, einmal je Overlay. mkgmap liest die OSM-Dateien, ordnet über `mkgmap/overlays/style/lines` jedem Tag-Satz einen Garmin-Linientyp zu und verpackt alles mit der TYP-Datei in eine `gmapsupp.img`. Der Name im Gerätemenü kommt aus `--description`.
5. **Umbenennen** nach `swisstopo_overlay_<name>.img` im Ausgabeordner.

| Overlay | Family-ID | Mapname (64 + Family-ID + laufende Nr.) |
|---|---|---|
| Wanderwege | 3911 | 64391101 bis 64391104 (4 Kacheln) |
| Wanderland | 3912 | 643912xx |
| Veloland | 3913 | 643913xx |
| Mountainbikeland | 3914 | 643914xx |
| Skirouten blau | 3915 | 643915xx |
| Skirouten nach Schwierigkeit | 3916 | 643916xx |
| Haltestellen | 3918 | 64391801 |
| Skilifte (`scripts/build_skilifte.sh`) | 3921 | 64392101 |
| Unterkünfte Winter (`scripts/build_unterkuenfte_winter.sh`) | 3922 | 64392201 |
| Schneeschuhrouten (`scripts/build_schneeschuhrouten.sh`) | 3923 | 64392301 |
| Skipisten (`scripts/build_skipisten.sh`, OSM) | 3926 | 64392601 |
| Hangneigung (`scripts/build_hangneigung.sh`) | 3924 | 64392401 bis 64392444 (44 Blöcke à 40 km) |
| Hangneigungsklassen (`scripts/build_hangneigung.sh`) | 3925 | 64392501 bis 64392544 |

### Aussehen anpassen
- **Farben, Breiten, Strichmuster:** `scripts/make_overlay_typ.py` (Konstanten oben: `YELLOW`, `LBLUE`, `ORANGE`, `SKI_BLUE`, Breiten je Kategorie). Danach `build_overlays.sh` neu starten; die OSM-Zwischendateien werden wiederverwendet.
- **Zuordnung Kategorie → Linientyp:** `mkgmap/overlays/style/lines`.
- **Ab welchem Zoom sichtbar:** `resolution`-Werte in `mkgmap/overlays/style/lines` (höher = erst bei stärkerer Vergrösserung).

### Technische Fallstricke (mkgmap)
- `--style-file` zeigt direkt auf das Style-Verzeichnis. Mit zusätzlichem `--style=.` nutzt mkgmap still den Standard-Style und ignoriert die eigenen Tags.
- Erweiterte Linientypen: Code `0x10f00`–`0x10f1f` (Subtyp höchstens `0x1f`), Skirouten `0x11000`–`0x11004`.
- Die TYP-Compiler-Fehler sind stumm (nur `MapFailedExceptions: 1`). Muster-Linien brauchen Breite 32 (`Xpm="32 H N 1"`), und die durchsichtige Farbe (`none`) muss in der Farbtabelle **zuerst** stehen.
- `--mapname` hat 8 Ziffern und muss über **alle** geladenen `.img`-Dateien eindeutig sein. Schema: Vektorkarten `6390NNNN` (Edge) und `6391NNNN` (Fenix), Höhenlinien `6392NNNN` (20 m) und `6393NNNN` (10 m), mit NNNN = i*100+j der 20-km-Kachel. Overlays: `64` + Family-ID (4 Ziffern) + laufende Nummer (2 Ziffern, 01..99), z. B. Wanderwege `64391101`–`64391104`. Das Präfix 64 kann nie mit 6390–6393 kollidieren (frühere Overlay-Nummern wie `63911001` kollidierten mit Fenix-Kacheln).
- Polygone erscheinen nur, wenn sie im TYP unter `[_drawOrder]` stehen (relevant für SwissTOPO Vector).

## Höhenlinien-Overlay (`swisstopo_overlay_hoehenlinien.img`)
`scripts/build_hoehenlinien.sh` berechnet aus swissALTI3D (2 m Raster) Höhenlinien mit **20 m Äquidistanz** für die ganze Schweiz (109 MB, Family-ID 3917). Jede 50 m eine Zwischenlinie, jede 100 m eine Hauptlinie, beide mit Höhenangabe. Es ist ein Overlay: es lässt sich über die Basiskarte und die Routen-Overlays legen. Auf keinem Gerät geprüft.
```
scripts/swissalti3d_kachelliste.py tiles_2m.json                  # einmalig, 15–20 Minuten
scripts/build_hoehenlinien.sh tiles_2m.json mkgmap.jar out/                     # ganze Schweiz
scripts/build_hoehenlinien.sh tiles_2m.json mkgmap.jar out/ 8.24 47.44 8.38 47.51   # Region
```
Ablauf: 20-km-Blöcke im LV95-Raster → je Block parallel (3 Prozesse) die 1-km-Kacheln laden (ca. 1 MB je Kachel, die ganze Schweiz sind rund 45 GB Download, nichts davon wird gespeichert), mit `contourpy` Linien im Abstand von 10 m berechnen, mit 2,5 m vereinfachen, als OSM-XML schreiben, mit mkgmap zur Block-Karte bauen, am Ende alle Blöcke und die TYP-Datei zusammenführen. Dauer für die ganze Schweiz: etwa 40 Minuten. Fortsetzbar. Die Linien liegen im Typ `0x20` (10 m), `0x21` (50 m), `0x22` (100 m); Farben und Breiten stehen in `scripts/make_overlay_typ.py`, Sichtbarkeit je Zoom in `mkgmap/overlays/style/lines`.

## Skipisten-Overlay (OpenStreetMap)
`swisstopo_overlay_skipisten.img` (Family-ID 3926, Kartennummer 64392601, Menü «OSM Skipisten», 1,3 MB) ist die **einzige Karte im Repo aus OpenStreetMap**, auf ausdrücklichen Wunsch des Nutzers; alle übrigen Daten stammen von swisstopo/ASTRA. Daten © OpenStreetMap-Mitwirkende, ODbL: die Karte enthält den Hinweis, bei Weitergabe die Namensnennung beibehalten.
```
scripts/build_skipisten.sh switzerland-latest.osm.pbf mkgmap.jar out/                        # ganze Schweiz, ca. 3 Minuten
scripts/build_skipisten.sh switzerland-latest.osm.pbf mkgmap.jar out/ 9.75 46.75 9.95 46.90   # Region
```
- **Ablauf:** `skipisten2mkgmap.py` liest den Auszug mit pyosmium (Relationen, Wege, Knoten in drei Durchgängen), baut Linien und Flächen (Multipolygone mit shapely) und schreibt OSM-XML mit `piste_layer` (downhill, nordic, sled), `piste_class` (blue, red, black, orange, grey) und `name` (`piste:name`, sonst `name`, `piste:ref`, `ref`); danach mkgmap und TYP (`make_skipisten_typ.py`).
- **Zählung (Stand 2026-11-11):** Abfahrt 10'077 Objekte (Linien 9'158, Flächen 919): easy 4'636, intermediate 3'739, advanced 930, freeride 339, novice 273, expert 20, ohne Angabe 137 (der Rest sind Tippfehler wie «eaasy» und «difficult», grau). Langlauf 5'348 (easy 3'052, intermediate 1'149, novice 510, advanced 213, ohne Angabe 421), Schlitteln 610 (Skitouren wurden am 2026-11-17 entfernt: der Nutzer hat eigene Skirouten-Overlays). Schlitteln trägt oft kein `piste:difficulty`. Vorschau (eigene Zeichnung, kein Geräte-Rendering): `karten/overlays_schweiz/vorschau_skipisten.png`, erzeugt mit `scripts/preview_skipisten.py`.
- **Farben** (europäische Konvention, nach `piste:difficulty`): novice/easy blau `#0B5CD6`, intermediate rot `#E01B1B`, advanced/expert schwarz, freeride/extreme orange `#FF8A00` gestrichelt, unbekannt grau. Linien 3 px mit 1 px weissem Rand. Flächen (nur Abfahrt): Schachbrett aus Farbe und `none` plus 1-px-Umriss; die Schwierigkeit gilt für die ganze Fläche.
- **Typen und Zoom:** erweiterte Linientypen `0x10f00`–`0x10f0c`, Flächentypen `0x10e00`–`0x10e04` (in keiner anderen TYP-Datei belegt). Linien ab Auflösung 20, Flächen ab 20, Umrisse ab 21, Namen ab 22. Draw-Priority 30.
- **Grenzen:** der OSM-France-Auszug ist an der Landesgrenze beschnitten (Koordinatenbereich 6,04–10,52 E, 45,87–47,79 N); Pisten jenseits (z. B. Portes du Soleil auf französischer Seite) fehlen. Pisten sind in OSM unterschiedlich gut gepflegt; offene, nicht präparierte Pisten und Freeride-Linien sind keine Sicherheitsangabe. **Auf keinem Gerät geprüft** (Darstellung der Muster mit `none`, Lesbarkeit, Namen).

## Hangneigungs-Overlays
Zwei Flächen-Overlays aus derselben Neigungsberechnung, je eine eigene Karte (auf keinem Gerät geprüft):

| Datei | Gerätemenü | Family-ID | Inhalt | Raster | Grösse |
|---|---|---|---|---|---|
| `swisstopo_overlay_hangneigung.img` | «swisstopo Hangneigung» | 3924 | 10–20, 20–25, 25–30, 30–35, 35–40, 40–45, 45–50, > 50° (unter 10° leer) | 20 m | 75 MB |
| `swisstopo_overlay_hangneigungsklassen.img` | «swisstopo Hangneigungsklassen» | 3925 | nur die Lawinenklassen 30–35, 35–40, 40–45, 45–50, > 50° | 10 m | 45 MB |

```
scripts/build_hangneigung.sh swissBOUNDARIES3D_1_5_LV95_LN02.gpkg mkgmap.jar out/                        # ganze Schweiz
scripts/build_hangneigung.sh swissBOUNDARIES3D_1_5_LV95_LN02.gpkg mkgmap.jar out/ 9.75 46.75 9.95 46.90   # Region
```
- **Daten:** swissALTIRegio (10 m) statt swissALTI3D: swisstopo bietet die Neigung nicht als Datensatz an (im STAC gibt es keine Collection dazu, nur die WMTS-Ebenen), und swissALTI3D gibt es nur in 0,5 m und 2 m (45 GB Download für die Schweiz). swissALTIRegio ist ein einziges Cloud-Optimized GeoTIFF; das Skript liest nur die Blockausschnitte (rund 3 GB Download für die Schweiz, nichts wird gespeichert). Die swisstopo-Ebenen «Hangneigung ab 30°» sind laut Beschreibung ebenfalls aus einem 10-m-Modell abgeleitet.
- **Neigung:** Horn-Verfahren (3 × 3 Zellen, wie `gdaldem slope`) auf 10 m. Abgleich mit der WMTS-Ebene `ch.swisstopo.hangneigung-ueber_30` (Raum Davos, Zoom 14, 262'000 Pixel, davon 93'600 farbig): bei 99,9 % der Pixel fällt die eigene Neigung in dieselbe Klasse wie bei swisstopo (Median gelb 32,5°, orange 37,2°, rot 41,6°, violett 46,7°, grau 52,2°); swisstopo rechnet also offenbar gleich. Daraus auch: swisstopo hat eine fünfte Klasse **über 50° (grau `#4B4B4B`)**.
- **Flächen:** Klassenraster → Flecken unter 400 m² gehen in der Nachbarklasse auf (`rasterio.features.sieve`) → Polygone (`rasterio.features.shapes`) → gemeinsam vereinfacht als Flächendeckung (`shapely.coverage_simplify`, 0,6 × Rasterweite, Nachbarflächen behalten die gemeinsame Kante) → exakt am Blockrand zugeschnitten. Die Karte Hangneigung nutzt das Mittel von 2 × 2 Zellen (20 m), weil sie mit 10 m hochgerechnet rund 100 MB gross würde (Testregion Davos: 0,85 statt 0,65 MB) und für die Übersicht unter 30° kein 10-m-Detail braucht; die Klassen-Karte bleibt bei 10 m.
- **Dauer und Bedarf:** ganze Schweiz rund 26 Minuten (4 Kerne, `JOBS=3`, je Block bis etwa 3 GB RAM und bis 1,3 GB OSM-Zwischendatei, die gleich wieder gelöscht wird). Python braucht zusätzlich `rasterio` (`venv/bin/pip install rasterio`).
- **Blöcke:** 40 × 40 km im LV95-Raster (Ursprung 2480000/1070000, also je 2 × 2 der 20-km-Kacheln der anderen Karten), 44 Blöcke. Grund: das Nummernschema `64<FamilyID>NN` erlaubt höchstens 99 Kacheln, mit 20 km wären es 148.
- **Semitransparent:** Garmin-TYP kennt kein Alpha. Jede Klasse ist ein 32 × 32-Muster aus einer Farbe und `none` (durchsichtig): ab 30° Schachbrett (50 % der Pixel farbig), unter 30° jeder zweite Pixel jeder zweiten Zeile (25 %). Ein Dichtetest (eigene Zeichnung) zeigte: 25 % ist für die Lawinenklassen zu blass (gelb verschwindet fast), 50 % für die grossen Flächen unter 30° zu deckend. Dichte änderbar mit `scripts/make_hangneigung_typ.py --dichte 50|25 --dichte-flach 50|25`.
- **Typen und Zoom:** erweiterte Flächentypen `0x10e0d`–`0x10e0f` (unter 30°) und `0x10e1b`–`0x10e1f` (ab 30°), in keiner anderen TYP-Datei des Repos belegt; Standardtypen vermieden, weil ein Kartenthema sie umfärben kann. Sichtbar ab Auflösung 20 (`mkgmap/hangneigung/style/polygons`), Ebenen `0:22, 1:20` (die feinste Ebene 22 statt 24 halbiert die Dateigrösse, die Koordinaten sind dann auf rund 5–10 m gerundet, passend zum 10-m-Raster). `--draw-priority=26`: über SwissTOPO Vector (20), unter den Linien-Overlays (30).
- Die Neigung ist eine Planungshilfe; sie ersetzt weder Lawinenbulletin noch Beurteilung vor Ort. Nahe der Landesgrenze stammt swissALTIRegio aus den Modellen der Nachbarländer (Genauigkeit laut swisstopo dort nicht garantiert).

![Vorschau Hangneigung](karten/overlays_schweiz/vorschau_hangneigung.png)

*Raum Davos, Schiahorn (Zoom 15): links eigene Zeichnung der beiden Overlays mit den TYP-Mustern 1:1 über der grauen Landeskarte, rechts die swisstopo-WMTS-Ebenen. Eigene Zeichnung, kein Rendering vom Gerät.*

## SwissTOPO Vector, zwei Varianten (Family-ID 3900 und 3901)
Vektorkarten der ganzen Schweiz aus swissTLM3D (Stand 2026-02), je eine Datei in vier Teilen wegen der GitHub-Grenze von 100 MB. **Seit 2026-11-24 folgt die Darstellung strikt der swisstopo-Zeichenerklärung «Landeskarten 1:10 000, 1:25 000 und 1:50 000»** (Farben, Muster und Symbole am PDF gemessen, `scripts/vector_palette.py`); die frühere Darstellung nach Bildschirmfotos der Garmin-Karte ist ersetzt, ebenso die daraus ausgelesenen Fels- und Rebenmuster (`vector_pattern_tiles.py` entfällt). Es gibt nur noch **eine** Darstellung: die vier TYP-Dateien (`edge`, `fenix`, `edge_swisstopo`, `fenix_swisstopo`) sind bis auf die Family-ID gleich. **Auf keinem Gerät geprüft.**

| | **SwissTOPO Vector Edge** (3900) | **SwissTOPO Vector Fenix** (3901) |
|---|---|---|
| Ordner | `karten/swisstopo_vector_edge_schweiz/` | `karten/swisstopo_vector_fenix_schweiz/` |
| Grundsatz | voller Detailgrad der Legende | gleiche Farben und Symbole, aber **Details weggelassen** statt vereinfachte Stile zu erfinden |
| Gebäude | schwarz; offene Gebäude, Treibhäuser, Flugdächer schraffiert | alle schwarz, keine Untertypen |
| Muster (Fels, Geröll, Wald offen, Gebüschwald) | ab Auflösung 21 (Fels, Geröll, Wald offen, Gebüschwald) | erst ab Auflösung 22 |
| Punktsymbole (Quelle, Brunnen, Gipfelkreuz, Denkmal, Spital, Heliport, Windturbine, Antennen, Lift, Durchfahrtssperre, Raststätte, Autoverlad) | ja | nein; nur Höhenkoten an Gipfeln und Pässen |
| Einzelbäume | grünes Plus 3 × 3, eine pro 70-m-Zelle, nur feinste Stufe | wie Edge (nur feinste Stufe) |
| Namen | Orts- (Schrift nach Einwohnerzahl), Strassen-, Gewässer-, Flur-, Gelände-, Gebietsnamen, Berge mit Höhe | nur die Höhe an Gipfeln und Pässen |
| Grenzen (swissBOUNDARIES3D) | Landes-, Kantons-, Bezirks-, Gemeindegrenze, Nationalparkgrenze | keine (Nationalpark ebenfalls nicht) |
| Strassenschilder | Nationalstrassen, Hauptstrassen (ASTRA) und 264 weitere Hauptstrassen-Nummern (swissTLM3D) | keine |
| Weitere Ebenen | Sport- und Freizeitanlagen, Sportbauten, Hafenstege, Fähren | Freizeitanlagen (nur Fläche) |

### Darstellung nach der Zeichenerklärung (Stand 2026-11-24)
Typnummern nach Art: Flächen `0x4b`…`0x10e0f`, Linien `0x01`…`0x1f`, `0x10e00`–`0x10e1f` (Strassen, Brücken, Tunnel, Galerien, Grenzen) und `0x11300`–`0x11315` (neu), Punkte `0x10f00` (Einzelbaum), `0x11300`–`0x1130f` (neu), Schilder `0x10f01`–`0x10f19`, `0x11100`–`0x11217`, `0x11400`–`0x11c07`.

| Element | Darstellung (Typ) |
|---|---|
| Untergrund | `#FEFFED` (0x4b); das abgeleitete graue Siedlungsgebiet entfällt (nicht in der Legende) |
| Wald | `#CBE5D3` (0x50); **Wald offen** grüne 2 × 2-Punkte `#00964E` ca. 8 % (0x10e01); **Gebüschwald** 1-px-Punkte ca. 12 % (0x10e02); **Gehölz/Hecke** Punkte (0x4f) |
| Obstanlage, Baumschule, Reben | auf Weiss: Punktraster 4 px mit 1-px-Punkt (0x10e08), dichter 3-px-Raster mit versetzten Reihen (0x10e09), senkrechte kurze Striche (0x4e); alle `#00964E` |
| Einzelbaum | grünes Plus 3 × 3, Ecken durchsichtig (0x10f00) |
| Fels, «Fels locker» | schwarze Striche, ca. 12 % (0x52); früher graue Fläche |
| **Felsblöcke** (Blockfeld) | kleine unregelmässige schwarze Blockumrisse auf Untergrundfarbe, 8 Umrisse à 3–5 px je 32 × 32-Kachel (teils eine Ecke abgeschnitten, teils offen), ca. 9 % (0x10e10); **«Felsblöcke locker»** gleiche Art mit halber Blockzahl (4 Umrisse), ca. 5 % (0x10e11). Zeichenreihenfolge Stufe 3 nach Geröll und Fels. Muster **nicht lagetreu** (Zufallsverteilung, keine einzelnen Blöcke) und **auf dem Gerät ungeprüft**; Vorschau `docs/vergleich/legende_vorschau_bloecke.png` (Engstligenalp, kein Geräte-Rendering) |
| Geröll (Lockergestein, auch «locker») | schwarze Punkte, Dichte 0.06 (0x53) |
| **Gletscher, Schneefeld/Toteis** | weiss mit blauen Eisstruktur-Strichen `#6EC1EE` (32 × 32-Muster, ca. 7 %, 0x10e00; Vorschau `docs/vergleich/legende_vorschau_gletscher_blau.png`; vorher einfarbig weiss) |
| Feuchtgebiet | kurze waagrechte Striche `#008AD2`, 32-px-Muster, Reihen versetzt (0x51) |
| Seen, Flussflächen | `#D4EDFC` (0x3f), `#BCE4FA` (0x10e03); **See mit wechselndem Wasserstand** heller `#E9F5FD` (0x10e0f, aus `WSTAND_WE`); Seeinsel Untergrundfarbe (0x10e0e; vorher fälschlich Rebenmuster) |
| Bäche, Flüsse, Suonen | `#008AD2`, 1 px (0x18), jetzt für `VERLAUF` oberirdisch, Wasserfall und Brücke (schliesst Lücken; vorher nur `STUFE=0`); Seeufer als eigene Linie (0x11315, nur Seen ab 150 m Umfang); Druckleitung mit Querstrichen (0x11308), Druckstollen gestrichelt (0x11309), Trockenrinne schwarz gepunktet 1/2 (0x10e03), Gewässerverbauung blaue Linie (0x1130a, nur feinste Stufe), Hafensteg schwarz (0x1130b) |
| Gewässernamen | blau `#008AD2` über Schriftfarbe der TYP-Datei (Flächen 0x3f/0x10e0f, Linien 0x18) – ob das Gerät die Farbe übernimmt, ungeprüft |
| Bahn | rot `#E3000B`: Normalspur 3 px (0x14), Schmalspur/Kleinbahn 2 px (0x11300), Anschlussgleis und Tram 1 px (0x11301), Tunnel rot gestrichelt 4/3 (0x10e14), Galerie mit Kästchenreihe (0x11302); **Bahnübergang-Balken entfällt** (nicht in der Legende, `0x10e19` ungenutzt) |
| Seilbahnen | Luftseilbahn rot 2 px (0x11303), Gondel-/Sesselbahn rot 1 px (0x11304), Transportseil und «ausser Betrieb» schwarz 1 px (0x11305), Skilift `#CE7611` mit Querstrichen (0x11306), Förderband schwarz mit Punkten (0x11307), Lift als rotes Quadrat (Punkt 0x1130a); keine Masten |
| Grenzen (Edge) | Landesgrenze `#E5007C` 2 px mit Band `#F5B4D2` (0x10e0a), Kantonsgrenze 1 px mit Band (0x10e0b), Bezirksgrenze `#F5B4D2` (0x1130e), Gemeindegrenze gestrichelt 6/3 (0x10e0c), Nationalparkgrenze Band `#9DCC8F` mit Linie `#05A535` (0x1130f) |
| Gebäude | `#000000` (0x10e05) jetzt auch Kapelle, Sakraler Turm, Turm, Hochkamin, Lagertank, Im Bau, Mauer gross, Verbindungsbrücke; Offenes Gebäude/Treibhaus/Flugdach schwarze Schraffur auf Weiss (0x10e0a, nur Edge); Mauer schwarz 2 px (0x10e04); Trockenmauer schwarz gepunktet (0x1130d); Schutz-/Lawinenverbauung schwarz 2 px (0x10e06) |
| Areale | Park, Freizeit, Sport, Camping, Golf `#E1EFE2` (0x19); Friedhof `#E1EFE2` mit schwarzen Kreuzen (0x1a); Schrebergarten `#E1EFE2` mit schwarzen Punkten (0x10e04); Deponie `#E9D9C4` (0x10e06); die übrigen Areale (Schule, Industrie, Parkplatz u. a., «Wald nicht bestockt») ohne Füllung (früher graues 0x0c/0x0e, «Wald nicht bestockt» fälschlich grau) |
| Neue Ebenen | Hochspannungsleitung `#0789CB` Strich-Punkt (0x11310); Staumauer grau mit schwarzem Umriss (0x10e07), Staudamm hellgrau (0x10e0b, Näherung), Wehr schwarz; Sportbauten: Laufbahn, Skisprunganlage (0x11312), Rodelbahn (0x11313), Schiessstand und Pferderennbahn gepunktet, Sportplatz (0x19 mit Umriss 0x11311); Flugplatzpiste Hartbelag weiss, Gras `#E1EFE2`, beide mit schwarzem Umriss; Fähren schwarz gestrichelt (0x1130c) |
| Punkte (Edge) | Quelle «c» blau, Brunnen blauer Ring, Wasserversorgung blaues Quadrat mit Punkt, Gipfelkreuz/Bildstock schwarzes Kreuz, Denkmal, Triangulationspyramide, Höhle, Spital blaues «H», Heliport «H» im Kreis, Windturbine, Antennen, Durchfahrtssperre rotes Kreuz (nur feinste Stufe, 23'796 Stück), Raststätte, Autoverlad (vereinfachte Symbole); **Gipfel und Pässe** schwarzes «×» mit Höhe statt braunem Rhombus |
| Ortsnamen | Schriftgrösse nach Einwohnerzahl (`EINWOHNERK`): ab 10'000 gross, ab 100 normal, darunter klein (Punkttypen 0x0a00, 0x0b00, 0x0c00); Quartier/Ortsteil normal, Quartierteil klein; Gebietsnamen (`GEBIETSNAME`: Grossregion gross nur in groben Stufen, Landschaftsname normal, Gebiet klein) |
| Strassen | unverändert (Abschnitt «Strassenfarben» unten) |

**Muster-Auflösung der Garmin-Karte:** Garmin-TYP-Muster sind 32 × 32 Pixel, die Karte zeigt sie unabhängig vom Massstab in voller Pixelgrösse. Für Fenix sind Fels, Geröll, Wald offen und Gebüschwald deshalb erst ab Auflösung 22 gezeichnet (darunter nur Untergrund). Ob die Muster auf dem kleinen Display lesbar sind, ist ungeprüft.

**Nicht umsetzbar oder angenähert:** Felsschraffur der Rasterkarte (nicht in den Vektordaten; stattdessen Strichmuster), Staudamm nur als hellgraue Fläche mit Umriss, Masten der Seilbahnen und Tunnelportal-Querstriche fehlen, die Gebäudesignaturen der Legende (Hochhaus mit Rand, Kirchturm als Kreis, Kühlturm, Aussichtsturm) nur als schwarze Fläche, Wasserbecken/Schwimmbecken (71'164 Flächen in `STAUBAUTE`) weggelassen, Solarkraftwerk, Unterwerk-Signatur und Raststätten-Fläche fehlen, Landesgrenze «Drittstaaten» und «umstritten» sowie Grenzsteine ohne Unterscheidung, Gewässerverbauung als einfache blaue Linie. Die Legende zeigt bei der Fähre schwarze Striche auf blauem Band: umgesetzt sind schwarz gestrichelte Linien.

**Farben, Muster und Stil ändern:** `scripts/vector_palette.py` (Farben), `scripts/vector_patterns.py` (Flächenmuster, mit festem Zufallswert erzeugt), `scripts/vector_shields.py` (Strassenschilder), `scripts/make_vector_typ.py [edge|fenix]` (Linien, Punkte, Reihenfolge), Zuordnung Objektart → Typ in `mkgmap/vector/style/{lines,polygons,points}` mit Varianten in `inc/polygons_{edge,fenix}` und `inc/points_edge` (`build_vector.sh` setzt `--style-option=variant=edge|fenix`). **Vorschau:** `scripts/preview_legende.py` (Flächen mit Mustern, Linien mit Muster, Punkte, Namen; wertet den echten Stil mit `style_eval.py` und die TYP-Datei mit `typ_read.py` aus; kein Garmin-Rendering) und `scripts/preview_tafel.py` (Tafel aller Signaturen neben den Ausschnitten der Zeichenerklärung); Ergebnisse in `docs/vergleich/`.

Kantonsstrassen-Schilder: `scripts/kantonsschilder.py <shp-ordner> <csv>` liest swissTLM3D `STRASSENROUTE` (Hauptstrasse A/B/C mit `ROUTENNUMM`) und `STRASSENROUTE_STRASSE` (Verknüpfung per UUID zu `STRASSE`) und setzt alle 4000 m einen Punkt je Route (1'375 Schilder, 264 Nummern wie 279, 288, 566; Nummern des ASTRA-Netzes fallen weg, damit nichts doppelt erscheint); der Bau liest die CSV mit `KANTONSSCHILDER=<csv>`.

Skilifte, Unterkünfte Winter und Schneeschuhrouten sind ebenfalls eigene Layer (`karten/overlays_schweiz/`, Family-ID 3921, 3922 und 3923, auf keinem Gerät geprüft):
```
scripts/build_skilifte.sh daten/bahnen-winter_2056.gpkg mkgmap.jar out/ [W S E N]
scripts/build_unterkuenfte_winter.sh daten/unterkuenfte-winter_2056.gpkg daten/swissnames3d_2026_2056.gpkg mkgmap.jar out/ [W S E N]
scripts/build_schneeschuhrouten.sh daten/snowshoe_routes_2056.gpkg mkgmap.jar out/ [W S E N]
```

Haltestellen sind **nicht** in der Basiskarte, sondern ein eigener Layer: `karten/overlays_schweiz/swisstopo_overlay_haltestellen.img` (Family-ID 3918, 28'042 Haltestellen aus swissTLM3D mit Namen und Symbolen für Bus, Bahn, Schiff, übrige Bahnen). Gebaut mit `scripts/build_haltestellen.sh <shp-ordner> mkgmap.jar out/`.

```
# ganze Schweiz, Edge (Grenzen und Schilder brauchen die Zusatzdaten, siehe unten)
VARIANT=edge GRENZEN=<gpkg> ACHSEN=<gdb> HAUPT=<gdb> KANTONSSCHILDER=<csv> scripts/build_vector.sh <shp-ordner> mkgmap.jar out/
VARIANT=fenix scripts/build_vector.sh <shp-ordner> mkgmap.jar out/
scripts/build_vector.sh <shp-ordner> mkgmap.jar out/ 8.24 47.44 8.38 47.51   # Region (Datei *_region.img)
scripts/download_vector_zusatz.sh <ordner>    # swissBOUNDARIES3D, ASTRA Nationalstrassenachsen und Hauptstrassennetz
```
Die Shapefiles stammen aus dem swissTLM3D-Download (`swisstlm3d_2026-02_2056_5728.shp.zip`, 3,6 GB, Link im STAC unter `ch.swisstopo.swisstlm3d`) und müssen entpackt im `<shp-ordner>` liegen (`swissTLM3D_TLM_*.shp`). Seit der Legenden-Darstellung zusätzlich nötig (alle in derselben ZIP-Datei): `LEITUNG`, `STAUBAUTE`, `SPORTBAUTE_LIN`, `SPORTBAUTE_PLY`, `VERKEHRSBAUTE_LIN`, `VERKEHRSBAUTE_PLY`, `SCHUTZGEBIET`, `VERSORGUNGSBAUTE_PKT`, `SCHIFFFAHRT`, `STRASSENINFO`, `GEBIETSNAME` (je `.shp .shx .dbf .prj .cpg`) sowie die Tabellen `STRASSENROUTE.dbf` und `STRASSENROUTE_STRASSE.dbf` (für `scripts/kantonsschilder.py`); sie lassen sich ohne den ganzen Download einzeln per HTTP-Range aus der ZIP-Datei lesen (Zentralverzeichnis am Ende, dann nur die Bereiche der gewünschten Dateien).

Ablauf: Kachelliste im LV95-Raster (20 × 20 km, 234 Kacheln) → je Kachel parallel (3 Prozesse) swissTLM3D → OSM-XML (das ist nur das Zwischenformat für mkgmap, keine OpenStreetMap-Daten; es werden keine OSM-Daten verwendet; Ausnahme: das Skipisten-Overlay, siehe dort) → mkgmap → Kachel-`.img` → mkgmap fügt alle Kacheln und die TYP-Datei zusammen. Fertige Kacheln werden übersprungen. Dauer je Variante etwa 45 bis 60 Minuten mit 4 Kernen und 15 GB RAM. Ist das Ergebnis über 90 MB, entstehen Teile `*.img.part_aa, _ab, …`.

**Farben und Muster ändern:** `scripts/vector_palette.py` (Farben), `scripts/vector_pattern_tiles.py` und `scripts/vector_patterns.py` (Flächenmuster), `scripts/vector_shields.py` (Strassenschilder), `scripts/make_vector_typ.py [edge|fenix]` (Linien, Punkte, Reihenfolge). Zuordnung Objektart → Typ: `mkgmap/vector/style/`. Zeichnungen zum Vergleich mit der Rasterkarte: `scripts/compare_vector.py`, Ergebnisse in `docs/vergleich/` (eigene Zeichnungen, **kein** Geräte-Rendering).

**Noch nicht umgesetzt:** POIs wie Restaurants, Parkplatzsymbole, Museen (nicht in swisstopo-Daten; als eigene Karte aus OpenStreetMap geplant, braucht Freigabe von `download.geofabrik.de`), Brücken mit Geländer, Felsschraffur wie auf der Rasterkarte (nicht als Vektordaten vorhanden).

### Strassenfarben nach swisstopo-Zeichenerklärung (2026-11-24)
Quelle: «Zeichenerklärung Landeskarten 1:10 000 bis 1:1 Million» (swisstopo 2024), Seite 2, am PDF gemessen (Orange `#F7A71F`, Durchgangsstrasse `#F8C7C8`, Verbindungsstrasse `#FFF481`, Rand `#000000`, Klettersteig `#E3000B`). Bis dahin färbte `lines` nach Breite (10/8 m orange); die Hauptstrasse 5 (6-m-Strasse, Durchgangsstrasse) war deshalb nicht orange. Jetzt entscheidet `VERKEHRSBD` (immer als `tlm_vbed` im OSM, nicht nur mit `--routing`). Zuordnung `lines` (Auflösung): Autobahn 0x01 (18), Autostrasse 0x01 (19), Durchgangsstrasse der Breiten 10/8/6/4/3 m und Verbindung 0x02 (19), Verbindungsstrasse 0x03 (20), sonst 10/8 m 0x05 (19), 6 m 0x04 (20), 4/3 m 0x06 (22), Naturbelag 4/3 m 0x07. Erweiterte Typen (Linien; alle 0x10e00–0x10e1f sind jetzt belegt): Tunnel 0x10e10–0x10e13 nur nach Breite, schwarz gestrichelt; Brücken 0x10e15 (Autobahn/Autostrasse), 0x10e1a (Durchgang), 0x10e1b (Verbindung), 0x10e16–0x10e18 (übrige); Galerien/gedeckte Brücken 0x10e1c (Durchgang), 0x10e1d (Verbindung), 0x10e1e (übrige), 0x10e1f (Autobahn/Autostrasse); Klettersteig 0x10e00. KUNSTBAUTE ganze Schweiz: Keine 1'961'749, Treppe 38'328, Bruecke 56'012, Unterfuehrung 6'555, k_W 27'155, Furt 1'702, Tunnel 1'739, Bruecke mit Treppe 876, Galerie 440, Gedeckte Bruecke 424, Unterfuehrung mit Treppe 415, Steg 334, Staumauer/Wehr 232, in/auf Gebaeude 610, Staudamm 43, Bruecke mit Galerie 18; Zuordnung: Treppe/mit Treppe Treppensymbol, Galerie/Gedeckte Bruecke/Bruecke mit Galerie Galerie (nur Strassen, Wege bleiben Wege), Steg 0x0b, Tunnel und Brücke wie oben, Unterführung, Furt, Staumauer, Staudamm und «in/auf Gebäude» wie gewöhnliche Strasse (die Zeichenerklärung führt keine eigenen Symbole). Vorschau: `scripts/preview_strassen.py` (wertet die echten Stildateien aus, **kein Geräte-Rendering**).

## Reliefschattierung (DEM)
Die Edge-Karte (3900) enthält je Kachel ein eingebettetes Höhenmodell (`DEM=<hgt-ordner>` in `scripts/build_vector.sh`, `--dem-dists=1648,6592,13184,26368,52736`, fein, mehrstufig; `DEM_DISTS` überschreibt). Die Fenix-Karte (3901) bleibt ohne DEM (Unterstützung der Fenix 5S Plus ungeprüft, rund +117 MB). Einschalten am Edge: Karteneinstellungen → Reliefschattierung. Höhendaten (`scripts/make_dem_hgt.py --all`): swissALTIRegio (© swisstopo); ausserhalb des Datensatzes viewfinderpanoramas.org (J. de Ferranti). Technik, Messwerte, Risiken: `docs/relief.md`.

## Routing (Status: Test)
Ziel: SwissTOPO Vector soll auf dem Edge 1040 (später Fenix 5S Plus) mit Garmins eigenem Routing nutzbar sein. **Stand 2026-11-22: beide grossen Karten (3900 Edge, 3901 Fenix) sind mit `ROUTING=1` für die ganze Schweiz neu gebaut** (je 153 WGS84-Kacheln, NET und NOD in jeder Kachel, MapFailedExceptions 0; Bauzeit 22 bzw. 25 Minuten mit 3 Prozessen). Der Bau erfolgte auf Wunsch des Nutzers **ohne vorherigen Gerätetest** der Testkarte (`karten/routing_test/`, Family-ID 3930, bleibt als Vergleich). **Gerätetest offen, auf keinem Gerät geprüft.** Grösse Edge 323'764'224 Byte, Fenix 304'742'400 Byte (Vorversion ohne Routing 240'799'744 bzw. 225'202'176 Byte, also +83 bzw. +80 MB, Hochrechnung unten +80 MB traf zu). Nicht routbar bzw. fehlend: **Einbahnstrassen** (swissTLM3D kennt nur richtungsgetrennte Fahrbahnen, Rampen, Kreisel) und **Abbiegeverbote**; Fahrverbote gelten nur für Motorfahrzeuge. Das Auto-Routing kann gegen Einbahnstrassen führen.

```
# routingfähig bauen (Region; ohne Bounding Box ganze Schweiz). Ohne ROUTING=1 baut das Skript wie bisher.
ROUTING=1 VARIANT=edge scripts/build_vector.sh <shp-ordner> mkgmap.jar out/ [W S E N]
# Testkarte wie in karten/routing_test/ (eigene Family-ID und Kartennummern, kleine Kacheln):
ROUTING=1 ROUTING_BLOECKE="2 2" VARIANT=edge FAMILY_ID=3930 MAP_PREFIX=6394 \
  MAP_LABEL="SwissTOPO Vector Routing Test" OUT_NAME=swisstopo_vector_routing_test_baden \
  scripts/build_vector.sh <shp-ordner> mkgmap.jar out/ 8.24 47.43 8.37 47.50
```
Prüfen nach dem Bau: in `out/logs/*.log` je Kachel `Number of MapFailedExceptions: 0`; die `.img` enthält je Kachel `<8 Ziffern>.NET` und `.NOD`.

**Was ROUTING=1 ändert** (Entscheide, Quellen: mkgmap `doc/options.txt` zu `--route`, `--add-boundary-nodes-at-admin-boundaries`, `--ignore-osm-bounds`; Style-Handbuch Kap. 4.5, 4.6.4–4.6.7, 5.1.1):
- **Kacheln in WGS84 statt LV95.** mkgmap schreibt die Begrenzungsknoten (NOD3), über die das Gerät von Kachel zu Kachel routet, nur dort, wo eine Strasse die Kachelgrenze (das `<bounds>`-Rechteck in Länge/Breite) schneidet; ohne `<bounds>` funktioniert Routing über Kacheln laut Doku nicht. Die bisherigen LV95-Quadrate sind in Länge/Breite schief, ihre Schnittpunkte lägen nicht auf der mkgmap-Kachelgrenze. Darum: Rechtecke in WGS84, Kanten auf Vielfachen von 2048 Garmin-Einheiten (0,0439°, dasselbe Raster wie bei splitter), Standard `ROUTING_BLOECKE="6 4"` = 0,264° × 0,176° ≈ 20 × 19,5 km, Kartennummer `<Präfix><i*100+j>` wie bisher.
- **mkgmap schneidet zu, nicht der Konverter.** `vector2mkgmap.py --routing --wgs-tile W S E N` schreibt das genaue Rechteck als `<bounds>` und gibt Objekte nur grob (100 m Rand) zugeschnitten aus; mkgmap schneidet alles am Rechteck ab, die Kacheln überlappen also nicht (die früheren Lücken in Wäldern an Kachelrändern kamen von überlappenden Kacheln ohne `<bounds>`). Strassen werden gar nicht zugeschnitten, damit beide Nachbarkacheln dieselbe Geometrie haben und mkgmap den Schnittpunkt gleich rundet. Strassen-Stützpunkte, die weniger als eine Garmin-Einheit neben einer Kachelkante liegen, werden um 1,5 Einheiten (ca. 3 m) weggeschoben, sonst fehlt in einer der beiden Kacheln das Stück der Länge 0 und damit das Gegenstück des Begrenzungsknotens. Ergebnis im Test: alle 516 Begrenzungsknoten an den 7 inneren Kanten haben in der Nachbarkachel ein Gegenstück mit identischen Koordinaten.
- **Gemeinsame Knoten an Kreuzungen.** Strassen werden auf cm gerundet und teilen Knoten mit gleichen Koordinaten (`mkgmap_xml_writer.Writer.way(..., share=True)`). Geprüft an swissTLM3D (Raum Baden, 112'331 Strassenstücke): jede Kreuzung ist ein gemeinsamer Endpunkt, kein loses Ende liegt auf oder weniger als 0,5 m neben einer anderen Strasse, und alle 1'501 Kreuzungen ohne gemeinsamen Punkt liegen auf verschiedener STUFE (Brücke/Tunnel). Zusätzliche Schnittpunkte sind deshalb nicht nötig.
- **Routbare Typen.** mkgmap macht nur die Linientypen 0x01–0x13, 0x16, 0x1a, 0x1b routbar, keine erweiterten Typen (0x10e..). Die Strassen mit Standardtyp (Autobahn und Autostrasse 0x01, Durchgangsstrasse 0x02, Verbindungsstrasse 0x03, 6-m-Strasse 0x04, 8/10-m-Strasse 0x05, 3/4-m-Strasse 0x06, Naturstrasse 0x07, 2-m-Weg Hartbelag 0x0a, 2-m-Weg Naturbelag und Steg 0x0b) bekommen `road_class`/`road_speed`. Treppen, Tunnel, Brücken, Galerien, 1-m-Wege und markierte Spuren behalten ihren erweiterten Typ und bekommen **zusätzlich eine unsichtbare routbare Linie** (0x13 für Strassen, 0x16 für Wege, in der TYP-Datei alle Pixel durchsichtig). Verworfen: Umstellung auf freie Standardtypen mit gleichem TYP-Aussehen, weil es nur zehn unbelegte routbare Typen ohne Sonderbedeutung gibt (0x08/0x09 Rampe, 0x0c Kreisel, 0x1a/0x1b Fähre fallen weg), elf gebraucht würden und sich die Zeichenreihenfolge (Brücke über Strasse) ändern könnte.
- **Style** `mkgmap/vector/style/inc/routing_lines`, eingebunden am Anfang von `lines` nur mit `--style-option=routing=1`; ohne die Option entfallen nur Klassen, Zugang und Einbahn (die Darstellung ist gleich; `tlm_vbed` und die Farbregeln gelten immer, die Ausgabe ohne `ROUTING=1` ist seit 2026-11-24 nicht mehr byte-gleich mit der früheren). Klassen/Geschwindigkeiten: Autobahn 4/7, Autostrasse 4/6, Ein-/Ausfahrt 4/4, 10-m- und 8-m-Strasse 3/5, 6-m-Strasse 2/4, 4-m-Strasse und Verbindung 1/3, 3-m-Strasse 0/2, Platz/Zufahrt/Dienstzufahrt/2-m-Weg 0/1, 1-m-Weg/markierte Spur/Treppe 0/0, Naturbelag 0/1 und `mkgmap:unpaved`; Durchgangs- und Hochleistungsstrassen (VERKEHRSBD) mindestens Klasse 3 und Geschwindigkeit 4, Verbindungsstrassen mindestens Klasse 2 (in `inc/routing_lines` als Aktionen und in den Typregeln gesetzt).
- **Einbahn** aus RICHTUNGSG=Wahr (richtungsgetrennte Fahrbahnen, Rampen, Kreisel). Geprüft: die Erfassungsrichtung ist die Fahrtrichtung (von 3'044 Knoten der Einbahn-Fahrbahnen im Raum Baden sind nur 3 reine Senken/Quellen; 752 von 755 Kreiselstücken gegen den Uhrzeigersinn). **swissTLM3D hat kein Attribut für gewöhnliche Einbahnstrassen und keine Abbiegeverbote.**
- **Zugang:** Wege (2 m, 1 m, markierte Spur, Wegfragmente) und Treppen keine Motorfahrzeuge, Treppen auch kein Velo; Autobahn, Autostrasse, Rampen, Raststätten weder Velo noch Fussgänger; Dienstzufahrt, «Allgemeine Verkehrsbeschraenkung» (Fahrverbot), Teststrecke, Panzerpiste und BEFAHRBARK=Falsch keine Motorfahrzeuge; «Gesperrt» für alle. «Zeitlich geregelt» bleibt offen.
- **Autostrassen** (OBJEKTART `Autostrasse`, 1'542 Stücke) wurden früher gar nicht gezeichnet; seit 2026-11-22 gezeichnet, seit 2026-11-24 orange wie die Autobahn (Typ 0x01, Tunnel 0x10e10, Brücke 0x10e15, Routing Klasse 4, Geschwindigkeit 6, kein Velo/Fuss, in `lines` und `inc/routing_lines`). **Wegfragmente** (`1m Wegfragment`, `2m Wegfragment`, 9'927 Stücke) werden seit demselben Datum wie 1-m-/2-m-Wege gezeichnet und sind routbar (kein Auto). Weiterhin ohne Darstellungsregel und nicht routbar: `Raststaette` (705; nur unsichtbar routbar), `Faehre` (27), `Autozug` (6) (Werteliste aus STRASSE.shp, ganze Schweiz; bewusst nicht verändert, nicht eindeutig).
- mkgmap wird mit `--route --style-option=routing=1 --drive-on=right` aufgerufen; die TYP-Datei entsteht mit `make_vector_typ.py <variante> --fid <FID> --routing --out <datei>` im Ausgabeordner (die Dateien der Varianten in `mkgmap/vector/typ/` bleiben unverändert).

**Prüfungen an der Testkarte** (ausserhalb des Geräts; ein Werkzeug, das Garmin-`.img` routet, war nicht verfügbar): MapFailedExceptions 0 in allen 6 Kacheln und beim Zusammenfügen; jede Kachel hat NET und NOD; Begrenzungsknoten siehe oben (mit einem kleinen Java-Programm über die mkgmap-Klassen aus der `.img` gelesen). Auf den Zwischen-OSM-Dateien, mit nachgebildetem mkgmap-Zuschnitt (Kacheln hängen nur über die auf Garmin-Einheiten gerundeten Schnittpunkte zusammen): 45'586 Netzknoten, davon 30'715 mit Grad ≥ 3; 64 Komponenten, die grösste umfasst 99,7 % der Knoten und alle 6 Kacheln (die übrigen 63 haben höchstens 6 Knoten); Auto-Netz zu 97,4 % stark zusammenhängend. Kürzeste Wege (networkx) Baden Bahnhof → Kloster Wettingen: Auto 3,2 km, Velo 3,0 km, zu Fuss 2,8 km, je über eine Kachelgrenze; Turgi → Würenlos über drei Kachelgrenzen 10,5–10,7 km. Das sagt nichts darüber, ob das Gerät die Karte routet.

**Grösse:** Testregion 5,8 MB mit Routing gegenüber 3,6 MB für dieselben Kacheln ohne `--route` (+60 %; NOD 1,5 MB, NET 0,6 MB, unsichtbare Linien). Der Zuwachs hängt an der Zahl der Strassenstücke (rund 37 Byte je Stück; Testregion 59'517, ganze Schweiz 2,1 Mio.), für die ganze Schweiz geschätzt **+80 MB, also rund 320 MB** statt 241 MB (Hochrechnung; gebaut: Edge 323,8 MB, Fenix 304,7 MB). Dauer: mkgmap braucht mit `--route` etwa 30 % länger (Testkachel 3,3 s statt 2,5 s), die Umwandlung in OSM-XML gleich lang; für die ganze Schweiz geschätzt 50–75 Minuten je Variante mit 3 Prozessen; **gebaut: 22 Minuten (Edge) und 25 Minuten (Fenix)**, ohne Download der Daten (swissTLM3D ca. 15 GB entpackt, nur die benötigten Ebenen).

## Weitere Anleitungen
- [Populäre Trails finden: Strava-Heatmap in Gaia und Route auf den Edge](docs/anleitung_strava_heatmap_gaia.md) (nicht getestet, kein Teil der Pipeline)

## Grenzen
- **Fenix 5S Plus ungeprüft:** Laden mehrerer `.img` gleichzeitig, Lesbarkeit der Linien auf dem kleinen Display, einzelnes Ein-/Ausschalten der Overlays. Auf dem Edge 1040 laufen die Overlays (siehe Teststand).
- SwissTOPO Vector ist auf keinem Gerät geprüft, das Routing (Testkarte 3930) ebenfalls nicht.
- Die Overlays und die Höhenlinien haben keine Basiskarte. Sie ergänzen eine vorhandene Karte, zum Beispiel SwissTOPO Vector.
- Die Skirouten und die Hangneigung ersetzen weder das Lawinenbulletin noch eine Tourenplanung.
