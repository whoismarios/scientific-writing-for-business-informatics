"""Reads the LaTeX log and the biber log of the last build and turns problems into findings with file and line."""

import re
from datetime import datetime
from pathlib import Path

from ruleset import make

FILE_OPEN = re.compile(r'\(\"?((?:\.{0,2}/|[A-Za-z]:|[\w-]+/)?[^\s()"]+\.(?:tex|sty|cls|cfg|def|clo|fd|aux|toc|lof|lot|bbl|out|gls|acr|ist|ldf|lua|bbx|cbx|lbx|dbx))')
REF = re.compile(r"LaTeX Warning: Reference [`'](.+?)' on page \S+ undefined on input line (\d+)")
CITE = re.compile(r"(?:LaTeX|Package natbib) Warning: Citation [`'](.+?)' on page \S+ undefined on input line (\d+)")
MULTI = re.compile(r"LaTeX Warning: Label [`'](.+?)' multiply defined")
OVERFULL = re.compile(r"Overfull \\hbox \(([\d.]+)pt too wide\) (?:in paragraph at lines (\d+)--\d+|in alignment at lines (\d+)--\d+|detected at line (\d+))")
RERUN = re.compile(r"Rerun to get (?:cross-references|outlines|citations)|Label\(s\) may have changed")
ERROR = re.compile(r"^! (.+)")
ERROR_LINE = re.compile(r"^l\.(\d+)")
BIBER = re.compile(r"\b(WARN|ERROR) - (.+)")
BIBER_KEY = re.compile(r"entry '([^']+)'|key '([^']+)'|Entry '([^']+)'")
PAGE = re.compile(r"\[\d+")
MAX_PRINT_LINE = 79
OVERFULL_MIN_PT = 2.0


def _unwrap(text):
    """Joins lines that TeX wrapped at max_print_line."""
    out, buf = [], ""
    for line in text.splitlines():
        buf += line
        if len(line) != MAX_PRINT_LINE:
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


def _events(lines, src):
    """Yields (log line, current input file) while tracking the file stack from the parentheses in the log."""
    stack = []
    for line in lines:
        current = next((f for f in reversed(stack) if f), None)
        yield line, current
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "(":
                m = FILE_OPEN.match(line, i)
                if m:
                    name = m.group(1)
                    path = (src / name).resolve() if not Path(name).is_absolute() else Path(name)
                    stack.append(path)
                    i = m.end()
                    continue
                stack.append(None)
            elif ch == ")" and stack:
                stack.pop()
            i += 1


def check(project, newest_source):
    """Findings from the last build log, plus a status for the summary."""
    cfg = project.config
    log = project.root / cfg["project"]["log"] if cfg["project"].get("log") else project.main.with_suffix(".log")
    status = {"log": None}
    if not log.exists():
        return [], status
    stamp = log.stat().st_mtime
    status = {"log": project.rel(log), "time": datetime.fromtimestamp(stamp).isoformat(timespec="minutes"),
              "stale": newest_source > stamp}
    body = {(ln.file.resolve(), ln.no) for ln in project.lines if "\\begin{document}" not in ln.code}
    findings, seen = [], set()

    def add(rule, path, line, message, suggestion=""):
        if path is None or not line or (path.resolve(), int(line)) not in body:
            return
        key = (rule, path.resolve(), line, message)
        if key in seen:
            return
        seen.add(key)
        b = make(cfg, rule, project.rel(path), int(line), message, "", suggestion, "log")
        if b:
            findings.append(b)

    lines = _unwrap(log.read_text(encoding="utf-8", errors="replace"))
    pending_error = None
    rerun = False
    recent = []
    for line, current in _events(lines, project.src):
        recent = (recent + [line])[-5:]
        if m := REF.search(line):
            add("LOG-VERWEIS", current, m.group(2), f"Verweis {m.group(1)} ist im PDF nicht aufgelöst und erscheint als ??",
                "Label prüfen oder LaTeX erneut übersetzen")
        elif m := CITE.search(line):
            add("LOG-ZITAT", current, m.group(2), f"Quelle {m.group(1)} ist im PDF nicht aufgelöst",
                "Schlüssel in der Bibliografie prüfen und biber erneut laufen lassen")
        elif m := MULTI.search(line):
            label = m.group(1)
            for ln in project.lines:
                if f"\\label{{{label}}}" in ln.code:
                    add("LOG-VERWEIS", ln.file, ln.no, f"Label {label} ist mehrfach vergeben", "eindeutiges Label vergeben")
        elif m := OVERFULL.search(line):
            pt = float(m.group(1))
            at = m.group(2) or m.group(3) or m.group(4)
            in_output = m.group(4) and any(PAGE.search(r) for r in recent[:-1])
            if pt >= OVERFULL_MIN_PT and not in_output:
                add("LOG-UEBERVOLL", current, at, f"Zeile ragt {pt:.1f} pt über den Satzspiegel hinaus",
                    "Umformulieren, Trennhilfe \\- setzen, lange URL oder Code umbrechen, Tabelle verkleinern")
        elif RERUN.search(line):
            rerun = True
        if m := ERROR.match(line):
            pending_error = (m.group(1).strip(), current)
        elif pending_error and (m := ERROR_LINE.match(line)):
            add("LOG-FEHLER", pending_error[1], m.group(1), f"LaTeX-Fehler: {pending_error[0]}", "Fehler beheben, das PDF ist sonst unvollständig")
            pending_error = None
    status["rerun"] = rerun
    status.update(_biber(project, findings, add))
    return findings, status


def _biber(project, findings, add):
    blg = project.main.with_suffix(".blg")
    if not blg.exists():
        return {}
    from bib import parse_bib
    keys = {}
    for b in project.config["project"].get("bib", []):
        path = project.root / b
        if path.exists():
            for e in parse_bib(path.read_text(encoding="utf-8", errors="replace")):
                keys[e["key"]] = (path, e["line"])
    warnings = 0
    for line in blg.read_text(encoding="utf-8", errors="replace").splitlines():
        m = BIBER.search(line)
        if not m:
            continue
        warnings += 1
        text = re.sub(r"\s*-\s*run biber with.*$", "", m.group(2)).strip()
        km = BIBER_KEY.search(text)
        key = next((g for g in km.groups() if g), None) if km else None
        if key in keys:
            path, line_no = keys[key]
            b = make(project.config, "LOG-BIBER", project.rel(path), line_no, f"biber: {text}", "",
                     "Eintrag korrigieren", "log")
            if b:
                findings.append(b)
    return {"biber_warnings": warnings}
