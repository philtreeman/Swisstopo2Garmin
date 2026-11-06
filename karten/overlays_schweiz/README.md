# Routen-Overlays ganze Schweiz

Neun Overlay-Karten (Vektor, ohne Basiskarte), je eine eigene `.img`. Gebaut mit `scripts/build_overlays.sh` ohne Bounding Box (2 × 2 Kacheln, mkgmap r4924). Beschreibung der Ebenen, Farben und Quellen: siehe `README.md` im Repo-Wurzelordner.

| Datei | Grösse |
|---|---|
| `swisstopo_overlay_wanderwege.img` | 7,5 MB |
| `swisstopo_overlay_wanderland.img` | 1,3 MB |
| `swisstopo_overlay_veloland.img` | 1,1 MB |
| `swisstopo_overlay_mountainbike.img` | 1,1 MB |
| `swisstopo_overlay_skirouten_blau.img` | 1,7 MB |
| `swisstopo_overlay_skirouten_schwierigkeit.img` | 1,7 MB |
| `swisstopo_overlay_haltestellen.img` | 0,2 MB (28'042 Haltestellen, `scripts/build_haltestellen.sh`, Family-ID 3918) |
| `swisstopo_overlay_skilifte.img` | 0,13 MB (1'805 Bahnen Winter, `scripts/build_skilifte.sh`, Family-ID 3921, Menü «swisstopo Skilifte») |
| `swisstopo_overlay_huetten.img` | 0,08 MB (1'520 Hütten, `scripts/build_huetten.sh`, Family-ID 3922, Menü «swisstopo Huetten») |

`vorschau_skilifte_huetten.png`: Raum Davos/Parsenn, links eigene Zeichnung der beiden neuen Overlays mit denselben Farben und Symbolen über einer grauen Landeskarte, rechts die Landeskarte Winter. **Kein Rendering vom Gerät.**

Stand der Daten: Wanderwege 2026-07, SchweizMobil-Routen 2026-02, Skirouten 2025-12, Bahnen und Unterkünfte Winter 2025-11-20, swissNAMES3D 2026.
