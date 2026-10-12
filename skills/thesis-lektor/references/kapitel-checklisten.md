# Kapitel-Checklisten

Pflichtbestandteile je Kapiteltyp einer empirischen Abschlussarbeit in der Wirtschaftsinformatik. Grundlage für `STR-KAPITELINHALT`. Die Kapitel einer Arbeit können anders heißen oder anders geschnitten sein. Entscheidend ist, dass jeder Bestandteil irgendwo an passender Stelle steht.

## Einleitung

- Problem und Relevanz, belegt (Praxis und Forschung)
- Forschungslücke, präzise und mit Quellen
- Ziel der Arbeit
- Forschungsfragen, nummeriert und im Wortlaut, wie sie später beantwortet werden
- Vorgehen und Forschungsansatz (etwa Design Science, Experiment, Literaturanalyse)
- Aufbau der Arbeit mit Verweisen auf die Kapitel

## Theoretische Grundlagen

- Definition aller Kernbegriffe, die später verwendet werden
- Theorien und Modelle, auf die Hypothesen oder Design aufbauen
- nur, was später gebraucht wird

## Stand der Forschung

- nachvollziehbare Suche (Datenbanken, Suchbegriffe, Zeitraum, Ein- und Ausschlusskriterien) oder begründete Auswahl
- konzeptzentrierte Ordnung statt Aufzählung einzelner Arbeiten
- Synthese: was ist bekannt, was nicht
- Ableitung der Lücke, die die Arbeit schließt

## Forschungsmodell und Hypothesen

- Modell mit Variablen (unabhängig, abhängig, Moderatoren, Kontrollgrößen)
- jede Hypothese theoretisch hergeleitet, gerichtet und mit Quelle
- Unterscheidung konfirmatorisch und explorativ

## Methodik und Studiendesign

- Design (zwischen oder innerhalb von Personen, Balancierung, Zuweisung)
- Stichprobe: Zielgröße mit Begründung (Teststärke), Rekrutierung, Ein- und Ausschluss
- Instrumente mit Quelle, Übersetzung und Anpassungen
- Operationalisierung jeder Variable
- Ablauf der Erhebung
- Auswertungsplan: Tests, Seitigkeit, Korrektur, Umgang mit verletzten Annahmen
- Gütekriterien und deren Sicherung
- Setzungen offen benannt

## Implementierung (bei gestaltungsorientierten Arbeiten)

- Architektur auf einer Abbildung
- Umsetzung der in der Methodik festgelegten Bedingungen
- begründete Technik- und Modellwahl
- Verweis statt Wiederholung der Methodik
- Details (Tabellen, Datenmodell, Prompts) im Anhang

## Ergebnisse

- Stichprobe: angemeldet, ausgeschlossen mit Grund, ausgewertet
- Messgüte der Skalen in der eigenen Stichprobe
- Manipulationsprüfung
- deskriptive Werte
- Hypothesentests in der Reihenfolge der Hypothesen, mit Teststatistik, p, Effektgröße und Konfidenzintervall
- keine Deutung

## Diskussion

- Zusammenfassung der Ergebnisse in Bezug auf die Hypothesen
- Deutung und Abgleich mit der Literatur aus dem Stand der Forschung
- Implikationen für Forschung und Praxis
- Limitationen, vollständig und mit Folgen für die Aussagekraft

## Fazit

- jede Forschungsfrage einzeln und ausdrücklich beantwortet
- Beitrag der Arbeit
- Ausblick

## Abgabe

Im Modus `abgabe` jeden Punkt mit erfüllt oder offen ausgeben.

| Punkt | Prüfung |
|---|---|
| keine Fehler | Bericht: Fehler = 0 |
| keine offenen Marker | Bericht: Offen = 0 |
| alle Zitierschlüssel aufgelöst | keine `ZIT-SCHLUESSEL` |
| alle Verweise aufgelöst | keine `FMT-VERWEIS-UNBEKANNT`, im LaTeX-Log keine undefined references |
| jede Abbildung mit Herkunft | keine `FMT-ABB-QUELLE` |
| Forschungsfragen beantwortet | keine `INH-FORSCHUNGSFRAGEN` |
| Zahlen konsistent | keine `INH-ZAHLEN` |
| Literaturverzeichnis ohne Altlasten | `BIB-UNGENUTZT` geprüft |
| Verzeichnisse vollständig | keine `STR-VERZEICHNIS`, Inhaltsverzeichnis im PDF vorhanden |
| Stand gesichert | keine `ABG-VERSIONIERUNG` und `ABG-GIT-STAND`: privates Repository, alles committet und gepusht |
| Erklärung zur Eigenständigkeit | im PDF vorhanden und unterschrieben |
| Einsatz von KI-Werkzeugen dokumentiert | sofern von der Prüfungsordnung verlangt, im Anhang |
| Titelblatt nach Vorgabe | Titel, Name, Matrikelnummer, Betreuende, Datum |
