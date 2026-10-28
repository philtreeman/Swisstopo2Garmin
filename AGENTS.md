# AGENTS.md – Projektkontext für KI-Assistenten

Stand: 2026-10-22. Sprache des Nutzers: Deutsch (Schweiz). Das README beschreibt Bedienung und Technik; diese Datei hält Ziel, Entscheide und offene Punkte fest. Nicht wiederholen, was schon im README steht.

## Ziel
Offene swisstopo-/SchweizMobil-Daten als **Vektor-Overlays für die Garmin Fenix 5S Plus** (`.img`, je Ebene eine eigene Karte): Wanderwege, Wanderland, Veloland, Mountainbikeland, Skirouten. Die Farben hat der Nutzer festgelegt: Wanderwege nach Kategorie (gelb/rot/blau gestrichelt), Wanderland gelb, Veloland hellblau, Mountainbike orange, Skirouten in zwei Versionen (blau durchgezogen wie auf der Rasterkarte, und nach SAC-Schwierigkeit). **Jede Ebene muss eine eigene `.img` sein.**

Der Nutzer hat ausserdem Wunsch nach einer aktuellen Vektor-Basiskarte im Stil der swisstopo-Landeskarte (**SwissTOPO Vector**, `scripts/build_vector.sh`, ganze Schweiz gebaut; die Höhenlinien sind ein eigenes Overlay). Das Repo bleibt **privat**; die Datenlizenzen stehen im STAC als «proprietary».

Geräte: **Edge 1040** (Overlays **vom Nutzer getestet und funktionsfähig**), **Fenix 5S Plus** (Vektor-IMG, OpenTopoMap installiert; Test der Overlays offen), Forerunner 935 (keine Karten).

