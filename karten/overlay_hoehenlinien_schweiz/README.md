# Höhenlinien-Overlays ganze Schweiz (zwei Varianten)

Aus **swissALTI3D** (2 m Raster, jüngstes Jahr je Kachel), berechnet mit `scripts/build_hoehenlinien.sh`. Zwei getrennte Karten mit **eigener Family-ID** und eigenem Dateinamen, damit das Gerät beide laden kann und der Name im Kartenmenü stimmt:

| Datei (zusammensetzen mit `cat`) | Gerätemenü | Family-ID | Inhalt | Grösse |
|---|---|---|---|---|
| `swisstopo_overlay_hoehenlinien_20m.img` | «swisstopo Hoehenlinien 20 m» | 3920 | alle 20 m, alle 100 m eine dunklere, dickere Hauptlinie mit Höhenzahl | 109 MB |
| `swisstopo_overlay_hoehenlinien_10m.img` | «swisstopo Hoehenlinien 10 m» | 3919 | alle 10 m, 50 m als Zwischenlinie, 100 m als Hauptlinie mit Höhenzahl | 168 MB |

```
cat swisstopo_overlay_hoehenlinien_20m.img.part_* > swisstopo_overlay_hoehenlinien_20m.img
cat swisstopo_overlay_hoehenlinien_10m.img.part_* > swisstopo_overlay_hoehenlinien_10m.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```

**Wichtig:** Die frühere Datei `swisstopo_overlay_hoehenlinien.img` (Family-ID 3917, Menüname «Hoehenlinien 10 m» bzw. später 20 m) vom Gerät **löschen**. Gleiche Family-IDs lädt das Gerät nur einmal; wer die alte Datei liegen lässt, sieht womöglich nur sie.

Hellbraun (1 px), 50 m mittelbraun, 100 m dunkelbraun (2 px). Die Linien verwenden erweiterte Garmin-Linientypen (0x10f10 bis 0x10f12) wie die Routen-Overlays; die Standardtypen 0x20 bis 0x22 zeigte der Edge früher nicht. Der Edge zeigte die Höhenlinien der 20-m-Fassung mit Beschriftung («137 M»), nach Screenshots vom 2026-10-27. Die 10-m-Variante ist auf keinem Gerät geprüft. Daten: © swisstopo (swissALTI3D).
