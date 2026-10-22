# Vergleichsbilder: Rasterkarte und SwissTOPO Vector

Links die swisstopo-Pixelkarte (WMTS, passende Kachelstufe), rechts eine **eigene Zeichnung** von SwissTOPO Vector mit den Farben aus `scripts/vector_palette.py`. Das ist **kein Rendering vom Gerät**: Schrift, Linienbreiten und Muster auf der Garmin weichen ab.

Erzeugt mit `scripts/compare_vector.py <shp-ordner> <präfix> <lon> <lat> <breite_m>…`.

| Gebiet | Dateien |
|---|---|
| Berg mit Fels und Schutzverbauungen (Glarus, Rietalp) | `berg_glarus_{400,1500,5000}m.png` |
| Berg mit Fels (Andermatt, Witenstock) | `berg_andermatt_{400,1500,5000}m.png` |
| Wald (Sihlwald) | `wald_sihlwald_{400,1500,5000}m.png` |
| Stadt (Zürich) | `stadt_zuerich_{400,1500,5000}m.png` |
| Kleinstadt, Hang mit Reben und Treppen (Baden) | `baden_{400,1500,5000}m.png` |
| Reben (Twann) | `reben_twann_{400,1500}m.png` |

Die Zoomstufen sind angenommen: 400 m = feinste Ebene (24), 1500 m = 22, 5000 m = 20. Einzelbäume, Schutzverbauungen und Treppen erscheinen nur in der feinsten Ebene. Bei welchem Massstab das Gerät die Ebenen wechselt, ist ungeprüft.

Fels und Geröll: SwissTOPO Vector hat dafür eine Textur (Fels = graue Fläche mit kurzen dunklen Strichen, Geröll = Punkte), die dem Muster der Garmin-Vektorkarte nachempfunden ist. Die Zeichnung deutet sie nur mit Schraffur an; auf dem Gerät sieht sie anders aus (ungeprüft). Die Striche der Rasterkarte, die der Geländeform folgen, gibt es in den Daten nicht.

Es fehlen hier: Höhenlinien und Wanderwege (eigene Overlays), Bergnamen, Höhenpunkte.
