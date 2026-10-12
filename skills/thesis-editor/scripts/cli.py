#!/usr/bin/env python3
"""Command line of the thesis-editor skill: init, check, context, report, annotate, clean, rules."""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bib  # noqa: E402
import environment  # noqa: E402
from ruleset import OUT_DIR, RULESET, RULES, SEVERITY_RANK, SKILL_DIR, config_path, from_dict, load_config  # noqa: E402
from linter import Linter  # noqa: E402
from texmodel import Project  # noqa: E402


def run_dir(root):
    d = Path(root) / OUT_DIR / "run"
    (d / "agents").mkdir(parents=True, exist_ok=True)
    return d


def detect(root):
    """Detects main file, bibliography, glossary and colored marker macros of a LaTeX project."""
    root = Path(root).resolve()
    mains = []
    for p in root.rglob("*.tex"):
        if {OUT_DIR, ".thesis-lektor", ".lektorat", ".claude", ".agents", "node_modules"} & set(p.parts):
            continue
        txt = p.read_text(errors="replace")
        if "\\documentclass" in txt and "\\begin{document}" in txt:
            mains.append(p)
    if not mains:
        raise SystemExit(f"Keine LaTeX-Hauptdatei mit \\documentclass und \\begin{{document}} unter {root} gefunden. "
                         "Der Skill prüft nur LaTeX-Projekte.")
    main = min(mains, key=lambda p: (len(p.relative_to(root).parts), p.name.lower() not in {"main.tex", "thesis.tex"}, str(p)))
    tex_all = {p: p.read_text(errors="replace") for p in main.parent.rglob("*.tex")}
    bibs, gloss, source_markers, open_markers = [], [], [], []
    for p, t in tex_all.items():
        for m in re.finditer(r"\\(?:addbibresource|bibliography)\{([^}]+)\}", t):
            for b in m.group(1).split(","):
                b = b.strip()
                b = b if b.endswith(".bib") else b + ".bib"
                cand = (main.parent / b)
                if cand.exists():
                    bibs.append(str(cand.relative_to(root)))
        if "\\newacronym" in t:
            gloss.append(str(p.relative_to(root)))
        for m in re.finditer(r"\\(?:re)?newcommand\{?\\(\w+)\}?(?:\[\d\])?\{\\textcolor", t):
            name = m.group(1)
            (source_markers if re.search(r"quelle|cite|fehl|missing", name, re.I) else open_markers).append(name)
    preamble = tex_all.get(main, "").split("\\begin{document}")[0] + "".join(
        t for p, t in tex_all.items() if p != main and "\\usepackage" in t)
    engine = "lualatex" if re.search(r"fontspec|unicode-math|luacode|luatex", preamble) else "pdflatex"
    return {
        "project": {"title": root.name, "main": str(main.relative_to(root)), "bib": sorted(set(bibs)),
                    "glossary": sorted(set(gloss)), "engine": engine},
        "markers": {"missing_source": source_markers or ["quellefehlt"], "open": open_markers or ["offen"]},
    }


def configuration(root):
    """thesis-editor.toml if present, otherwise the detected values."""
    if config_path(root):
        return load_config(root)
    return load_config(root, detect(root))


