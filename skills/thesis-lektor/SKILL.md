---
name: thesis-lektor
description: >-
  Lektorat für deutschsprachige wissenschaftliche Arbeiten in LaTeX, zugeschnitten auf die Wirtschaftsinformatik
  (Bachelor- und Masterarbeiten, Seminararbeiten, Paper). Prüft mechanisch und reproduzierbar Typografie, Sprache, Satzbau,
  Begriffe, Zitation, Bibliografie, Verweise, Verzeichnisse und Gliederung, dazu den Sicherungsstand in Git.
  Gutachter-Agenten in unterschiedlichen Rollen prüfen Inhalt, Methodik, Formeln, roten Faden und Quellentreue.
  Ergebnis ist ein HTML-Bericht mit Verlauf und eine farbig markierte PDF-Fassung. Fehlende Quellen und offene Punkte werden eigens ausgewiesen.
  Diesen Skill immer verwenden, wenn eine Arbeit, ein Kapitel oder ein Abschnitt in LaTeX geprüft, gegengelesen, lektoriert oder korrigiert werden soll,
  oder vor einer Abgabe. Auch bei beiläufigen Bitten wie "schau mal über Kapitel 5", "ist das so abgabereif?", "such wertende Wörter",
  "fehlen irgendwo Quellen?", "passt der rote Faden?", "proofread my thesis" oder "check my chapter for style issues".
argument-hint: "[schnell | kapitel <Name> | voll | abgabe]"
compatibility: Nur LaTeX-Projekte. Python 3.11 oder neuer ohne Zusatzpakete. Optional latexmk für die markierte PDF, git und gh für die Prüfung der Versionierung.
license: MIT
---

# thesis-lektor

Der Skill prüft eine wissenschaftliche Arbeit in zwei Schichten:

1. **Mechanisch** über `scripts/lektorat.py`. Gleicher Text ergibt immer dieselben Befunde. Diese Schicht deckt alles ab, was sich an Zeichen, Wörtern und LaTeX-Struktur erkennen lässt.
2. **Urteilend** über Gutachter-Agenten mit festen Rollen. Diese Schicht prüft nur, was ein Skript nicht kann: Bedeutung, Begründung, Zusammenhang und ob eine Quelle die Aussage trägt.

Der Skill ist für Arbeiten in **LaTeX** gebaut. Er liest `.tex`-Dateien ab `\begin{document}` der Hauptdatei, löst `\input` und `\include` auf und wertet biblatex- oder BibTeX-Dateien aus. Word-, Markdown- oder Google-Docs-Texte prüft er nicht. Liegt die Arbeit in einem anderen Format vor, das der Person sagen, statt die Skripte daran scheitern zu lassen. Die Gutachter-Agenten könnten zwar jeden Text lesen, ihre Befunde verweisen aber auf Datei und Zeile im LaTeX-Quelltext.

Beide Schichten liefern Befunde im selben Format, mit Regel-ID aus `regelwerk.toml`. Das Regelwerk ist die einzige Quelle für Regeln, Schweregrade, Farben und Wortlisten. `references/regelwerk.md` ist daraus erzeugt und erklärt jede Regel mit Begründung und Beispiel.

## Aufruf

Der Skill startet von selbst bei passenden Bitten oder ausdrücklich als `/thesis-lektor`. Steht hinter dem Befehl etwas, bestimmt es Modus und Umfang: `$ARGUMENTS`

- leer: Modus `schnell` über die ganze Arbeit, danach anbieten, Gutachter einzusetzen
- `schnell`, `voll` oder `abgabe`: dieser Modus für die ganze Arbeit
- `kapitel <Name>` oder nur ein Kapitelname wie `Methodik` oder `05`: Modus `kapitel` für die passende Datei

Eine Einrichtung ist nicht nötig. Ohne `lektorat.toml` erkennt der Skill Hauptdatei, Bibliografie, Glossar und Marker selbst.

## Grundsätze

