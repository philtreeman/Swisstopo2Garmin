# Vektorkarte für Garmin Fenix 5S Plus (swissTLM3D + mkgmap)

Baut aus den offenen swisstopo-Vektordaten **swissTLM3D** eine Garmin-Vektorkarte (`gmapsupp.img`) im Stil der Landeskarte. Zielgerät: Fenix 5S Plus. Unabhängig vom Raster-Teil des Repos (KMZ für den Edge 1040).

## Pipeline
1. `swissTLM3D` (Shapefile, LV95) von data.geo.admin.ch laden: STAC `ch.swisstopo.swisstlm3d`, neuste Ausgabe (getestet: 2026-02, 3,6 GB).
2. `tlm2osm.py`: Shapefile → OSM-XML mit eigenen Tags (`tlm_layer`, `tlm_type`, `tlm_hiking`, ...).
3. `style/` (mkgmap-Style): Tags → Garmin-Typen.
4. `typ/swisstopo.txt` (TYP): Farben, Linien, Muster (an der Landeskarte 1:25'000 orientiert).
5. `build.sh`: mkgmap → `gmapsupp.img`.
6. `preview.py`: Vorschau-PNG mit denselben Farben (kein echtes Garmin-Rendering).

## Werkzeuge
Python 3 mit `pyogrio shapely pyproj geopandas numpy matplotlib` (im venv), Java 21, mkgmap (www.mkgmap.org.uk/download/mkgmap.html).

```
python3 tlm2osm.py --shp shp/ --bbox 8.24 47.44 8.38 47.51 --out osm/
java -jar mkgmap.jar --style-file=style --family-id=3900 --product-id=1 --gmapsupp --keep-going osm/*.osm typ/swisstopo.txt
```
`--tile-km 20` zerlegt grosse Gebiete (ganze Schweiz) in Kacheln.

## Bekannte Eigenheiten / Fallstricke
- `--style-file` zeigt direkt auf das Style-Verzeichnis, **kein** `--style=.` (sonst wird still der Standard-Style genutzt und die Tags werden ignoriert).
- Pattern-Linien im TYP brauchen Breite **32** (`Xpm="32 H N 1"`); sonst bricht der TYP-Compiler ohne Fehlermeldung ab (MapFailedExceptions: 1).
- Polygone, die nicht in `[_drawOrder]` stehen, werden nicht gezeichnet.
- Eigene Typen nutzen erweiterte Codes `0x10e00`–`0x10e05`.
- Noch nicht umgesetzt: Höhenlinien (swissTLM3D hat keine; geplant aus Höhenmodell), Geländeschummerung, Baum-/Rebpunkte, Beschriftungsstil.
- Ein Rendering auf dem Gerät wurde noch nicht geprüft.

## Skirouten-Overlay (`ski2osm.py`, `ski/`)
Eigene, ein-/ausschaltbare Overlay-Karte (eigene Family-ID 3901, Mapname 63901001) aus dem swisstopo-Datensatz `ch.swisstopo-karto.skitouren` (STAC, `ski_routes_2056.gpkg`, Stand 2025-12-11, 10'789 Routen). Linien nach SAC-Schwierigkeit gefärbt (L grün, WS blau, ZS orange, S rot, unbekannt violett), Beschriftung «Name Schwierigkeit».

```
PYTHONPATH=. python3 ski2osm.py --gpkg ski_routes_2056.gpkg --out ski.osm [--sources swisstopo_sac]
java -jar mkgmap.jar --style-file=ski/style --family-id=3901 --product-id=1 --mapname=63901001 \
  --gmapsupp --transparent --keep-going ski.osm ski/typ/ski.txt
```
Quellen im Datensatz: swisstopo/SAC (9'384), Petzl Foundation/Skitourenguru (884), DAV/ÖAV/AVS (439), topo.verlag (82). Die Nicht-swisstopo-Quellen haben eigene Lizenzbedingungen (siehe Feld `source_url`); mit `--sources swisstopo_sac` nur die swisstopo-eigenen Routen verwenden.

TYP-Falle: In Muster-Linien muss die durchsichtige Farbe (`none`) **zuerst** in der Farbtabelle stehen, sonst bricht der Compiler ab.

## Routen-Overlays (`routes2osm.py`, `routes/`)
Ein `gmapsupp.img` mit **5 eigenen, einzeln schaltbaren Karten** (je ein Mapname, gemeinsame Family-ID 3902 und TYP):

| Karte | Quelle (data.geo.admin.ch) | Stand | Darstellung |
|---|---|---|---|
| Wanderwege | `ch.swisstopo.swisstlm3d-wanderwege` (409'276 Abschnitte) | 2026-07 | gelb (Wanderweg), rot (Berg-), blau (Alpinwanderweg), gestrichelt |
| Wanderland Routen | `ch.astra.wanderland`, Layer `Route` | 2026-02 | national rot, regional orange, lokal gelb-orange, hindernisfrei blau |
| Veloland Routen | `ch.astra.veloland` | 2026-02 | blau (national dunkel, lokal hell) |
| Mountainbikeland Routen | `ch.astra.mountainbikeland` | 2026-02 | violett |
| Skirouten | `ch.swisstopo-karto.skitouren` | 2025-12 | nach SAC-Schwierigkeit |

Beschriftung der SchweizMobil-Routen: «Nummer Name». Lizenz: «proprietary» laut STAC; Nutzungsbedingungen der Anbieter (swisstopo, ASTRA/SchweizMobil) beachten.
```
routes/build.sh <daten-ordner> mkgmap.jar <out> 8.50 46.85 9.05 47.21     # Region Oberiberg
```
Fallen: Extended-Typen = `0x10f00` bis `0x10f1f` (Subtyp max. 0x1f); Konfigurationsdatei für mkgmap braucht absolute Pfade; lange Routen werden auf `--bbox` zugeschnitten.