## Stand
- Die 6 Overlays sind für die ganze Schweiz gebaut (`karten/overlays_schweiz/`, 14 MB) und für Oberiberg als Test (`karten/overlays_oberiberg_test/`).
- **Edge 1040: geprüft.** Skirouten, Wanderwege und Fahrradrouten als Overlays funktionieren, mehrere `.img` nebeneinander werden geladen (Rückmeldung des Nutzers vom 2026-10-16; welche Fahrradkarte genau, nicht festgehalten).
- **Fenix 5S Plus ungeprüft:** Laden mehrerer `.img` (mögliche Lösung: alle Overlays in eine `gmapsupp.img` bündeln; mkgmap kann mehrere Karten pro Datei), Lesbarkeit der Linien auf dem kleinen Display, einzelnes Schalten der Overlays.
- **Höhenlinien in zwei Varianten** (neu gebaut am 2026-10-28, `karten/overlay_hoehenlinien_schweiz/`): `..._20m.img` (109 MB, Family-ID 3920) und `..._10m.img` (168 MB, 3919), beide aus swissALTI3D 2 m, erweiterte Linientypen 0x10f10-0x10f12. Die frühere Datei mit Family-ID 3917 liegt auf dem Gerät des Nutzers vermutlich noch und überdeckt die neuen (Nutzer sah im Menü nur «10 m»); er muss sie löschen. Auf dem Edge zeigte die 20-m-Fassung nach Screenshots vom 2026-10-27 Linien mit Beschriftung. Skript: `scripts/build_hoehenlinien.sh` (beide Varianten in einem Durchlauf, ca. 1,5 Stunden, rund 45 GB Download).
- **SwissTOPO Vector in zwei Varianten** (ganze Schweiz, gebaut am 2026-10-22, `karten/swisstopo_vector_{edge,fenix}_schweiz/`, je 3 Teile): **Edge** (241 MB, Family-ID 3900: Fels mit Textur, Orts-/Strassen-/Gewässer-/Flur-/Geländenamen, Berge mit Höhe, Grenzen, Schilder der Nationalstrassen und Hauptstrassen, Sportplätze orange) und **Fenix** (225 MB, 3901: Fels einfach grau, nur Höhen an Gipfeln und Pässen, keine Grenzen/Schilder/Sportplätze). Beide mit Einzelbäumen, Schutzverbauungen (2 px braun), Treppen (rot gepunktet), Reben (orange Blitzstriche), Tunnel (graue Punktreihen), Brücken (schwarzer Rand), Wege dunkelgrau 2 px. Stil aus Bildschirmfotos der Garmin-Karte auf dem Edge 1040; Fels- und Reben-Kacheln wurden mit `scripts/extract_pattern.py` aus diesen Fotos ausgelesen (Nutzer: persönlicher Gebrauch, besitzt die Garmin-Lizenz, Repo privat). **Auf keinem Gerät geprüft** (der Nutzer sah frühere Fassungen auf dem Edge, sie luden). Stand 2026-10-28: Einzelbäume als exaktes Garmin-Symbol (3 x 3, drei Grüntöne), auf eine pro 70-m-Zelle ausgedünnt (Garmin zeigt etwa 165/km², die swisstopo-Daten haben 1300/km²), nur in der feinsten Stufe (Garmin zeigt sie bei 80 und 120 m, nicht bei 200 m); Obstanlage/Baumschule: Punktdichte an der Garmin-Karte gezählt (7 % der Fläche). Stand 2026-10-27: Objekte werden an den Kachelgrenzen zugeschnitten (vorher überlappten die Kacheln, das Gerät zeichnete dann Wälder/Reben an Kachelrändern nicht: «scharfe Kante» östlich von Baden), Obstanlagen und Baumschulen eigene Muster, Bahnübergänge roter Balken (aus Kreuzung Strasse/Bahn abgeleitet), Detailstufen nach Garmin-Zoomscreenshots (Gebäude, Wege, Flurnamen, Bäume bis ca. 300–500 m), `--merge-lines` für Strassennamen. Kantonsstrassen-Nummernschilder («279») fehlen: nicht in den geladenen Daten.
- **Haltestellen-Overlay** (`swisstopo_overlay_haltestellen.img`, 3918, 28'042 Haltestellen) ist ein eigener Layer, nicht mehr in der Basiskarte. Ungeprüft.
- Alle Daten stammen aus swisstopo, SchweizMobil/ASTRA (Schilder, Routen); das «OSM» in früheren Skriptnamen war nur das XML-Zwischenformat für mkgmap, die Skripte heissen jetzt `*2mkgmap.py`. OpenStreetMap wird nirgends verwendet.
- Vorschau-PNGs sind eigene Zeichnungen mit denselben Farben und **kein Rendering** vom Gerät; so auch benennen.

## Entscheide und verworfene Wege (Details in der Git-History)
- **Raster-KMZ (Garmin Custom Maps) wurde verworfen und aus dem Repo entfernt.** Gründe: Garmin begrenzt auf ca. 500 Kacheln pro Gerät (100 pro KMZ, je ≤ 1 Megapixel), die ganze Schweiz bräuchte 940 bis über 15'000 Kacheln. Der Nutzer wollte keine Regionen laden. Am Edge 1040 funktionierten 300 Bilder, 1'110 nicht (dann erscheint gar nichts). Die Skripte stehen in der History vor dem Commit «Restructure repo».
- **Garmins eigene Raster-IMG (TOPO Schweiz PRO) wird nicht nachgebaut.** Der Nutzer besitzt `TopoCHProV5raster.img` (Stand 2017, läuft auf dem Edge, veraltet). Das Format (DSKIMG mit GMP-Teildateien) ist proprietär; kein Umgehen von Kopierschutz. Ein Versuch des Nutzers, JPEG-Kacheln darin zu ersetzen, liegt in `experimente/raster_img_kachel_test.py` (nicht von der KI geschrieben, nicht ausgeführt).
- Ein Google-Drive-Link mit einem Garmin-Kartenfile wurde bewusst nicht geöffnet (unklare Lizenzquelle).
- Neuere Fenix-Modelle (7/8) haben laut Foren einen `CustomMaps`-Ordner und laden vielleicht KMZ; nicht bestätigt, nicht Ziel.

## Technische Fallstricke
Siehe README, Abschnitt «Technische Fallstricke (mkgmap)». Zusätzlich:
- **Labels:** mkgmap schreibt Namen nur, wenn die Stilregel `name=* { name '${name}' }` (am Anfang von lines/points/polygons) sie ausdrücklich setzt, und in Grossbuchstaben, wenn `--lower-case` fehlt. Ohne beides enthält die Karte keine Beschriftungen (bei den ersten Fassungen der Fall). Prüfen: LBL-Teildatei enthält Text; Umlaute stehen als Latin-1 (`grep -P 'Z\xfcrcherstrasse'`).
- Standardlinientypen 0x20-0x22 (Höhenlinien) zeigte der Edge im Overlay nicht; erweiterte Typen 0x10f.. funktionieren.
- Skripte im Repo **nicht** mit `python3 -I` starten (der isolierte Modus findet `mkgmap_xml_writer.py` nicht). Heruntergeladene Daten nur lesen, nie als Python-Code ausführen.
- Die Cloud-Umgebung blockiert unbekannte Hosts. Freigegeben werden mussten `wmts.geo.admin.ch`, `data.geo.admin.ch`, `www.mkgmap.org.uk`, `viewfinderpanoramas.org` (Netzwerkzugriff → «Benutzerdefiniert»). «Zugangsdaten hinzufügen» ist der falsche Dialog.
- Dateien an den Nutzer im Chat: höchstens 30 MiB je Datei.
- `.gitignore` schliesst `*.img` aus, mit Ausnahme `karten/**/*.img`. `out/` ist lokal in `.git/info/exclude`.
- Der Nutzer pusht selbst auf den Branch `claude/jolly-ptolemy-j0ceai`; vor dem Push `git fetch` und mergen.

## Offene Punkte
1. Rückmeldung des Nutzers zur Fenix 5S Plus abwarten (Laden mehrerer `.img`, Lesbarkeit). Bei Problemen Overlays bündeln oder Wanderwege ausdünnen (`resolution` in `mkgmap/overlays/style/lines`).
2. Skirouten blau: Nutzer schrieb «blaudurchegzigen»; gelesen als «blau durchgezogen» (an der Rasterkarte geprüft). Bei Zweifel nachfragen.
3. Optional: Hangneigung (> 30°) aus swissALTI3D (Daten und Skript für die Höhenlinien sind vorhanden), Wildruhezonen (BAFU, nicht geprüft).
4. Beide Vektorkarten auf dem Gerät prüfen: Laden, Lesbarkeit, Ortsnamen und Strassennamen (ob das Gerät die als Text definierten Punkte zeigt), Schilder, Tunnel, Speicherbedarf (rund 240 MB je Karte), Reaktionszeit beim Zoomen, ab welchem Massstab die feinste Ebene (Bäume, Schutzverbauungen, Treppen) beginnt.
5. **POI-Layer aus OpenStreetMap** (Restaurants, Cafés, Parkplätze, Toiletten, Museen, Schulen, Geschäfte): vom Nutzer gewünscht, **noch nicht gebaut**. Braucht die Freigabe von `download.geofabrik.de` (Netzwerkzugriff → «Benutzerdefiniert»); Plan: Geofabrik-Auszug Schweiz, als eigene Karte (eigene Family-ID), ODbL-Namensnennung.
6. Offen aus Nutzerwünschen: Parkplatz-Symbol «P» aus VERKEHRSAREAL, Galerien, Kantonsstrassen-Schilder (nicht in den ASTRA-Daten), Repo-Grösse (jede Kartenversion +ca. 270 MB; bei Wachstum Releases oder LFS).

## Kommunikationsvorgaben des Nutzers
Direkte, kritische Beratung auf Deutsch: unbequeme Wahrheit zuerst, keine Floskeln («Absolut», «Du hast völlig recht»), Aussagen mit **[Sicher]**, **[Wahrscheinlich]**, **[Vermutung]** kennzeichnen, bei Widerspruch begründen (Grund, Alternative, Risiko), bei unveränderter Faktenlage nicht einknicken. Ungeprüftes (Verhalten am Gerät) ausdrücklich als ungeprüft markieren.
