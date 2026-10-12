"""Matches citation commands against the BibLaTeX files and checks the entries."""

import re

from ruleset import make
from texmodel import CITE_CMD, CODE_ENVS, group_end

REQUIRED_FIELDS = {
    "article": [("author",), ("title",), ("date", "year"), ("journaltitle", "journal")],
    "inproceedings": [("author",), ("title",), ("date", "year"), ("booktitle", "eventtitle")],
    "incollection": [("author",), ("title",), ("date", "year"), ("booktitle",)],
    "book": [("author", "editor"), ("title",), ("date", "year"), ("publisher",)],
    "thesis": [("author",), ("title",), ("date", "year"), ("institution", "school")],
    "report": [("author", "institution"), ("title",), ("date", "year")],
    "online": [("author", "editor", "organization"), ("title",), ("date", "year", "urldate"), ("url",)],
    "misc": [("author", "editor", "organization"), ("title",), ("date", "year")],
}
DOI_TYPES = {"article", "inproceedings", "incollection"}


def parse_bib(text):
    """Returns entries as a list of dicts with type, key, line and fields."""
    entries = []
    i = 0
    while True:
        i = text.find("@", i)
        if i < 0:
            break
        m = re.match(r"@(\w+)\s*\{", text[i:])
        if not m:
            i += 1
            continue
        typ = m.group(1).lower()
        start = i + m.end() - 1
        end = group_end(text, start)
        body = text[start + 1:end - 1]
        line = text.count("\n", 0, i) + 1
        i = end
        if typ in {"comment", "preamble", "string"}:
            continue
        key, _, rest = body.partition(",")
        fields = {}
        j = 0
        while j < len(rest):
            fm = re.match(r"\s*,?\s*([\w-]+)\s*=\s*", rest[j:])
            if not fm:
                break
            name = fm.group(1).lower()
            j += fm.end()
            if j < len(rest) and rest[j] == "{":
                e = group_end(rest, j)
                val = rest[j + 1:e - 1]
            elif j < len(rest) and rest[j] == '"':
                e = rest.find('"', j + 1) + 1 or len(rest)
                val = rest[j + 1:e - 1]
            else:
                vm = re.match(r"[^,]*", rest[j:])
                e = j + vm.end()
                val = vm.group(0)
            fields[name] = val.strip()
            j = e
        entries.append({"type": typ, "key": key.strip(), "line": line, "fields": fields})
    return entries


def used_keys(project):
    """Collects (key, line) of all citation commands in the project."""
    out = []
    nocite_all = False
    for ln in project.lines:
        if ln.in_any(CODE_ENVS - {"equation", "align"}):
            continue
        c = ln.code
        for m in CITE_CMD.finditer(c):
            multi = m.group(0).rstrip("*").endswith("cites")
            j = m.end()
            while j < len(c):
                k = j
                while k < len(c) and c[k] in " \t":
                    k += 1
                if k < len(c) and c[k] in "[(":
                    if c[k] == "(":
                        j = c.find(")", k) + 1 or len(c)
                    else:
                        j = group_end(c, k)
                    continue
                if k < len(c) and c[k] == "{":
                    e = group_end(c, k)
                    for key in c[k + 1:e - 1].split(","):
                        key = key.strip()
                        if key == "*":
                            nocite_all = True
                        elif key:
                            out.append((key, ln))
                    j = e
                    if not multi:
                        break
                    continue
                break
    return out, nocite_all


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\\[a-zA-Z]+|[{}]", "", t.lower()))


def is_preprint(e):
    f = e["fields"]
    blob = " ".join(f.get(k, "") for k in ("eprinttype", "archiveprefix", "journaltitle", "journal", "publisher", "url", "howpublished")).lower()
    return "arxiv" in blob or "ssrn" in blob or "biorxiv" in blob or "preprint" in blob


def check(project):
    cfg = project.config
    out = []
    entries = []
    for b in cfg["project"].get("bib", []):
        path = project.root / b
        if path.exists():
            for e in parse_bib(path.read_text(encoding="utf-8", errors="replace")):
                e["file"] = b
                entries.append(e)
    by_key = {}
    for e in entries:
        by_key.setdefault(e["key"], e)
    used, nocite_all = used_keys(project)
    used_set = {k for k, _ in used}

    def add(rule, file, line, message, excerpt="", suggestion=""):
        b = make(cfg, rule, file, line, message, excerpt, suggestion, source="bib")
        if b:
            out.append(b)

    lower_keys = {k.lower(): k for k in by_key}
    for key, ln in used:
        if project.ignored(ln, "ZIT-SCHLUESSEL"):
            continue
        if key not in by_key:
            near = lower_keys.get(key.lower(), "")
            add("ZIT-SCHLUESSEL", project.rel(ln.file), ln.no, f"Schlüssel {key} fehlt in der Bibliografie", ln.code.strip(), near or "Eintrag in Zotero anlegen und exportieren")
    if not nocite_all:
        for e in entries:
            if e["key"] not in used_set:
                add("BIB-UNGENUTZT", e["file"], e["line"], f"{e['key']} wird nicht zitiert", e["fields"].get("title", "")[:120], "zitieren oder aus der Bibliografie entfernen")
    seen_doi, seen_title = {}, {}
    for e in entries:
        f = e["fields"]
        doi = f.get("doi", "").lower().strip()
        title = norm_title(f.get("title", ""))
        for val, seen in ((doi, seen_doi), (title, seen_title)):
            if val and len(val) > 8:
                if val in seen and seen[val] != e["key"]:
                    add("BIB-DUPLIKAT", e["file"], e["line"], f"{e['key']} und {seen[val]} beschreiben dieselbe Quelle", f.get("title", "")[:120], "einen Schlüssel behalten und Zitate angleichen")
                    break
                seen.setdefault(val, e["key"])
        if e["key"] not in used_set:
            continue
        for alts in REQUIRED_FIELDS.get(e["type"], []):
            if not any(f.get(a) for a in alts):
                add("BIB-FELDER", e["file"], e["line"], f"{e['key']} ({e['type']}) ohne {' oder '.join(alts)}", f.get("title", "")[:120], f"Feld {alts[0]} in Zotero ergänzen")
        if is_preprint(e):
            add("BIB-PREPRINT", e["file"], e["line"], f"{e['key']} ist ein Preprint", f.get("title", "")[:120], "nach begutachteter Fassung suchen (Konferenz, Zeitschrift)")
        elif e["type"] in DOI_TYPES and not f.get("doi"):
            add("BIB-DOI", e["file"], e["line"], f"{e['key']} ohne DOI", f.get("title", "")[:120], "DOI über doi.org oder Crossref ergänzen")
    stats = {"entries": len(entries), "cited": len(used_set & set(by_key)), "citations": len(used)}
    return out, stats
