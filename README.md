<p align="center">
  <img src="assets/banner.svg" alt="thesis-editor: Lektorat für wissenschaftliche Arbeiten in LaTeX" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="LaTeX" src="https://img.shields.io/badge/LaTeX-only-008080?style=flat-square&logo=latex&logoColor=white">
  <img alt="Claude Code Skill" src="https://img.shields.io/badge/Claude_Code-skill-D97757?style=flat-square&logo=claude&logoColor=white">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-skill-412991?style=flat-square&logo=openai&logoColor=white">
  <img alt="npx skills" src="https://img.shields.io/badge/npx-skills_add-CB3837?style=flat-square&logo=npm&logoColor=white">
  <br>
  <img alt="84 Regeln" src="https://img.shields.io/badge/Regeln-84-7a3fc4?style=flat-square">
  <img alt="Trefferquote 100 %" src="https://img.shields.io/badge/Trefferquote-100%25-22c55e?style=flat-square">
  <img alt="Fehlalarme 0" src="https://img.shields.io/badge/Fehlalarme-0-22c55e?style=flat-square">
  <img alt="Keine Abhängigkeiten" src="https://img.shields.io/badge/dependencies-none-64748b?style=flat-square">
</p>

<p align="center">
  <b>Ein Agent-Skill, der deine Abschlussarbeit liest wie Lektorat, Erst- und Zweitgutachten zusammen.</b><br>
  Er markiert, was fehlt oder besser werden kann, und ändert keine einzige Zeile deines Quelltexts.
</p>

<p align="center">
  <a href="#installation">Installation</a> ·
  <a href="#schnellstart">Schnellstart</a> ·
  <a href="#was-geprüft-wird">Was geprüft wird</a> ·
  <a href="#ergebnisse">Ergebnisse</a> ·
  <a href="#konfiguration">Konfiguration</a> ·
  <a href="#english">English</a>
</p>

---

## Warum

Wer eine Abschlussarbeit schreibt, bekommt Rückmeldung meist spät und verstreut. Am Ende fehlen Quellen, Begriffe wechseln, Wertungen stehen ohne Beleg im Text, und die Forschungsfragen werden im Fazit nicht beantwortet. `thesis-editor` prüft das laufend und nachvollziehbar:

|  | Mechanische Prüfung | Gutachter-Agenten |
|---|---|---|
| **Was** | Typografie, Sprache, Satzbau, Begriffe, Zitation, Bibliografie, Verweise, Verzeichnisse, Formeln | Inhalt, Methodik, Formeln, roter Faden, Quellentreue |
| **Wie** | Python-Skript, gleicher Text ergibt immer dieselben Befunde | fünf Rollen mit festen Prüfaufträgen, laufen parallel |
| **Belegt durch** | Datei, Zeile, Auszug, Regel-ID | Datei, Zeile, wörtlicher Auszug, Regel-ID |

Jeder Befund verweist auf eine Regel mit Begründung, Herkunft und Beispiel. So lässt sich jede Anmerkung prüfen, annehmen oder begründet ablehnen.

## Installation

Empfohlen ist die Installation für alle Projekte. Dann steht `/thesis-editor` in jedem Ordner zur Verfügung, in dem du den Agenten startest.

```bash
npx skills add whoismarios/scientific-writing-for-german-business-informatics --global
```

Wie bei `npm` gilt: Ohne `--global` installiert die CLI nur in das Projekt, in dem du den Befehl ausführst. Der Skill liegt dann im Projektordner und lässt sich mit dem Projekt teilen.

| Ziel | Befehl | Speicherort bei Claude Code |
|---|---|---|
| für alle Projekte (empfohlen) | `npx skills add whoismarios/scientific-writing-for-german-business-informatics --global` | `~/.claude/skills/thesis-editor` |
| nur für das aktuelle Projekt | `npx skills add whoismarios/scientific-writing-for-german-business-informatics` | `./.claude/skills/thesis-editor` |

Ohne weitere Angaben fragt die CLI, für welche Agenten installiert werden soll. Diese Optionen ersetzen die Rückfragen:

