# Conventions

Explanations for rules that need more context than one line in the rule set. Examples are German, as in the texts under review.

## Tense (`SPR-TEMPUS`)

In German academic writing the tense follows the content, not the chapter. The basic rule: present tense (Präsens) for what holds, simple past (Präteritum) for what happened in the writer's own study.

| Content | Tense | Example |
|---|---|---|
| Theory, definitions, widely accepted findings | Präsens | Extraversion beschreibt die Neigung zu Geselligkeit. |
| Reporting literature | Präsens | \textcite{goldberg1990} zeigt, dass ... |
| Concrete procedure of an earlier single study | Präteritum possible | In der Studie bewerteten 388 Personen vier Stimmen. |
| Structure and content of the own work, cross-references | Präsens | \cref{tab:x} zeigt die Kennwerte. Kapitel 5 beschreibt ... |
| Description of the system or prototype | Präsens | Das Backend speichert jede Runde. |
| Study design, instruments, analysis plan | Präsens | Die Zuweisung erfolgt nach Anmeldeposition. |
| Conduct of the own data collection, sample | Präteritum | Es nahmen 48 Personen teil. Vier brachen ab. |
| Concrete own results | Präteritum or Präsens, consistently | Die adaptive Bedingung erzielte höhere Werte. |
| Interpretation, discussion, conclusion | Präsens | Das Ergebnis spricht dafür, dass ... |
| Outlook | Präsens or Futur | Künftige Arbeiten können prüfen, ob ... |

Consistency matters more than any single assignment. Within a paragraph the tense only changes when the content changes. The Perfekt sounds spoken and stays the exception.

For a method chapter written before data collection and finished afterwards: design and instruments in Präsens, because they describe the study as designed. What actually happened (recruitment, dropouts, deviations from the plan) in Präteritum.

## Numbers (`TYP-ZAHLWORT`)

In running text the numbers zero to twelve are written as words, from 13 on as digits. This is a common convention of German style guides and Duden recommendations. APA 7 sets the limit at ten for English, the rule set follows the German convention.

Digits are used nevertheless for:

- units and percent: 8\,s, 5\,\%
- identifiers: Kapitel 5, Item 3, H1, Stufe 2, Version 19
- scale values, measurements, weights and results: Skalenmitte 3, Gewicht 0,5
- series with larger numbers: zwischen 5 und 40 Personen
- tables, figures, formulas and dates

## Figure sources (`FMT-ABB-QUELLE`)

Every figure states its origin at the end of the caption.

| Case | Wording |
|---|---|
| created entirely by the writer | `Eigene Darstellung` |
| created by the writer after a template, modified | `Eigene Darstellung nach \textcite{key}` |
| taken over unchanged | `Quelle: \textcite{key}` (mind usage rights) |
| screenshot of the writer's own software | `Eigene Darstellung` |

Example:

```latex
\caption{Architektur des Prototyps. Eigene Darstellung}
\caption{Forschungsmodell. Eigene Darstellung nach \textcite{davis1989}}
```

The same applies to tables as soon as they take over or adapt content from a source. Tables with the writer's own data need no statement.

## Citation style (`ZIT-*`)

- `\textcite{key}` inside the sentence: \textcite{goldberg1990} zeigt ...
- `\parencite{key}` at the end of the sentence before the period: ... \parencite{goldberg1990}.
- several sources: `\parencites{a}{b}` or `\parencite{a,b}`, chronological or alphabetical, but consistent
- page for verbatim quotes: `\parencite[S.~12]{key}`
- Citations refer to the sentence. If one source covers a whole paragraph, it goes into the first sentence and the paragraph makes clear that it keeps reporting it.
- Secondary citations (zitiert nach) only if the original is not accessible.

## Abbreviations and typography

| Case | Notation |
|---|---|
| multi-part abbreviation | `z.\,B.`, `d.\,h.`, `u.\,a.`, `i.\,d.\,R.` |
| percent | `15\,\%` |
| equation in text | `$N = 40$` |
| range | `S.~12--15`, `2020--2026` |
| quotation marks | `\enquote{...}` |
| technical abbreviation | `\gls{a:LLM}` from the glossary, first use writes it out |
| decimal number | comma: 0,5. In formulas via `{,}` or the icomma package |

## Gender-inclusive language

The rules contain no requirement. If the work chooses a form (Doppelnennung, participles like Teilnehmende, neutral forms like Person), `TERM-VARIANTEN` only checks that it stays consistent.
