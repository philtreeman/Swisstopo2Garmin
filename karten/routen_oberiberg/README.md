# Routen-Overlays Region Oberiberg (Testdateien)

Sechs Garmin-Overlay-Karten, je eine eigene `.img` (Vektor, ohne Basiskarte), erzeugt mit `vector/routes/build.sh`.
Gebiet: Bounding Box `8.50 46.85 9.05 47.21` (WGS84), ca. 40 × 40 km um Oberiberg SZ.

| Datei | Inhalt | Darstellung |
|---|---|---|
| `swisstopo_wanderwege.img` | Wanderwegnetz swissTLM3D (Stand 2026-07) | gelb / rot / blau gestrichelt (Wander-, Berg-, Alpinwanderweg) |
| `swisstopo_wanderland.img` | Wanderland-Routen (SchweizMobil, 2026-02) | gelb |
| `swisstopo_veloland.img` | Veloland-Routen (SchweizMobil, 2026-02) | hellblau |
| `swisstopo_mountainbike.img` | Mountainbikeland-Routen (SchweizMobil, 2026-02) | orange |
| `swisstopo_skirouten_blau.img` | Skirouten swisstopo/SAC (2025-12) | blau, durchgezogen, wie auf der Rasterkarte |
| `swisstopo_skirouten_schwierigkeit.img` | gleiche Skirouten | nach SAC-Schwierigkeit gefärbt, gestrichelt |

`vorschau.png` ist eine eigene Zeichnung mit denselben Farben, kein Rendering vom Gerät.

Installation: Datei nach `Garmin/` auf der Uhr kopieren, neu starten, Karte aktivieren. Ungeprüft: ob die Fenix 5S Plus mehrere `.img` nebeneinander lädt (sonst `gmapsupp.img` nutzen).

Datenquellen: © swisstopo, ASTRA/SchweizMobil. Lizenz laut STAC «proprietary» – Nutzungsbedingungen beachten.
