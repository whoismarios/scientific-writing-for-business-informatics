# Working on this repository

The repository holds two independent skills under `skills/`: `thesis-editor` and `code-docs`. Each has its own `VERSION` and `CHANGELOG.md`. Everything technical is English, rule texts, findings, changelogs and the README are German.

## Versions

Each skill follows Semantic Versioning on its own. Decide the step by what a user notices after updating:

| Step | When | Examples |
|---|---|---|
| Patch `x.y.Z` | nothing to adapt, findings only change where a bug is fixed | false alarm fixed, wording, typo, documentation |
| Minor `x.Y.0` | new behavior, old configuration and data keep working | new rule, new check, new option, new language, new report feature |
| Major `X.0.0` | the user has to adapt something | configuration key removed or renamed without a legacy alias, history or report data no longer readable, command or rule removed |

Prefer a legacy alias over a major step: renamed config keys stay readable through `LEGACY_KEYS` in `skills/thesis-editor/scripts/ruleset.py`. While a skill is below 1.0.0, breaking changes may go into a minor step but are still marked in the changelog.

## Changelog

- Every change gets a line in `CHANGELOG.md` of the skill it touches, under `## Unreleased` at the top. Create that heading if it is missing.
- Write from the user's point of view, in German, one line per change. Say what the user notices, not which function changed.
- Mark changes that move findings or the Lektoratsindex, for example "neue Regel, kann den Index erhöhen".
- A major step gets lines starting with `Anpassen:` that say exactly what the user has to change.
- Keep the format `## X.Y.Z (YYYY-MM-DD)` and `- ` bullets. `scripts/update.py` parses exactly this to show users what is new.

## Release

Only when the maintainer asks for a release:

1. Rename `## Unreleased` to `## X.Y.Z (YYYY-MM-DD)` and write the same version into `VERSION`.
2. Update the version and rule count in the README badges and in the table "Die Skills", and the banner pills in `assets/banner.svg` if counts changed.
3. Tell the maintainer the tag to create: `<skill>-vX.Y.Z`, for example `thesis-editor-v1.1.0`.

Agents do not commit, tag or push. The maintainer does.

## Before a change is done

```bash
python3 skills/thesis-editor/evals/run_evals.py
```

```bash
python3 skills/code-docs/evals/run_evals.py
```

`scripts/update.py` is the same file in both skills. Change both or neither and compare them with `cmp`. README, SKILL.md, references and changelog must match the code: rule counts, options, file names, versions.