def cmd_init(a):
    root = Path(a.root).resolve()
    target = config_path(root) or root / "thesis-editor.toml"
    if target.exists() and not a.force:
        print(f"{target} existiert bereits. Mit --force überschreiben.")
        return
    e = detect(root)
    pr, mk = e["project"], e["markers"]
    lines = [
        "# thesis-editor configuration. Values and messages are German, keys are English.",
        "# All options: thesis-editor.example.toml in the skill folder.",
        "",
        "# Content rules only the reviewer agents can check. Must stay above the first [table].",
        "project_rules = []",
        "",
        "[project]",
        f"title = {json.dumps(pr['title'], ensure_ascii=False)}",
        f"main = {json.dumps(pr['main'])}",
        f"bib = {json.dumps(pr['bib'])}",
        f"glossary = {json.dumps(pr['glossary'])}",
        f'engine = "{pr["engine"]}"',
        "",
        "[markers]",
        f"missing_source = {json.dumps(mk['missing_source'])}",
        f"open = {json.dumps(mk['open'])}",
        "",
        "[sentences]",
        "max_words = 35",
        "max_clauses = 2",
        "",
        "[structure]",
        'skip_sections = ["Anhang"]',
        "",
        "[terms]",
        "compounds = []",
        "variants = [",
        '  ["Nutzer|Nutzers|Nutzern", "User|Users", "Anwender|Anwendern"],',
        "]",
        "",
        "[terms.forbidden]",
        "",
        "[severity]",
        "",
        "[exceptions]",
        "words = []",
        "",
        "[research_questions]",
        '# FF1 = "Wortlaut der ersten Forschungsfrage"',
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Angelegt: {target}")


def run_checks(root, only=None):
    cfg = configuration(root)
    project = Project(root, cfg)
    linter = Linter(project)
    findings = linter.run()
    bib_findings, bib_stats = bib.check(project)
    findings += bib_findings
    list_findings, list_status = environment.check_lists(project)
    git_findings, git_status = environment.git(project)
    if not only:
        findings += list_findings + git_findings
    words = linter.words_by_file
    formula_counts = {}
    for ln in project.lines:
        if ln.code.lstrip().startswith(("\\begin{equation", "\\begin{align", "\\[")):
            f = project.rel(ln.file)
            formula_counts[f] = formula_counts.get(f, 0) + 1
    if only:
        selected = project.select(only)
        findings = [b for b in findings if b.file in selected or (b.source == "bib" and b.rule == "ZIT-SCHLUESSEL" and b.file in selected)]
        words = {f: n for f, n in words.items() if f in selected}
    findings.sort(key=lambda b: (b.file, b.line, SEVERITY_RANK.get(b.severity, 9)))
    meta = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "ruleset": RULESET["meta"]["version"],
        "files": [project.rel(f) for f in project.files],
        "words": sum(words.values()),
        "words_per_file": words,
        "formulas_per_file": formula_counts,
        "selection": only or "",
        "sentences": len(project.sentences),
        "bib": bib_stats,
        "lists": list_status,
        "git": git_status,
        "outline": [{"level": h.level, "title": h.title, "file": project.rel(h.line.file), "line": h.line.no,
                        "sentences": h.sentences} for h in project.headings],
    }
    return cfg, project, findings, meta


def print_summary(findings, meta):
    c = Counter(b.severity for b in findings)
    print(f"Wörter: {meta['words']}  Sätze: {meta['sentences']}  Dateien: {len(meta['files'])}")
    print("Befunde: " + "  ".join(f"{k} {c.get(k, 0)}" for k in ("Fehler", "Offen", "Warnung", "Hinweis")))
    by_rule = Counter(b.rule for b in findings)
    print("\nRegel                        Anzahl  Schwere")
    for rule, n in sorted(by_rule.items(), key=lambda kv: (SEVERITY_RANK.get(RULES.get(kv[0], {}).get("severity"), 9), -kv[1])):
        print(f"{rule:<28} {n:>6}  {RULES.get(rule, {}).get('severity', '')}")
    print("\n" + environment_lines(meta))


def environment_lines(meta):
    out = []
    v = meta.get("lists", {})
    if v:
        out.append("Verzeichnisse: " + ", ".join(
            f"{k} {'ja' if s['present'] else ('fehlt' if s['needed'] else 'nicht nötig')}" for k, s in v.items())
            + f" (Grundlage: {next(iter(v.values()))['basis']})")
    g = meta.get("git", {})
    if g.get("checked") is False:
        out.append("Git: Prüfung abgeschaltet")
    elif g.get("repo") is None:
        out.append("Git: nicht installiert")
    elif not g.get("repo"):
        out.append("Git: kein Repository")
    else:
        segments = [f"Remote {g['remote'][0]}" if g.get("remote") else "kein Remote"]
        if g.get("visibility"):
            segments.append({"PRIVATE": "privat", "PUBLIC": "öffentlich"}.get(g["visibility"], g["visibility"].lower()))
        segments.append(f"nicht committet: {g.get('uncommitted', 0)} Dateien")
        if g.get("unpushed") is not None:
            segments.append(f"nicht gepusht: {g['unpushed']} Commits")
        segments.append(f"letzter Commit {g.get('last_commit') or '-'}")
        out.append("Git: " + ", ".join(segments))
    return "\n".join(out)