- **Der Quelltext der Arbeit wird nicht verändert.** Der Skill markiert und schlägt vor. Änderungen gibt es nur auf ausdrückliche Anweisung, und dann einzeln und nachvollziehbar. Die markierte PDF entsteht aus einer Kopie unter `.lektorat/build/`.
- **Jeder Befund ist belegt** mit Datei, Zeile und dem wörtlichen Auszug. Ein Befund ohne Fundstelle ist eine Meinung und gehört nicht in den Bericht.
- **Lieber wenige, belastbare Befunde.** Ein Gutachten mit 300 Kleinigkeiten wird nicht gelesen. Die Agenten priorisieren und begrenzen sich.
- **Vorschläge halten sich selbst an das Regelwerk.** Kein Semikolon, kein Gedankenstrich, keine Ich-Form in einem Verbesserungsvorschlag.
- **Fehlende Quellen werden nie erfunden.** Wo ein Beleg fehlt, wird `\quellefehlt{...}` (oder der konfigurierte Marker) vorgeschlagen, mit einem Hinweis, wonach zu suchen ist.

## Modi

Den Modus aus der Bitte ableiten. Im Zweifel `kapitel` für einzelne Kapitel und `voll` für die ganze Arbeit.

| Modus | Wann | Umfang |
|---|---|---|
| `schnell` | "kurz drüberschauen", nach kleinen Änderungen | nur Skripte, Bericht |
| `kapitel` | ein Kapitel oder Abschnitt genannt | Skripte, Lektor, und je nach Kapitel Methodiker oder Mathematiker |
| `voll` | ganze Arbeit, "alles prüfen" | Skripte, alle Gutachter außer Quellenprüfer, Bericht, PDF |
| `abgabe` | "abgabereif?", vor der Abgabe | wie `voll`, dazu Quellenprüfer und Abgabe-Checkliste |

## Ablauf

Alle Befehle laufen aus der Projektwurzel, also dem Verzeichnis mit `lektorat.toml`. `S` steht für das Verzeichnis dieses Skills, so wie es beim Laden als Basisverzeichnis gemeldet wird. Liegen eine projektlokale und eine globale Kopie vor, ist das gemeldete Verzeichnis maßgeblich.

### 1. Einrichten (optional)

Ohne `lektorat.toml` arbeiten alle Befehle mit automatisch erkannten Werten. Das genügt für den Modus `schnell`. Vor dem ersten Lauf mit Gutachtern lohnt sich eine Konfiguration, weil Begriffe, Forschungsfragen und Projektregeln die Gutachten schärfen. Dann `python3 S/scripts/lektorat.py init` ausführen und mit der Person kurz abstimmen und eintragen:

- feste Begriffe (`[begriffe.verboten]`) und Komposita
- Synonymgruppen (`varianten`, Formen eines Wortes mit `|` getrennt)
- Forschungsfragen (`[forschungsfragen]`) für den roten Faden
- inhaltliche Projektregeln (`projektregeln`), die nur Agenten prüfen können. Der Schlüssel steht ganz oben vor der ersten `[Tabelle]`, sonst ordnet TOML ihn der vorangehenden Tabelle zu

Eine Vorlage mit allen Optionen steht in `lektorat.beispiel.toml`. Liegt die Arbeit in einem Git-Repository, `.lektorat/` in die `.gitignore` aufnehmen, dort liegen nur erzeugte Dateien.

### 2. Mechanisch prüfen

```bash
python3 S/scripts/lektorat.py pruefen            # ganze Arbeit
python3 S/scripts/lektorat.py pruefen --nur 03_methodik  # ein Kapitel samt eingebundener Unterdateien
```

Das Ergebnis landet in `.lektorat/lauf/linter.json`. Die Ausgabe zeigt die Zahl der Befunde je Regel. Mit `--nur` gelten Befunde, Wortzahl und Index nur für die ausgewählten Dateien. Dateien, die eine passende Datei per `\input` einbindet, zählen automatisch mit.

Bei einer Prüfung der ganzen Arbeit kommen zwei Umfeldprüfungen dazu. Ihr Stand steht am Ende der Ausgabe, auch wenn alles in Ordnung ist:

- **Verzeichnisse** (`STR-VERZEICHNIS`): Enthält die Arbeit Abbildungen, Tabellen oder Abkürzungen, muss es das jeweilige Verzeichnis geben. Grundlage ist die Recorder-Datei `.fls` des letzten LaTeX-Laufs, weil Vorlagen die Verzeichnisse oft in Klassendateien und hinter Optionen erzeugen. Ohne Build wird der Quelltext samt Vorlagen durchsucht.
- **Versionierung** (`ABG-VERSIONIERUNG`, `ABG-GIT-STAND`): Empfehlung, die Arbeit in einem privaten Git-Repository zu sichern. Ist eines eingerichtet, prüft der Skill, ob es ein Remote gibt, ob es privat ist (über `gh`, falls installiert), wie viele Dateien nicht committet und wie viele Commits nicht gepusht sind. `.lektorat/` zählt nicht mit. Der Skill committet und pusht nie selbst. Mit `[git] pruefen = false` in `lektorat.toml` lässt sich die Prüfung abschalten.

