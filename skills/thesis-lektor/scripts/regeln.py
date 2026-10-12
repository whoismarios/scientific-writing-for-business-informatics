"""Mechanische Prüfregeln. Jede Prüfung liefert Befunde mit Regel-ID, Datei und Zeile."""

import re

from regelwerk import WORTLISTEN, make, word_pattern
from texmodell import (CITE_CMD, CODE_ENVS, FLOAT_ENVS, INLINE_MATH, LIST_ENVS, MATH_ENVS, QUOTE_ENVS,
                       TABLE_ENVS, WORD, command_args, group_end, to_prose)

ZAHLWORT = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf"]

P_ICH = word_pattern(WORTLISTEN["ich_wir"])
P_WERTUNG = word_pattern(WORTLISTEN["wertung"])
P_SELBST = word_pattern(WORTLISTEN["selbstverstaendlich"])
P_FLOSKEL = word_pattern(WORTLISTEN["floskel"])
P_HEDGE = word_pattern(WORTLISTEN["hedging"])
P_FUELL = word_pattern(WORTLISTEN["fuellwort"])
P_DOPPEL = word_pattern(WORTLISTEN["doppelung"])
P_BELEG = word_pattern(WORTLISTEN["beleg_signal"])
P_NEBENSATZ = re.compile(
    r",\s*(?:(?:in|mit|von|für|bei|aus|auf|über|unter|nach|zu|an|durch|gegen|ohne|um|wegen)\s+)?(?:"
    + "|".join(WORTLISTEN["nebensatz_einleiter"]) + r")\b", re.IGNORECASE)
_DET = r"(?:des|der|eines|einer)\s+(?:[a-zäöü]+(?:en|er|es)\s+)?[A-ZÄÖÜ][\wäöüß-]+"
P_GENITIV = re.compile(r"\b" + _DET + r"\s+" + _DET + r"\s+" + _DET)
P_NOMEN = re.compile(r"^\w+(?:ung|heit|keit|ion|ität|ismus)(?:en)?$", re.IGNORECASE)
P_MANUELL = re.compile(
    r"\b[A-ZÄÖÜ][\wäöüß'-]+(?:\s+et\s+al\.|\s+(?:und|&)\s+[A-ZÄÖÜ][\wäöüß'-]+)?,?\s*\(\s*(?:19|20)\d{2}[a-z]?\s*\)"
    r"|\(\s*[A-ZÄÖÜ][\wäöüß'-]+(?:\s+et\s+al\.)?,?\s+(?:19|20)\d{2}[a-z]?\s*\)"
    r"|\bet\s+al\.")
P_ABK = re.compile(r"(?<![A-Za-z\\])([zdusmvio])\.(\s|~)?([BhaäTUouEeRA])\.")
P_HALBGEVIERT = re.compile(r"[\w)\]}]\s+(?:--|–)\s+[\w(\\]")
P_ANF = re.compile(r"„|“|”|``|''|\"`|\"'|(?<![\\\w=])\"(?=[A-Za-zÄÖÜäöü])")
P_EINHEIT = re.compile(r"(?<![\w$])[A-Za-z]\s=\s\d")
P_ZAHL = re.compile(r"(?<![\w.,/%-])\d+(?:[.,]\d+)*(?![\w/%-]|[.,]\d)")
P_URL = re.compile(r"\\url\{|\\href\{|https?://")
P_REF = re.compile(r"(?<![A-Za-z])\\(?:ref|autoref|pageref|vref)\{")
P_CITE_PLAIN = re.compile(r"\\(?:cite|citep|citet)\*?(?![A-Za-z])")
P_VLINE = re.compile(r"\\(?:hline|cline|vline)(?![A-Za-z])")
P_TAB_BEGIN = re.compile(r"\\begin\{(tabular\*?|tabularx|tabulary|longtable)\}")
P_WERTKONTEXT = re.compile(r"Skal|Wert|kodiert|Punkt|Gewicht|Stufe|Index|Faktor", re.I)
P_SIGNIFIKANT = re.compile(r"\bsignifikant\w*", re.IGNORECASE)


