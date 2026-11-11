# Routen-Overlays ganze Schweiz

Zwölf Overlay-Karten (Vektor, ohne Basiskarte), je eine eigene `.img`. Gebaut mit `scripts/build_overlays.sh` ohne Bounding Box (2 × 2 Kacheln, mkgmap r4924); die übrigen mit dem in der Tabelle genannten Skript. Beschreibung der Ebenen, Farben und Quellen: siehe `README.md` im Repo-Wurzelordner.

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
| `swisstopo_overlay_unterkuenfte_winter.img` | 0,08 MB (506 Unterkünfte Winter als roter Ring, dazu 27 SAC-Hütten und 987 übrige Hütten aus swissNAMES3D nur in der feinsten Stufe; `scripts/build_unterkuenfte_winter.sh`, Family-ID 3922, Menü «swisstopo Unterkuenfte Winter»; bis 2026-11-06 hiess die Datei `swisstopo_overlay_huetten.img`, Menü «swisstopo Huetten»; die alte Datei auf dem Gerät löschen, sie hat dieselbe Family-ID 3922) |
| `swisstopo_overlay_schneeschuhrouten.img` | 0,35 MB (2'825 Schneeschuhrouten, `scripts/build_schneeschuhrouten.sh`, Family-ID 3923, Menü «swisstopo Schneeschuhrouten») |
| `swisstopo_overlay_hangneigung.img` | 75 MB (Hangneigung 10–20 … > 50° in 8 Stufen, 20-m-Raster, semitransparentes Punktmuster; `scripts/build_hangneigung.sh`, Family-ID 3924, Kartennummern 64392401–64392444, Menü «swisstopo Hangneigung») |
| `swisstopo_overlay_hangneigungsklassen.img` | 45 MB (Lawinen-Hangneigungsklassen 30–35, 35–40, 40–45, 45–50, > 50° wie `ch.swisstopo.hangneigung-ueber_30`, 10-m-Raster, Schachbrettmuster; Family-ID 3925, 64392501–64392544, Menü «swisstopo Hangneigungsklassen») |

`vorschau_unterkuenfte_winter.png`: Raum Kesch-Hütte/Chamanna d'Es-cha (Zoom 15), links eigene Zeichnung des Overlays Unterkünfte Winter mit den TYP-Symbolen in Originalgrösse (13 px) über einer grauen Landeskarte, rechts die Landeskarte Winter mit der swisstopo-Ebene Unterkünfte Winter (roter Ring dort 35 px). **Eigene Zeichnung, kein Rendering vom Gerät.**

`vorschau_hangneigung.png`: Raum Davos/Schiahorn (Zoom 15), links eigene Zeichnung der Overlays Hangneigungsklassen (oben) und Hangneigung (unten) mit den TYP-Mustern 1:1 über der grauen Landeskarte, rechts die swisstopo-WMTS-Ebenen `ch.swisstopo.hangneigung-ueber_30` und `ch.swisstopo-karto.hangneigung`. **Eigene Zeichnung, kein Rendering vom Gerät.**

Stand der Daten: Wanderwege 2026-07, SchweizMobil-Routen 2026-02, Skirouten 2025-12, Bahnen und Unterkünfte Winter 2025-11-20, Schneeschuhrouten 2025-12-11, swissNAMES3D 2026, swissALTIRegio 2026-05 (Hangneigung).
