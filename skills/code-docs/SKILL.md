---
name: code-docs
description: >-
  Documents a code base following the Google Python and TypeScript style guides: docstrings in Python and JSDoc in TypeScript
  and JavaScript with a summary line, parameters and return value, an ARCHITECTURE.md that explains modules and data flow,
  and a README whose setup, scripts, environment variables and paths match the code. A script finds undocumented functions,
  documented parameters that no longer exist, README commands that are not defined and paths that are gone.
  Changes only comments, docstrings and documentation files, never program logic. Built for the practical part of a thesis
  in business informatics, but works for any Python or TypeScript project. Java, C#, R and Go are documented from the
  matching style guide without mechanical check.
  Use this skill when code should be documented, docstrings added or fixed, a README brought up to date, or an architecture
  overview written, also for requests like "dokumentier den Code", "README aktualisieren", "fehlen Docstrings?",
  "schreib eine ARCHITECTURE.md" or "document this module".
argument-hint: "[check | docstrings <path> | architecture | readme | all]"
disable-model-invocation: true
compatibility: Python 3.11+ without extra packages. Checks Python, TypeScript and JavaScript mechanically. Java, C#, R and Go are documented from references only. Git is optional and only used to respect .gitignore and for --since.
license: MIT
---

# code-docs

The skill documents code in three layers. Each layer has a fixed place, so nothing is said twice:

| Layer | Where | Answers |
|---|---|---|
| Docstrings and JSDoc | at each function and class | what this does, what goes in, what comes out |
| `ARCHITECTURE.md` | project root | how the parts fit together and where to start reading |
| `README.md` | project root | what the project is, how to install, configure and run it |

`scripts/check.py` finds the mechanical gaps: missing docstrings, parameters that are documented but no longer exist, README commands without a matching script, paths that are gone, environment variables nobody documents. The agent writes the text. The script cannot judge whether a summary is accurate, so read the code before describing it.

## Invocation

The skill runs when called as `/code-docs`. Whatever follows sets the scope: `$ARGUMENTS`

- empty or `check`: run the check, summarize the findings by area, offer the next step. Change nothing.
- `docstrings <path>`: document functions and classes in that file or folder.
- `architecture`: write or update `ARCHITECTURE.md`.
- `readme`: bring the README in line with the code.
- `all`: all three, in the order docstrings, architecture, README, because each later layer builds on the one before.

## Languages

The skill picks the convention by file extension. Read only the reference for the languages in scope.

| Extension | Reference | Convention | Mechanical check |
|---|---|---|---|
| `.py` | python.md | Google Python Style Guide | yes |
| `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs` | typescript.md | Google TypeScript and JavaScript Style Guide | yes |
| `.java` | java.md | Google Java Style Guide, Javadoc | no |
| `.cs` | csharp.md | Microsoft XML documentation comments | no, the compiler checks `<param>` |
| `.R`, `.r` | r.md | roxygen2, tidyverse style guide | no |
| `.go` | go.md | Go Doc Comments | no |

For the languages without mechanical check, the check output lists the files under `not checked mechanically`. Read the code and the reference, document by hand, and say in the answer that these files were not checked by the script. For any other language, follow the conventions already in the project and tell the person that the skill has no reference for it.

## Workflow

