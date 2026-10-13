# AGENTS.md – Projektkontext für KI-Assistenten

Stand: 2026-10-13. Diese Datei fasst Ziel, Erkenntnisse, Stand und offene Entscheidungen zusammen, damit eine andere KI (oder ein Mensch) ohne den bisherigen Chatverlauf weiterarbeiten kann. Sprache des Nutzers: Deutsch (Schweiz).

## 1. Ziel des Nutzers

Die **aktuelle** swisstopo-Landeskarte (Pixelkarte, Raster) soll auf dem **Garmin Edge 1040** angezeigt werden.

Anforderungen, die der Nutzer ausdrücklich genannt hat:
- Aussehen der swisstopo-Rasterkarte (nicht eine Vektor-Nachbildung). Die gekaufte Garmin-Vektorkarte «TOPO Schweiz» sieht für ihn deutlich anders aus und genügt nicht.
- **Möglichst die ganze Schweiz**, ohne Regionenwechsel. Er will den Edge **nicht regelmässig (z. B. wöchentlich) am PC anschliessen**. Einzelne Regionen sind für ihn «keine Option».
- Die Karte soll **aktuell** sein (neue Wege vorhanden, alte entfernt). Grund: Die Garmin-Rasterkarte, die er besitzt, ist veraltet (Dateistand April 2017).
- 1:50'000 wirkt ihm im Gelände «etwas grob»; 1:25'000 bevorzugt. Beim Rauszoomen soll die 1:50'000-Karte erst spät statt «eine Zoomstufe zu früh» erscheinen.

Geräte des Nutzers:
| Gerät | Karten? | Bemerkung |
|---|---|---|
| Edge 1040 | ja | Zielgerät. Custom Maps (KMZ) funktionieren. |
| Forerunner 935 | nein | keine Kartenanzeige, nur Kurse/Breadcrumbs |
| Fenix 5S **Plus** | ja (Vektor-IMG) | OpenTopoMap installiert, nicht Ziel dieses Repos |

## 2. Harte Randbedingungen (Garmin Custom Maps / KMZ)

