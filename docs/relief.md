# Reliefschattierung (DEM in den Vektorkarten)

Stand: 2026-11-24. mkgmap kann in jede Kartenkachel ein Höhenmodell (DEM-Teildatei) einbetten (`--dem=<Ordner mit .hgt>`, `--dem-dists=...`). Geräte mit Reliefschattierung berechnen daraus den Schattenwurf selbst. Hier ist nur eine **Testkarte für Baden** gebaut (`karten/relief_test/`); die grossen Karten 3900/3901 sind **nicht** mit DEM gebaut. **Verhalten am Gerät ungeprüft.**

## Höhendaten: HGT-Kacheln (`scripts/make_dem_hgt.py`)
- **Quelle:** swissALTIRegio (swisstopo, 10 m, LV95, Cloud-Optimized GeoTIFF `data.geo.admin.ch/ch.swisstopo.swissaltiregio/…/swissaltiregio_2056_5728.tif`), dieselbe Datei wie bei der Hangneigung. Swissalti3d (0,5/2 m) wäre für 30-m-Gitter unnötig genau und ein Mehrfaches an Download.
- Die Datei deckt ein Rechteck 2385000–2935000 / 974000–1404000 (LV95) mit **Daten auch jenseits der Landesgrenze** (Stichproben im Südschwarzwald: Abweichung zu viewfinderpanoramas bis 16 m, kein Nodata). Dadurch gibt es an der Landesgrenze keine Klippe. Kontrolle an N47E008: mittlere Abweichung zum 3"-Modell von viewfinderpanoramas −3 m, Standardabweichung 41 m (Hang-/Bewuchsunterschiede), keine Stufe an der Grenze.
- **Rückfall** ausserhalb dieses Rechtecks (nur Randkacheln wie N45E005): viewfinderpanoramas.org (`dem3/L31.zip`, `L32.zip`, 3", je ca. 38 MB; nur gelesen, Zip wird gecacht), bilinear auf das Zielgitter, über 2 km Breite am Rand der swissALTIRegio-Datei überblendet. Wo keine Quelle Daten hat: −32768. Probelauf N45E005, N46E005, N47E010 (3"): keine Lücken.
- **Format:** SRTM-HGT, 1° × 1°, int16 big-endian, WGS84, punktregistriert (Zeile 0 = Nordrand). `--res 1` = 3601 × 3601 (26 MB je Kachel, Standard), `--res 3` = 1201 × 1201 (2,9 MB). Mittelwert (GDAL `average`) aus den 10-m-Zellen. Dateien `N45E005.hgt` … `N47E010.hgt` (`--all`, 18 Kacheln; nur Baden: `--tiles N47E008`).
- **Laufzeit:** rund 90 s je Kachel (Netzwerk, 1" wie 3"), ganze Schweiz also ca. 27 Minuten und 18 × 26 MB = 470 MB HGT. Abhängigkeiten: rasterio, pyproj, scipy, numpy (die venv der Hangneigung). Aufruf: `python3 scripts/make_dem_hgt.py --out hgt/ --all`.
- **Lizenz:** swisstopo-Daten laut STAC «proprietär», wie die übrigen Daten (privater Gebrauch). Die Randgebiete der swissALTIRegio-Datei stammen nicht von swisstopo selbst; viewfinderpanoramas ist für nichtkommerzielle Nutzung frei und verlangt Namensnennung (J. de Ferranti).

## Testbau (`scripts/build_dem_test.sh`)
```
scripts/build_dem_test.sh <shp-ordner> <mkgmap.jar> <out-ordner>
```
`build_vector.sh` bleibt **unverändert**; das Skript legt eine Kopie an, in der `$DEM_OPT` im mkgmap-Aufruf je Kachel steht. Gleiches Raster wie `karten/routing_test` (`ROUTING=1`, `ROUTING_BLOECKE="2 2"`, Edge, Bbox 8.24 47.43 8.37 47.50), aber Family-ID 3931, Kartennummern 6395NNNN, «SwissTOPO Relief Test Baden». Es entstehen fünf Karten: ohne DEM, `--dem-dists` 3312 und 1648 je einstufig und mehrstufig (`HGT_TILES`/`BBOX` für andere Räume). Das DEM ist **in den Kachel-IMG** und geht beim Zusammenfügen unverändert in die gmapsupp-Datei.