def cmd_check(a):
    cfg, project, findings, meta = run_checks(a.root, a.only)
    d = run_dir(a.root)
    (d / "linter.json").write_text(json.dumps({"meta": meta, "findings": [b.as_dict() for b in findings]}, ensure_ascii=False, indent=1), encoding="utf-8")
    print_summary(findings, meta)
    print(f"\nGespeichert: {d / 'linter.json'}")


def cmd_clean(a):
    d = run_dir(a.root) / "agents"
    n = 0
    for f in d.glob("*.json"):
        f.unlink()
        n += 1
    print(f"{n} alte Agentendateien entfernt.")


def cmd_context(a):
    cfg, project, findings, meta = run_checks(a.root)
    print(f"# Gliederung ({meta['words']} Wörter)\n")
    for h in meta["outline"]:
        if h["level"] <= 2:
            print(f"{'  ' * max(h['level'], 0)}- {h['title']}  [{h['file']}:{h['line']}, {h['sentences']} Sätze]")
    print("\n# Dateien")
    for f in meta["files"]:
        n = meta["formulas_per_file"].get(f, 0)
        print(f"- {f}  ({meta['words_per_file'].get(f, 0)} Wörter" + (f", {n} abgesetzte Formeln)" if n else ")"))
    marks = [b for b in findings if b.rule.startswith("MARK-")]
    print(f"\n# Marker ({len(marks)})")
    for b in marks:
        print(f"- {b.rule} {b.file}:{b.line}  {b.message}")
    if cfg.get("research_questions"):
        print("\n# Forschungsfragen")
        for k, v in cfg["research_questions"].items():
            print(f"- {k}: {v}")
    if cfg.get("project_rules"):
        print("\n# Projektregeln")
        for r in cfg["project_rules"]:
            print(f"- {r}")
    print("\n# Begriffe")
    for k, v in cfg["terms"].get("forbidden", {}).items():
        print(f"- {k} -> {v}")


