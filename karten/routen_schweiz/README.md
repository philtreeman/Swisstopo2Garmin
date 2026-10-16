# Routen-Overlays ganze Schweiz

Sechs Garmin-Overlay-Karten (Vektor, ohne Basiskarte), je eine eigene `.img`, erzeugt mit `vector/routes/build.sh` (ohne Bounding Box, 2×2 Kacheln, mkgmap r4924).

| Datei | Grösse | Inhalt | Darstellung |
|---|---|---|---|
| `swisstopo_wanderwege.img` | 7,5 MB | Wanderwegnetz swissTLM3D (409'276 Abschnitte, Stand 2026-07) | gelb / rot / blau gestrichelt (Wander-, Berg-, Alpinwanderweg) |
| `swisstopo_wanderland.img` | 1,3 MB | Wanderland-Routen (SchweizMobil, 2026-02) | gelb |
| `swisstopo_veloland.img` | 1,1 MB | Veloland-Routen (SchweizMobil, 2026-02) | hellblau |
| `swisstopo_mountainbike.img` | 1,1 MB | Mountainbikeland-Routen (SchweizMobil, 2026-02) | orange |
| `swisstopo_skirouten_blau.img` | 1,7 MB | Skirouten swisstopo/SAC u. a. (2025-12) | blau, durchgezogen, weisser Rand (wie Rasterkarte) |
| `swisstopo_skirouten_schwierigkeit.img` | 1,7 MB | gleiche Skirouten | nach SAC-Schwierigkeit gefärbt, gestrichelt |

Installation: Datei(en) nach `Garmin/` auf der Uhr kopieren, neu starten, Karte aktivieren. Family-IDs 3911–3916, deshalb unabhängig ladbar. Ungeprüft: ob die Fenix 5S Plus mehrere `.img` nebeneinander lädt.

Datenquellen: © swisstopo, ASTRA/SchweizMobil; Skirouten teils Petzl Foundation/Skitourenguru, DAV/ÖAV, topo.verlag (siehe `source_url` im Datensatz). Lizenz laut STAC «proprietary»; Repo nicht öffentlich machen oder Bedingungen prüfen.
