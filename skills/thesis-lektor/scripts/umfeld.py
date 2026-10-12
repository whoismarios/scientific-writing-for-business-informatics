"""Prüft das Umfeld der Arbeit: Verzeichnisse im Dokument und die Versionierung mit Git."""

import re
import subprocess
from pathlib import Path

from regelwerk import make
from texmodell import strip_comment

LISTEN = {
    "Abbildungsverzeichnis": (".lof", re.compile(r"\\listoffigures(?![A-Za-z])")),
    "Tabellenverzeichnis": (".lot", re.compile(r"\\listoftables(?![A-Za-z])")),
    "Abkürzungsverzeichnis": (".acr", re.compile(
        r"\\printacronyms|\\printabbreviations|\\printglossaries|\\printnoidxglossaries"
        r"|\\print(?:noidx)?glossary\s*\[[^\]]*type\s*=\s*\\?(?:acronymtype|acronym|abbreviations)"
        r"|\\begin\{acronym\}")),
}
ABKUERZUNG_DEF = re.compile(r"\\newacronym|\\newabbreviation|\\acro\{|\\acrodef\{")


def _quellen(project):
    """Alle LaTeX-Quellen im Verzeichnis der Hauptdatei, auch Vorlagen- und Klassendateien."""
    out = {}
    for p in project.src.rglob("*"):
        if p.suffix in {".tex", ".cls", ".sty"} and ".lektorat" not in p.parts and p.is_file():
            out[p] = "\n".join(strip_comment(l) for l in p.read_text(encoding="utf-8", errors="replace").splitlines())
    return out


def _gelesen(project):
    """Dateien, die der letzte LaTeX-Lauf laut Recorder-Datei (.fls) eingelesen hat, oder None ohne Build."""
    fls = project.main.with_suffix(".fls")
    if not fls.exists():
        return None
    return {Path(l[6:].strip()).suffix for l in fls.read_text(errors="replace").splitlines() if l.startswith("INPUT ")}


