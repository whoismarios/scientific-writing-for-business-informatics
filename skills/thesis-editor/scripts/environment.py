"""Checks the environment of the thesis: lists in the document and versioning with Git."""

import re
import subprocess
from pathlib import Path

from ruleset import OUT_DIR, make
from texmodel import strip_comment

LISTS = {
    "Abbildungsverzeichnis": (".lof", re.compile(r"\\listoffigures(?![A-Za-z])")),
    "Tabellenverzeichnis": (".lot", re.compile(r"\\listoftables(?![A-Za-z])")),
    "Abkürzungsverzeichnis": (".acr", re.compile(
        r"\\printacronyms|\\printabbreviations|\\printglossaries|\\printnoidxglossaries"
        r"|\\print(?:noidx)?glossary\s*\[[^\]]*type\s*=\s*\\?(?:acronymtype|acronym|abbreviations)"
        r"|\\begin\{acronym\}")),
}
ABBREVIATION_DEF = re.compile(r"\\newacronym|\\newabbreviation|\\acro\{|\\acrodef\{")


def _sources(project):
    """All LaTeX sources below the main file, including template and class files."""
    out = {}
    for p in project.src.rglob("*"):
        if p.suffix in {".tex", ".cls", ".sty"} and OUT_DIR not in p.parts and ".lektorat" not in p.parts and p.is_file():
            out[p] = "\n".join(strip_comment(l) for l in p.read_text(encoding="utf-8", errors="replace").splitlines())
    return out


def _files_read(project):
    """File suffixes read by the last LaTeX run according to the recorder file (.fls), or None without a build."""
    fls = project.main.with_suffix(".fls")
    if not fls.exists():
        return None
    return {Path(l[6:].strip()).suffix for l in fls.read_text(errors="replace").splitlines() if l.startswith("INPUT ")}


def check_lists(project):
    """Reports missing lists of figures, tables and abbreviations when the thesis needs them."""
    sources = _sources(project)
    everything = "\n".join(sources.values())
    needed = {
        "Abbildungsverzeichnis": sum(1 for f in project.floats if f.kind.startswith(("figure", "wrapfigure", "sidewaysfigure")) and f.caption),
        "Tabellenverzeichnis": sum(1 for f in project.floats if f.kind.startswith(("table", "sidewaystable")) and f.caption),
        "Abkürzungsverzeichnis": len(ABBREVIATION_DEF.findall(everything)),
    }
    files_read = _files_read(project)
    main_rel = project.rel(project.main)
    line = next((i for i, l in enumerate(project.main.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
                  if "\\begin{document}" in strip_comment(l)), 1)
    findings, status = [], {}
    for name, (ext, pat) in LISTS.items():
        in_source = any(pat.search(t) for t in sources.values())
        if files_read is not None:
            present = ext in files_read or (name == "Abkürzungsverzeichnis" and "\\begin{acronym}" in everything)
            basis = "letzter Build"
        else:
            present = in_source
            basis = "Quelltext"
        status[name] = {"needed": needed[name], "present": present, "basis": basis}
        if needed[name] and not present:
            unit = {"Abbildungsverzeichnis": "Abbildungen", "Tabellenverzeichnis": "Tabellen",
                       "Abkürzungsverzeichnis": "Abkürzungen"}[name]
            note = " Im Quelltext steht der Befehl, im letzten Build wurde das Verzeichnis aber nicht erzeugt." if in_source and files_read is not None else ""
            b = make(project.config, "STR-VERZEICHNIS", main_rel, line,
                     f"{name} fehlt, die Arbeit enthält {needed[name]} {unit} ({basis}).{note}",
                     name, {"Abbildungsverzeichnis": "\\listoffigures", "Tabellenverzeichnis": "\\listoftables",
                            "Abkürzungsverzeichnis": "\\printglossary[type=\\acronymtype] oder \\printacronyms"}[name]
                     + " nach dem Inhaltsverzeichnis")
            if b:
                findings.append(b)
    return findings, status


def _git(root, *args, timeout=10):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip()


def _visibility(url):
    """PUBLIC, PRIVATE, or None if the GitHub CLI is missing or does not answer."""
    if "github.com" not in url:
        return None
    try:
        r = subprocess.run(["gh", "repo", "view", url, "--json", "visibility", "-q", ".visibility"],
                           capture_output=True, text=True, timeout=8)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def git(project):
    """Checks whether the thesis is versioned, backed up remotely and up to date."""
    cfg = project.config.get("git", {})
    if cfg.get("enabled", True) is False:
        return [], {"checked": False}
    root = project.root.resolve()
    main_rel = project.rel(project.main)
    findings, status = [], {"checked": True}

    def flag(rule, message, suggestion):
        b = make(project.config, rule, main_rel, 0, message, "", suggestion)
        if b:
            findings.append(b)

    try:
        code, top = _git(root, "rev-parse", "--show-toplevel")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        status["repo"] = None
        return findings, status
    if code != 0:
        status["repo"] = False
        flag("ABG-VERSIONIERUNG", "Die Arbeit liegt in keinem Git-Repository. Ein Datenverlust wäre nicht abgesichert.",
              "git init, .thesis-editor/ und LaTeX-Hilfsdateien in .gitignore, privates Repository anlegen und regelmäßig pushen")
        return findings, status
    status["repo"] = True
    _, remotes = _git(root, "remote", "-v")
    urls = sorted({l.split()[1] for l in remotes.splitlines() if len(l.split()) >= 2})
    status["remote"] = urls
    if not urls:
        flag("ABG-VERSIONIERUNG", "Das Repository hat kein Remote. Der Datenstand liegt nur auf diesem Rechner.",
              "privates Repository anlegen (z.B. gh repo create --private --source . --push)")
    elif cfg.get("check_visibility", True):
        visibility = _visibility(urls[0])
        status["visibility"] = visibility
        if visibility == "PUBLIC":
            flag("ABG-VERSIONIERUNG", f"Das Repository {urls[0]} ist öffentlich. Eine unveröffentlichte Arbeit gehört bis zur Abgabe in ein privates Repository.",
                  "gh repo edit --visibility private --accept-visibility-change-consequences")

    _, porcelain = _git(root, "status", "--porcelain", "--untracked-files=all", "--", ".")
    dirty = [l[3:] for l in porcelain.splitlines() if l and OUT_DIR + "/" not in l and ".lektorat/" not in l]
    status["uncommitted"] = len(dirty)
    if dirty:
        examples = ", ".join(Path(p.split(" -> ")[-1].strip('"')).name for p in dirty[:5])
        flag("ABG-GIT-STAND", f"{len(dirty)} Datei{'en' if len(dirty) > 1 else ''} mit nicht committeten Änderungen, z.B. {examples}. Dieser Stand ist nicht gesichert.",
              "Änderungen prüfen, committen und pushen")
    code, ahead = _git(root, "rev-list", "--count", "@{upstream}..HEAD")
    if code == 0 and ahead.isdigit():
        status["unpushed"] = int(ahead)
        if int(ahead):
            flag("ABG-GIT-STAND", f"{ahead} Commit{'s sind' if int(ahead) > 1 else ' ist'} noch nicht gepusht. Der Stand liegt nur lokal.", "git push")
    elif urls:
        status["unpushed"] = None
        flag("ABG-GIT-STAND", "Der aktuelle Branch hat keinen Upstream. Es ist unklar, ob der Stand extern gesichert ist.",
              "git push -u origin <branch>")
    _, last = _git(root, "log", "-1", "--format=%cs")
    status["last_commit"] = last
    return findings, status