Ein fehlendes Verzeichnis ist ein Mangel der Arbeit und zählt wie jede Warnung zum Lektoratsindex. Die Git-Befunde zählen nicht, weil sie nichts über die Arbeit selbst sagen.

### 3. Gutachter einsetzen (Modi `kapitel`, `voll`, `abgabe`)

Zuerst `python3 S/scripts/lektorat.py kontext` ausführen. Das liefert Gliederung, Dateien mit Wort- und Formelzahl, Marker und Projektregeln. Danach die Gutachter so zuschneiden, dass jeder höchstens etwa 6.000 Wörter liest. Bei längeren Arbeiten den Lektor auf mehrere Instanzen nach Kapiteln aufteilen.

| Rolle | Datei | Liest | Prüft |
|---|---|---|---|
| Lektor | `agents/lektor.md` | die zugeteilten Kapitel | Klarheit, versteckte Wertungen, Tempus, Begriffe, Hauptaussage |
| Methodiker | `agents/methodiker.md` | Einleitung, Modell, Methodik, Ergebnisse, Diskussion, Fazit | Forschungsfragen, Hypothesen, Setzungen, Limitationen, Begründungen, Kapitelinhalt |
| Mathematiker | `agents/mathematiker.md` | nur Dateien, für die `kontext` abgesetzte Formeln meldet | Verständlichkeit, Notation, Rechenbeispiele, Verteidigbarkeit |
| Roter Faden | `agents/roter-faden.md` | die ganze Arbeit überfliegend, Anfang und Ende jedes Kapitels genau | Zusammenhang, Doppelungen, Zahlenkonsistenz, Detailtiefe, Abbildungen |
| Quellenprüfer | `agents/quellenpruefer.md` | Sätze mit Zitaten und belegpflichtige Aussagen | Quellentreue, Belegpflicht |

Alle Gutachter **parallel in einer Nachricht** über das Agent-Tool starten. Jeder bekommt im Prompt:

- den Pfad seiner Rollendatei und von `agents/_gemeinsam.md` (beide zuerst lesen)
- die zu lesenden Dateien mit absolutem Pfad
- den Pfad zu `.lektorat/lauf/linter.json`, damit mechanisch gefundene Punkte nicht doppelt gemeldet werden
- Projektregeln und Forschungsfragen aus der `kontext`-Ausgabe
- die Ausgabedatei `.lektorat/lauf/agenten/<rolle>.json` (bei mehreren Lektoren `lektor-1.json`, `lektor-2.json`)

Im Modus `kapitel` gibt es keinen eigenen Gutachter für den roten Faden. Der Methodiker übernimmt dann `STR-DOPPELUNG` und `INH-ZAHLEN` innerhalb des Kapitels. Alle Gutachter dürfen Nachbarkapitel und Anhang zum Abgleich lesen (etwa, ob eine Festlegung in der Methodik steht), melden aber nur Befunde in den zugeteilten Dateien. Widersprüche zu anderen Kapiteln nennen sie in der Meldung mit Datei und Zeile.

Steht kein Agent-Tool zur Verfügung, die Rollen nacheinander selbst abarbeiten und die Dateien ebenso schreiben.

Vor jedem Lauf mit Gutachtern `python3 S/scripts/lektorat.py aufraeumen` ausführen. Der Befehl entfernt alte Agentendateien, sonst mischen sich Ergebnisse älterer Fassungen in den Bericht.

### 4. Bericht erzeugen

```bash
python3 S/scripts/lektorat.py bericht
```

Führt Linter- und Agentenbefunde zusammen, schreibt `.lektorat/Lektoratsbericht.html`, legt einen Eintrag in `.lektorat/verlauf/` an und gibt eine Zusammenfassung mit Lektoratsindex aus. Der Index zählt Fehler fünffach, Warnungen doppelt und Hinweise halb, je 1.000 Wörter. Über den Verlauf wird sichtbar, wie die Arbeit besser wird. Mit `--ohne-verlauf` entsteht ein Bericht ohne Verlaufseintrag, etwa für Zwischenstände.

### 5. Markierte PDF (Modi `voll`, `abgabe` oder auf Wunsch)

```bash
python3 S/scripts/lektorat.py annotieren
```