1. **Find the house rules first.** Read `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the linter config (`ruff`/`pydocstyle` convention in `pyproject.toml`, `eslint-plugin-jsdoc` or `tsdoc` settings) and a few documented functions in the code. **House rules win over this skill.** If a project says "a one-line docstring only where name and signature are not enough", follow that and set `style = "summary"` or `min_lines` in `code-docs.toml` after asking. Mention the conflict once instead of documenting against the project's rule.
2. **Run the check** from the project root:
   ```bash
   python3 <skill-dir>/scripts/check.py . --json
   ```
   `--only code,readme,arch` limits the areas, `--since <rev>` limits code findings to files changed since that Git revision.
3. **Agree on the scope** when the check reports more than about 40 code findings. Propose an order (public API and entry points first, then services, then helpers) and do one module per pass. A large diff of comments is hard to review.
4. **Write**, following the reference for the layer. Each reference names the section of the style guide behind every rule:
   - Python: [references/python.md](references/python.md)
   - Java: [references/java.md](references/java.md)
   - C#: [references/csharp.md](references/csharp.md)
   - R: [references/r.md](references/r.md)
   - Go: [references/go.md](references/go.md)
   - TypeScript and JavaScript: [references/typescript.md](references/typescript.md)
   - Architecture: [references/architecture-guide.md](references/architecture-guide.md)
   - README: [references/readme-guide.md](references/readme-guide.md)
5. **Verify.** Run the check again and confirm the findings you worked on are gone. For Python, make sure each touched file still parses (`python3 -m py_compile <file>`). Report what is left.

## Principles

- **Only documentation changes.** Edit docstrings, comments, `ARCHITECTURE.md` and the README. Never rename, reformat or refactor code along the way, even when it looks wrong. If you notice a bug, mention it in the answer.
- **Describe what the code does, not what it should do.** Read the function body and its callers before writing. A docstring that is wrong is worse than none, because readers trust it.
- **Every fact must come from the project.** Commands from `package.json`, `pyproject.toml`, `Makefile` or `docker-compose.yml`. Versions from `engines`, `requires-python`, `.nvmrc` or `.python-version`. Variables from `.env.example`. Ports from the compose file or the dev script. If a fact is not in the project, leave it out or ask, never guess.
- **No claims the code cannot back.** No "fast", "secure", "production-ready" or coverage figures unless the project measures them.
- **Do not repeat types.** With type hints or TypeScript the signature already states the types. The docstring explains meaning, units, allowed values and edge cases.
- **Keep the language of the project.** Docstrings follow the language of the existing ones, English if there are none. The README and `ARCHITECTURE.md` follow the language of the existing README. Answer the person in their language.
- **Do not run setup.** Do not install packages, start servers or run migrations to find out how the project works. Read the configuration instead.
- **Respect house rules on links.** Some projects forbid links from the README to other Markdown files. Check before linking `ARCHITECTURE.md` from the README.

## Rules of the check

Every finding carries the source of its rule in the field `source`. `check.py --rules` lists all rules with their source.

| Rule | Severity | Finds | Basis |
|---|---|---|---|
| `DOC-MISSING` | warning | public function or class without docstring or JSDoc | [G-PY] 3.8.3, [G-TS] top-level exports |
| `DOC-ARGS-MISSING` | warning | docstring with a body but no Args section. In style `full` also one-line docstrings and JSDoc without `@param` | [G-PY] 3.8.3 |
| `DOC-PARAM-MISSING` | warning | a parameter missing from Args or from the `@param` tags | [G-PY] 3.8.3 Args |
| `DOC-PARAM-STALE` | error | Args or `@param` names a parameter the signature no longer has | [G-PY] 3.8.3, [G-TS] method comments |
| `DOC-RETURNS-MISSING` | hint | value returned but no Returns, Yields or `@returns`, where parameters are documented | [G-PY] 3.8.3 Returns |
| `README-MISSING` | warning | no README in the project root | [GH], [SR] |
| `README-SCRIPT` | error | README calls `npm run`, `pnpm`, `yarn` or `make` targets that do not exist | [SR] Install, Usage |
| `README-PATH` | error | README or ARCHITECTURE points to a path that does not exist | convention of this skill |
| `README-ENV` | warning | variable in `.env.example` that no README or ARCHITECTURE mentions | [SR] Usage, convention of this skill |
| `ARCH-MISSING` | hint | no `ARCHITECTURE.md` | [K21] |
| `ARCH-DIR` | hint | top-level source folder that `ARCHITECTURE.md` does not mention | [K21] codemap |

Public means: not starting with `_` in Python, exported in TypeScript and JavaScript. Dunder methods, `@overload` and `@override` are skipped, properties only need a summary. Tests, migrations, type declarations and everything in `.gitignore` are excluded.

## Standards and sources

The skill documents according to published style guides, so every decision can be traced to a source. Cite them in the thesis when describing how the code is documented, for example: "Die Dokumentation des Quellcodes folgt dem Google Python Style Guide (Abschnitt 3.8) und dem Google TypeScript Style Guide."

| Key | Source | Used for |
|---|---|---|
| [G-PY] | Google. *Google Python Style Guide*, section 3.8 "Comments and Docstrings". https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings | Python docstrings |
| [PEP257] | Goodger, D., & van Rossum, G. (2001). *PEP 257 – Docstring Conventions*. https://peps.python.org/pep-0257/ | basic docstring form that [G-PY] builds on |
| [G-TS] | Google. *Google TypeScript Style Guide*, section "Comments and documentation". https://google.github.io/styleguide/tsguide.html#comments-documentation | TypeScript JSDoc |
| [G-JS] | Google. *Google JavaScript Style Guide*, section 7 "JSDoc". https://google.github.io/styleguide/jsguide.html#jsdoc | JavaScript JSDoc with types |
| [JSDOC] | *JSDoc*. https://jsdoc.app/ and Microsoft. *TSDoc*. https://tsdoc.org/ | tag syntax |
| [K21] | Kladov, A. (2021, February 6). *ARCHITECTURE.md*. https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html | `ARCHITECTURE.md` |
| [SR] | Littauer, R. et al. *Standard Readme*. https://github.com/RichardLitt/standard-readme | README sections and order |
| [G-JAVA] | Google. *Google Java Style Guide*, section 7 "Javadoc". https://google.github.io/styleguide/javaguide.html#s7-javadoc | Java |
| [ORA] | Oracle. *How to Write Doc Comments for the Javadoc Tool*. https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html | wording of Javadoc |
| [MS] | Microsoft. *XML documentation comments* and *Recommended XML tags for C# documentation comments*. https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/ | C# |
| [ROXY] | *roxygen2*, article "Documenting functions". https://roxygen2.r-lib.org/articles/rd.html | R |
| [TIDY] | The tidyverse team. *Tidyverse style guide*, chapter 7 "Documentation". https://style.tidyverse.org/documentation.html | R |
| [GO] | The Go Authors. *Go Doc Comments*. https://go.dev/doc/comment | Go |
| [GH] | GitHub. *About READMEs*. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes | purpose of a README |

The style guides are living documents without version numbers. When citing them in a thesis, give the access date.

**Where the skill differs from the guides, and why:**

- **Private functions** are not reported by default. [G-PY] requires a docstring also for private functions of non-trivial size or with non-obvious logic, which a script cannot judge. The agent documents such helpers when it works on a module. `private = true` reports all of them.
- **Style `full`** asks for Args and Returns on every public function, even where the guides allow a one-line docstring. It is a house rule a project can choose, stricter than the guides.
- **Complete `@param` lists.** [G-TS] allows leaving out obvious parameter descriptions. Once a JSDoc comment documents some parameters, the check expects all of them, following the Args rule of [G-PY], so a comment is either a one-liner or complete.
- **README facts.** That every command, path and variable in the README exists in the project is a convention of this skill. The README sources describe content and order, not checks.

## Configuration

Optional `code-docs.toml` in the project root:

```toml
style = "google"   # "google": as in the guides, one-liners allowed. "full": Args and Returns always. "summary": a docstring is enough.
private = false    # also require docstrings for _private functions
min_lines = 0      # skip functions whose body is shorter than this
exclude = ["*/generated/*"]
architecture = ""  # path to the architecture file if not ARCHITECTURE.md