def load_all(root):
    cfg = configuration(root)
    d = run_dir(root)
    data = json.loads((d / "linter.json").read_text(encoding="utf-8"))
    findings = [from_dict({**b, "source": b.get("source", b.get("quelle", "linter"))}, cfg) for b in data.get("findings", data.get("befunde", []))]
    agents = {}
    for f in sorted((d / "agents").glob("*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Übersprungen, kein gültiges JSON: {f.name} ({e})")
            continue
        items = raw.get("findings", raw.get("befunde", raw)) if isinstance(raw, dict) else raw
        role = f.stem
        n = 0
        for it in items:
            it.setdefault("source", it.get("quelle", f"agent:{role}"))
            b = from_dict(it, cfg)
            if b:
                findings.append(b)
                n += 1
        agents[role] = n
    findings = [b for b in findings if b]
    return cfg, data["meta"], findings, agents


def cmd_report(a):
    import report
    cfg, meta, findings, agents = load_all(a.root)
    root = Path(a.root)
    hist_dir = root / OUT_DIR / "history"
    hist_dir.mkdir(parents=True, exist_ok=True)
    previous = sorted(hist_dir.glob("*.json"))
    prev = report.load_history(previous[-1].read_text(encoding="utf-8")) if previous else None
    entry = report.history_entry(meta, findings, agents)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if not a.no_history:
        (hist_dir / f"{stamp}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    history = [report.load_history(p.read_text(encoding="utf-8")) for p in sorted(hist_dir.glob("*.json"))]
    if a.no_history:
        history.append(entry)
    out = root / OUT_DIR / "report.html"
    out.write_text(report.render_html(cfg, meta, findings, agents, history, prev), encoding="utf-8")
    print(report.render_summary(meta, findings, agents, entry, prev))
    print("\n" + environment_lines(meta))
    print(f"\nBericht: {out}")


def cmd_annotate(a):
    import annotate
    cfg, meta, findings, agents = load_all(a.root)
    project = Project(a.root, cfg)
    pdf = annotate.build(project, findings, compile_pdf=not a.no_build)
    print(f"Annotierte Fassung: {pdf}")


def cmd_rules(a):
    out = ["# Regelwerk thesis-editor", "",
           f"Version {RULESET['meta']['version']}. Erzeugt aus `rules.toml` mit `cli.py rules`, nicht von Hand bearbeiten.", "",
           "Schweregrade: **Fehler** muss vor der Abgabe behoben sein. **Warnung** sollte behoben oder begründet werden. "
           "**Hinweis** ist eine Empfehlung. **Offen** sind Marker des Schreibenden.", "",
           "Prüfung: `linter` und `bib` laufen deterministisch über Skripte. `environment` prüft die Versionierung mit Git und zählt nicht zum Lektoratsindex. `agent` prüfen die Gutachter-Agenten.", "",
           "Herkunft: SR = Schreibregeln aus der Betreuung einer Masterarbeit, FB = Festlegung im Schreibprozess, APA7 = APA Publication Manual, "
           "WI = Konvention der Wirtschaftsinformatik, DUDEN = Duden-Empfehlung, TYPO = Typografie-Konvention.", ""]
    groups = {}
    for r in RULESET["rule"]:
        groups.setdefault(r["id"].split("-")[0], []).append(r)
    names = {"TYP": "Typografie", "SPR": "Sprache und Ton", "SAT": "Satzbau", "TERM": "Begriffe",
             "ZIT": "Zitation", "INH": "Inhalt", "BIB": "Bibliografie", "FMT": "Formatierung und Verweise", "ABG": "Abgabe und Datensicherung",
             "STR": "Struktur", "FORM": "Formeln", "ABB": "Abbildungen", "MARK": "Arbeitsmarker"}
    out.append("## Übersicht\n")
    out.append("| ID | Regel | Schwere | Prüfung | Farbe |")
    out.append("|---|---|---|---|---|")
    for r in RULESET["rule"]:
        out.append(f"| `{r['id']}` | {r['title']} | {r['severity']} | {r['check']} | {r['color']} |")
    for g, rules in groups.items():
        out.append(f"\n## {names.get(g, g)}\n")
        for r in rules:
            out.append(f"### `{r['id']}` {r['title']}\n")
            out.append(f"{r['severity']}, Prüfung: {r['check']}, Herkunft: {r['origin']}\n")
            out.append(f"{r['why']}\n")
            out.append(f"- Falsch: {r['wrong']}")
            out.append(f"- Richtig: {r['right']}\n")
    wl = RULESET["wordlists"]
    out.append("\n## Wortlisten\n")
    for k in ("judgment", "obvious", "phrases", "hedging", "fillers", "redundant", "evidence_cue"):
        out.append(f"**{k}:** " + ", ".join(wl[k]) + "\n")
    (SKILL_DIR / "references" / "rules.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Geschrieben: {SKILL_DIR / 'references' / 'rules.md'}")


def main():
    ap = argparse.ArgumentParser(prog="thesis-editor", description="Lektorat für LaTeX-Arbeiten. Befunde und Berichte auf Deutsch.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    help_texts = {"init": "write thesis-editor.toml with detected settings", "check": "run the deterministic checks",
             "context": "outline, word counts, markers and project rules for reviewer agents",
             "report": "merge findings into the HTML report and history", "annotate": "build the annotated PDF",
             "clean": "remove findings of earlier reviewer runs", "rules": "regenerate references/rules.md"}
    for name, h in help_texts.items():
        p = sub.add_parser(name, help=h)
        p.add_argument("--root", default=".", help="project root (default: current directory)")
        if name == "init":
            p.add_argument("-f", "--force", action="store_true", help="overwrite an existing config")
        if name == "check":
            p.add_argument("-o", "--only", help="regex on file paths, included files count too, e.g. 03_methodik")
        if name == "report":
            p.add_argument("--no-history", action="store_true", help="do not add a history entry")
        if name == "annotate":
            p.add_argument("--no-build", action="store_true", help="prepare the annotated copy without compiling")
    a = ap.parse_args()
    {"init": cmd_init, "check": cmd_check, "context": cmd_context, "report": cmd_report,
     "annotate": cmd_annotate, "rules": cmd_rules, "clean": cmd_clean}[a.cmd](a)


if __name__ == "__main__":
    main()