| Option | Kurzform | Wirkung | Beispiel |
|---|---|---|---|
| `--global` | `-g` | für alle Projekte des Benutzerkontos statt nur für das aktuelle Projekt | `--global` |
| `--agent <name>` | `-a` | nur für diese Agenten, mehrfach angebbar | `--agent claude-code --agent codex` |
| `--yes` | `-y` | keine Rückfragen, etwa für Skripte | `--yes` |
| `--copy` | | Dateien kopieren statt verlinken | `--copy` |
| `--list` | `-l` | nur anzeigen, was das Repository enthält, nichts installieren | `--list` |

Aktualisieren und entfernen:

```bash
npx skills update thesis-editor --global
```

```bash
npx skills remove thesis-editor --global
```

<details>
<summary><b>Ohne npx installieren</b></summary>

<br>

Den Ordner `skills/thesis-editor` in das Skill-Verzeichnis des Agenten kopieren:

| Agent | für alle Projekte | nur für ein Projekt |
|---|---|---|
| Claude Code | `~/.claude/skills/thesis-editor` | `.claude/skills/thesis-editor` |
| Codex | `~/.agents/skills/thesis-editor` | `.agents/skills/thesis-editor` |

```bash
git clone https://github.com/whoismarios/scientific-writing-for-german-business-informatics.git
```

```bash
cp -R scientific-writing-for-german-business-informatics/skills/thesis-editor ~/.claude/skills/
```

</details>

**Voraussetzungen**

| | Wofür | Pflicht |
|---|---|:---:|
| Arbeit in LaTeX | Grundlage aller Prüfungen | ✅ |
| Python 3.11 oder neuer | Skripte, ohne weitere Pakete | ✅ |
| `latexmk` | markierte PDF | ➖ |
| `git` und `gh` | Prüfung der Datensicherung | ➖ |

## Schnellstart

Im Ordner der Arbeit den Agenten starten und eingeben:

```text
/thesis-editor
```

Eine Einrichtung ist nicht nötig. Der Skill findet Hauptdatei, Bibliografie, Glossar und Marker-Makros selbst. Hinter dem Befehl lässt sich der Umfang angeben:

| Befehl | Umfang | Dauer |
|---|---|---|
| `/thesis-editor` | mechanische Prüfung der ganzen Arbeit | Sekunden |
| `/thesis-editor since HEAD` | nur Absätze, die seit dem letzten Commit geändert wurden | Sekunden |
| `/thesis-editor chapter Methodik` | ein Kapitel, mit Editor und Methodologist oder Mathematician | wenige Minuten |
| `/thesis-editor full` | ganze Arbeit, alle Gutachter, markierte PDF | mehrere Minuten |
| `/thesis-editor submit` | wie `full`, dazu Quellenprüfung und Abgabe-Checkliste | mehrere Minuten |
| `/thesis-editor defense` | Fragenkatalog für das Kolloquium mit Antworten und offenen Flanken | einige Minuten |

Der Skill reagiert auch ohne Befehl auf Bitten wie *„Schau mal über Kapitel 5“*, *„Was habe ich seit gestern geändert?“*, *„Fehlen irgendwo Quellen?“*, *„Ist die Arbeit abgabereif?“* oder *„Was fragen die mich im Kolloquium?“*.

## Was geprüft wird

