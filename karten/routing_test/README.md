# SwissTOPO Vector Routing Test, Raum Baden–Wettingen–Dättwil

`swisstopo_vector_routing_test_baden.img` (5,8 MB, Family-ID **3930**, Kartennummern 63942618–63942819, Name im Gerätemenü **«SwissTOPO Vector Routing Test»**): die Edge-Variante von SwissTOPO Vector (swissTLM3D 2026-02, mit Einzelbäumen; ohne Grenzen und Strassenschilder, weil die Zusatzdaten für den Test weggelassen wurden) als **routingfähige Karte** (mkgmap `--route`, NET- und NOD-Teildateien). Gebaut am 2026-11-22 mit

```
ROUTING=1 ROUTING_BLOECKE="2 2" VARIANT=edge FAMILY_ID=3930 MAP_PREFIX=6394 \
  MAP_LABEL="SwissTOPO Vector Routing Test" OUT_NAME=swisstopo_vector_routing_test_baden \
  scripts/build_vector.sh <shp-ordner> mkgmap.jar out/ 8.24 47.43 8.37 47.50
```

Zweck: prüfen, ob das Garmin-Routing auf dem Edge 1040 mit dieser Karte funktioniert, **bevor** die ganze Schweiz neu gebaut wird. **Auf keinem Gerät geprüft.** Technik und Entscheide: README im Repo, Abschnitt «Routing».

## Ausschnitt und Kachelgrenzen
Sechs Kacheln zu je 0,0879° × 0,0879° (etwa 6,6 km breit × 9,8 km hoch), zusammen 8,17°–8,44° Ost und 47,37°–47,55° Nord (West–Ost etwa Brugg bis Würenlos, Süd–Nord etwa nördlich von Bremgarten bis Würenlingen). Die Kacheln sind für den Test absichtlich klein, damit Kachelgrenzen mitten im Raum Baden liegen:

| Grenze | Lage |
|---|---|
| 47,4609° N (waagrecht) | etwa 150 m nördlich vom Bahnhof Wettingen; westlich davon zwischen Baden und Dättwil (Baregg) |
| 8,2617° E (senkrecht) | westlich von Dättwil, zwischen Birmenstorf und Fislisbach |
| 8,3496° E (senkrecht) | zwischen Wettingen und Würenlos, etwa bei Killwangen |

## Was zu testen ist
1. **Baden Bahnhof → Kloster Wettingen** (Klosterhalbinsel an der Limmat). Die Route kreuzt die Kachelgrenze bei 47,4609° N. Je einmal
   - **Velo** (Routing-Modus Rennrad/Radfahren o. ä.),
   - **zu Fuss**, falls das Gerät einen Fussgänger-Modus anbietet,
   - **Auto**, falls das Gerät einen Auto-Modus anbietet.

   Erwartet: Die Route folgt Strassen und Wegen der Karte (keine Luftlinie), Abbiegehinweise nennen Strassennamen (z. B. Bruggerstrasse, Mellingerstrasse, Wettingerstrasse, Klosterstrasse). Länge laut Kontrollrechnung auf den Zwischendaten: Auto 3,2 km, Velo 3,0 km, zu Fuss 2,8 km (das Gerät rechnet mit eigenen Gewichten, Abweichungen sind normal).
2. **Über mehrere Kachelgrenzen:** Turgi Bahnhof → Würenlos Bahnhof (kreuzt alle drei Grenzen, Kontrollrechnung 10,5–10,7 km). Wenn die Route an einer Grenze abbricht, einen Umweg fährt oder «keine Route» meldet, funktioniert das Routing über Kachelgrenzen nicht.
3. **Zugang:** Mit dem Velo darf die Route nicht über die Autobahn A1 (Baregg) und nicht über Treppen führen. Zu Fuss sind Treppen erlaubt. Mit dem Auto keine Wege (2-m-Weg, 1-m-Weg) und keine Strassen mit Fahrverbot.
4. **Darstellung:** Die Karte soll genau wie die grosse Edge-Karte aussehen. Besonders prüfen: Tunnel, Brücken, 1-m-Wege, markierte Spuren und Treppen. Unter diesen liegt eine unsichtbare Routing-Linie (Typ 0x13/0x16, in der TYP durchsichtig). Sieht man dort zusätzliche Linien (z. B. graue oder schwarze Standardlinien) oder doppelte Strassennamen, das bitte melden (Foto).
5. Optional: Zeit für die Routenberechnung; ob das Gerät beim Navigieren auf der Strasse «einrastet».

Rückmeldung am besten mit Bildschirmfotos (Route auf der Karte, Abbiegeliste).

## Einstellungen am Edge 1040 (ungeprüft, Menünamen können je nach Firmware abweichen)
- Datei nach `Garmin/` auf das Gerät kopieren (USB), keine vorhandene `gmapsupp.img` überschreiben, Gerät neu starten.
- **Nicht gleichzeitig mit der grossen Edge-Karte** (`swisstopo_vector_edge_schweiz.img`, «SwissTOPO Vector Edge», 3900) aktiv haben: Beide decken denselben Raum ab; welche Karte das Gerät zeichnet und auf welcher es routet, ist dann unklar. Am einfachsten die grosse Karte unter Karteninformationen ausschalten (oder vorübergehend vom Gerät nehmen).
- Im Aktivitätsprofil: Navigation → Karte → Karteninformationen (Karte auswählen): «SwissTOPO Vector Routing Test» **ein**, «SwissTOPO Vector Edge» **aus**, auch Garmins eigene Karten (Garmin Cycle Map/TopoActive) für den Test **aus**, sonst routet das Gerät vermutlich auf Garmins Karte. Die Overlays (Wanderwege usw.) dürfen eingeschaltet bleiben; sie sind nicht routbar.
- Navigation → Routing: **Popularity Routing (Trendline) aus** (funktioniert nur mit Garmin-Karten), Routing-Modus wählen (z. B. Rennrad, Mountainbike, Gravel), Berechnungsmethode beliebig, «Auf Strasse einrasten» ein.
- Ziel setzen: Navigation → Karte durchsuchen (Punkt auf der Karte antippen) oder Koordinaten; Kloster Wettingen etwa 47,4558° N, 8,3160° E; Baden Bahnhof 47,4765° N, 8,3075° E.

## Bekannte Grenzen
- swissTLM3D kennt **keine Einbahnstrassen** und keine Abbiegeverbote. Einbahn gilt nur für richtungsgetrennte Fahrbahnen (Autobahn, Rampen, Kreisel, getrennte Fahrbahnen; Attribut RICHTUNGSG). Mit dem Auto kann die Route deshalb gegen eine Einbahnstrasse in der Stadt führen.
- «Allgemeine Verkehrsbeschränkung» (Fahrverbot) sperrt nur Motorfahrzeuge; Ausnahmen wie «Zubringerdienst gestattet» stehen nicht in den Daten. Velos und Fussgänger dürfen durch.
- Autostrassen und Raststätten sind routbar, werden aber (wie in der grossen Karte) nicht gezeichnet.
- Daten: © swisstopo, Lizenz laut STAC «proprietär».
