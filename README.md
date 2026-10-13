# Swisstopo 1:50'000 / 1:25'000 auf dem Garmin Edge 1040

> Für KI-Assistenten und Weiterarbeit: zuerst **[AGENTS.md](AGENTS.md)** lesen (Ziel, Grenzen, Stand, offene Entscheidungen).

Lädt die aktuelle swisstopo-Pixelkarte (Raster) über den offenen WMTS-Dienst und packt sie als Garmin **Custom Maps (`.kmz`)** für den **Edge 1040**.

## Was geht und was nicht

- **Geht:** Eine Region in 1:25'000 (oder 1:50'000), aktuell, im Original-Aussehen der Landeskarte.
- **Geht nicht:** Die ganze Schweiz als Raster. Garmin erlaubt höchstens **500 Kacheln** pro Gerät (100 pro KMZ, je ≤ 1 Megapixel). Für die ganze Schweiz bräuchte man ca. 940 (Zoom 14) bis über 15'000 Kacheln (Zoom 16).
- **Kein `.img`:** Rasterkarten laufen auf dem Edge als KMZ. Garmins eigene Raster-IMG ist proprietär und wird hier nicht nachgebaut.
- Der **Forerunner 935** hat keine Kartenanzeige. Die **Fenix 5S Plus** nimmt nur Vektor-IMG (z. B. OpenTopoMap).

## Voraussetzungen

Python 3 und Pillow:
```
python3 -m pip install pillow
```
Internetzugang zu `wmts.geo.admin.ch` (kein API-Key nötig).

## Verwendung

```
python3 swisstopo2garmin.py --bbox W S E N [Optionen]
```
`--bbox` = West Süd Ost Nord in Grad (WGS84), z. B. aus bboxfinder.com.

| Option | Standard | Bedeutung |
|---|---|---|
| `--layer` | `ch.swisstopo.pixelkarte-farbe-pk50.noscale` | Detailkarte. 1:25k: `ch.swisstopo.pixelkarte-farbe-pk25.noscale` |
| `--zoom` | 15 | WMTS-Zoom. 15 ≈ 3,3 m/px, 16 ≈ 1,6 m/px (bei 47° N) |
| `--overview-layer` | – | gröbere Karte darunter, damit beim Rauszoomen die 1:50k-Karte erscheint |
| `--overview-zoom` | 14 | Zoom der Übersichtsebene |
| `--per-kmz` | 100 | max. Bilder pro KMZ (inkl. Übersicht). Kleiner wählen, wenn Dateien klein bleiben sollen |
| `--quality` | 75 | JPEG-Qualität (50 ≈ −25 % Grösse, Schrift wird unschärfer) |
| `--lod` | 0 | KML-Zoomregel für die Detailebene (am Edge ungetestet) |
| `--chunk` | 4 | 4×4 WMTS-Kacheln pro JPEG (= 1024×1024 px) |
| `--out` | `out` | Ausgabeordner |

Das Skript meldet vor dem Download «N Detail-JPEGs, M Uebersichts-JPEGs, K KMZ». **Detail + Übersicht, aufsummiert über alle KMZ, müssen ≤ 500 bleiben.** Jede KMZ bringt ihre eigenen Übersichtsbilder mit, die zählen pro KMZ erneut.

### Beispiele

1:25k Zoom 16 über 1:50k Zoom 14 (Variante «A», am Edge bestätigt), Raum Baden:
```
python3 swisstopo2garmin.py \
  --layer ch.swisstopo.pixelkarte-farbe-pk25.noscale --zoom 16 \
  --overview-layer ch.swisstopo.pixelkarte-farbe-pk50.noscale --overview-zoom 14 \
  --bbox 8.24 47.44 8.38 47.51 --out out/baden
```

Grosse Heimregion (ca. 65 × 65 km um Baden, 1:25k Zoom 15, 462 Bilder):
```
python3 swisstopo2garmin.py \
  --layer ch.swisstopo.pixelkarte-farbe-pk25.noscale --zoom 15 \
  --bbox 7.866 47.181 8.750 47.765 --per-kmz 45 --out out/heimregion
```

Grobe Faustregel für die Dateigrösse (Mittelland, Qualität 75): 1:25k Zoom 16 ≈ 0,13 MB pro km², Zoom 15 ≈ 0,05 MB pro km². Gebirge ist meist kleiner, Siedlungen grösser.

## Auf den Edge 1040

1. Edge per USB anschliessen (am Mac ggf. OpenMTP oder Android File Transfer).
2. Alle `*.kmz` nach `Garmin/CustomMaps/` kopieren. Alte Test-KMZ vorher löschen.
3. Edge trennen und neu starten.
4. Karte unter Einstellungen → Karte → Kartenübersicht aktivieren.

Garmin-Raster-Dateien (`*.img`) liegen direkt in `Garmin/` und sind davon unabhängig.

## Bekannte Eigenheiten

- **Zoomverhalten:** Beim Rauszoomen blendet der Edge die 1:25k-Bilder früher aus als gewünscht und zeigt dann die 1:50k-Ebene (bzw. die Vektorkarte darunter). Das Verhalten ist nicht steuerbar; ein niedrigerer `--zoom` (grössere Fläche pro Kachel) könnte es verlängern, ist aber nicht geprüft.
- **Zu viele Kacheln:** Bei mehr als der Gerätegrenze erscheint **gar keine** Rasterkarte. Getestet: ca. 300 Bilder funktionieren, 1'110 nicht.
- Erzeugte Dateien (`out/`, `*.kmz`) sind absichtlich nicht im Git.
- Download-Dauer: ca. 15 Kacheln pro Sekunde, 1'000 Bilder brauchen rund 30 Minuten.

## Lizenz und Daten

Kartendaten: © swisstopo, offene Behördendaten (Open Government Data). Namensnennung gemäss swisstopo-Nutzungsbedingungen beachten.
