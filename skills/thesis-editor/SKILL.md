---
name: thesis-editor
description: >-
  Editorial review for German-language academic writing in LaTeX, tailored to business informatics (Wirtschaftsinformatik):
  bachelor and master theses, seminar papers, papers. Deterministically checks typography, language, sentence structure, terminology,
  citations, bibliography, cross-references, lists of figures/tables/abbreviations, outline and whether the work is safely versioned in Git.
  Reviewer agents in fixed roles check content, methodology, formulas, coherence and whether sources support the claims.
  Produces an HTML report with history and a color-annotated PDF. Missing sources and open points are reported separately.
  Use this skill whenever a thesis, chapter or section written in LaTeX should be checked, proofread, edited or reviewed, or before submission,
  also for casual requests such as "schau mal über Kapitel 5", "ist das so abgabereif?", "such wertende Wörter",
  "fehlen irgendwo Quellen?", "passt der rote Faden?", "proofread my thesis" or "check my chapter for style issues".
argument-hint: "[quick | chapter <name> | full | submit]"
compatibility: LaTeX projects only. Python 3.11+ without extra packages. Optional latexmk for the annotated PDF, git and gh for the versioning check.
license: MIT
---

# thesis-editor

The skill reviews an academic text in two layers:

1. **Mechanical** via `scripts/cli.py`. The same text always yields the same findings. This layer covers everything recognizable from characters, words and LaTeX structure.
2. **Judgment** via reviewer agents in fixed roles. This layer only checks what a script cannot: meaning, justification, coherence, and whether a source supports a claim.

The skill is built for **LaTeX**. It reads `.tex` files from `\begin{document}` of the main file on, resolves `\input` and `\include`, and parses biblatex or BibTeX files. It does not check Word, Markdown or Google Docs. If the work is in another format, tell the person instead of letting the scripts fail. The reviewer agents could read any text, but their findings point to file and line in the LaTeX source.

**Language.** Commands, flags, config keys and these instructions are English. The texts under review are German, and so is everything the person reads: rule titles, findings, suggestions, report and chat answer. Write findings and the chat answer in German unless the person writes in another language.

Both layers produce findings in the same format, with a rule ID from `rules.toml`. The rule set is the single source for rules, severities, colors and word lists. `references/rules.md` is generated from it and explains every rule with rationale and examples.

## Invocation

The skill triggers on matching requests or explicitly as `/thesis-editor`. Whatever follows the command sets mode and scope: `$ARGUMENTS`

- empty: mode `quick` on the whole work, then offer to run the reviewers
- `quick`, `full` or `submit`: that mode on the whole work
- `chapter <name>` or just a chapter name such as `Methodik` or `05`: mode `chapter` for the matching file
- German words such as `schnell`, `kapitel`, `voll` or `abgabe` map to the same modes

No setup is required. Without `thesis-editor.toml` the skill detects main file, bibliography, glossary and marker macros itself.

## Principles

- **Never modify the source.** The skill marks and suggests. Changes happen only on explicit request, one at a time and traceable. The annotated PDF is built from a copy under `.thesis-editor/build/`.
- **Every finding is evidenced** with file, line and a verbatim excerpt. A finding without location is an opinion and does not belong in the report.
- **Few, solid findings beat many.** A review with 300 nitpicks does not get read. Reviewers prioritize and cap themselves.
- **Suggestions follow the rule set themselves.** No semicolon, no dash as parenthesis, no first person in a suggestion.
- **Never invent sources.** Where evidence is missing, suggest `\quellefehlt{...}` (or the configured marker) with a hint what to search for.

## Modes

Derive the mode from the request. If unsure, `chapter` for single chapters and `full` for the whole work.

| Mode | When | Scope |
|---|---|---|
| `quick` | "kurz drüberschauen", after small edits | scripts, report |
| `chapter` | a chapter or section is named | scripts, editor, plus methodologist or mathematician depending on the chapter |
| `full` | whole work, "alles prüfen" | scripts, all reviewers except source checker, report, PDF |
| `submit` | "abgabereif?", before submission | like `full`, plus source checker and submission checklist |

