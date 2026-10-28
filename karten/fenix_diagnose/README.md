# Fenix-Diagnose: Warum fehlen Wald und Seen?

Vier kleine Testkarten (je etwa 3 MB, nur der Raum Baden, 20 × 20 km um 8.3 °E / 47.47 °N) mit **denselben Daten** und vier verschiedenen Designs (TYP). Auf der Fenix 5S Plus als `gmapsupp.img` ins Verzeichnis `Garmin/` legen, **immer nur eine Datei auf einmal**, und die Datei in `gmapsupp.img` umbenennen. Die anderen Karten im Menü «Karteneinstellung» ausschalten.

| Datei | Design | Was sie klärt |
|---|---|---|
| `test_A_normal.img` | wie `swisstopo_vector_fenix_schweiz.img` | Ausgangslage: zeigt sie Wald und Seen nicht? |
| `test_B_ohne_typ.img` | kein TYP, Garmin-Standarddarstellung | Wenn hier Wald und Seen erscheinen, liegt es an meiner TYP-Datei |
| `test_C_nur_standardtypen.img` | TYP ohne die erweiterten Flächentypen (Gebäude, Sportplatz, Obst, Baumschule) | Wenn hier Wald und Seen erscheinen, verträgt das Gerät die erweiterten Flächentypen nicht |
| `test_D_swisstopo_stil.img` | Farben der Landeskarte (Wald hellgrün, See hellblau, Gebäude schwarz, Strassen weiss mit schwarzem Rand) | das gewünschte swisstopo-Design |

Familien-ID aller vier: 3901 (wie die Fenix-Karte). Diese Dateien sind **ungeprüft auf dem Gerät**. Die Karte «swisstopo-Stil» für die ganze Schweiz entsteht in wenigen Minuten (`scripts/retyp_vector.sh`), sobald klar ist, welcher Test funktioniert.
