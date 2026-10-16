# Basiskarte (Pilot) Raum Baden

`swisstopo_basiskarte_baden.img` (0,7 MB): Vektor-Basiskarte aus swissTLM3D 2026-02 für Baden AG (Bounding Box `8.24 47.44 8.38 47.51`), Family-ID 3900. Im Stil der Landeskarte 1:25'000. Es fehlen Höhenlinien und Schummerung.

`vergleich_landeskarte.png`: links die Landeskarte (Vorbild), rechts eine eigene Zeichnung mit den Farben der Basiskarte. Kein Rendering vom Gerät.

Neu bauen: `scripts/build_basiskarte.sh <shp-ordner> mkgmap.jar out/ 8.24 47.44 8.38 47.51`