- **500 Kacheln insgesamt** auf dem Gerät, **100 Bilder pro KMZ**, jedes JPEG ≤ 1 Megapixel (wir nutzen 1024×1024) und ≤ 3 MB, Gesamtgrösse ca. ≤ 500 MB. Quellen: okmap.org (Garmin Custom Maps), github.com/NINAnor/GarminCustomMaps, github.com/brilliantcontract/GarminCustomMaps (PR #11). Das sind Angaben aus Doku zu Handgeräten.
- **Vom Nutzer am Edge 1040 getestet:** 3 KMZ mit ca. 300 Bildern → Karte erscheint. 13 KMZ mit 1'110 Bildern → es erscheint **gar keine** Rasterkarte (nicht nur die überzähligen). Die genaue Grenze zwischen 300 und 1'110 ist **nicht gemessen**; 500 ist die dokumentierte Zahl. Ein Test mit 5 und 8 Dateien aus `out/baden50` (je 100 Bilder) würde sie eingrenzen.
- Bilder in verschiedenen KMZ zählen **alle** zur Gesamtzahl. Das Skript legt in jede KMZ die passenden 1:50k-Übersichtsbilder ab (Duplikate!). Diese Duplikate zählen mit.
- **Folgerechnung (nicht verhandelbar):** Schweiz ≈ 41'000 km². Mit 500 Kacheln à 1024 px braucht es ca. 9 m/px. Selbst die grobe Zoomstufe 14 (≈ 6,5 m/px) braucht ca. 940 Kacheln. → **Die ganze Schweiz als aktuelle Raster-KMZ ist auf dem Edge nicht möglich.** Das ist eine Grenze des Formats, kein Fehler im Skript. Nicht schönreden.

## 3. Ergebnis der Machbarkeitsprüfung

| Weg | Aktuell | Ganze Schweiz | swisstopo-Optik | Status |
|---|---|---|---|---|
| KMZ (Raster) | ja | **nein** (Kachelgrenze) | ja | funktioniert für Regionen |
| Garmin TOPO Schweiz PRO Raster (`TopoCHProV5raster.img`) | **nein (2017)** | ja | ja | Nutzer hat Lizenz, läuft auf dem Edge, aber veraltet |
| Garmin TOPO Vektor (gekauft) | je nach Version | ja | nein | Nutzer hat sie, Darstellung genügt nicht |
| Eigenes Vektor-IMG (mkgmap, OSM/swissTLM3D) | ja | ja | nein, nur ähnlich | vorgeschlagen, vom Nutzer als nicht ausreichend eingestuft |
| Eigenes Raster-IMG | – | – | – | nicht machbar (siehe Abschnitt 5) |

**Vorgeschlagener Kompromiss (noch nicht vom Nutzer bestätigt):** Eine grosse **Raster-Heimregion** (ca. 65 × 65 km, 1:25k, WMTS-Zoom 15, 462 Bilder, ohne Übersichtsebene; die ca. 38 verbleibenden Bilder reichen höchstens für eine sehr grobe Übersicht) einmalig laden. Ausserhalb und beim starken Rauszoomen zeigt der Edge die gekaufte Garmin-Vektorkarte. Region nur bei Ortswechsel tauschen. Offene Frage an den Nutzer: **Mittelpunkt der Heimregion** (Baden wurde vorgeschlagen).

## 4. Technische Erkenntnisse

### swisstopo WMTS
- URL: `https://wmts.geo.admin.ch/1.0.0/{layer}/default/current/3857/{z}/{x}/{y}.jpeg`
- Layer 1:50'000: `ch.swisstopo.pixelkarte-farbe-pk50.noscale`
- Layer 1:25'000: `ch.swisstopo.pixelkarte-farbe-pk25.noscale`
- Kein API-Key nötig. Getestet (HTTP 200, JPEG, 256×256).
- Kachelschema Web-Mercator (EPSG:3857), Standard-Slippy-Map-Indizes.
- **[Vermutung]** Für pk25 ist Zoom 16 die höchste echte Auflösung; Zoom 17 liefert nur vergrösserte Kacheln (visuell kein Gewinn, 18 MB statt 11 MB für Baden).
- Auflösung bei 47° N: Zoom 14 ≈ 6,5 m/px, Zoom 15 ≈ 3,3 m/px, Zoom 16 ≈ 1,6 m/px.

### Dateigrössen (gemessen, Baden ≈ 82 km²)
| Variante | Grösse |
|---|---|
| 1:50k, Zoom 15 | 3,7 MB |
| 1:25k, Zoom 16 | 10,8 MB |
| 1:25k, Zoom 17 | 18,2 MB |
| 1:25k Zoom 16 + 1:50k Zoom 14 (Variante A) | 13,2 MB |
JPEG-Qualität 75 (Standard im Skript). Neukomprimierung der Baden-Daten: Qualität 60 ≈ −13 %, 50 ≈ −24 %, 40 ≈ −40 %. PNG mit 32/64 Farben ist grösser. Visuell nicht geprüft.

### Zoomverhalten am Edge
- **Variante A funktioniert** (vom Nutzer bestätigt): 1:50k-Bilder (`drawOrder` 10) liegen unter 1:25k-Bildern (`drawOrder` 50). Beim Rauszoomen blendet der Edge die 1:25k-Bilder aus, die 1:50k-Ebene bleibt sichtbar. Nutzer: Umschaltung kommt «eine Zoomstufe zu früh».
- Variante B (KML `Region/Lod`, `minLodPixels` 512) ist gebaut, aber **nicht getestet**. Ob der Edge LOD liest, ist unbekannt.
- **[Vermutung]** Der Edge blendet Bilder nach ihrer Grösse auf dem Display aus. Grössere Fläche pro Kachel (niedrigerer WMTS-Zoom) könnte die Sichtbarkeit nach aussen verlängern. Ein Test mit 1:25k Zoom 15 + 1:50k Zoom 13 wurde erzeugt (`out/baden50_z15`, 8 KMZ), der Nutzer hat ihn **nicht** getestet.

## 5. Die Garmin-IMG des Nutzers (`TopoCHProV5raster.img`)

Gelesen aus einem 2-MB-Ausschnitt, den der Nutzer geschickt hat (Lizenz laut Nutzer vorhanden):
- Garmin IMG-Container («DSKIMG», Bezeichnung «TOPO Switzerland PRO», Blockgrösse 64 KB, 3,71 GB, Stand 26.04.2017).
- Enthält `TOPO_SWI.MPS` und > 200 `.GMP`-Teildateien (Garmin NT-Format; Unterdateien TRE/RGN/LBL). Die grossen GMP (20–46 MB, ab ca. Offset 380 MB) sind vermutlich die Rasterdaten; nicht gesehen.
- **Kein JNX.** Das Rasterformat in den GMP ist proprietär und nicht öffentlich dokumentiert; kein offenes Werkzeug bekannt, das so etwas schreibt.
- **Entscheidung:** Das Format wird nicht nachgebaut. Gründe: hoher Aufwand ohne Erfolgsgarantie, mögliche Gerätebindung/Kopierschutz (nicht umgehen), Datei stammt aus kostenpflichtigem Garmin-Produkt.
- Ein früherer Google-Drive-Link des Nutzers wurde bewusst nicht geöffnet (unklare Lizenzquelle).
- Wichtige Korrektur: Ein früherer Webbefund («Raster-TOPO nicht mit Edge kompatibel») war falsch. Auf dem Edge läuft die Raster-IMG des Nutzers tatsächlich; Beobachtung gilt vor Recherche.

## 6. Repository

```
swisstopo2garmin.py   Hauptskript: lädt WMTS-Kacheln, erzeugt KMZ
README.md             Kurzanleitung für Menschen (Mac)
AGENTS.md             diese Datei
.gitignore            schliesst out/, *.kmz, __pycache__/ aus
out/                  erzeugte Dateien (nicht versioniert)
```

### `swisstopo2garmin.py`
Abhängigkeit: Python 3 + Pillow. Aufruf aus einem **anderen** Verzeichnis als Downloads; bei untrusted Daten `python3 -I` nutzen.

Wichtige Optionen:
- `--bbox W S E N` (WGS84, Grad) – Pflicht
- `--layer` (Standard: pk50) – Detailebene
- `--zoom` (Standard 15)
- `--overview-layer`, `--overview-zoom` (Standard 14) – optionale gröbere Ebene darunter; wird **pro KMZ** für das jeweilige Gebiet mitgebündelt (`drawOrder` 10; Detail `drawOrder` 50)
- `--lod N` – KML-LOD für die Detailebene (ungetestet)
- `--per-kmz` (Standard 100) – max. Bilder pro KMZ inkl. Übersicht; gruppiert greedy
- `--chunk` (Standard 4 → 4×4 Kacheln = 1024×1024 px je JPEG)
- `--quality` (Standard 75)
- `--out`

Beispiele:
```
# Variante A (vom Nutzer bestätigt): 1:25k Zoom 16 über 1:50k Zoom 14
python3 -I swisstopo2garmin.py --layer ch.swisstopo.pixelkarte-farbe-pk25.noscale --zoom 16 \
  --overview-layer ch.swisstopo.pixelkarte-farbe-pk50.noscale --overview-zoom 14 \
  --bbox 8.24 47.44 8.38 47.51 --out out/baden

# Heimregion-Vorschlag (ca. 65x65 km um Baden, 1:25k Zoom 15) – noch NICHT erzeugt
python3 -I swisstopo2garmin.py --layer ch.swisstopo.pixelkarte-farbe-pk25.noscale --zoom 15 \
  --bbox 7.866 47.181 8.750 47.765 --per-kmz 45 --out out/heimregion
```
Per Trockenlauf (Download durch Dummy-Kacheln ersetzt) ermittelt: diese Bounding Box ergibt **462 Detail-JPEGs** (ohne Übersicht). Ca. 70 × 70 km (`7.843 47.158 8.773 47.788`) ergibt 506 und überschreitet die Grenze; ca. 60 × 60 km (`7.89 47.20 8.73 47.74`) ergibt 380. Bei jeder neuen Region zuerst die Ausgabezeile «N Detail-JPEGs, M Uebersichts-JPEGs» prüfen: die Summe muss **≤ 500** bleiben (Übersichtsbilder werden pro KMZ dupliziert und zählen jeweils mit).

Laufzeit: ca. 15 Kacheln pro Sekunde; 1'100 Bilder (16'000 Kacheln) dauerten rund 30 Minuten.

