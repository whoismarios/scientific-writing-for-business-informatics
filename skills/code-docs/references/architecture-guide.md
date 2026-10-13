# ARCHITECTURE.md

An `ARCHITECTURE.md` gives a new reader a map of the code: which parts exist, how data flows between them and where to start reading. The idea follows Kladov, A. (2021, February 6). *ARCHITECTURE.md* (https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html): a short, rarely changing document with a bird's eye view, a codemap and the invariants, naming files and modules but not linking to them, so it does not go stale. It describes things that change rarely, so it does not go stale with every commit.

## Sections

```markdown
# Architecture

One paragraph: what the system does and its main parts.

## Overview

A small diagram (Mermaid or ASCII) of the parts and how they talk to each other:
browser, frontend, backend, database, external services.

## Code map

### `backend/`
What lives here, the entry point (`app/main.py`), the important modules and what each is responsible for.

### `frontend/`
Same for the frontend.

## Data flow

The path of one typical request, step by step, naming the modules involved.

## Boundaries and invariants

Rules the code relies on that are not visible in one file:
"the frontend only writes to schema assessment", "all LLM calls go through agent/llm.py".

## Cross-cutting concerns

Configuration, authentication, persistence and migrations, logging, error handling, tests.
```

## Rules

- Name modules and folders, not every file. A file list goes stale, a responsibility does not.
- Every top-level source folder appears in the code map. The check reports missing ones as `ARCH-DIR`.
- Every path and name must exist. The check reports broken paths as `README-PATH`.
- No line numbers, no function counts, no version numbers that are already in the configuration.
- Keep it to what a new developer needs in the first hour, usually 60 to 150 lines.
- Invariants are worth the most. Ask the person if they are not visible in the code or the project instructions.