[update]
check = true       # look for a newer version on GitHub at most once a day
auto = false       # install it at the end of a run and only report it
```

## Updates

The last line of the check output starts with `update:` and names the installed version. The script asks GitHub at most once a day, stays silent when offline, and can be switched off. If a newer version is available, the line names it and lists the new changelog entries below it.

- **Automatic update off (default):** finish the task, then tell the person once at the end of the answer: the new version, the one to three changes that matter to them, and the question whether to update. On yes, run `python3 <skill-dir>/scripts/update.py apply` and report its result. After a no, do not ask again in the same conversation.
- **Automatic update on** (`auto = true` under `[update]` in `code-docs.toml`, or `SKILL_AUTO_UPDATE=1`): finish the task, then run `update.py apply` without asking and report in one line that the new version was loaded and applies from the next call, with the main changes.
- **Never update in the middle of a run.** The scripts would change under the running task.
- **Installed from a Git checkout:** `apply` only prints the hint to run `git pull`. Pass it on, never pull yourself.
- If the line says the check is disabled or GitHub is not reachable, say nothing about updates.

## Answer

After a pass, tell the person in a few lines: what was documented (files and count), which README facts changed and why, what the check still reports, and anything in the code that looked wrong. Do not paste the docstrings into the chat. The diff shows them.
