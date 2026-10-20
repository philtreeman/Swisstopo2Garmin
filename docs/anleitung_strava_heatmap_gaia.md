# Anleitung: Populäre Trails finden (Strava-Heatmap in Gaia, Route auf den Edge 1040)

Stand: 2026-10-20. Ziel: Auf der Strava-**Global**-Heatmap beliebte Trails finden, die Route planen und aufs Garmin-Gerät bringen. Die Heatmap bleibt dabei im Browser. Auf dem Gerät liegen die Karten und Overlays aus diesem Repo.

**Teststand:** Diese Anleitung ist aus Quellen im Netz zusammengestellt und **nicht selbst getestet**. Rückmeldung des Nutzers (2026-10-20): Mit der öffentlichen Adresse aus Schritt 1 zeigt Gaia **nichts** an, vermutlich wegen der Anmeldepflicht bei Strava. Die URL-Vorlage stammt aus einer GitHub-Anleitung ([NickCrews, Gist](https://gist.github.com/NickCrews/bdd7dc9d5d82003611dce0932a202644)). Berichte über die Anmeldepflicht stammen aus Blogs ([Medium](https://alonsalant.medium.com/how-to-show-the-strava-global-heatmap-in-gaia-gps-ae26eb557b25), [Trail Peaches, 2026](https://trailpeaches.com/2026/08/14/strava-heatmap-gaia/)), die ich nicht lesen konnte. Strava ändert den Zugang immer wieder: zuerst die Vorschau in Gaia prüfen.

## Voraussetzungen
- **Gaia GPS Premium** («Gaia Pro»). Eigene Kartenquellen gibt es nur mit Premium.
- Ein Strava-Konto (kostenlos) kann nötig sein, siehe Schritt 2. Die **globale** Heatmap braucht nach den Quellen kein Strava Pro, die persönliche schon.
- Edge 1040, auf dem die Overlays aus `karten/` liegen (optional).

## 1. Heatmap in Gaia als eigene Kartenquelle anlegen
Gaia-Webseite (gaiagps.com/map):
1. Links **Layers** öffnen.
2. Ganz nach unten scrollen, **Add Map Layers**.
3. Wieder ganz nach unten, **Add Custom Source**.
4. Als URL-Vorlage eintragen:
   ```
   https://heatmap-external-b.strava.com/tiles/all/hot/{z}/{x}/{y}.png
   ```
   Für eine einzelne Aktivitätsart `all` ersetzen durch `ride` (Velo), `run` (Laufen), `water` oder `winter`.
5. Den **Zoombereich auf das Maximum** stellen (laut einer Quelle zeigt die Heatmap nur bis Stufe 18).
6. In der **Vorschau** prüfen, ob Kacheln erscheinen, dann **Save**.
7. Die neue Ebene als Overlay über eine Basiskarte legen (z. B. «Gaia Topo» oder «Swisstopo»), Transparenz bei Bedarf anpassen.

Die Gaia-Oberfläche kann anders heissen oder liegen. Die Quelle sagt nichts dazu, ob die Ebene als Basiskarte oder Overlay angelegt werden muss.

## Fehlersuche: Gaia zeigt nichts an
Die Adresse direkt im Browser-Tab öffnen: `https://heatmap-external-b.strava.com/tiles/all/hot/10/535/360.png`
- **Fehlermeldung** (403, «Missing Key-Pair-Id»): Strava verlangt eine Anmeldung, die öffentliche Adresse reicht nicht mehr. Weiter mit Schritt 2 oder mit dem einfacheren Weg unten.
- **Bild sichtbar:** Die Adresse geht. Dann Zoombereich in Gaia auf Maximum stellen, prüfen, ob die Ebene als Overlay eingeschaltet ist, und die Vorschau neu laden.

**Einfacherer Weg ohne Gaia:** In nakarte (`nakarte.me`) läuft die Heatmap bereits. Dort die Heatmap-Ebene einschalten, die Route mit dem Track-Werkzeug zeichnen und als GPX speichern (**[Wahrscheinlich]** über das Track-Menü, nicht von mir getestet). Die GPX wie in Schritt 4 auf den Edge laden. Gaia ist dann nicht nötig. Zum reinen Ansehen genügt auch die Strava-Webseite mit einem kostenlosen Konto.

## 2. Wenn die Ebene leer oder sehr unscharf ist
Nach dem Gist funktioniert die Adresse ohne Anmeldung, die Heatmap ist dann **unscharf**, weil Strava die Auflösung für nicht angemeldete Nutzer begrenzt. Neuere Berichte sagen, dass Strava für die scharfen Kacheln eine **Anmeldung** verlangt und Gaia diese nicht selbst erledigen kann. Die Blogs nennen zwei Wege:
- Zugangsdaten (Cookies aus dem eigenen, angemeldeten Strava-Konto) in die Adresse einbauen. Sie laufen ab und müssen neu eingetragen werden.
- Einen eigenen Proxy (z. B. Cloudflare Workers), der die Anmeldung übernimmt und nicht abläuft.

Die genauen Schritte stehen in den verlinkten Blogs. Dieses Repo enthält dafür **keinen Code und keine Zugangsdaten**. Gib deine Strava-Anmeldedaten nie an fremde Server weiter. Beides läuft auf eigene Verantwortung, siehe «Rechtliches».

## 3. Beliebte Trails lesen
- Aktivitätsart passend wählen (`ride` für Mountainbike und Velo, `run` für Wandern und Trailrunning).
- Je heller und dicker die Linie, desto mehr Aktivitäten. Wege, die nur schwach leuchten, sind selten befahren.
- Die Heatmap zeigt **alle** Aktivitäten: auch Strassen, Pendlerwege und Wege, die gesperrt oder privat sein können. Mit den Overlays aus diesem Repo prüfen:
  - `swisstopo_overlay_wanderwege.img` (Wanderweg, Bergwanderweg, Alpinwanderweg),
  - `swisstopo_overlay_mountainbike.img`, `swisstopo_overlay_veloland.img`,
  - Wildruhezonen und Wegsperrungen: bei den kantonalen Stellen und auf der Wanderland-/Veloland-Seite von SchweizMobil nachsehen. Das Repo enthält sie nicht.
- Höhenlinien und Steilheit beachten: `swisstopo_overlay_hoehenlinien.img`.

## 4. Route planen und auf das Gerät bringen
1. In Gaia die Route zeichnen (mit der Heatmap als Hilfe) und als **GPX** exportieren.
2. Auf den **Edge 1040**:
   - GPX in den Ordner `Garmin/NewFiles/` auf dem Gerät kopieren. **[Wahrscheinlich]** Der Edge importiert sie beim Trennen als Kurs. Alternativ die Datei in Garmin Connect (Training → Kurse → Importieren) hochladen und mit dem Gerät synchronisieren.
   - Auf dem Gerät unter Navigation → Kurse die Strecke wählen.
3. Auf der **Fenix 5S Plus** funktioniert der Import von GPX-Kursen ähnlich über Garmin Connect. Die Karten-Overlays sind auf dieser Uhr noch ungetestet.

## Rechtliches und Vorsicht
- Die Strava-Heatmap ist **nicht offen**. Strava bezeichnet das Abgreifen von Daten als Verstoss gegen die Nutzungsbedingungen, und kommerzielle Nutzung braucht vermutlich eine Erlaubnis (Berichte in [Cycling News](https://road.cc/content/tech-news/strava-flaw-could-give-away-user-addresses-say-researchers-301837) und [Agilytics](https://www.agilytics.in/post/integrating-strava-global-heat-map); den Klauseltext habe ich nicht gesehen). Das hier beschriebene persönliche Ansehen im Kartenprogramm ist deine Entscheidung. **Nicht** Kacheln für den Offline-Gebrauch herunterladen, in Dateien umwandeln oder weitergeben.
- Dieses Repo wandelt die Heatmap bewusst **nicht** in ein Garmin-Overlay um.
- Beliebt heisst nicht erlaubt oder sicher: Wildruhezonen, Wegsperrungen und Fahrverbote gelten unabhängig von der Heatmap. Im Winter und bei Lawinengefahr ersetzt sie das Lawinenbulletin nicht.
