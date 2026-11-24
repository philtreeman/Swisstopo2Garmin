# Kartenthema «Swisstopo» (Garmin .kmtf)

`Swisstopo.kmtf` ist ein Garmin-Kartenthema mit den Farben der swisstopo-Landeskarte. Es entstand aus den Feldern der Themen `Popularity.kmtf` und `Dark.kmtf` des Nutzers (`scripts/make_kmtf.py`), 136 Felder, Tag und Nacht gleich. **Ungeprüft auf dem Gerät.** Ein fertiges swisstopo-ähnliches Thema habe ich im Netz nicht gefunden (nur das Bearbeitungswerkzeug «Theme Editor» von pinns.co.uk).

Farben: Untergrund `#FEFFED`, Wald `#C8E6B2`, See `#D3EEFF` mit blauem Rand, Gewässerlinien `#7BC5F0`, Gebäude schwarzgrau `#222222`, Autobahn/Autostrasse orange `#F7A71F`, Durchgangsstrassen rosa `#F8C7C8` (Typ 0x02), Verbindungsstrassen gelb `#FFF481` (0x03), übrige Strassen weiss mit schwarzem Rand (Farben seit 2026-11-24 aus der swisstopo-Zeichenerklärung), Bahn schwarz, Höhenlinien braun, Schrift schwarz mit weissem Rand.

## Installieren
1. Die Datei dorthin kopieren, wo die anderen Themen (`Popularity.kmtf`, `Dark.kmtf`) auf dem Gerät liegen.
2. Am Gerät unter Karte → Kartenthema «Swisstopo» wählen.

## Wichtig
Das Kartenthema überschreibt die Farben der Standardflächentypen der Karte. Wenn auf der Fenix Wald und Seen fehlen, prüfe zuerst, welches Thema aktiv ist (zum Beispiel «Popularity» macht Wald weiss). Probiere es mit «Swisstopo» und danach ohne Thema («Keine», wenn dein Gerät das anbietet; dann gilt das Design aus der Karte selbst).
