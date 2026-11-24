# Vorschaubilder: SwissTOPO Vector nach der swisstopo-Zeichenerklärung

Alle Bilder sind **eigene Zeichnungen, kein Rendering vom Gerät**: `scripts/preview_legende.py` wertet den echten mkgmap-Stil (`mkgmap/vector/style`, mit `scripts/style_eval.py`) und die echte TYP-Datei aus (Farben, 32 × 32-Muster, Linienmuster, Punktsymbole) und zeichnet jeden TYP-Bildpunkt als einen Bildpunkt. Abweichungen zum Gerät: Reihenfolge und Mischen der Typen, Schrift (hier DejaVu mit einfacher Kollisionsvermeidung), Skalierung der Muster, Rundung der Linienbreiten. Die Aufloesungen sind angenommen: 2.4 m je Bildpunkt = Ebene 24, 9.6 m = 22.

| Datei | Inhalt |
|---|---|
| `legende_vorschau_baden_{edge,fenix}_res24.png`, `_res22.png` | Baden (Limmat, Stadt, Hang mit Reben und Wald; Testregion LV95 2'656'000–2'666'000 / 1'257'000–1'265'000), feinste Ebene (1,5 km) und Ebene 22 (6 km) |
| `legende_vorschau_grimsel_{edge,fenix}_res24.png`, `_res22.png`, `_gletscher_res22.png` | Grimsel/Oberaar (Staumauer, Staudamm, Seilbahnen, Hochspannungsleitung, Fels, Geröll, Gletscher; LV95 2'664'000–2'674'000 / 1'156'000–1'164'000) |
| `legende_vorschau_tafel_{edge,fenix}_{linien,flaechen,punkte}.png` | Tafel aller Signaturen mit den Tags, die der Konverter schreibt (Fenix: ohne die in dieser Variante weggelassenen Punkte und Untertypen) |
| `legende_vorschau_tafel_{edge,fenix}_vergleich_{linien,flaechen,punkte}.png` | links Ausschnitte der Zeichenerklärung (Landeskarten 1:10 000 bis 1:50 000, swisstopo), rechts die Tafel (3-fach vergrössert) |
| `strassen_vorschau.png`, `strassen_legende_vergleich.png` | Strassen (`scripts/preview_strassen.py`, Stand 2026-11-24) |

Erzeugen: `python3 scripts/vector2mkgmap.py --shp <tlm> --lv95-tile X0 Y0 X1 Y1 --out-file t.osm --variant edge --trees ...`, dann `python3 scripts/preview_legende.py t.osm mkgmap/vector/typ/swisstopo_vector_edge.txt out.png --variant edge --mpp 2.4 --box x0 y0 x1 y1 --labels`; Tafeln mit `scripts/preview_tafel.py <typ> <präfix> --variant edge --legende-dir <Ausschnitte der Zeichenerklärung>`.

Die frühere Garmin-Darstellung (Vergleichsbilder gegen die Pixelkarte, `scripts/compare_vector.py`) ist mit der Umstellung entfallen; die Bilder sind aus dem Repo entfernt (Git-History vor dem Commit «SwissTOPO Vector: Darstellung strikt nach der swisstopo-Zeichenerklärung»).