def verzeichnisse(project):
    """Meldet fehlende Abbildungs-, Tabellen- und Abkürzungsverzeichnisse, wenn die Arbeit sie braucht."""
    quellen = _quellen(project)
    alles = "\n".join(quellen.values())
    bedarf = {
        "Abbildungsverzeichnis": sum(1 for f in project.floats if f.kind.startswith(("figure", "wrapfigure", "sidewaysfigure")) and f.caption),
        "Tabellenverzeichnis": sum(1 for f in project.floats if f.kind.startswith(("table", "sidewaystable")) and f.caption),
        "Abkürzungsverzeichnis": len(ABKUERZUNG_DEF.findall(alles)),
    }
    gelesen = _gelesen(project)
    main_rel = project.rel(project.main)
    zeile = next((i for i, l in enumerate(project.main.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
                  if "\\begin{document}" in strip_comment(l)), 1)
    befunde, status = [], {}
    for name, (endung, pat) in LISTEN.items():
        im_text = any(pat.search(t) for t in quellen.values())
        if gelesen is not None:
            da = endung in gelesen or (name == "Abkürzungsverzeichnis" and "\\begin{acronym}" in alles)
            grundlage = "letzter Build"
        else:
            da = im_text
            grundlage = "Quelltext"
        status[name] = {"benoetigt": bedarf[name], "vorhanden": da, "grundlage": grundlage}
        if bedarf[name] and not da:
            einheit = {"Abbildungsverzeichnis": "Abbildungen", "Tabellenverzeichnis": "Tabellen",
                       "Abkürzungsverzeichnis": "Abkürzungen"}[name]
            hinweis = " Im Quelltext steht der Befehl, im letzten Build wurde das Verzeichnis aber nicht erzeugt." if im_text and gelesen is not None else ""
            b = make(project.config, "STR-VERZEICHNIS", main_rel, zeile,
                     f"{name} fehlt, die Arbeit enthält {bedarf[name]} {einheit} ({grundlage}).{hinweis}",
                     name, {"Abbildungsverzeichnis": "\\listoffigures", "Tabellenverzeichnis": "\\listoftables",
                            "Abkürzungsverzeichnis": "\\printglossary[type=\\acronymtype] oder \\printacronyms"}[name]
                     + " nach dem Inhaltsverzeichnis")
            if b:
                befunde.append(b)
    return befunde, status


def _git(root, *args, timeout=10):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip()


def _sichtbarkeit(url):
    """PUBLIC, PRIVATE oder None, wenn die GitHub-CLI fehlt oder nicht antwortet."""
    if "github.com" not in url:
        return None
    try:
        r = subprocess.run(["gh", "repo", "view", url, "--json", "visibility", "-q", ".visibility"],
                           capture_output=True, text=True, timeout=8)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def git(project):
    """Prüft, ob die Arbeit versioniert, extern gesichert und auf dem aktuellen Stand ist."""
    cfg = project.config.get("git", {})
    if cfg.get("pruefen", True) is False:
        return [], {"geprueft": False}
    root = project.root.resolve()
    main_rel = project.rel(project.main)
    befunde, status = [], {"geprueft": True}

    def melde(regel, meldung, vorschlag):
        b = make(project.config, regel, main_rel, 0, meldung, "", vorschlag)
        if b:
            befunde.append(b)

    try:
        code, top = _git(root, "rev-parse", "--show-toplevel")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        status["repo"] = None
        return befunde, status
    if code != 0:
        status["repo"] = False
        melde("ABG-VERSIONIERUNG", "Die Arbeit liegt in keinem Git-Repository. Ein Datenverlust wäre nicht abgesichert.",
              "git init, .lektorat/ und LaTeX-Hilfsdateien in .gitignore, privates Repository anlegen und regelmäßig pushen")
        return befunde, status
    status["repo"] = True
    _, remotes = _git(root, "remote", "-v")
    urls = sorted({l.split()[1] for l in remotes.splitlines() if len(l.split()) >= 2})
    status["remote"] = urls
    if not urls:
        melde("ABG-VERSIONIERUNG", "Das Repository hat kein Remote. Der Datenstand liegt nur auf diesem Rechner.",
              "privates Repository anlegen (z.B. gh repo create --private --source . --push)")
    elif cfg.get("sichtbarkeit_pruefen", True):
        sicht = _sichtbarkeit(urls[0])
        status["sichtbarkeit"] = sicht
        if sicht == "PUBLIC":
            melde("ABG-VERSIONIERUNG", f"Das Repository {urls[0]} ist öffentlich. Eine unveröffentlichte Arbeit gehört bis zur Abgabe in ein privates Repository.",
                  "gh repo edit --visibility private --accept-visibility-change-consequences")

    _, porcelain = _git(root, "status", "--porcelain", "--untracked-files=all", "--", ".")
    offen = [l[3:] for l in porcelain.splitlines() if l and ".lektorat/" not in l]
    status["uncommitted"] = len(offen)
    if offen:
        beispiele = ", ".join(Path(p.split(" -> ")[-1].strip('"')).name for p in offen[:5])
        melde("ABG-GIT-STAND", f"{len(offen)} Datei{'en' if len(offen) > 1 else ''} mit nicht committeten Änderungen, z.B. {beispiele}. Dieser Stand ist nicht gesichert.",
              "Änderungen prüfen, committen und pushen")
    code, ahead = _git(root, "rev-list", "--count", "@{upstream}..HEAD")
    if code == 0 and ahead.isdigit():
        status["ungepusht"] = int(ahead)
        if int(ahead):
            melde("ABG-GIT-STAND", f"{ahead} Commit{'s sind' if int(ahead) > 1 else ' ist'} noch nicht gepusht. Der Stand liegt nur lokal.", "git push")
    elif urls:
        status["ungepusht"] = None
        melde("ABG-GIT-STAND", "Der aktuelle Branch hat keinen Upstream. Es ist unklar, ob der Stand extern gesichert ist.",
              "git push -u origin <branch>")
    _, last = _git(root, "log", "-1", "--format=%cs")
    status["letzter_commit"] = last
    return befunde, status
