"""Builds an annotated copy of the thesis with colored finding marks and compiles it. The original stays untouched."""

import re
import shutil
import subprocess
from pathlib import Path

from ruleset import COLORS, OUT_DIR, SEVERITY_RANK
from texmodel import CODE_ENVS, FLOAT_ENVS, LIST_ENVS, TABLE_ENVS, strip_comment

UNSAFE = CODE_ENVS | FLOAT_ENVS | TABLE_ENVS | {"displaymath"}
BUILD_IGNORE_PATTERNS = ("*.aux", "*.log", "*.bbl", "*.bcf", "*.blg", "*.fls", "*.fdb_latexmk",
                                      "*.toc", "*.lof", "*.lot", "*.out", "*.run.xml", "*.glg", "*.glo", "*.gls",
                                      "*.acn", "*.acr", "*.alg", "*.ist", "*.synctex.gz", "*-blx.bib")
LEGEND = [("source", "Quelle fehlt (Marker des Schreibenden)"), ("open", "Offener Punkt (Marker des Schreibenden)"),
           ("evidence", "Beleg prüfen"), ("style", "Sprache und Typografie"), ("structure", "Struktur, Verweise, Inhalt")]


def tex_escape(s):
    rep = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "_": r"\_",
           "%": r"\%", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(c, c) for c in s)


def macros():
    lines = ["% thesis-editor: Befundmarken"]
    for name, col in COLORS.items():
        lines.append(f"\\colorlet{{lek{name}}}{{{col}}}")
    lines += [
        r"\newcommand{\editorlink}[1]{\ifdefined\hyperlink\hyperlink{lek#1}{[#1]}\else[#1]\fi}",
        r"\newcommand{\lekmark}[2]{\textcolor{lek#1}{\textsuperscript{\textbf{\editorlink{#2}}}}}",
        r"\newcommand{\lekziel}[1]{\ifdefined\hypertarget\hypertarget{lek#1}{}\fi}",
    ]
    return "\n".join(lines) + "\n"


def legend_page(n, title):
    rows = "\n".join(f"\\textcolor{{lek{k}}}{{\\rule{{1.2em}}{{0.8em}}}} & {v} \\\\" for k, v in LEGEND)
    return (
        "\\begin{titlepage}\\centering\\vspace*{3cm}\n"
        f"{{\\LARGE Lektoratsfassung\\par}}\\vspace{{0.5cm}}{{\\large {tex_escape(title)}\\par}}\\vspace{{1cm}}\n"
        f"Erzeugt mit thesis-editor. {n} Befunde sind im Text als hochgestellte, farbige Nummern markiert.\\\\\n"
        "Die Nummer verlinkt auf die Erläuterung im Kapitel \\emph{Lektoratsbefunde} am Ende.\\par\\vspace{1cm}\n"
        f"\\begin{{tabular}}{{cl}}\n{rows}\n\\end{{tabular}}\\vfill\\end{{titlepage}}\n"
    )


def findings_chapter(numbered):
    out = ["\\clearpage", "\\chapter*{Lektoratsbefunde}", "\\addcontentsline{toc}{chapter}{Lektoratsbefunde}", "\\markboth{Lektoratsbefunde}{Lektoratsbefunde}",
           "\\small"]
    for n, b in numbered:
        loc = tex_escape(f"{Path(b.file).name}:{b.line}")
        head = f"\\lekziel{{{n}}}\\noindent\\textcolor{{lek{b.color}}}{{\\textbf{{[{n}]}}}} \\texttt{{{tex_escape(b.rule)}}} {tex_escape(b.severity)}, {loc}"
        if b.source and b.source != "linter":
            head += f", {tex_escape(b.source)}"
        body = tex_escape(b.message)
        if b.suggestion:
            body += f"\\\\\\emph{{Vorschlag:}} {tex_escape(b.suggestion)}"
        out.append(f"{head}\\\\\n{body}\\par\\smallskip")
    return "\n".join(out) + "\n"


