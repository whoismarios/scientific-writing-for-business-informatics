# README

The README answers: what is this, how do I get it running, how do I configure and use it. Everything in it must match the project as it is now.

Sources: GitHub, *About READMEs* (https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), on what a README should tell, and Littauer, R. et al., *Standard Readme* (https://github.com/RichardLitt/standard-readme), on the order of sections (title, short description, install, usage, license). The rules that every command, path and variable must exist in the project are conventions of code-docs, checked by the script.

## Sections

Keep the existing structure and language. Add missing sections in this order:

1. **Title and one or two sentences** on what the project does and for whom.
2. **Requirements** with versions taken from the project: `engines` in `package.json`, `requires-python` in `pyproject.toml`, `.nvmrc`, `.python-version`, `docker-compose.yml` images.
3. **Setup:** the exact commands, in order, copied from the scripts that exist. Each command in its own code block.
4. **Configuration:** a table of environment variables from `.env.example` with meaning and whether it is required. Never real values or secrets.
5. **Running:** development and production commands, ports, URLs.
6. **Tests and checks:** the commands that exist (`npm test`, `uv run pytest`, lint).
7. **Project structure:** a short tree of the top level, or a link to `ARCHITECTURE.md` if the house rules allow links.
8. **Deployment**, only if the project contains deployment configuration.
9. **License**, if there is a license file.

## Rules

- Every `npm run`, `pnpm`, `yarn` and `make` command must exist. The check reports others as `README-SCRIPT`.
- Every variable in `.env.example` is documented. The check reports gaps as `README-ENV`.
- Every path must exist. The check reports broken ones as `README-PATH`.
- Copy facts from the configuration, never from memory. When a script, port or variable changes, the README changes in the same pass.
- No badges or claims that the project does not measure: test coverage, performance, "production-ready".
- In a monorepo each part may have its own README. The root README then explains how the parts fit together and how to start everything.