Der Bau dauert bei einer Masterarbeit einige Minuten, daher im Hintergrund starten. Das Ergebnis ist `.lektorat/Lektoratsfassung.pdf`: eine Legende vorn, farbige hochgestellte Nummern im Text und ein Kapitel *Lektoratsbefunde* am Ende, auf das jede Nummer verlinkt.

| Farbe | Bedeutung |
|---|---|
| Rot | Quelle fehlt (Marker der schreibenden Person, schon im Original rot) |
| Orange | offener Punkt (Marker der schreibenden Person) |
| Magenta | Beleg prüfen |
| Blau | Sprache und Typografie |
| Violett | Struktur, Verweise, Inhalt |

Liegt ein Befund in einer Tabelle, Abbildung oder Formel, steht die Marke direkt vor dem Objekt, damit der Bau nicht bricht.

### 6. Antworten

Die Antwort im Chat bleibt kurz und priorisiert:

1. Index und Zahlen aus der Zusammenfassung, bei Folgeläufen auch, was behoben und was neu ist. Im Modus `schnell` dazusagen, dass Inhalt, Methodik und Quellentreue nicht geprüft wurden.
2. Die wichtigsten fünf bis zehn Befunde, Fehler und inhaltliche Warnungen zuerst, mit Fundstelle als Link `[datei:zeile](pfad:zeile)`.
3. Offene Marker als Zahl, mit Verweis auf den Bericht.
4. Den Stand von Verzeichnissen und Git in einem Satz. Gibt es kein privates Repository oder ungesicherte Änderungen, das als Empfehlung nennen, nicht als Textfehler.
5. Link zum Bericht, und zur PDF nur, wenn sie in diesem Lauf gebaut wurde. Eine ältere `Lektoratsfassung.pdf` ausdrücklich als veraltet kennzeichnen.
6. Ein Angebot, bestimmte Befunde zu beheben. Keine Änderung ohne Zustimmung.

Im Modus `abgabe` zusätzlich die Checkliste aus `references/kapitel-checklisten.md` (Abschnitt Abgabe) mit erfüllt oder offen ausgeben.

## Ausnahmen

Ein Befund, der bewusst so bleiben soll, wird im Quelltext ausgenommen. So bleibt die Entscheidung sichtbar und begründbar.

```latex
Die Werte liegen zwischen 1 und 5. % lektorat: ignore TYP-ZAHLWORT
% lektorat: ignore SAT-LAENGE
Ein bewusst langer Satz, der in der nächsten Zeile steht ...
% lektorat: ignore-file FMT-QUELLTEXT-ZEILE
```

Regeln lassen sich je Projekt in `lektorat.toml` unter `[schwere]` umstufen oder mit `"aus"` abschalten. Einzelne Wörter, die nie gemeldet werden sollen, stehen unter `[ausnahmen] woerter`.

## Befundformat der Gutachter

Jede Agentendatei ist ein JSON-Array:

```json
[
  {
    "regel": "INH-SETZUNG",
    "schwere": "Warnung",
    "datei": "src/Chapters/03_methodik.tex",
    "zeile": 300,
    "auszug": "wörtlicher Auszug aus der Zeile",
    "meldung": "Was das Problem ist, in einem Satz.",
    "vorschlag": "Konkreter Ersatz oder nächster Schritt."
  }
]
```

`datei` ist relativ zur Projektwurzel, wie in `linter.json`. `regel` stammt aus `regelwerk.toml`. Passt keine Regel, die naheliegendste wählen und das in der Meldung sagen, statt neue IDs zu erfinden.

## Weiterführend

- `references/regelwerk.md`: alle Regeln mit Begründung, Herkunft und Beispiel
- `references/konventionen.md`: Zeitformen, Zahlen, Abbildungsquellen, Zitierweise, Abkürzungen
- `references/kapitel-checklisten.md`: Pflichtbestandteile je Kapiteltyp und Abgabe-Checkliste
- `references/wi-methodik.md`: Gütekriterien und Methodik in der Wirtschaftsinformatik
- `evals/`: Testkorpus mit eingebauten Fehlern und Messung von Trefferquote und Fehlalarmen (`python3 S/evals/run_evals.py`)

Nach einer Änderung an `regelwerk.toml`: `python3 S/scripts/lektorat.py regeln` erzeugt `references/regelwerk.md` neu, und `python3 S/evals/run_evals.py` prüft, dass die Erkennung nicht schlechter wurde.