### Auf dem Gerät
`*.kmz` nach `Garmin/CustomMaps/` kopieren (USB), Edge neu starten, Karte unter Einstellungen → Karte → Kartenübersicht aktivieren. Die Garmin-Raster-IMG des Nutzers liegt direkt in `Garmin/`.

## 7. Bekannte Fallstricke

- **Netzwerk:** In der Claude-Code-Cloud-Umgebung war `wmts.geo.admin.ch` anfangs blockiert (HTTP 403 vom Egress-Proxy). Der Nutzer musste unter «Cloud-Umgebung bearbeiten → Netzwerkzugriff» die Domain freigeben. Der Dialog «Zugangsdaten hinzufügen» ist dafür falsch.
- **GitHub-Push** scheiterte zuerst mit 403, bis die Claude-GitHub-App für das Repo installiert war.
- **Upload-Limit** für Dateien an den Nutzer im Chat: 30 MiB. Grosse Ausgaben mit `--per-kmz 45` oder kleiner erzeugen.
- KMZ-Dateien gehören nicht ins Git (`.gitignore`).
- Der Nutzer hat «Vertraut» als Netzwerkstufe gewählt und eine eigene Domain-Freigabe ergänzt.

## 8. Offene Entscheidungen / nächste Schritte

1. **Heimregion** vom Nutzer erfragen (Mittelpunkt, ggf. Ausdehnung) und das 500-Kachel-Paket erzeugen. Vorher Anzahl Bilder prüfen.
2. Optional: Grenze am Edge messen (5 und 8 Dateien aus `out/baden50` laden) – falls höher als 500, grössere Region oder 1:50k-Übersicht der ganzen Schweiz (Zoom 13, ca. 240 Kacheln) wäre denkbar.
3. Optional: Zoom-15-Test (`out/baden50_z15`) und Variante B am Gerät testen, um das «zu früh»-Umschalten zu beeinflussen.
4. Optional: JPEG-Qualität senken (50–55), um Dateigrösse zu reduzieren; Lesbarkeit der Schrift am Edge prüfen.
5. Falls der Nutzer doch «ganze Schweiz» über alles stellt: Vektor-IMG aus OSM (Geofabrik) bzw. swissTLM3D mit mkgmap und TYP-Datei. Der Nutzer hat dies bisher abgelehnt, weil die Darstellung vom Raster abweicht. Nicht erneut als Standard vorschlagen, nur als ehrliche Alternative nennen.

## 9. Kommunikationsvorgaben des Nutzers

Der Nutzer wünscht direkte, kritische Beratung auf Deutsch: unbequeme Wahrheit zuerst, keine Floskeln wie «Absolut» oder «Du hast völlig recht», Aussagen mit **[Sicher]**, **[Wahrscheinlich]**, **[Vermutung]** kennzeichnen, bei Widerspruch begründen (Grund, Alternative, Risiko) und bei unveränderter Faktenlage nicht einknicken. Ungeprüfte Dinge (z. B. Verhalten am Edge) ausdrücklich als ungeprüft markieren.
