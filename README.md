# swisstopo → Garmin: Routen-Overlays und Vektor-Basiskarte

Dieses Repo baut aus offenen Bundesdaten **Vektor-Overlays für Garmin-Geräte** (`.img`). Jede Ebene ist eine **eigene Karte** mit eigener Family-ID, die auf eine Basiskarte (z. B. die Garmin-Karte oder OpenTopoMap) gelegt wird.

**Teststand:**
- **Garmin Edge 1040: geprüft, funktioniert.** Der Nutzer hat Overlays für Skirouten, Wanderwege und Fahrradrouten aufs Gerät geladen. Mehrere `.img`-Dateien nebeneinander werden also geladen. Welche der beiden Fahrradkarten (Veloland, Mountainbike) einzeln geprüft wurde, ist nicht festgehalten.
- **Garmin Fenix 5S Plus: Test offen.** Ob die Uhr mehrere `.img` nebeneinander lädt und wie die Linien auf dem kleinen Display aussehen, ist ungeprüft.

Die Overlays:

| Datei | Inhalt | Darstellung |
|---|---|---|
| `swisstopo_overlay_wanderwege.img` | Wanderwegnetz der Schweiz (swissTLM3D, Stand 2026-07) | gelb = Wanderweg, rot = Bergwanderweg, blau = Alpinwanderweg, jeweils gestrichelt |
| `swisstopo_overlay_wanderland.img` | Wanderland-Routen (SchweizMobil) | gelb |
| `swisstopo_overlay_veloland.img` | Veloland-Routen (SchweizMobil) | hellblau |
| `swisstopo_overlay_mountainbike.img` | Mountainbikeland-Routen (SchweizMobil) | orange |
| `swisstopo_overlay_skirouten_blau.img` | Skirouten (swisstopo/SAC u. a.) | blau, durchgezogen, weisser Rand (wie auf der Rasterkarte) |
| `swisstopo_overlay_skirouten_schwierigkeit.img` | gleiche Skirouten | gestrichelt, nach SAC-Schwierigkeit: grün L, blau WS, orange ZS, rot S, violett unbekannt |

Die Routen von SchweizMobil tragen «Nummer Name» als Beschriftung (z. B. «1 Via Alpina»), die Skirouten «Name Schwierigkeit». Bei Wanderland, Veloland und Mountainbikeland sind die Linien nach national (breit), regional und lokal gestuft.

Fertige Dateien liegen im Ordner `karten/` (siehe unten).

![Vorschau Oberiberg](karten/overlays_oberiberg_test/vorschau.png)

*Vorschau: eigene Zeichnung mit denselben Farben über einer grauen Landeskarte, kein Rendering vom Gerät.*

## Fertige Karten (`karten/`)

| Ordner | Inhalt | Grösse |
|---|---|---|
| `karten/basiskarte_schweiz/` | Vektor-Basiskarte, ganze Schweiz, in 3 Teilen (zusammensetzen mit `cat`, siehe README im Ordner) | 190 MB |
| `karten/overlays_schweiz/` | alle 6 Overlays, ganze Schweiz | 14 MB |
| `karten/overlays_oberiberg_test/` | alle 6 Overlays, Testausschnitt Oberiberg SZ (ca. 40 × 40 km) plus `vorschau.png` | 0,8 MB |
| `karten/basiskarte_baden_pilot/` | Pilot einer Vektor-Basiskarte aus swissTLM3D, nur Raum Baden (ca. 10 × 8 km) | 0,7 MB |

Installation: gewünschte `.img` nach `Garmin/` auf das Gerät kopieren (USB), neu starten, unter Einstellungen → Karte aktivieren. Eine vorhandene `gmapsupp.img` nicht überschreiben.

## Datenquellen

Alle Daten sind offen auf `data.geo.admin.ch` verfügbar (STAC-Collection in Klammern). Die Lizenz steht dort als «proprietary»; die Nutzungsbedingungen von swisstopo bzw. ASTRA/SchweizMobil gelten. Repo daher nicht öffentlich machen, ohne sie geprüft zu haben.