| Bereich | Regeln | Beispiele |
|---|:---:|---|
| ✍️ Sprache und Ton | 12 | keine Ich- und Wir-Form, keine Wertungen ohne Beleg, keine Floskeln, kein Hedging, Zeitformen |
| 🔤 Typografie | 9 | kein Semikolon, kein Gedankenstrich als Einschub, Zahlen bis zwölf ausgeschrieben, `z.\,B.` |
| 📐 Satzbau | 4 | Satzlänge, Schachtelsätze, Genitivketten, Hauptaussage vorn |
| 🏷️ Begriffe | 7 | feste Begriffe, Synonyme, Komposita mit Bindestrich, Abkürzungen über `\gls` |
| 📚 Zitation | 8 | `\textcite` und `\parencite`, keine manuellen Zitate, Quellentreue |
| 🗂️ Bibliografie | 5 | ungenutzte Einträge, Pflichtfelder, DOI, Dubletten, Preprints |
| 🔗 Formatierung und Verweise | 10 | Abbildungsquelle, `\cref`, Verweis vor dem Objekt, booktabs |
| 🧭 Struktur | 8 | Einleitung je Abschnitt, roter Faden, Doppelungen, Verzeichnisse |
| 🔬 Inhalt und Methodik | 8 | Belegpflicht, Forschungsfragen beantwortet, Setzungen begründet, Limitationen |
| ➗ Formeln | 3 | Variablen erklärt, Rechenbeispiel, einheitliche Notation |
| 🖼️ Abbildungen | 1 | Gestaltung und Lesbarkeit |
| 🛠️ Build-Log | 5 | LaTeX-Fehler, Verweise und Zitate als ??, Zeilen im Rand, biber-Warnungen, jeweils an der Quelltextzeile |
| 💾 Abgabe | 2 | privates Git-Repository, alles committet und gepusht |
| 📌 Marker | 2 | offene Punkte und fehlende Quellen der schreibenden Person |

Alle Regeln mit Begründung und Beispielen stehen in [rules.md](skills/thesis-editor/references/rules.md).

### Die Gutachter

| Rolle | Liest wie | Achtet auf |
|---|---|---|
| 📝 **Editor** | Lektorat | Klarheit, versteckte Wertungen, Zeitformen, Begriffe, Hauptaussage je Absatz |
| 🎓 **Methodologist** | Erstgutachten | Forschungsfragen, Hypothesen, Setzungen, Begründungen, Limitationen |
| ➗ **Mathematician** | Zweitgutachten | Verständlichkeit und Verteidigbarkeit jeder Formel |
| 🧵 **Coherence** | Erstlesende | Zusammenhang, Doppelungen, Zahlenkonsistenz, Detailtiefe |
| 🔎 **Source checker** | Peer Review | ob die zitierte Quelle die Aussage trägt, Belegpflicht |
| 🎤 **Examiner** | Prüfungskommission | wahrscheinliche Fragen im Kolloquium, Stichpunktantworten aus der Arbeit, Lücken |

## Ergebnisse

Alles landet im Ordner `.thesis-editor/` der Arbeit. Er gehört in die `.gitignore`.

| Datei | Inhalt |
|---|---|
| `report.html` | alle Befunde mit Filtern, Suche, Lektoratsindex und Verlauf über alle Läufe |
| `annotated.pdf` | Kopie der Arbeit mit farbigen Befundnummern, Legende und verlinktem Befundkapitel |
| `defense.html` | Übungsseite fürs Kolloquium: Fragen nach Kategorie und Schwierigkeit, Antworten zum Aufklappen, zufällige Reihenfolge, offene Flanken |

Der **Lektoratsindex** zählt Fehler fünffach, Warnungen doppelt und Hinweise halb, je 1.000 Wörter. Niedriger ist besser. Über den Verlauf wird sichtbar, was behoben wurde und was neu ist.

