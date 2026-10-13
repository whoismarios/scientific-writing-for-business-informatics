# Changelog

Alle Änderungen an `code-docs`. Die Versionen folgen [Semantic Versioning](https://semver.org/lang/de/): Eine neue Hauptversion ändert die Konfiguration so, dass etwas angepasst werden muss. Neue Regeln und Funktionen erhöhen die mittlere Stelle, Korrekturen die letzte. Vor 1.0.0 können sich Regeln und Optionen noch ändern.

## 0.1.1 (2026-10-13)

- Neue Adresse des Repositorys in README und Update-Prüfung: github.com/whoismarios/scientific-writing-for-business-informatics

## 0.1.0 (2026-10-13)

- Erste Version: Docstrings nach Google-Stil für Python, JSDoc für TypeScript und JavaScript, `ARCHITECTURE.md` und Abgleich der README mit dem Code
- Prüfskript mit elf Regeln zu fehlenden und veralteten Docstrings, Skripten, Pfaden und Umgebungsvariablen
- Jede Regel nennt ihre Quelle: Google Python Style Guide, Google TypeScript und JavaScript Style Guide, PEP 257, Kladov (2021) zu `ARCHITECTURE.md`, Standard Readme. Abweichungen sind in der SKILL.md begründet
- Referenzen für Java (Javadoc), C# (XML-Kommentare), R (roxygen2) und Go (Doc Comments) mit Quellen. Diese Sprachen werden nach Konvention dokumentiert, aber nicht mechanisch geprüft, die Prüfung listet ihre Dateien auf
- Drei Stile: `google` wie in den Guides, `full` mit Parametern und Rückgabewert an jeder Funktion, `summary` nur mit Einzeiler
- Regeln des Projekts aus `AGENTS.md`, `CLAUDE.md` und Linter-Konfiguration haben Vorrang
- Sucht höchstens einmal am Tag nach einer neueren Version und meldet sie, auf Wunsch mit automatischem Update