| Ebene | Datensatz | Stand |
|---|---|---|
| Wanderwege | swissTLM3D Wanderwege, Layer `tlm_strassen_strasse` mit Feld `wanderwege` (`ch.swisstopo.swisstlm3d-wanderwege`), 409'276 Abschnitte | 2026-07 |
| Wanderland, Veloland, Mountainbikeland | SchweizMobil, Layer `Route` (`ch.astra.wanderland`, `ch.astra.veloland`, `ch.astra.mountainbikeland`) | 2026-02 |
| Skirouten | `ch.swisstopo-karto.skitouren`, 10'789 Routen: swisstopo/SAC 9'384, Petzl Foundation/Skitourenguru 884, DAV/ÖAV/AVS 439, topo.verlag 82 (Feld `source`) | 2025-12 |
| Basiskarte (Pilot) | swissTLM3D (`ch.swisstopo.swisstlm3d`), Ausgabe 2026-02 | 2026-02 |

## Aufbau des Repos

```
README.md                      diese Datei
AGENTS.md                      Kontext für KI-Assistenten (Ziel, Entscheide, Stand)
scripts/                       alle Skripte
  download_daten.sh              lädt die Overlay-Datensätze von data.geo.admin.ch
  build_overlays.sh              baut die 6 Overlay-.img (Hauptskript, siehe unten)
  routes2osm.py                  GeoPackage → OSM-XML für die Overlays
  make_overlay_typ.py            schreibt die TYP-Dateien (Farben, Breiten, Muster)
  osm_writer.py                  gemeinsame OSM-XML-Ausgabe
  build_basiskarte.sh            baut die Basiskarte (Pilot)
  basiskarte2osm.py              swissTLM3D-Shapefiles → OSM-XML für die Basiskarte
  preview_basiskarte.py          Vorschau-Zeichnung der Basiskarte
mkgmap/
  overlays/style/                mkgmap-Regeln: Tags → Garmin-Linientypen
  overlays/typ/                  erzeugte TYP-Dateien, eine je Overlay
  basiskarte/style/, typ/        dasselbe für die Basiskarte
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
2. **Konvertieren** (`routes2osm.py`). Liest je Ebene das GeoPackage, schneidet die Linien auf die Kachel zu, vereinfacht sie (2 m) und schreibt OSM-XML mit den Tags `route_layer` (wanderwege, wanderland, veloland, mtb, ski), `route_class` (z. B. national/regional/lokal, Wanderweg/Berg/Alpin, SAC-Klasse 1–4) und `name`. Hin- und Rückweg identischer SchweizMobil-Routen werden nur einmal geschrieben.
3. **TYP-Dateien schreiben** (`make_overlay_typ.py`). Pro Overlay eine TYP-Datei mit eigener Family-ID: Farben, Linienbreiten, Strichmuster.
4. **mkgmap aufrufen**, einmal je Overlay. mkgmap liest die OSM-Dateien, ordnet über `mkgmap/overlays/style/lines` jedem Tag-Satz einen Garmin-Linientyp zu und verpackt alles mit der TYP-Datei in eine `gmapsupp.img`. Der Name im Gerätemenü kommt aus `--description`.
5. **Umbenennen** nach `swisstopo_overlay_<name>.img` im Ausgabeordner.

| Overlay | Family-ID | Mapname |
|---|---|---|
| Wanderwege | 3911 | 63911001 |
| Wanderland | 3912 | 63912001 |
| Veloland | 3913 | 63913001 |
| Mountainbikeland | 3914 | 63914001 |
| Skirouten blau | 3915 | 63915001 |
| Skirouten nach Schwierigkeit | 3916 | 63916001 |

### Aussehen anpassen
- **Farben, Breiten, Strichmuster:** `scripts/make_overlay_typ.py` (Konstanten oben: `YELLOW`, `LBLUE`, `ORANGE`, `SKI_BLUE`, Breiten je Kategorie). Danach `build_overlays.sh` neu starten; die OSM-Zwischendateien werden wiederverwendet.
- **Zuordnung Kategorie → Linientyp:** `mkgmap/overlays/style/lines`.
- **Ab welchem Zoom sichtbar:** `resolution`-Werte in `mkgmap/overlays/style/lines` (höher = erst bei stärkerer Vergrösserung).

### Technische Fallstricke (mkgmap)
- `--style-file` zeigt direkt auf das Style-Verzeichnis. Mit zusätzlichem `--style=.` nutzt mkgmap still den Standard-Style und ignoriert die eigenen Tags.
- Erweiterte Linientypen: Code `0x10f00`–`0x10f1f` (Subtyp höchstens `0x1f`), Skirouten `0x11000`–`0x11004`.
- Die TYP-Compiler-Fehler sind stumm (nur `MapFailedExceptions: 1`). Muster-Linien brauchen Breite 32 (`Xpm="32 H N 1"`), und die durchsichtige Farbe (`none`) muss in der Farbtabelle **zuerst** stehen.
- `--mapname` hat 8 Ziffern und muss je Overlay eindeutig sein.
- Polygone erscheinen nur, wenn sie im TYP unter `[_drawOrder]` stehen (relevant für die Basiskarte).

## Basiskarte (`swisstopo_basiskarte_schweiz.img`)
`scripts/build_basiskarte.sh` baut aus swissTLM3D eine Vektor-Basiskarte im Stil der Landeskarte 1:25'000: Strassen nach Klassen, Wege, Wanderwege, Wald, Fels, Gewässer, Bahn, Gebäude, Ortsnamen. Es fehlen Höhenlinien, Geländeschummerung, Baum-/Rebpunkte und ein Schriftstil. **Auf keinem Gerät geprüft.** Die fertige Karte der ganzen Schweiz (190 MB) liegt in `karten/basiskarte_schweiz/`.

```
scripts/build_basiskarte.sh <shp-ordner> mkgmap.jar out/                      # ganze Schweiz → swisstopo_basiskarte_schweiz.img
scripts/build_basiskarte.sh <shp-ordner> mkgmap.jar out/ 8.24 47.44 8.38 47.51   # Region → swisstopo_basiskarte_region.img
```
Die Shapefiles stammen aus dem swissTLM3D-Download (`swisstlm3d_2026-02_2056_5728.shp.zip`, 3,6 GB, Link im STAC unter `ch.swisstopo.swisstlm3d`) und müssen im Ordner `<shp-ordner>` entpackt liegen (`swissTLM3D_TLM_*.shp`; gebraucht werden Strassen, Bodenbedeckung, Gewässer, Bahn, Gebäude-Footprints, Namen, Areale).

Ablauf: Kachelliste im LV95-Raster (20 × 20 km) → je Kachel parallel (3 Prozesse) swissTLM3D → OSM-XML → mkgmap → Kachel-`.img` (das OSM wird gelöscht, die ganze Schweiz wären ca. 14 GB) → mkgmap fügt alle Kacheln und die TYP-Datei zu einer Datei zusammen. Bereits fertige Kacheln werden bei einem erneuten Aufruf übersprungen. Dauer für die ganze Schweiz: etwa 20 Minuten mit 4 Kernen und 15 GB RAM. Ist das Ergebnis über 90 MB, entstehen zusätzlich Teile `*.img.part_aa, _ab, …`.

## Grenzen
- **Fenix 5S Plus ungeprüft:** Laden mehrerer `.img` gleichzeitig, Lesbarkeit der Linien auf dem kleinen Display, einzelnes Ein-/Ausschalten der Overlays. Auf dem Edge 1040 laufen die Overlays (siehe Teststand).
- Die Basiskarte ist auf keinem Gerät geprüft.
- Die Overlays haben keine Basiskarte. Sie ergänzen eine vorhandene Karte.
- Die Skirouten ersetzen weder das Lawinenbulletin noch eine Tourenplanung.
