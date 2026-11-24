# Höhenlinien-Overlays ganze Schweiz (zwei Varianten)

Aus **swissALTI3D** (2 m Raster, jüngstes Jahr je Kachel), berechnet mit `scripts/build_hoehenlinien.sh`. Zwei getrennte Karten mit **eigener Family-ID** und eigenem Dateinamen, damit das Gerät beide laden kann und der Name im Kartenmenü stimmt:

| Datei (zusammensetzen mit `cat`) | Gerätemenü | Family-ID | Inhalt | Grösse |
|---|---|---|---|---|
| `swisstopo_overlay_hoehenlinien_20m.img` | «swisstopo Hoehenlinien 20 m» | 3920 | alle 20 m, alle 100 m eine dunklere, dickere Hauptlinie mit Höhenzahl | 113 MB |
| `swisstopo_overlay_hoehenlinien_10m.img` | «swisstopo Hoehenlinien 10 m» | 3919 | alle 10 m, 50 m als Zwischenlinie, 100 m als Hauptlinie mit Höhenzahl | 172 MB |

```
cat swisstopo_overlay_hoehenlinien_20m.img.part_* > swisstopo_overlay_hoehenlinien_20m.img
cat swisstopo_overlay_hoehenlinien_10m.img.part_* > swisstopo_overlay_hoehenlinien_10m.img
shasum -a 256 -c SHA256SUMS        # Linux: sha256sum -c SHA256SUMS
```

**Wichtig:** Die frühere Datei `swisstopo_overlay_hoehenlinien.img` (Family-ID 3917, Menüname «Hoehenlinien 10 m» bzw. später 20 m) vom Gerät **löschen**. Gleiche Family-IDs lädt das Gerät nur einmal; wer die alte Datei liegen lässt, sieht womöglich nur sie.

**Farbe nach Untergrund (Stand 2026-11-24, wie die Landeskarte 1:25 000):** auf Boden braun (Hellbraun `#D2A878` 1 px, 50 m `#B8864F`, 100 m `#A5733A` 2 px), **auf Gletschern blau** (`#5CB5E1` 1 px, 50 m `#2F9DD8`, 100 m `#008AD2` 2 px, Höhenzahl bleibt). Gletscher = swissTLM3D BODENBEDECKUNG «Gletscher» (851 km², ohne «Schneefeld Toteis»); die Linien werden dazu mit `scripts/untergrund_polygone.py` und `hoehenlinien2mkgmap.py --untergrund` an den Gletscherrändern getrennt (`TLM_DIR` in `build_hoehenlinien.sh`). **Fels bleibt braun:** in der Landeskarte sind Höhenlinien auf Fels schwarz; das ist nicht umgesetzt, weil die Vereinigung der rund 250'000 Felspolygone den Arbeitsspeicher sprengte (15 GB) und die Linien dort sehr oft getrennt würden. Seen: keine Höhenlinien in den Daten. Vorschau (eigene Zeichnung, kein Geräte-Rendering): `docs/vergleich/hoehenlinien_gletscher.png`. Die Linien verwenden erweiterte Garmin-Linientypen (braun 0x10f10 bis 0x10f12, Gletscher blau 0x10f13 bis 0x10f15) wie die Routen-Overlays; die Standardtypen 0x20 bis 0x22 zeigte der Edge früher nicht. Der Edge zeigte die Höhenlinien der 20-m-Fassung mit Beschriftung («137 M»), nach Screenshots vom 2026-10-27. Die 10-m-Variante ist auf keinem Gerät geprüft. Daten: © swisstopo (swissALTI3D).
