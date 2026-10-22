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

Aufgefallen: Felsstriche der Rasterkarte gibt es in den Daten nicht, im Vektor erscheinen Fels und Geröll als graue Flächen. Höhenlinien fehlen hier (eigenes Overlay), ebenso Wanderwege (eigenes Overlay), Bergnamen und Höhenpunkte.
