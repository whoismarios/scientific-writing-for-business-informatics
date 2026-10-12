#!/usr/bin/env python3
"""Kommandozeile des Skills thesis-lektor: einrichten, prüfen, berichten, annotieren."""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bib  # noqa: E402
import umfeld  # noqa: E402
from regelwerk import REGELWERK, RULES, SCHWERE_RANG, SKILL_DIR, from_dict, load_config  # noqa: E402
from regeln import Linter  # noqa: E402
from texmodell import Project  # noqa: E402


def lauf_dir(root):
    d = Path(root) / ".lektorat" / "lauf"
    (d / "agenten").mkdir(parents=True, exist_ok=True)
    return d


def erkennen(root):
    """Findet Hauptdatei, Bibliografie, Glossar und farbige Marker-Makros eines LaTeX-Projekts."""
    root = Path(root).resolve()
    mains = []
    for p in root.rglob("*.tex"):
        if {".lektorat", ".claude", ".agents", "node_modules"} & set(p.parts):
            continue
        txt = p.read_text(errors="replace")
        if "\\documentclass" in txt and "\\begin{document}" in txt:
            mains.append(p)
    if not mains:
        raise SystemExit(f"Keine LaTeX-Hauptdatei mit \\documentclass und \\begin{{document}} unter {root} gefunden. "
                         "Der Skill prüft nur LaTeX-Projekte.")
    main = min(mains, key=lambda p: (len(p.relative_to(root).parts), p.name.lower() not in {"main.tex", "thesis.tex"}, str(p)))
    tex_all = {p: p.read_text(errors="replace") for p in main.parent.rglob("*.tex")}
    bibs, gloss, quelle, offen = [], [], [], []
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
            (quelle if re.search(r"quelle|cite|fehl|missing", name, re.I) else offen).append(name)
    praeambel = tex_all.get(main, "").split("\\begin{document}")[0] + "".join(
        t for p, t in tex_all.items() if p != main and "\\usepackage" in t)
    engine = "lualatex" if re.search(r"fontspec|unicode-math|luacode|luatex", praeambel) else "pdflatex"
    return {
        "projekt": {"titel": root.name, "main": str(main.relative_to(root)), "bib": sorted(set(bibs)),
                    "glossar": sorted(set(gloss)), "engine": engine},
        "marker": {"quelle_fehlt": quelle or ["quellefehlt"], "offen": offen or ["offen"]},
    }


def konfiguration(root):
    """lektorat.toml, falls vorhanden, sonst die automatisch erkannten Werte."""
    if (Path(root) / "lektorat.toml").exists():
        return load_config(root)
    return load_config(root, erkennen(root))


