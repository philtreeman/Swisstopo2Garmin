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