**Integration in `build_vector.sh` (später):** `$DEM_OPT` hinter `$ROUTE_OPT` im mkgmap-Aufruf der Kacheln, `export DEM_OPT`; ohne gesetzte Variable ist die Ausgabe unverändert. `--dem-dists` braucht **fünf Werte** (die Karte hat fünf Stufen, `mkgmap/vector/style/options`: `levels = 0:24, 1:22, 2:21, 3:20, 4:18`); mkgmap bricht sonst ab («More dem-dist values than levels», MapFailedException). Mit weniger Werten (z. B. nur 3312) baut mkgmap eine einzige DEM-Stufe.

## Ergebnis (mkgmap r4924, 0 Fehler, DEM-Teildatei in allen 6 Kacheln)
Baden, 6 Kacheln, 387,7 km²:

| Variante | `--dem-dists` | IMG | Zuwachs | je km² |
|---|---|---|---|---|
| ohne DEM | | 5'832'704 B | | |
| grob einstufig | 3312 | 6'025'216 B | +192'512 B (+3,3 %) | 497 B |
| fein einstufig | 1648 | 6'345'728 B | +513'024 B (+8,8 %) | 1'323 B |
| grob mehrstufig | 3312,13248,26496,52992,105984 | 6'061'056 B | +228'352 B (+3,9 %) | 589 B |
| fein mehrstufig | 1648,6592,13184,26368,52736 | 6'449'152 B | +616'448 B (+10,6 %) | 1'590 B |

Gegenprobe im Gebirge (Region Grindelwald/Finsteraarhorn, Bbox 8.0 46.55 8.1 46.62, 4 Kacheln, 263 km², eigener Testbau, nicht ausgeliefert): ohne DEM 916'992 B; 3312 +208'896 B (795 B/km²); 1648 +539'648 B (2'053 B/km²); 3312 mehrstufig +241'152 B (917 B/km²); 1648 mehrstufig +642'048 B (2'442 B/km²). Hochalpines Gelände braucht also rund das **1,5-fache** je km² (das DEM kodiert Höhenunterschiede je Block, steiles Gelände braucht mehr Bits).

## Hochrechnung ganze Schweiz
Grundlage: 153 Kacheln × 387,7 km² = rund 59'300 km² Kartenfläche (die Kacheln der routingfähigen Karten, auch Randkacheln werden voll mit DEM belegt). Untere Grenze = Baden-Wert je km² für alles, obere Grenze = Grindelwald-Wert für alles; die Schweiz liegt dazwischen (ca. 60 % Berg- und Hügelland, geschätzt Mittel 0,4 × unten + 0,6 × oben):

| Variante | untere Grenze | obere Grenze | Schätzung | gegenüber Edge 324 MB / Fenix 305 MB |
|---|---|---|---|---|
| 3312 einstufig | 29 MB | 47 MB | ca. 40 MB | +9 bis +15 % (Fenix +10 bis +15 %) |
| 3312 mehrstufig | 35 MB | 54 MB | ca. 46 MB | +11 bis +17 % |
| 1648 einstufig | 78 MB | 122 MB | ca. 104 MB | +24 bis +38 % |
| 1648 mehrstufig | 94 MB | 145 MB | ca. 124 MB | +29 bis +45 % |

(MB = 10^6 Byte; Mittel nur grob, nur zwei Messgebiete. Die Mehrgrösse kommt zu den bestehenden Dateien dazu und ist je Karte (Edge/Fenix) einmal fällig; beide Karten enthalten dasselbe DEM, wenn man beide baut. Bei SPLIT_MB = 90 kommen entsprechend 1 bis 2 Teile dazu. Der Bau selbst wird nicht merklich langsamer: je Kachel einige Sekunden.)

## Offen / Risiken
- **Gerät:** Ob Edge 1040 und Fenix 5S Plus das eingebettete DEM einer Fremdkarte zeichnen, ist unbekannt. Edge: Karteneinstellungen → Reliefschattierung (Name ungeprüft). Fenix 5S Plus: ob das Gerät Reliefschattierung überhaupt kennt, ist nicht belegt; wenn nicht, bringt das DEM dort nur Grösse.
- Ob einstufige DEM bei anderen als der einen Zoomstufe ignoriert werden, ist offen (deshalb die mehrstufigen Varianten).
- Zusammenspiel mit den Overlays und mit Garmins eigener Karte (welche Karte schattiert, Reihenfolge der Zeichnung) ungeprüft.
- Nach einem Wechsel von swissALTIRegio auf ein anderes Höhenmodell neue HGT bauen; die Karten müssen für das DEM neu kompiliert werden (nicht nachträglich einfügbar).