def excerpt(text, start=0, end=None, width=70):
    end = end if end is not None else start
    a = max(0, start - width)
    b = min(len(text), end + width)
    return ("…" if a > 0 else "") + text[a:b].strip() + ("…" if b < len(text) else "")


def semi_code(code):
    s = INLINE_MATH.sub(" ", code)
    s = s.replace("\\;", " ")
    for cmd in ("url", "href", "texttt", "verb", "includegraphics"):
        while True:
            i = s.find("\\" + cmd + "{")
            if i < 0:
                break
            s = s[:i] + s[group_end(s, i + len(cmd) + 1):]
    return s


def strip_cmd(s, cmd):
    while True:
        i = s.find("\\" + cmd + "{")
        if i < 0:
            return s
        s = s[:i] + " Q " + s[group_end(s, i + len(cmd) + 1):]


class Linter:
    def __init__(self, project):
        self.p = project
        self.cfg = project.config
        self.out = []
        self.seen = set()
        self.words_by_file = {}
        exc = {w.lower() for w in self.cfg.get("ausnahmen", {}).get("woerter", [])}
        self.exceptions = exc

    def emit(self, rule, line, meldung, auszug="", vorschlag=""):
        if self.p.ignored(line, rule):
            return
        key = (rule, line.file, line.no, meldung)
        if key in self.seen:
            return
        self.seen.add(key)
        b = make(self.cfg, rule, self.p.rel(line.file), line.no, meldung, auszug or line.prose or line.code.strip(), vorschlag)
        if b:
            self.out.append(b)

    def run(self):
        self.text_lines = [l for l in self.p.lines if not l.in_any(CODE_ENVS)]
        self.heading_lines = {h.line.index for h in self.p.headings}
        for check in (self.typography, self.wordlists, self.sentences_checks, self.numbers, self.lists,
                      self.terms, self.acronyms, self.emph, self.formatting, self.floats, self.refs,
                      self.structure, self.formulas, self.markers):
            check()
        for s in self.p.sentences:
            f = self.p.rel(s.line.file)
            self.words_by_file[f] = self.words_by_file.get(f, 0) + len(s.words)
        return self.out

    def typography(self):
        for ln in self.text_lines:
            if "\\tikz" in ln.code:
                continue
            sc = semi_code(ln.code)
            for m in re.finditer(";", sc):
                self.emit("TYP-SEMIKOLON", ln, "Semikolon im Text", excerpt(sc, m.start()), "Punkt und neuer Satz, Komma oder Nebensatz")
            for m in re.finditer("—|---", sc):
                self.emit("TYP-GEDANKENSTRICH", ln, "Geviertstrich als Einschub", excerpt(sc, m.start()), "Komma, Doppelpunkt oder Nebensatz")
            for m in P_HALBGEVIERT.finditer(strip_cmd(sc, "enquote")):
                self.emit("TYP-HALBGEVIERT", ln, "Halbgeviertstrich mit Leerzeichen wirkt als Gedankenstrich", excerpt(sc, m.start()), "Komma oder Nebensatz, -- nur für Bereiche")
            for m in P_ANF.finditer(sc):
                self.emit("TYP-ANFUEHRUNG", ln, f"Von Hand gesetztes Anführungszeichen {m.group(0)}", excerpt(sc, m.start()), "\\enquote{...}")
            for m in P_ABK.finditer(ln.code):
                fix = f"{m.group(1)}.\\,{m.group(3)}."
                self.emit("TYP-ABKUERZUNG", ln, f"Abkürzung {m.group(0)} ohne schmalen Abstand", excerpt(ln.code, m.start()), fix)
            for m in re.finditer(r"\d(?:\s|~)?\\%", ln.code):
                self.emit("TYP-PROZENT", ln, "Prozentzeichen ohne schmalen Abstand", excerpt(ln.code, m.start()), "15\\,\\%")
            if ln.code != ln.raw and re.search(r"\d\s?$", ln.code) and not ln.raw[len(ln.code):].startswith("%%") \
                    and not ln.in_any(TABLE_ENVS) and re.search(r"[A-Za-zÄÖÜäöü]", ln.code):
                rest = ln.raw[len(ln.code) + 1:].lstrip()
                if not rest or rest[:1].islower() or rest[:1] in ".,)":
                    self.emit("TYP-PROZENT", ln, "Unmaskiertes % nach einer Zahl beginnt einen Kommentar, der Rest der Zeile fehlt im PDF", excerpt(ln.raw, len(ln.code)), "15\\,\\%")
            for m in P_EINHEIT.finditer(sc):
                self.emit("TYP-EINHEIT", ln, "Gleichung im Fließtext ohne Mathematikmodus oder schmalen Abstand", excerpt(sc, m.start()), "$N = 40$")

    def _wordlist(self, rule, pattern, ln, text, meldung, vorschlag):
        for m in pattern.finditer(text):
            if m.group(0).lower() in self.exceptions:
                continue
            self.emit(rule, ln, meldung.format(w=m.group(0)), excerpt(text, m.start(), m.end()), vorschlag)

    def wordlists(self):
        for ln in self.text_lines:
            if not ln.prose_q:
                continue
            t = ln.prose_q
            if not ln.in_any(QUOTE_ENVS):
                self._wordlist("SPR-ICH-WIR", P_ICH, ln, t, "Ich- oder Wir-Form: {w}", "unpersönlich formulieren: Die Arbeit ..., Es wird ...")
            self._wordlist("SPR-WERTUNG", P_WERTUNG, ln, t, "Wertendes Wort: {w}", "durch Zahl, Vergleich oder Beleg ersetzen oder streichen")
            self._wordlist("SPR-SELBSTVERSTAENDLICH", P_SELBST, ln, t, "Scheinselbstverständlichkeit: {w}", "streichen oder begründen")
            self._wordlist("SPR-FLOSKEL", P_FLOSKEL, ln, t, "Floskel: {w}", "direkt aussagen oder Querverweis setzen")
            self._wordlist("SPR-FUELLWORT", P_FUELL, ln, t, "Füllwort: {w}", "streichen")
            self._wordlist("SPR-DOPPELUNG", P_DOPPEL, ln, t, "Doppelung: {w}", "eines der Wörter streichen")

    def sentences_checks(self):
        max_w = self.cfg["satz"]["max_woerter"]
        max_ns = self.cfg["satz"]["max_nebensaetze"]
        stat_cues = set(WORTLISTEN["signifikant_kontext"])
        prev = None
        for s in self.p.sentences:
            ln = s.line
            t = s.text
            n = len(s.words)
            if n > max_w:
                self.emit("SAT-LAENGE", ln, f"Satz mit {n} Wörtern (Grenze {max_w})", excerpt(t, 0, 0, 120), "an einem und oder Relativsatz teilen")
            ns = len(P_NEBENSATZ.findall(t))
            if ns > max_ns:
                self.emit("SAT-SCHACHTEL", ln, f"{ns} Nebensätze in einem Satz", excerpt(t, 0, 0, 120), "in zwei oder drei Hauptsätze aufteilen")
            m = P_GENITIV.search(t)
            if m:
                self.emit("SAT-GENITIV", ln, "Genitivkette", excerpt(t, m.start(), m.end()), "mit Verb oder Präposition auflösen")
            hedges = [h.group(0) for h in P_HEDGE.finditer(t) if h.group(0).lower() not in self.exceptions]
            if len(hedges) >= 2:
                self.emit("SPR-HEDGING", ln, "Gestapelte Einschränkungen: " + ", ".join(hedges), excerpt(t, 0, 0, 120), "eine Einschränkung klar benennen")
            if P_SIGNIFIKANT.search(t):
                toks = {w.lower() for w in s.words}
                codes = " ".join(l.code for l in s.lines)
                if not any(w.startswith(c) for w in toks for c in stat_cues) and "$p" not in codes and "\\alpha" not in codes:
                    self.emit("SPR-SIGNIFIKANT", ln, "signifikant ohne statistischen Bezug", excerpt(t, 0, 0, 120), "deutlich, erheblich oder Testergebnis nennen")
            nouns = [w for w in s.words if P_NOMEN.match(w)]
            if len(nouns) >= 6 and len(nouns) / max(n, 1) >= 0.2:
                self.emit("SPR-NOMINALSTIL", ln, f"Nominalstil: {len(nouns)} Substantivierungen ({', '.join(nouns[:5])})", excerpt(t, 0, 0, 120), "eine Substantivierung durch ein Verb ersetzen")
            if not s.has_cite and "[Verweis]" not in t:
                m = P_BELEG.search(t)
                if m:
                    self.emit("ZIT-BELEG", ln, f"Belegsignal ohne Quelle: {m.group(0)}", excerpt(t, m.start(), m.end()), "\\parencite{...} ergänzen oder \\quellefehlt{...} setzen")
            if not s.has_cite:
                m = P_MANUELL.search(t)
                if m:
                    self.emit("ZIT-MANUELL", ln, f"Von Hand gesetztes Zitat: {m.group(0)}", excerpt(t, m.start(), m.end()), "\\textcite{key} oder \\parencite{key}")
            if prev is not None and prev.lines[-1] is s.lines[0] and prev.lines[-1].file == s.lines[0].file:
                self.emit("FMT-QUELLTEXT-ZEILE", s.lines[0], "Mehrere Sätze in einer Quelltextzeile", excerpt(s.lines[0].prose, 0, 0, 100), "nach jedem Satz umbrechen")
            prev = s

    def numbers(self):
        before = set(WORTLISTEN["zahl_kennung_davor"]) | {"gewicht", "gewichte", "schwelle", "faktor", "stufen"}
        after = set(WORTLISTEN["zahl_einheit_danach"])
        for s in self.p.sentences:
            t = s.text
            toks = list(P_ZAHL.finditer(t))
            if any(not re.fullmatch(r"\d+", m.group(0)) or int(m.group(0)) > 12 for m in toks):
                continue
            if "[Formel]" in t or P_WERTKONTEXT.search(t):
                continue
            for m in toks:
                v = int(m.group(0))
                pm = re.search(r"(\S+)\s*$", t[:m.start()])
                prev_tok = pm.group(1).lower().strip("(„\"") if pm else ""
                nm = re.match(r"\s*(\S+)", t[m.end():])
                next_tok = nm.group(1).lower() if nm else ""
                if prev_tok in before or prev_tok.rstrip(".") in before or prev_tok.endswith(("-", "(")):
                    continue
                if next_tok.rstrip(".,;:)") in after or t[m.end():m.end() + 1] in ".)":
                    continue
                if prev_tok in {"bis", "und", "von", "zwischen", "oder", "–", "--"} or next_tok in {"bis", "–", "--"}:
                    continue
                if prev_tok.isupper() and len(prev_tok) <= 3:
                    continue
                line = next((l for l in s.lines if re.search(rf"(?<![\w.,]){m.group(0)}(?![\w,])", l.prose)), s.line)
                self.emit("TYP-ZAHLWORT", line, f"Zahl {v} im Fließtext", excerpt(t, m.start(), m.end()), ZAHLWORT[v])

    def lists(self):
        lines = self.p.lines
        for i, ln in enumerate(lines):
            if ln.raw.strip() == "" and ln.in_any(LIST_ENVS) and not ln.in_any(CODE_ENVS):
                nxt = next((l for l in lines[i + 1:] if l.raw.strip()), None)
                prv = next((l for l in reversed(lines[:i]) if l.raw.strip()), None)
                if nxt and prv and nxt.code.strip().startswith("\\item") and "\\begin{" not in prv.code and nxt.file == ln.file:
                    self.emit("TYP-AUFZAEHLUNG-LEER", nxt, "Leerzeile vor \\item", nxt.code.strip()[:80], "Leerzeile entfernen")

    def terms(self):
        b = self.cfg["begriffe"]
        verboten = b.get("verboten", {})
        pats = {w: word_pattern([w]) for w in verboten}
        komposita = []
        for c in b.get("komposita", []):
            parts = c.split("-")
            pat = re.compile(r"(?<![\w-])" + r"[\s-]+".join(re.escape(p) for p in parts) + r"\w*", re.IGNORECASE)
            komposita.append((c, pat))
        groups = b.get("varianten", [])
        gpats = [[(v.split("|")[0], word_pattern(v.split("|"))) for v in g] for g in groups]
        counts = [{v: [] for v, _ in g} for g in gpats]
        for ln in self.text_lines:
            t = ln.prose_q
            if not t:
                continue
            for w, pat in pats.items():
                for m in pat.finditer(t):
                    self.emit("TERM-VERBOTEN", ln, f"{m.group(0)} ist durch {verboten[w]} ersetzt", excerpt(t, m.start(), m.end()), verboten[w])
            for c, pat in komposita:
                for m in pat.finditer(t):
                    if re.search(r"\s", m.group(0)):
                        self.emit("TERM-KOMPOSITUM", ln, f"{m.group(0)} ohne Durchkopplung", excerpt(t, m.start(), m.end()), c)
            for gi, g in enumerate(gpats):
                for v, pat in g:
                    for m in pat.finditer(t):
                        counts[gi][v].append((ln, m))
        for c in counts:
            used = {v: occ for v, occ in c.items() if occ}
            if len(used) < 2:
                continue
            main = max(used, key=lambda v: len(used[v]))
            summary = ", ".join(f"{v} {len(o)}×" for v, o in sorted(used.items(), key=lambda kv: -len(kv[1])))
            for v, occ in used.items():
                if v == main:
                    continue
                for ln, m in occ[:8]:
                    self.emit("TERM-VARIANTEN", ln, f"{m.group(0)} statt {main} ({summary})", excerpt(ln.prose_q, m.start(), m.end()), main)

    def acronyms(self):
        shorts = {}
        for g in self.cfg["projekt"].get("glossar", []):
            path = self.p.root / g
            if not path.exists():
                continue
            txt = path.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"^[^%\n]*\\newacronym(?:\[[^\]]*\])?\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", txt, re.M):
                key, short = m.group(1), to_prose(m.group(2), False).replace("®", "").strip()
                if len(short) >= 2 and "." not in short and re.fullmatch(r"[A-Za-zÄÖÜ0-9-]+", short) and short != short.lower():
                    shorts[short] = key
        if not shorts:
            return
        pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(s) for s in sorted(shorts, key=len, reverse=True)) + r")s?(?![\w-])")
        for ln in self.text_lines:
            if ln.index in self.heading_lines or "\\caption" in ln.code or not ln.prose_q:
                continue
            for m in pat.finditer(ln.prose_q):
                key = shorts[m.group(1)]
                self.emit("TERM-ABKUERZUNG", ln, f"{m.group(0)} ohne \\gls", excerpt(ln.prose_q, m.start(), m.end()), f"\\gls{{{key}}}")

    def emph(self):
        seen = {}
        for ln in self.text_lines:
            i = 0
            while True:
                i = ln.code.find("\\emph{", i)
                if i < 0:
                    break
                args, _ = command_args(ln.code, i + 5)
                i += 6
                if not args:
                    continue
                term = to_prose(args[0], False).lower()
                if not term:
                    continue
                if term in seen and ln.index not in self.heading_lines:
                    first = seen[term]
                    self.emit("TERM-EMPH", ln, f"\\emph{{{args[0]}}} erneut kursiv, eingeführt in {self.p.rel(first.file)}:{first.no}", args[0], args[0])
                else:
                    seen.setdefault(term, ln)

    def formatting(self):
        for ln in self.text_lines:
            c = ln.code
            if "\\textbf" in c and not ln.in_any(TABLE_ENVS | FLOAT_ENVS) and ln.index not in self.heading_lines \
                    and not re.match(r"\s*\\item\s*\\textbf\{[^}]*\}", c):
                self.emit("FMT-FETT", ln, "Fettdruck im Fließtext", excerpt(c, c.find("\\textbf")), "Betonung über Satzbau")
            for m in P_REF.finditer(c):
                self.emit("FMT-REF", ln, "\\ref statt \\cref", excerpt(c, m.start()), "\\cref{...}")
            for m in P_CITE_PLAIN.finditer(c):
                self.emit("ZIT-BEFEHL", ln, f"{m.group(0)} statt \\textcite oder \\parencite", excerpt(c, m.start()), "\\textcite{...} oder \\parencite{...}")
            if not ln.in_any(TABLE_ENVS | FLOAT_ENVS) and "\\footnote" not in c:
                for m in P_URL.finditer(c):
                    self.emit("ZIT-URL", ln, "URL im Fließtext", excerpt(c, m.start()), "Quelle im Literaturverzeichnis oder Fußnote")
            for m in P_TAB_BEGIN.finditer(c):
                args, _ = command_args(c, m.end())
                if args and "|" in args[-1]:
                    self.emit("FMT-VLINIE", ln, "Senkrechte Linien in der Spaltendefinition", args[-1], args[-1].replace("|", ""))
            for m in P_VLINE.finditer(c):
                self.emit("FMT-VLINIE", ln, f"{m.group(0)} statt booktabs", excerpt(c, m.start()), "\\toprule, \\midrule, \\bottomrule")
            i = 0
            while True:
                i = c.find("\\enquote{", i)
                if i < 0:
                    break
                end = group_end(c, i + 8)
                content = to_prose(c[i + 9:end - 1], False)
                n = len(WORD.findall(content))
                tail = c[end:end + 160]
                nxt = self.p.lines[ln.index + 1].code if ln.index + 1 < len(self.p.lines) else ""
                cm = CITE_CMD.search(tail) or CITE_CMD.search(nxt)
                if n >= 40 and cm:
                    self.emit("ZIT-WOERTLICH", ln, f"Wörtliches Zitat mit {n} Wörtern", excerpt(content, 0, 0, 80), "paraphrasieren oder als Blockzitat setzen")
                elif n >= 8 and cm:
                    src = tail if CITE_CMD.search(tail) else nxt
                    seg = src[cm.start():cm.start() + 60]
                    if not re.search(r"\[\s*(?:S\.|p\.|pp\.|Kap\.)", seg):
                        self.emit("ZIT-WOERTLICH", ln, "Wörtliches Zitat ohne Seitenzahl", excerpt(content, 0, 0, 80), "\\parencite[S.~12]{key}")
                i = end

    def floats(self):
        for f in self.p.floats:
            if not f.caption:
                self.emit("FMT-CAPTION", f.begin, f"{f.kind} ohne \\caption", f.begin.code.strip())
            if not f.labels:
                self.emit("FMT-LABEL", f.begin, f"{f.kind} ohne \\label", f.caption[:100])
            has_cite = bool(CITE_CMD.search(f.code))
            text = to_prose(f.caption, False) + " " + to_prose(f.code, False)
            nach = re.search(r"Eigene Darstellung\s+(?:nach|in Anlehnung)|in Anlehnung an|\bnach\s*$", text, re.I)
            if nach and not has_cite:
                self.emit("FMT-ABB-QUELLE", f.begin, "Angepasste Vorlage ohne Zitat der Vorlage", f.caption[:120], "Eigene Darstellung nach \\textcite{key}")
            elif f.kind == "figure" and not re.search(r"Eigene Darstellung|Quelle\s*:", text, re.I) and not has_cite:
                self.emit("FMT-ABB-QUELLE", f.begin, "Abbildung ohne Herkunftsangabe", f.caption[:120], "Eigene Darstellung, Eigene Darstellung nach \\textcite{key} oder Quelle: \\textcite{key}")

    def refs(self):
        float_lines = {}
        for f in self.p.floats:
            for lab in f.labels:
                float_lines[lab] = {l.index for l in f.lines}
        for lab, ln in self.p.refs:
            if lab not in self.p.labels:
                self.emit("FMT-VERWEIS-UNBEKANNT", ln, f"Verweisziel {lab} existiert nicht", excerpt(ln.code, ln.code.find(lab)), "Label anlegen oder Schreibweise prüfen")
        for f in self.p.floats:
            if not f.labels:
                continue
            inside = {l.index for l in f.lines}
            outside = [ln for lab, ln in self.p.refs if lab in f.labels and ln.index not in inside]
            if not outside:
                self.emit("FMT-VERWEIS-FEHLT", f.begin, f"{', '.join(f.labels)} wird im Text nicht referenziert", f.caption[:120], f"wie \\cref{{{f.labels[0]}}} zeigt, ...")
            elif min(l.index for l in outside) > f.begin.index:
                first = min(outside, key=lambda l: l.index)
                self.emit("FMT-VERWEIS-REIHENFOLGE", f.begin, f"Erster Verweis auf {f.labels[0]} steht erst nach dem Objekt ({self.p.rel(first.file)}:{first.no})", f.caption[:120], "Verweis in den Absatz vor dem Objekt setzen")

    def structure(self):
        skip = [s.lower() for s in self.cfg["struktur"].get("ohne_strukturpruefung", [])]
        hs = self.p.headings
        chapter = ""
        for i, h in enumerate(hs):
            if h.level <= 0:
                chapter = h.title.lower()
            if h.level > 3 or any(s in chapter for s in skip):
                continue
            nxt = hs[i + 1] if i + 1 < len(hs) else None
            if nxt and nxt.level > h.level and h.sentences == 0:
                self.emit("STR-ORIENTIERUNG", h.line, f"{h.title}: Unterüberschrift folgt ohne einleitenden Text", h.title, "ein bis zwei Sätze, die Inhalt und Aufbau des Abschnitts nennen")
            elif (nxt is None or nxt.level <= h.level) and h.sentences < 3 and h.level >= 1:
                self.emit("STR-KURZ", h.line, f"{h.title}: {h.sentences} Sätze", h.title, "mit benachbartem Abschnitt zusammenführen oder ausbauen")

    def formulas(self):
        lines = self.p.lines
        i = 0
        while i < len(lines):
            ln = lines[i]
            is_math = bool(ln.envs & (MATH_ENVS | {"displaymath"}))
            if not is_math:
                i += 1
                continue
            j = i
            while j + 1 < len(lines) and lines[j + 1].envs & (MATH_ENVS | {"displaymath"}) and lines[j + 1].file == ln.file:
                j += 1
            after = " ".join(l.code for l in lines[j + 1:j + 16] if l.file == ln.file)
            around = " ".join(l.code for l in lines[max(0, i - 5):i] if l.file == ln.file) + " " + after
            later = " ".join(l.code for l in lines[j + 1:j + 35] if l.file == ln.file)
            missing = []
            if not re.search(r"\bwobei\b|\bdabei\b|bezeichne[nt]|steh(?:t|en) für|\\begin\{(?:itemize|description)\}|\bmit\b", around):
                missing.append("Erklärung der Variablen")
            if not re.search(r"Beispiel|beispielsweise|\betwa\b|ergibt sich|ergeben sich|Rechenweg", later):
                missing.append("Rechenbeispiel")
            if missing and not ln.in_any({"tikzpicture", "axis"}):
                self.emit("FORM-ERKLAERUNG", ln, "Formel ohne " + " und ".join(missing), ln.code.strip()[:100], "Variablenliste mit wobei ... und ein Beispiel mit echten Werten")
            i = j + 1

    def markers(self):
        platz = {}
        groups = [("MARK-QUELLE-FEHLT", self.cfg["marker"].get("quelle_fehlt", [])),
                  ("MARK-OFFEN", self.cfg["marker"].get("offen", []))]
        for rule, names in groups:
            for name in names:
                pat = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z])")
                for ln in self.p.lines:
                    for m in pat.finditer(ln.code):
                        rest = ln.code[m.end():]
                        k = ln.index + 1
                        while rest.count("{") > rest.count("}") and k < len(self.p.lines) and k < ln.index + 8:
                            rest += " " + self.p.lines[k].code
                            k += 1
                        args, _ = command_args(rest, 0)
                        if not args:
                            fl = next((f for f in self.p.floats if f.begin.index <= ln.index <= f.lines[-1].index), None)
                            anchor = fl.begin if fl else ln
                            key = (rule, name, anchor.index)
                            if key in platz:
                                platz[key].extra["anzahl"] += 1
                                platz[key].meldung = f"{platz[key].extra['anzahl']} Platzhalter \\{name}" + (f" in {fl.kind} {fl.labels[0] if fl.labels else ''}" if fl else "")
                                continue
                            b = make(self.cfg, rule, self.p.rel(anchor.file), anchor.no, f"1 Platzhalter \\{name}", (fl.caption[:120] if fl else ln.prose), "")
                            if b:
                                b.extra["anzahl"] = 1
                                platz[key] = b
                                self.out.append(b)
                            continue
                        text = to_prose(args[0], False)
                        b = make(self.cfg, rule, self.p.rel(ln.file), ln.no, text, ln.prose or ln.code.strip(), "")
                        if b:
                            self.out.append(b)
