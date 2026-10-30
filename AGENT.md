## Modellwahl und Subagents

Der Hauptagent koordiniert und delegiert. Er arbeitet selbst nur an Aufgaben, die wenige Tool-Calls brauchen, oder an solchen, die den ganzen Gesprächskontext benötigen.

### Subagents statt Selbermachen
- Alles, was viel lesen, suchen oder umsetzen muss, geht an einen Subagent mit sauberem Kontext. Der Hauptagent bekommt nur das Ergebnis zurück und keine Dateiauszüge.
- Unabhängige Teilaufgaben starte ich parallel in derselben Nachricht.
- Jeder Subagent bekommt einen vollständigen Auftrag: Ziel, relevante Dateien, was schon ausgeschlossen ist und woran man "fertig" erkennt. Er kennt den Gesprächsverlauf nicht.
- Review und Verifikation übernimmt ein anderer Subagent als der, der den Code geschrieben hat. Dabei gebe ich ihm den Code und nicht mein Urteil dazu.

### Modell pro Aufgabe (`model` beim Agent-Aufruf setzen)

**Opus** für Aufgaben, bei denen Urteilsvermögen zählt:
- Koordination: Aufgaben zerlegen, Reihenfolge und Abhängigkeiten festlegen, Ergebnisse zusammenführen
- Planung, Architektur- und Designentscheidungen
- Diagnose schwieriger Bugs, bei denen die Ursache unklar ist
- Code-Review und Sicherheits-Review
- Mehrdeutige Anforderungen, Abwägungen, Recherche mit widersprüchlichen Quellen

**Sonnet** für Aufgaben mit klarem Auftrag:
- Implementierung nach vorgegebenem Plan oder Spezifikation
- Tests schreiben und ausführen, Refactorings, Migrationen, Formatierung
- Bugfixes mit bekannter Ursache
- Dokumentation, Commit-Texte, Konfigurationsänderungen
- Codebase durchsuchen und zusammenfassen

**Haiku** für Triviales: einzelne Lookups, Dateien auflisten, einfache Umformatierungen.

### Faustregeln
- Ist der Auftrag so klar, dass ich ihn in wenigen Sätzen vollständig beschreiben kann, nehme ich Sonnet. Muss der Agent erst entscheiden, was richtig ist, nehme ich Opus.
- Eine Implementierung, die selbst Designentscheidungen verlangt, wird aufgeteilt: Opus plant, Sonnet setzt um.
- Nach zwei gescheiterten Versuchen eines Sonnet-Agents wechsle ich für denselben Auftrag auf Opus, statt ein drittes Mal zu wiederholen.
- Im Zweifel starte ich mit Sonnet. Opus lohnt sich dort, wo ein Fehler teuer ist oder Nacharbeit mehr kostet als der Preisunterschied.
