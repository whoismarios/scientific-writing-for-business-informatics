# Chapter checklists

Required parts per chapter type of an empirical thesis in business informatics. Basis for `STR-KAPITELINHALT`. Chapters of a thesis may be named or cut differently. What matters is that every part appears somewhere in a fitting place.

## Einleitung (introduction)

- problem and relevance, with evidence (practice and research)
- research gap, precise and with sources
- goal of the work
- research questions, numbered and worded as they are answered later
- approach and research paradigm (for example design science, experiment, literature review)
- structure of the work with references to the chapters

## Theoretische Grundlagen (foundations)

- definition of all core terms used later
- theories and models that hypotheses or design build on
- only what is needed later

## Stand der Forschung (related work)

- traceable search (databases, search terms, period, inclusion and exclusion criteria) or a justified selection
- concept-centric structure instead of listing single papers
- synthesis: what is known, what is not
- derivation of the gap the work closes

## Forschungsmodell und Hypothesen (research model and hypotheses)

- model with variables (independent, dependent, moderators, controls)
- every hypothesis derived from theory, directional and with a source
- distinction between confirmatory and exploratory

## Methodik und Studiendesign (method and study design)

- design (between or within subjects, counterbalancing, assignment)
- sample: target size with justification (power), recruitment, inclusion and exclusion
- instruments with source, translation and adaptations
- operationalization of every variable
- procedure of the data collection
- analysis plan: tests, sidedness, correction, handling of violated assumptions
- quality criteria and how they are ensured
- set parameters named openly

## Implementierung (implementation, for design-oriented work)

- architecture in one figure
- implementation of the conditions fixed in the method chapter
- justified choice of technology and models
- cross-reference instead of repeating the method chapter
- details (tables, data model, prompts) in the appendix

## Ergebnisse (results)

- sample: registered, excluded with reason, analyzed
- measurement quality of the scales in the own sample
- manipulation check
- descriptive values
- hypothesis tests in the order of the hypotheses, with test statistic, p, effect size and confidence interval
- no interpretation

## Diskussion (discussion)

- summary of the results with respect to the hypotheses
- interpretation and comparison with the literature from the related work
- implications for research and practice
- limitations, complete and with their consequences for the conclusions

## Fazit (conclusion)

- every research question answered individually and explicitly
- contribution of the work
- outlook

## Abgabe (submission)

In mode `submit` output every item as erfüllt or offen, in German.

| Item | Check |
|---|---|
| keine Fehler | report: Fehler = 0 |
| keine offenen Marker | report: Offen = 0 |
| alle Zitierschlüssel aufgelöst | no `ZIT-SCHLUESSEL` |
| alle Verweise aufgelöst | no `FMT-VERWEIS-UNBEKANNT`, no undefined references in the LaTeX log |
| jede Abbildung mit Herkunft | no `FMT-ABB-QUELLE` |
| Forschungsfragen beantwortet | no `INH-FORSCHUNGSFRAGEN` |
| Zahlen konsistent | no `INH-ZAHLEN` |
| Literaturverzeichnis ohne Altlasten | `BIB-UNGENUTZT` reviewed |
| Verzeichnisse vollständig | no `STR-VERZEICHNIS`, table of contents present in the PDF |
| Stand gesichert | no `ABG-VERSIONIERUNG` and `ABG-GIT-STAND`: private repository, everything committed and pushed |
| Erklärung zur Eigenständigkeit | present in the PDF and signed |
| Einsatz von KI-Werkzeugen dokumentiert | in the appendix if the examination regulations require it |
| Titelblatt nach Vorgabe | title, name, student ID, supervisors, date |