def cmd_init(a):
    root = Path(a.root).resolve()
    target = root / "lektorat.toml"
    if target.exists() and not a.force:
        print(f"{target} existiert bereits. Mit --force überschreiben.")
        return
    e = erkennen(root)
    pr, mk = e["projekt"], e["marker"]
    lines = [
        "# Projektkonfiguration für thesis-lektor",
        "",
        "# Inhaltliche Regeln, die nur die Gutachter-Agenten prüfen können. Muss vor der ersten [Tabelle] stehen.",
        "projektregeln = []",
        "",
        "[projekt]",
        f"titel = {json.dumps(pr['titel'], ensure_ascii=False)}",
        f"main = {json.dumps(pr['main'])}",
        f"bib = {json.dumps(pr['bib'])}",
        f"glossar = {json.dumps(pr['glossar'])}",
        f'engine = "{pr["engine"]}"',
        "",
        "[marker]",
        f"quelle_fehlt = {json.dumps(mk['quelle_fehlt'])}",
        f"offen = {json.dumps(mk['offen'])}",
        "",
        "[satz]",
        "max_woerter = 35",
        "max_nebensaetze = 2",
        "",
        "[struktur]",
        'ohne_strukturpruefung = ["Anhang"]',
        "",
        "[begriffe]",
        "komposita = []",
        "varianten = [",
        '  ["Nutzer*", "User*", "Anwender*", "Benutzer*"],',
        "]",
        "",
        "[begriffe.verboten]",
        "",
        "[schwere]",
        "",
        "[ausnahmen]",
        "woerter = []",
        "",
        "[forschungsfragen]",
        '# FF1 = "Wortlaut der ersten Forschungsfrage"',
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Angelegt: {target}")


def run_checks(root, nur=None):
    cfg = konfiguration(root)
    project = Project(root, cfg)
    linter = Linter(project)
    befunde = linter.run()
    bib_befunde, bib_stats = bib.check(project)
    befunde += bib_befunde
    verz_befunde, verz_status = umfeld.verzeichnisse(project)
    git_befunde, git_status = umfeld.git(project)
    if not nur:
        befunde += verz_befunde + git_befunde
    words = linter.words_by_file
    formeln = {}
    for ln in project.lines:
        if ln.code.lstrip().startswith(("\\begin{equation", "\\begin{align", "\\[")):
            f = project.rel(ln.file)
            formeln[f] = formeln.get(f, 0) + 1
    if nur:
        selected = project.select(nur)
        befunde = [b for b in befunde if b.datei in selected or (b.quelle == "bib" and b.regel == "ZIT-SCHLUESSEL" and b.datei in selected)]
        words = {f: n for f, n in words.items() if f in selected}
    befunde.sort(key=lambda b: (b.datei, b.zeile, SCHWERE_RANG.get(b.schwere, 9)))
    meta = {
        "zeit": datetime.now().isoformat(timespec="seconds"),
        "regelwerk": REGELWERK["meta"]["version"],
        "dateien": [project.rel(f) for f in project.files],
        "woerter": sum(words.values()),
        "woerter_je_datei": words,
        "formeln_je_datei": formeln,
        "auswahl": nur or "",
        "saetze": len(project.sentences),
        "bib": bib_stats,
        "verzeichnisse": verz_status,
        "git": git_status,
        "gliederung": [{"ebene": h.level, "titel": h.title, "datei": project.rel(h.line.file), "zeile": h.line.no,
                        "saetze": h.sentences} for h in project.headings],
    }
    return cfg, project, befunde, meta


def print_summary(befunde, meta):
    c = Counter(b.schwere for b in befunde)
    print(f"Wörter: {meta['woerter']}  Sätze: {meta['saetze']}  Dateien: {len(meta['dateien'])}")
    print("Befunde: " + "  ".join(f"{k} {c.get(k, 0)}" for k in ("Fehler", "Offen", "Warnung", "Hinweis")))
    by_rule = Counter(b.regel for b in befunde)
    print("\nRegel                        Anzahl  Schwere")
    for rule, n in sorted(by_rule.items(), key=lambda kv: (SCHWERE_RANG.get(RULES.get(kv[0], {}).get("schwere"), 9), -kv[1])):
        print(f"{rule:<28} {n:>6}  {RULES.get(rule, {}).get('schwere', '')}")
    print("\n" + umfeld_zeilen(meta))


def umfeld_zeilen(meta):
    out = []
    v = meta.get("verzeichnisse", {})
    if v:
        out.append("Verzeichnisse: " + ", ".join(
            f"{k} {'ja' if s['vorhanden'] else ('fehlt' if s['benoetigt'] else 'nicht nötig')}" for k, s in v.items())
            + f" (Grundlage: {next(iter(v.values()))['grundlage']})")
    g = meta.get("git", {})
    if g.get("geprueft") is False:
        out.append("Git: Prüfung abgeschaltet")
    elif g.get("repo") is None:
        out.append("Git: nicht installiert")
    elif not g.get("repo"):
        out.append("Git: kein Repository")
    else:
        teile = [f"Remote {g['remote'][0]}" if g.get("remote") else "kein Remote"]
        if g.get("sichtbarkeit"):
            teile.append({"PRIVATE": "privat", "PUBLIC": "öffentlich"}.get(g["sichtbarkeit"], g["sichtbarkeit"].lower()))
        teile.append(f"nicht committet: {g.get('uncommitted', 0)} Dateien")
        if g.get("ungepusht") is not None:
            teile.append(f"nicht gepusht: {g['ungepusht']} Commits")
        teile.append(f"letzter Commit {g.get('letzter_commit') or '-'}")
        out.append("Git: " + ", ".join(teile))
    return "\n".join(out)


def cmd_pruefen(a):
    cfg, project, befunde, meta = run_checks(a.root, a.nur)
    d = lauf_dir(a.root)
    (d / "linter.json").write_text(json.dumps({"meta": meta, "befunde": [b.as_dict() for b in befunde]}, ensure_ascii=False, indent=1), encoding="utf-8")
    print_summary(befunde, meta)
    print(f"\nGespeichert: {d / 'linter.json'}")


def cmd_aufraeumen(a):
    d = lauf_dir(a.root) / "agenten"
    n = 0
    for f in d.glob("*.json"):
        f.unlink()
        n += 1
    print(f"{n} alte Agentendateien entfernt.")


def cmd_kontext(a):
    cfg, project, befunde, meta = run_checks(a.root)
    print(f"# Gliederung ({meta['woerter']} Wörter)\n")
    for h in meta["gliederung"]:
        if h["ebene"] <= 2:
            print(f"{'  ' * max(h['ebene'], 0)}- {h['titel']}  [{h['datei']}:{h['zeile']}, {h['saetze']} Sätze]")
    print("\n# Dateien")
    for f in meta["dateien"]:
        n = meta["formeln_je_datei"].get(f, 0)
        print(f"- {f}  ({meta['woerter_je_datei'].get(f, 0)} Wörter" + (f", {n} abgesetzte Formeln)" if n else ")"))
    marks = [b for b in befunde if b.regel.startswith("MARK-")]
    print(f"\n# Marker ({len(marks)})")
    for b in marks:
        print(f"- {b.regel} {b.datei}:{b.zeile}  {b.meldung}")
    if cfg.get("forschungsfragen"):
        print("\n# Forschungsfragen")
        for k, v in cfg["forschungsfragen"].items():
            print(f"- {k}: {v}")
    if cfg.get("projektregeln"):
        print("\n# Projektregeln")
        for r in cfg["projektregeln"]:
            print(f"- {r}")
    print("\n# Begriffe")
    for k, v in cfg["begriffe"].get("verboten", {}).items():
        print(f"- {k} -> {v}")


def load_all(root):
    cfg = konfiguration(root)
    d = lauf_dir(root)
    data = json.loads((d / "linter.json").read_text(encoding="utf-8"))
    befunde = [from_dict({**b, "quelle": b.get("quelle", "linter")}, cfg) for b in data["befunde"]]
    agenten = {}
    for f in sorted((d / "agenten").glob("*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Übersprungen, kein gültiges JSON: {f.name} ({e})")
            continue
        items = raw.get("befunde", raw) if isinstance(raw, dict) else raw
        rolle = f.stem
        n = 0
        for it in items:
            it.setdefault("quelle", f"agent:{rolle}")
            b = from_dict(it, cfg)
            if b:
                befunde.append(b)
                n += 1
        agenten[rolle] = n
    befunde = [b for b in befunde if b]
    return cfg, data["meta"], befunde, agenten


def cmd_bericht(a):
    import bericht
    cfg, meta, befunde, agenten = load_all(a.root)
    root = Path(a.root)
    hist_dir = root / ".lektorat" / "verlauf"
    hist_dir.mkdir(parents=True, exist_ok=True)
    previous = sorted(hist_dir.glob("*.json"))
    prev = json.loads(previous[-1].read_text(encoding="utf-8")) if previous else None
    entry = bericht.history_entry(meta, befunde, agenten)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if not a.ohne_verlauf:
        (hist_dir / f"{stamp}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    history = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(hist_dir.glob("*.json"))]
    if a.ohne_verlauf:
        history.append(entry)
    out = root / ".lektorat" / "Lektoratsbericht.html"
    out.write_text(bericht.render_html(cfg, meta, befunde, agenten, history, prev), encoding="utf-8")
    print(bericht.render_summary(meta, befunde, agenten, entry, prev))
    print("\n" + umfeld_zeilen(meta))
    print(f"\nBericht: {out}")


def cmd_annotieren(a):
    import annotieren
    cfg, meta, befunde, agenten = load_all(a.root)
    project = Project(a.root, cfg)
    pdf = annotieren.build(project, befunde, kompilieren=not a.ohne_build)
    print(f"Annotierte Fassung: {pdf}")


def cmd_regeln(a):
    out = ["# Regelwerk thesis-lektor", "",
           f"Version {REGELWERK['meta']['version']}. Erzeugt aus `regelwerk.toml`, nicht von Hand bearbeiten.", "",
           "Schweregrade: **Fehler** muss vor der Abgabe behoben sein. **Warnung** sollte behoben oder begründet werden. "
           "**Hinweis** ist eine Empfehlung. **Offen** sind Marker des Schreibenden.", "",
           "Prüfung: `linter` und `bib` laufen deterministisch über Skripte. `umfeld` prüft die Versionierung mit Git und zählt nicht zum Lektoratsindex. `agent` prüfen die Gutachter-Agenten.", "",
           "Herkunft: SR = Schreibregeln aus der Betreuung einer Masterarbeit, FB = Festlegung im Schreibprozess, APA7 = APA Publication Manual, "
           "WI = Konvention der Wirtschaftsinformatik, DUDEN = Duden-Empfehlung, TYPO = Typografie-Konvention.", ""]
    groups = {}
    for r in REGELWERK["regel"]:
        groups.setdefault(r["id"].split("-")[0], []).append(r)
    names = {"TYP": "Typografie", "SPR": "Sprache und Ton", "SAT": "Satzbau", "TERM": "Begriffe",
             "ZIT": "Zitation", "INH": "Inhalt", "BIB": "Bibliografie", "FMT": "Formatierung und Verweise", "ABG": "Abgabe und Datensicherung",
             "STR": "Struktur", "FORM": "Formeln", "ABB": "Abbildungen", "MARK": "Arbeitsmarker"}
    out.append("## Übersicht\n")
    out.append("| ID | Regel | Schwere | Prüfung | Farbe |")
    out.append("|---|---|---|---|---|")
    for r in REGELWERK["regel"]:
        out.append(f"| `{r['id']}` | {r['titel']} | {r['schwere']} | {r['pruefung']} | {r['farbe']} |")
    for g, rules in groups.items():
        out.append(f"\n## {names.get(g, g)}\n")
        for r in rules:
            out.append(f"### `{r['id']}` {r['titel']}\n")
            out.append(f"{r['schwere']}, Prüfung: {r['pruefung']}, Herkunft: {r['herkunft']}\n")
            out.append(f"{r['warum']}\n")
            out.append(f"- Falsch: {r['falsch']}")
            out.append(f"- Richtig: {r['richtig']}\n")
    wl = REGELWERK["wortlisten"]
    out.append("\n## Wortlisten\n")
    for k in ("wertung", "selbstverstaendlich", "floskel", "hedging", "fuellwort", "doppelung", "beleg_signal"):
        out.append(f"**{k}:** " + ", ".join(wl[k]) + "\n")
    (SKILL_DIR / "references" / "regelwerk.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Geschrieben: {SKILL_DIR / 'references' / 'regelwerk.md'}")


def main():
    ap = argparse.ArgumentParser(prog="lektorat")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "pruefen", "kontext", "bericht", "annotieren", "regeln", "aufraeumen"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".")
        if name == "init":
            p.add_argument("--force", action="store_true")
        if name == "pruefen":
            p.add_argument("--nur", help="Regex auf Dateipfade, eingebundene Unterdateien zählen mit, z.B. 03_methodik")
        if name == "bericht":
            p.add_argument("--ohne-verlauf", action="store_true")
        if name == "annotieren":
            p.add_argument("--ohne-build", action="store_true")
    a = ap.parse_args()
    {"init": cmd_init, "pruefen": cmd_pruefen, "kontext": cmd_kontext, "bericht": cmd_bericht,
     "annotieren": cmd_annotieren, "regeln": cmd_regeln, "aufraeumen": cmd_aufraeumen}[a.cmd](a)


if __name__ == "__main__":
    main()