| Farbe | Bedeutung |
|---|---|
| ![](https://img.shields.io/badge/%20-%20-d92d20?style=flat-square) Rot | Quelle fehlt, Marker `\quellefehlt{...}` |
| ![](https://img.shields.io/badge/%20-%20-e8590c?style=flat-square) Orange | offener Punkt, Marker `\offen{...}` |
| ![](https://img.shields.io/badge/%20-%20-c11574?style=flat-square) Magenta | Beleg prüfen |
| ![](https://img.shields.io/badge/%20-%20-2a5bd7?style=flat-square) Blau | Sprache und Typografie |
| ![](https://img.shields.io/badge/%20-%20-7a3fc4?style=flat-square) Violett | Struktur, Verweise, Inhalt |

## Konfiguration

Optional. Wer Begriffe, Forschungsfragen oder eigene Regeln festlegen will, legt im Ordner der Arbeit eine Konfiguration an:

```bash
python3 ~/.claude/skills/thesis-editor/scripts/cli.py init
```

```toml
project_rules = ["Jede Modellwahl wird mit Kosten und Qualität begründet."]

[terms]
compounds = ["KI-Assistent"]
variants = [["Nutzer|Nutzers|Nutzern", "Anwender|Anwendern"]]

[terms.forbidden]
"Webseite*" = "Website"

[research_questions]
FF1 = "Wie wirkt sich X auf Y aus?"
```

Alle Optionen mit Kommentaren stehen in [thesis-editor.example.toml](skills/thesis-editor/thesis-editor.example.toml). Ein Befund, der bewusst so bleiben soll, wird im Quelltext ausgenommen:

```latex
Die Werte liegen zwischen 1 und 5. % thesis-editor: ignore TYP-ZAHLWORT
```

<details>
<summary><b>Kommandozeile ohne Agent</b></summary>

<br>

Die mechanische Prüfung läuft auch ohne Agent:

```bash
python3 ~/.claude/skills/thesis-editor/scripts/cli.py check
```

| Befehl | Wirkung |
|---|---|
| `init` | legt `thesis-editor.toml` mit erkannten Werten an |
| `check` | mechanische Prüfung und Auswertung des letzten LaTeX-Logs |
| `context` | Gliederung, Wortzahlen, Formeln, Marker und Projektregeln für die Gutachter |
| `report` | `report.html` und Verlaufseintrag |
| `annotate` | `annotated.pdf` |
| `defense` | erzeugt `defense.html` aus den Fragen des Examiners |
| `clean` | entfernt Befunde und Fragen älterer Agentenläufe |
| `rules` | erzeugt `references/rules.md` aus `rules.toml` |

| Option | Kurzform | Befehl | Wirkung | Beispiel |
|---|---|---|---|---|
| `--since <rev>` | `-s` | `check` | nur Absätze, die seit dieser Git-Revision geändert wurden, auch neue Dateien | `check --since HEAD~1` |
| `--only <regex>` | `-o` | `check` | nur Dateien, deren Pfad passt, samt eingebundener Dateien | `check --only 03_methodik` |
| `--force` | `-f` | `init` | vorhandene Konfiguration überschreiben | `init --force` |
| `--no-history` | | `report` | Bericht ohne Verlaufseintrag, etwa für Zwischenstände | `report --no-history` |
| `--no-build` | | `annotate` | markierte Kopie vorbereiten, aber nicht kompilieren | `annotate --no-build` |
| `--root <pfad>` | | alle | Projektwurzel, Standard ist das aktuelle Verzeichnis | `check --root ~/thesis` |
| `--help` | `-h` | alle | Hilfe zum Befehl | `check --help` |

</details>

## Mitwirken

Neue Regeln sind willkommen. Jede Regel steht in [rules.toml](skills/thesis-editor/rules.toml), und jede mechanische Regel braucht einen Testfall mit `% expect: REGEL-ID` in `skills/thesis-editor/evals/fixture/`.

```bash
python3 skills/thesis-editor/scripts/cli.py rules
```

```bash
python3 skills/thesis-editor/evals/run_evals.py
```

Die Messung muss bei 100 % Trefferquote und 0 Fehlalarmen bleiben.

Skill, Befehle, Optionen, Konfigurationsschlüssel und Dateinamen sind englisch. Regeln, Meldungen und Berichte sind deutsch, weil sie deutsche Texte prüfen und von der schreibenden Person gelesen werden.

## English

`thesis-editor` is an agent skill for Claude Code, Codex and other agents that reviews German academic writing in LaTeX, tailored to business informatics (Wirtschaftsinformatik). A deterministic linter checks typography, language, citations, bibliography, cross-references, lists of figures and tables, the LaTeX build log, and whether the work is safely versioned in Git. Five reviewer agents check content, method, formulas, coherence and whether sources support the claims. The result is an HTML report with history and an annotated PDF. The source is never modified.

```bash
npx skills add whoismarios/scientific-writing-for-german-business-informatics --global
```

Run `/thesis-editor` inside your thesis folder, optionally followed by `chapter <name>`, `since <rev>`, `full`, `submit` or `defense` (question catalogue for the oral defense). The check also reads the LaTeX and biber logs of the last build. Commands, flags and config keys are English. Rules, findings and reports are German.

## Lizenz

[MIT](LICENSE) © 2026 Marios Tzialidis
