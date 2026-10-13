# Changelog

Alle Änderungen an `thesis-editor`. Die Versionen folgen [Semantic Versioning](https://semver.org/lang/de/): Eine neue Hauptversion ändert Konfiguration oder Verlauf so, dass etwas angepasst werden muss. Neue Regeln und Funktionen erhöhen die mittlere Stelle, Korrekturen die letzte. Neue oder geänderte Regeln können den Lektoratsindex verschieben, das steht dann beim Eintrag.

## 1.0.0 (2026-10-13)

- Erste veröffentlichte Version mit 84 Regeln in 14 Bereichen und sechs Gutachter-Rollen
- Bericht `report.html` mit Filtern, Suche, Verlauf und Lektoratsindex, markierte PDF und Übungsseite `defense.html` fürs Kolloquium
- Prüfung des LaTeX- und biber-Logs, der Verzeichnisse und der Datensicherung in Git
- Meldet, ob die Marker-Makros `\quellefehlt` und `\offen` in der Präambel definiert sind
- Sucht höchstens einmal am Tag nach einer neueren Version und meldet sie, auf Wunsch mit automatischem Update