def anchor(project, line):
    """Line whose end can safely hold the mark, or the line before which it is inserted."""
    lines = project.lines
    if not line.in_any(UNSAFE):
        c = line.code.strip()
        if re.match(r"\\(begin|end)\{", c) or (line.in_any(LIST_ENVS) and not c.startswith("\\item") and c.startswith("\\")):
            return line, "before"
        if not c:
            return line, "before"
        return line, "after"
    k = line.index
    while k > 0 and lines[k - 1].file == line.file and lines[k - 1].in_any(UNSAFE):
        k -= 1
    return lines[k], "before"


def build(project, findings, compile_pdf=True):
    root = project.root
    out_dir = root / OUT_DIR
    build_dir = out_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    src_rel = project.src.relative_to(root.resolve()) if project.src.is_relative_to(root.resolve()) else Path(project.src.name)
    build_src = build_dir / src_rel
    ignore = shutil.ignore_patterns(*BUILD_IGNORE_PATTERNS, project.main.stem + ".pdf")
    shutil.copytree(project.src, build_src, ignore=ignore)
    rc = root / ".latexmkrc"
    if rc.exists():
        shutil.copy(rc, build_src / ".latexmkrc")

    by_loc = {(project.rel(l.file), l.no): l for l in project.lines}
    marks = [b for b in findings if b.color in {"evidence", "style", "structure"} and (b.file, b.line) in by_loc
             and "\\begin{document}" not in by_loc[(b.file, b.line)].code]
    marks.sort(key=lambda b: (by_loc[(b.file, b.line)].index, SEVERITY_RANK.get(b.severity, 9)))
    numbered = list(enumerate(marks, 1))

    edits = {}
    for n, b in numbered:
        ln = by_loc[(b.file, b.line)]
        target, mode = anchor(project, ln)
        edits.setdefault(target.file, {}).setdefault((target.no, mode), []).append(f"\\lekmark{{{b.color}}}{{{n}}}")

    for path in project.files:
        rel = path.resolve().relative_to(project.src.resolve())
        dst = build_src / rel
        raws = path.read_text(encoding="utf-8", errors="replace").splitlines()
        file_edits = edits.get(path, {})
        new = []
        for no, raw in enumerate(raws, 1):
            before = file_edits.get((no, "before"))
            if before:
                new.append("".join(before) + "%")
            after = file_edits.get((no, "after"))
            if after:
                code = strip_comment(raw)
                raw = code.rstrip() + "".join(after) + raw[len(code):]
            if path == project.main:
                if "\\begin{document}" in strip_comment(raw):
                    new.append("\\input{editor-macros}")
                    new.append(raw)
                    new.append("\\input{editor-legend}")
                    continue
                if "\\end{document}" in strip_comment(raw):
                    new.append("\\input{editor-findings}")
            new.append(raw)
        dst.write_text("\n".join(new) + "\n", encoding="utf-8")

    title = project.config["project"].get("title", "")
    (build_src / "editor-macros.tex").write_text(macros(), encoding="utf-8")
    (build_src / "editor-legend.tex").write_text(legend_page(len(numbered), title), encoding="utf-8")
    (build_src / "editor-findings.tex").write_text(findings_chapter(numbered), encoding="utf-8")

    if not compile_pdf:
        return build_src / project.main.name
    engine = project.config["project"].get("engine", "lualatex")
    cmd = ["latexmk", f"-{engine}" if engine in {"lualatex", "xelatex"} else "-pdf", "-interaction=nonstopmode", "-f",
           project.main.name]
    log = subprocess.run(cmd, cwd=build_src, capture_output=True, text=True, timeout=900)
    pdf = build_src / (project.main.stem + ".pdf")
    target = out_dir / "annotated.pdf"
    if pdf.exists():
        shutil.copy(pdf, target)
    logfile = build_src / (project.main.stem + ".log")
    errors = []
    if logfile.exists():
        errors = [l for l in logfile.read_text(errors="replace").splitlines() if l.startswith("! ")]
    if errors:
        print(f"LaTeX meldet {len(errors)} Fehler, erste: {errors[:3]}")
    if not pdf.exists():
        print(log.stdout[-2000:])
        raise SystemExit("Kein PDF erzeugt.")
    return target
