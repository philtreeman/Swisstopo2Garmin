# AGENTS.md – Projektkontext für KI-Assistenten

Stand: 2026-10-16. Sprache des Nutzers: Deutsch (Schweiz). Das README beschreibt Bedienung und Technik; diese Datei hält Ziel, Entscheide und offene Punkte fest. Nicht wiederholen, was schon im README steht.

## Ziel
Offene swisstopo-/SchweizMobil-Daten als **Vektor-Overlays für die Garmin Fenix 5S Plus** (`.img`, je Ebene eine eigene Karte): Wanderwege, Wanderland, Veloland, Mountainbikeland, Skirouten. Die Farben hat der Nutzer festgelegt: Wanderwege nach Kategorie (gelb/rot/blau gestrichelt), Wanderland gelb, Veloland hellblau, Mountainbike orange, Skirouten in zwei Versionen (blau durchgezogen wie auf der Rasterkarte, und nach SAC-Schwierigkeit). **Jede Ebene muss eine eigene `.img` sein.**

Der Nutzer hat ausserdem Wunsch nach einer aktuellen Vektor-Basiskarte im Stil der swisstopo-Landeskarte (Pilot: `scripts/build_basiskarte.sh`, nur Baden, ohne Höhenlinien). Das Repo bleibt **privat**; die Datenlizenzen stehen im STAC als «proprietary».

Geräte: **Edge 1040** (Overlays **vom Nutzer getestet und funktionsfähig**), **Fenix 5S Plus** (Vektor-IMG, OpenTopoMap installiert; Test der Overlays offen), Forerunner 935 (keine Karten).

## Stand
- Die 6 Overlays sind für die ganze Schweiz gebaut (`karten/overlays_schweiz/`, 14 MB) und für Oberiberg als Test (`karten/overlays_oberiberg_test/`).
- **Edge 1040: geprüft.** Skirouten, Wanderwege und Fahrradrouten als Overlays funktionieren, mehrere `.img` nebeneinander werden geladen (Rückmeldung des Nutzers vom 2026-10-16; welche Fahrradkarte genau, nicht festgehalten).
- **Fenix 5S Plus ungeprüft:** Laden mehrerer `.img` (mögliche Lösung: alle Overlays in eine `gmapsupp.img` bündeln; mkgmap kann mehrere Karten pro Datei), Lesbarkeit der Linien auf dem kleinen Display, einzelnes Schalten der Overlays.
- Die Basiskarte ist ein Pilot. Offen: Höhenlinien (aus Höhenmodell swissALTI3D oder SRTM erzeugen; swissTLM3D hat keine), Geländeschummerung, Baum-/Rebpunkte, Schriftstil, ganze Schweiz.
- Vorschau-PNGs sind eigene Zeichnungen mit denselben Farben und **kein Rendering** vom Gerät; so auch benennen.

## Entscheide und verworfene Wege (Details in der Git-History)
- **Raster-KMZ (Garmin Custom Maps) wurde verworfen und aus dem Repo entfernt.** Gründe: Garmin begrenzt auf ca. 500 Kacheln pro Gerät (100 pro KMZ, je ≤ 1 Megapixel), die ganze Schweiz bräuchte 940 bis über 15'000 Kacheln. Der Nutzer wollte keine Regionen laden. Am Edge 1040 funktionierten 300 Bilder, 1'110 nicht (dann erscheint gar nichts). Die Skripte stehen in der History vor dem Commit «Restructure repo».
- **Garmins eigene Raster-IMG (TOPO Schweiz PRO) wird nicht nachgebaut.** Der Nutzer besitzt `TopoCHProV5raster.img` (Stand 2017, läuft auf dem Edge, veraltet). Das Format (DSKIMG mit GMP-Teildateien) ist proprietär; kein Umgehen von Kopierschutz. Ein Versuch des Nutzers, JPEG-Kacheln darin zu ersetzen, liegt in `experimente/raster_img_kachel_test.py` (nicht von der KI geschrieben, nicht ausgeführt).
- Ein Google-Drive-Link mit einem Garmin-Kartenfile wurde bewusst nicht geöffnet (unklare Lizenzquelle).
- Neuere Fenix-Modelle (7/8) haben laut Foren einen `CustomMaps`-Ordner und laden vielleicht KMZ; nicht bestätigt, nicht Ziel.

## Technische Fallstricke
Siehe README, Abschnitt «Technische Fallstricke (mkgmap)». Zusätzlich:
- Skripte im Repo **nicht** mit `python3 -I` starten (der isolierte Modus findet `osm_writer.py` nicht). Heruntergeladene Daten nur lesen, nie als Python-Code ausführen.
- Die Cloud-Umgebung blockiert unbekannte Hosts. Freigegeben werden mussten `wmts.geo.admin.ch`, `data.geo.admin.ch`, `www.mkgmap.org.uk`, `viewfinderpanoramas.org` (Netzwerkzugriff → «Benutzerdefiniert»). «Zugangsdaten hinzufügen» ist der falsche Dialog.
- Dateien an den Nutzer im Chat: höchstens 30 MiB je Datei.
- `.gitignore` schliesst `*.img` aus, mit Ausnahme `karten/**/*.img`. `out/` ist lokal in `.git/info/exclude`.
- Der Nutzer pusht selbst auf den Branch `claude/jolly-ptolemy-j0ceai`; vor dem Push `git fetch` und mergen.

## Offene Punkte
1. Rückmeldung des Nutzers zur Fenix 5S Plus abwarten (Laden mehrerer `.img`, Lesbarkeit). Bei Problemen Overlays bündeln oder Wanderwege ausdünnen (`resolution` in `mkgmap/overlays/style/lines`).
2. Skirouten blau: Nutzer schrieb «blaudurchegzigen»; gelesen als «blau durchgezogen» (an der Rasterkarte geprüft). Bei Zweifel nachfragen.
3. Optional: Höhenlinien und Hangneigung (> 30°) aus swissALTI3D, Wildruhezonen (BAFU, nicht geprüft).
4. Optional: Basiskarte für die ganze Schweiz.

## Kommunikationsvorgaben des Nutzers
Direkte, kritische Beratung auf Deutsch: unbequeme Wahrheit zuerst, keine Floskeln («Absolut», «Du hast völlig recht»), Aussagen mit **[Sicher]**, **[Wahrscheinlich]**, **[Vermutung]** kennzeichnen, bei Widerspruch begründen (Grund, Alternative, Risiko), bei unveränderter Faktenlage nicht einknicken. Ungeprüftes (Verhalten am Gerät) ausdrücklich als ungeprüft markieren.