## Workflow

All commands run from the project root, the directory with `thesis-editor.toml` or the main `.tex` file. `S` is this skill's directory as reported as base directory when the skill loads. If a project-local and a global copy exist, the reported directory wins.

### 1. Configure (optional)

Without `thesis-editor.toml` all commands use detected values. That is enough for mode `quick`. Before the first run with reviewers a config pays off, because terms, research questions and project rules sharpen the reviews. Run `python3 S/scripts/cli.py init`, agree with the person briefly and fill in:

- fixed terms (`[terms.forbidden]`) and compounds
- synonym groups (`variants`, forms of a word separated by `|`)
- research questions (`[research_questions]`) for the coherence review
- content rules (`project_rules`) only agents can check. The key goes at the very top before the first `[table]`, otherwise TOML assigns it to the preceding table

`thesis-editor.example.toml` lists all options. If the work lives in a Git repository, add `.thesis-editor/` to `.gitignore`, it only holds generated files.

### 2. Mechanical check

```bash
python3 S/scripts/cli.py check                      # whole work
python3 S/scripts/cli.py check --only 03_methodik   # one chapter including its \input files
```

Results go to `.thesis-editor/run/linter.json`. The output shows findings per rule. With `--only`, findings, word count and index cover only the selected files. Files included by a matching file count automatically.

A check of the whole work adds two environment checks. Their status is printed at the end of the output, also when everything is fine:

- **Lists** (`STR-VERZEICHNIS`): if the work contains figures, tables or abbreviations, the matching list must exist. The evidence is the recorder file `.fls` of the last LaTeX run, because templates often create these lists in class files behind options. Without a build the source including templates is searched.
- **Versioning** (`ABG-VERSIONIERUNG`, `ABG-GIT-STAND`): recommends keeping the work in a private Git repository. If one exists, the skill checks for a remote, whether it is private (via `gh` if installed), how many files are uncommitted and how many commits are unpushed. `.thesis-editor/` is excluded. The skill never commits or pushes. `[git] enabled = false` in `thesis-editor.toml` turns the check off.

A missing list is a defect of the work and counts towards the index like any warning. Git findings do not count, they say nothing about the text.

### 3. Run reviewers (modes `chapter`, `full`, `submit`)

First run `python3 S/scripts/cli.py context`. It prints outline, files with word and formula counts, markers, research questions and project rules. Then size the reviewers so that each reads at most about 6,000 words. For longer works split the editor into several instances by chapter.

| Role | File | Reads | Checks |
|---|---|---|---|
| Editor | `agents/editor.md` | assigned chapters | clarity, hidden judgments, tense, terms, main statement |
| Methodologist | `agents/methodologist.md` | introduction, model, method, results, discussion, conclusion | research questions, hypotheses, set parameters, limitations, justifications, chapter content |
| Mathematician | `agents/mathematician.md` | only files for which `context` reports display formulas | comprehensibility, notation, worked examples, defensibility |
| Coherence | `agents/coherence.md` | skims the whole work, beginning and end of each chapter in full | flow, duplication, consistent numbers, level of detail, figures |
| Source checker | `agents/source-checker.md` | sentences with citations and claims that need evidence | fidelity to sources, evidence requirement |

Start all reviewers **in parallel in one message** with the Agent tool. Each prompt contains:

- the path of its role file and of `agents/_shared.md` (read both first)
- the files to read, with absolute paths
- the path to `.thesis-editor/run/linter.json`, so mechanical findings are not reported twice
- project rules and research questions from the `context` output
- the output file `.thesis-editor/run/agents/<role>.json` (with several editors `editor-1.json`, `editor-2.json`)

Mode `chapter` has no coherence reviewer. The methodologist then covers `STR-DOPPELUNG` and `INH-ZAHLEN` within the chapter. All reviewers may read neighbouring chapters and the appendix for comparison (for example whether a parameter is defined in the method chapter), but only report findings in their assigned files. Contradictions with other chapters go into the message with file and line.

