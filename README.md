# scientific-writing-for-german-business-informatics

**English summary:** `thesis-lektor` is an agent skill for Claude Code, Codex and other agents that reviews German academic writing in LaTeX, tailored to business informatics (Wirtschaftsinformatik). A deterministic linter checks typography, language, citations, bibliography, cross-references, lists of figures and tables, and whether the work is safely versioned in Git. Reviewer agents in fixed roles check content, method, formulas, coherence and whether sources support the claims. The output is an HTML report with a history and an annotated PDF. Install it with `npx skills add whoismarios/scientific-writing-for-german-business-informatics` and run `/thesis-lektor`. Rules and messages are in German.

---

`thesis-lektor` ist ein Lektorats-Skill für deutschsprachige wissenschaftliche Arbeiten in **LaTeX**, zugeschnitten auf die Wirtschaftsinformatik. Er prüft Bachelor- und Masterarbeiten, Seminararbeiten und Paper gegen ein festes Regelwerk. Am Quelltext ändert er nichts.

- **Mechanische Prüfung:** Ein Skript prüft Typografie, Sprache, Satzbau, Begriffe, Zitation, Bibliografie, Verweise, Verzeichnisse, Gliederung und Formeln. Gleicher Text ergibt immer dieselben Befunde.
- **Gutachter-Agenten:** Fünf Rollen prüfen, was ein Skript nicht erkennen kann: Lektor, Methodiker, Mathematiker, roter Faden und Quellenprüfer.
- **Datensicherung:** Der Skill empfiehlt ein privates Git-Repository und meldet nicht committete oder nicht gepushte Änderungen.
- **Ergebnis:** ein HTML-Bericht mit Lektoratsindex und Verlauf, dazu eine Kopie der Arbeit als PDF mit farbigen Befundmarken.

## Installation

```bash
npx skills add whoismarios/scientific-writing-for-german-business-informatics -g
```

Die CLI fragt, für welche Agenten installiert werden soll. Mit `-a claude-code` oder `-a codex` lässt sich das vorgeben. Ohne `-g` landet der Skill nur im aktuellen Projekt.

Ohne `npx` genügt es, den Ordner `skills/thesis-lektor` in das Skill-Verzeichnis des Agenten zu kopieren:

| Agent | für alle Projekte | nur für ein Projekt |
|---|---|---|
| Claude Code | `~/.claude/skills/thesis-lektor` | `.claude/skills/thesis-lektor` |
| Codex | `~/.agents/skills/thesis-lektor` | `.agents/skills/thesis-lektor` |

Voraussetzung ist Python 3.11 oder neuer. Weitere Pakete braucht der Skill nicht. Für die markierte PDF wird eine LaTeX-Distribution mit `latexmk` gebraucht. `git` und die GitHub-CLI `gh` braucht nur die Prüfung der Versionierung.

## Benutzung

Im Ordner der Arbeit den Agenten starten und den Befehl eingeben:

```text
/thesis-lektor
```

Eine Einrichtung ist nicht nötig. Der Skill findet Hauptdatei, Bibliografie, Glossar und Marker-Makros selbst. Hinter dem Befehl lässt sich der Umfang angeben:

| Aufruf | Umfang |
|---|---|
| `/thesis-lektor` oder `/thesis-lektor schnell` | nur Skripte über die ganze Arbeit |
| `/thesis-lektor kapitel Methodik` | ein Kapitel, mit Lektor und Methodiker oder Mathematiker |
| `/thesis-lektor voll` | ganze Arbeit mit allen Gutachtern und markierter PDF |
| `/thesis-lektor abgabe` | wie `voll`, dazu Quellenprüfung und Abgabe-Checkliste |

Der Skill reagiert auch ohne Befehl auf Bitten wie „Schau mal über Kapitel 5“, „Fehlen irgendwo Quellen?“ oder „Ist die Arbeit abgabereif?“.

Die Ergebnisse liegen danach im Ordner `.lektorat/` der Arbeit:

- `Lektoratsbericht.html` mit allen Befunden, Filtern und Verlauf
- `Lektoratsfassung.pdf` mit farbigen Marken im Text und einem Befundkapitel am Ende

Den Ordner in die `.gitignore` aufnehmen.

| Farbe | Bedeutung |
|---|---|
| Rot | Quelle fehlt (Marker `\quellefehlt{...}` der schreibenden Person) |
| Orange | offener Punkt (Marker `\offen{...}`) |
| Magenta | Beleg prüfen |
| Blau | Sprache und Typografie |
| Violett | Struktur, Verweise, Inhalt |

## Anpassen an eine Arbeit

Wer Begriffe, Forschungsfragen oder eigene Regeln festlegen will, legt mit `init` eine Konfigurationsdatei an. Der Befehl läuft im Ordner der Arbeit:

```bash
python3 ~/.claude/skills/thesis-lektor/scripts/lektorat.py init
```

Danach in `lektorat.toml` eintragen, was für diese Arbeit gilt:

- verbotene und feste Begriffe
- Synonymgruppen
- Forschungsfragen
- inhaltliche Regeln für die Gutachter

Alle Optionen mit Kommentaren stehen in [lektorat.beispiel.toml](skills/thesis-lektor/lektorat.beispiel.toml).

Ein Befund, der bewusst so bleiben soll, wird im Quelltext mit `% lektorat: ignore REGEL-ID` ausgenommen.

## Regelwerk

Alle Regeln stehen in [regelwerk.toml](skills/thesis-lektor/regelwerk.toml), jede mit Begründung, Herkunft und je einem falschen und einem richtigen Beispiel. Eine lesbare Fassung liegt in [regelwerk.md](skills/thesis-lektor/references/regelwerk.md). Beispiele für Regeln:

- kein Semikolon, kein Gedankenstrich als Einschub
- keine Ich- und Wir-Form, keine wertenden Wörter ohne Beleg
- Zahlen bis zwölf ausgeschrieben
- Zitation mit `\textcite` und `\parencite`
- jede Abbildung mit Herkunftsangabe
- jede Formel mit erklärten Variablen und Rechenbeispiel

## Mitwirken

Neue oder geänderte Regeln kommen in `regelwerk.toml`. Für jede mechanische Regel gehört ein Testfall mit `% erwartet: REGEL-ID` in `skills/thesis-lektor/evals/fixture/`. Danach die Übersicht neu erzeugen und den Testkorpus prüfen:

```bash
python3 skills/thesis-lektor/scripts/lektorat.py regeln
```

```bash
python3 skills/thesis-lektor/evals/run_evals.py
```

Die Messung muss bei 100 % Trefferquote und 100 % Genauigkeit bleiben.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