Without an Agent tool, work through the roles yourself one after another and write the same files.

Before every run with reviewers, run `python3 S/scripts/cli.py clean`. It removes old agent files, otherwise findings of older drafts mix into the report.

### 4. Build the report

```bash
python3 S/scripts/cli.py report
```

Merges linter and agent findings, writes `.thesis-editor/report.html`, adds an entry to `.thesis-editor/history/` and prints a summary with the editing index (Lektoratsindex). The index weighs errors five times, warnings twice and hints half, per 1,000 words. The history shows how the work improves. `--no-history` writes a report without history entry, for intermediate states.

### 5. Annotated PDF (modes `full`, `submit` or on request)

```bash
python3 S/scripts/cli.py annotate
```

The build takes a few minutes for a master thesis, so run it in the background. The result is `.thesis-editor/annotated.pdf`: a legend at the front, colored superscript numbers in the text, and a chapter *Lektoratsbefunde* at the end that every number links to.

| Color | Meaning |
|---|---|
| Red | source missing (the writer's own marker, already red in the original) |
| Orange | open point (the writer's own marker) |
| Magenta | check evidence |
| Blue | language and typography |
| Violet | structure, references, content |

If a finding sits inside a table, figure or formula, the mark goes directly before the object so the build does not break.

### 6. Answer

Keep the chat answer short and prioritized, in German:

1. Index and counts from the summary. On follow-up runs also what was fixed and what is new. In mode `quick` say that content, method and source fidelity were not reviewed.
2. The five to ten most important findings, errors and content warnings first, each with location as link `[file:line](path:line)`.
3. Open markers as a count, with a pointer to the report.
4. Status of lists and Git in one sentence. If there is no private repository or there are unsaved changes, phrase it as a recommendation, not as a text defect.
5. Link to the report, and to the PDF only if it was built in this run. Mark an older `annotated.pdf` explicitly as outdated.
6. An offer to fix specific findings. No change without consent.

In mode `submit` also output the checklist from `references/chapter-checklists.md` (section Abgabe) with done or open per item.

## Exceptions

A finding that should stay on purpose is excluded in the source. That keeps the decision visible and defensible.

```latex
Die Werte liegen zwischen 1 und 5. % thesis-editor: ignore TYP-ZAHLWORT
% thesis-editor: ignore SAT-LAENGE
Ein bewusst langer Satz, der in der nächsten Zeile steht ...
% thesis-editor: ignore-file FMT-QUELLTEXT-ZEILE
```

Per project, rules can be re-graded or turned off with `"off"` under `[severity]` in `thesis-editor.toml`. Words that should never be reported go under `[exceptions] words`.

## Reviewer finding format

Each agent file is a JSON array. Keys are English, values German:

```json
[
  {
    "rule": "INH-SETZUNG",
    "severity": "Warnung",
    "file": "src/Chapters/03_methodik.tex",
    "line": 300,
    "excerpt": "wörtlicher Auszug aus der Zeile",
    "message": "Was das Problem ist, in einem Satz.",
    "suggestion": "Konkreter Ersatz oder nächster Schritt."
  }
]
```

`file` is relative to the project root, as in `linter.json`. `severity` is `Fehler`, `Warnung` or `Hinweis`. `rule` comes from `rules.toml`. If no rule fits, pick the closest one and say so in the message instead of inventing new IDs.

## Further reading

- `references/rules.md`: all rules with rationale, origin and examples
- `references/conventions.md`: tense, numbers, figure sources, citation style, abbreviations
- `references/chapter-checklists.md`: required parts per chapter type and submission checklist
- `references/is-methodology.md`: quality criteria and methodology in business informatics
- `evals/`: test corpus with planted errors, measuring recall and false alarms (`python3 S/evals/run_evals.py`)

After changing `rules.toml`: `python3 S/scripts/cli.py rules` regenerates `references/rules.md`, and `python3 S/evals/run_evals.py` checks that detection did not get worse.
