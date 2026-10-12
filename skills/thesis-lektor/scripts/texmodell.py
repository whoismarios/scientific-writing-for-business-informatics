"""Liest ein LaTeX-Projekt ein und bildet Zeilen, Absätze, Sätze, Überschriften, Gleitobjekte und Verweise ab."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from regelwerk import ABKUERZUNGEN

CODE_ENVS = {
    "tikzpicture", "axis", "groupplot", "verbatim", "verbatim*", "lstlisting", "minted", "comment",
    "equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*",
    "displaymath", "math", "flalign", "flalign*", "alignat", "alignat*", "filecontents", "Verbatim",
}
FLOAT_ENVS = {"figure", "figure*", "table", "table*", "wrapfigure", "sidewaystable", "sidewaysfigure"}
TABLE_ENVS = {"tabular", "tabular*", "tabularx", "tabulary", "longtable", "tblr", "longtblr"}
QUOTE_ENVS = {"quote", "quotation", "verse"}
LIST_ENVS = {"itemize", "enumerate", "description"}
MATH_ENVS = {e for e in CODE_ENVS if e.rstrip("*") in {
    "equation", "align", "gather", "multline", "displaymath", "math", "flalign", "alignat"}}
HEADINGS = {"part": -1, "chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}

CITE_CMD = re.compile(
    r"\\(?:[Tt]extcites?|[Pp]arencites?|[Cc]ites?|[Ff]ootcites?|[Ff]ullcite|[Aa]utocites?|[Ss]martcites?"
    r"|citeauthor|citeyear|citetitle|citep|citet|nocite|supercite)\*?(?![A-Za-z])"
)
TEXTCITE = re.compile(r"^(?:[Tt]extcites?|[Cc]iteauthor)$")
REF_CMD = re.compile(r"\\(?:[Cc]ref|[Cc]pageref|labelcref|namecref|ref|autoref|pageref|vref|eqref)\*?\{([^}]*)\}")
LABEL_CMD = re.compile(r"\\label\{([^}]*)\}")
BEGIN_END = re.compile(r"\\(begin|end)\{([^}]+)\}")
HEADING_CMD = re.compile(r"^\s*\\(part|chapter|section|subsection|subsubsection|paragraph)\*?\s*(?:\[[^\]]*\])?\s*\{")
INPUT_CMD = re.compile(r"\\(?:input|include|subfile)\{([^}]+)\}")
INLINE_MATH = re.compile(r"(?<!\\)\$(?:\\.|[^$\\])+\$|\\\((?:.|\n)*?\\\)")
WORD = re.compile(r"[0-9A-Za-zÄÖÜäöüß]+(?:[-'’][0-9A-Za-zÄÖÜäöüß]+)*")
DISPLAY_OPEN = re.compile(r"(?<!\\)\\\[")
DISPLAY_CLOSE = re.compile(r"(?<!\\)\\\]")
IGNORE_LINE = re.compile(r"%\s*lektorat:\s*ignore(?!-)\s*([A-Z0-9,\- ]*)")
IGNORE_FILE = re.compile(r"%\s*lektorat:\s*ignore-file\s*([A-Z0-9,\- ]*)")

DROP_ALL = {
    "label", "cref", "Cref", "ref", "autoref", "pageref", "vref", "eqref", "cpageref", "Cpageref", "labelcref",
    "input", "include", "includegraphics", "begin", "end", "hspace", "vspace", "url", "href", "path",
    "newcommand", "renewcommand", "definecolor", "setlength", "addtocounter", "setcounter", "bibliography",
    "printbibliography", "addbibresource", "glsaddallunused", "phantomsection", "addcontentsline",
    "centering", "small", "footnotesize", "scriptsize", "normalsize", "large", "Large", "noindent",
    "toprule", "midrule", "bottomrule", "cmidrule", "hline", "newline", "linebreak", "pagebreak",
    "clearpage", "newpage", "item", "texttt", "verb", "textcolor", "color", "rowcolor",
    "multicolumn", "multirow", "resizebox", "scalebox", "makebox", "hfill", "vfill", "quad", "qquad",
}
REPLACE = {
    "gls": "[Abk]", "Gls": "[Abk]", "glspl": "[Abk]", "Glspl": "[Abk]", "acrshort": "[Abk]", "acrlong": "[Abk]",
    "acrfull": "[Abk]", "glsentryshort": "[Abk]", "glsentrylong": "[Abk]", "glsdesc": "[Abk]",
    "texttt": "[Code]", "verb": "[Code]", "url": "[URL]", "href": "[URL]", "path": "[Code]",
    "cref": "[Verweis]", "Cref": "[Verweis]", "ref": "[Verweis]", "autoref": "[Verweis]", "eqref": "[Verweis]", "pageref": "[Verweis]",
}


@dataclass
class Line:
    file: Path
    no: int
    raw: str
    code: str
    envs: frozenset
    index: int
    ignores: set = field(default_factory=set)
    prose: str = ""
    prose_q: str = ""

    def in_any(self, names):
        return bool(self.envs & names)


@dataclass
class Sentence:
    text: str
    lines: list
    has_cite: bool

    @property
    def line(self):
        return self.lines[0]

    @property
    def words(self):
        return WORD.findall(self.text)


@dataclass
class Heading:
    level: int
    title: str
    line: Line
    sentences: int = 0
    starred: bool = False


@dataclass
class Float:
    kind: str
    begin: Line
    lines: list
    labels: list = field(default_factory=list)
    caption: str = ""


def strip_comment(line):
    """Entfernt einen Kommentar ab dem ersten nicht maskierten Prozentzeichen."""
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\":
            i += 2
            continue
        if c == "%":
            return line[:i]
        i += 1
    return line


def group_end(s, i):
    """Index nach der zu s[i] passenden schließenden Klammer, oder len(s) bei offener Gruppe."""
    open_c = s[i]
    close_c = "}" if open_c == "{" else "]"
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return len(s)


def skip_args(s, i, limit=None):
    """Überspringt Stern, optionale und Pflichtargumente ab Position i."""
    n = 0
    while i < len(s):
        k = i
        while k < len(s) and s[k] in " \t":
            k += 1
        if k < len(s) and s[k] == "*" and n == 0:
            i = k + 1
            continue
        if k < len(s) and s[k] in "{[":
            if limit is not None and s[k] == "{" and n >= limit:
                break
            end = group_end(s, k)
            if s[k] == "{":
                n += 1
            i = end
            continue
        break
    return i


def command_args(s, i):
    """Liefert die Inhalte aller direkt folgenden {}-Gruppen ab Position i."""
    args = []
    while i < len(s):
        k = i
        while k < len(s) and s[k] in " \t":
            k += 1
        if k < len(s) and s[k] in "{[":
            end = group_end(s, k)
            if s[k] == "{":
                args.append(s[k + 1:end - 1])
            i = end
            continue
        break
    return args, i


def to_prose(code, mask_quotes):
    """Wandelt eine Quelltextzeile in lesbaren Text ohne Befehle, Mathematik und Verweise."""
    s = INLINE_MATH.sub(" [Formel] ", code)
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            j = i + len(m.group(0))
            if name == ",":
                i = j
                continue
            if name in {"%", "&", "_", "#", "$"}:
                out.append(name)
                i = j
                continue
            if name in {"\\", " ", ";", ":", "!", "/"}:
                out.append(" ")
                i = j
                continue
            if name == "enquote" and mask_quotes:
                out.append(" [Zitat] ")
                i = skip_args(s, j)
                continue
            if CITE_CMD.match(s, i):
                out.append(" [Autor] " if TEXTCITE.match(name) else " ")
                i = skip_args(s, j)
                continue
            if name in REPLACE:
                out.append(" " + REPLACE[name] + " ")
                i = skip_args(s, j)
                continue
            if name in DROP_ALL:
                i = skip_args(s, j)
                if name == "item":
                    out.append(" ")
                continue
            if name in {"quellefehlt", "offen", "platz"}:
                i = skip_args(s, j, limit=1)
                continue
            k = j
            while k < len(s) and s[k] == "[":
                k = group_end(s, k)
            i = k
            continue
        if c == "~":
            out.append(" ")
        elif c not in "{}":
            out.append(c)
        i += 1
    return re.sub(r"\s+", " ", "".join(out)).strip()


def parse_ignores(raw):
    m = IGNORE_LINE.search(raw)
    if not m:
        return None
    ids = {x.strip() for x in m.group(1).replace(" ", ",").split(",") if x.strip()}
    return ids or {"*"}


class Project:
    """Ein LaTeX-Projekt ab \\begin{document} der Hauptdatei, mit aufgelösten \\input-Befehlen."""

    def __init__(self, root, config):
        self.root = Path(root)
        self.config = config
        self.main = (self.root / config["projekt"]["main"]).resolve()
        self.src = self.main.parent
        self.files = []
        self.lines = []
        self.file_ignores = {}
        self.parent = {}
        self._read(self.main, top=True)
        self._analyse()

    def rel(self, path):
        try:
            return str(Path(path).resolve().relative_to(self.root.resolve()))
        except ValueError:
            return str(path)

    def _resolve(self, name):
        p = (self.src / name)
        if p.suffix != ".tex":
            p = p.with_suffix(p.suffix + ".tex") if p.suffix else p.with_suffix(".tex")
        return p if p.exists() else None

    def _read(self, path, top=False, envs=None, parent=None):
        if path in self.files:
            return
        self.files.append(path)
        self.parent[path] = parent
        text = path.read_text(encoding="utf-8", errors="replace")
        raws = text.splitlines()
        fid = set()
        for r in raws:
            m = IGNORE_FILE.search(r)
            if m:
                fid |= {x.strip() for x in m.group(1).replace(" ", ",").split(",") if x.strip()} or {"*"}
        self.file_ignores[path] = fid
        started = not top
        stack = list(envs or [])
        pending_ignore = set()
        display = False
        for no, raw in enumerate(raws, 1):
            code = strip_comment(raw)
            if not started:
                if "\\begin{document}" in code:
                    started = True
                continue
            if top and "\\end{document}" in code:
                break
            opened = []
            for m in BEGIN_END.finditer(code):
                kind, name = m.groups()
                if kind == "begin":
                    opened.append(name)
            current = set(stack) | set(opened)
            opens_display = DISPLAY_OPEN.search(code)
            if display or opens_display:
                current.add("displaymath")
            ign = parse_ignores(raw) or set()
            line = Line(path, no, raw, code, frozenset(current), len(self.lines), ign | pending_ignore)
            pending_ignore = ign if code.strip() == "" and ign else set()
            self.lines.append(line)
            for m in BEGIN_END.finditer(code):
                kind, name = m.groups()
                if kind == "begin":
                    stack.append(name)
                elif name in stack:
                    idx = len(stack) - 1 - stack[::-1].index(name)
                    stack.pop(idx)
            if opens_display and not DISPLAY_CLOSE.search(code, opens_display.end()):
                display = True
            elif display and DISPLAY_CLOSE.search(code):
                display = False
            for m in INPUT_CMD.finditer(code):
                sub = self._resolve(m.group(1))
                if sub:
                    self._read(sub, envs=stack, parent=path)

    def select(self, pattern):
        """Dateien, deren Pfad passt, samt allen darin eingebundenen Dateien."""
        rx = re.compile(pattern)
        out = set()
        for f in self.files:
            p = f
            while p is not None:
                if rx.search(self.rel(p)):
                    out.add(self.rel(f))
                    break
                p = self.parent.get(p)
        return out

    def ignored(self, line, rule):
        fi = self.file_ignores.get(line.file, set())
        return "*" in line.ignores or rule in line.ignores or "*" in fi or rule in fi

    def _analyse(self):
        for ln in self.lines:
            if ln.in_any(CODE_ENVS):
                continue
            ln.prose = to_prose(ln.code, mask_quotes=False)
            ln.prose_q = to_prose(ln.code, mask_quotes=True)
        self._headings()
        self._floats()
        self._labels_refs()
        self._sentences()

    def _headings(self):
        self.headings = []
        for ln in self.lines:
            m = HEADING_CMD.match(ln.code)
            if m and not ln.in_any(CODE_ENVS | FLOAT_ENVS):
                start = m.end() - 1
                title = ln.code[start + 1:group_end(ln.code, start) - 1]
                self.headings.append(Heading(HEADINGS[m.group(1)], to_prose(title, False), ln, starred="*" in ln.code[:m.end()]))

    def _floats(self):
        self.floats = []
        open_floats = []
        for ln in self.lines:
            for m in BEGIN_END.finditer(ln.code):
                kind, name = m.groups()
                if kind == "begin" and name in FLOAT_ENVS:
                    open_floats.append(Float(name.rstrip("*"), ln, []))
                elif kind == "end" and name in FLOAT_ENVS and open_floats:
                    f = open_floats.pop()
                    f.lines.append(ln)
                    self.floats.append(f)
            for f in open_floats:
                if not f.lines or f.lines[-1] is not ln:
                    f.lines.append(ln)
        for f in self.floats:
            code = "\n".join(l.code for l in f.lines)
            f.labels = LABEL_CMD.findall(code)
            i = code.find("\\caption")
            if i >= 0:
                j = i + len("\\caption")
                while j < len(code) and code[j] in " \t\n":
                    j += 1
                if j < len(code) and code[j] == "[":
                    j = group_end(code, j)
                    while j < len(code) and code[j] in " \t\n":
                        j += 1
                if j < len(code) and code[j] == "{":
                    f.caption = code[j + 1:group_end(code, j) - 1]
            f.code = code
        self.floats.sort(key=lambda f: f.begin.index)

    def _labels_refs(self):
        self.labels = {}
        self.refs = []
        float_of = {}
        for f in self.floats:
            for lab in f.labels:
                float_of[lab] = f
        for ln in self.lines:
            for lab in LABEL_CMD.findall(ln.code):
                self.labels.setdefault(lab, (ln, float_of.get(lab)))
            for m in REF_CMD.finditer(ln.code):
                for lab in m.group(1).split(","):
                    lab = lab.strip()
                    if lab:
                        self.refs.append((lab, ln))

    def _sentences(self):
        self.sentences = []
        self.paragraphs = []
        para = []
        heading_idx = {h.line.index: h for h in self.headings}
        current_heading = None

        def flush():
            nonlocal para
            if para:
                self.paragraphs.append(para)
                sents = split_sentences(para)
                self.sentences.extend(sents)
                if current_heading is not None:
                    current_heading.sentences += len(sents)
            para = []

        prev_file = None
        for ln in self.lines:
            if ln.file != prev_file:
                flush()
                prev_file = ln.file
            if ln.index in heading_idx:
                flush()
                current_heading = heading_idx[ln.index]
                continue
            if ln.in_any(CODE_ENVS | FLOAT_ENVS | TABLE_ENVS | QUOTE_ENVS):
                flush()
                continue
            stripped = ln.code.strip()
            if not stripped:
                if ln.raw.strip() == "":
                    flush()
                continue
            if re.match(r"\\(begin|end)\{", stripped) or stripped.startswith("\\item"):
                flush()
            if not ln.prose:
                continue
            para.append(ln)
        flush()


def split_sentences(lines):
    """Teilt einen Absatz in Sätze und ordnet jedem Satz seine Quelltextzeilen zu."""
    text = ""
    spans = []
    for ln in lines:
        if text:
            text += " "
        spans.append((len(text), len(text) + len(ln.prose), ln))
        text += ln.prose
    cuts = []
    for m in re.finditer(r"[.!?](?=[\"“”)\]]?\s+[\"„(\[]?[A-ZÄÖÜ0-9])", text):
        before = text[:m.start() + 1]
        tok = re.search(r"(\S+)$", before).group(1).lower().lstrip("(„\"")
        if tok in ABKUERZUNGEN or any(tok.endswith(a) and len(a) > 2 for a in ABKUERZUNGEN):
            continue
        if re.fullmatch(r"\d{1,2}\.", tok) or re.fullmatch(r"[a-zäöü]\.", tok):
            continue
        cuts.append(m.end())
    out = []
    start = 0
    for end in cuts + [len(text)]:
        seg = text[start:end].strip()
        if seg:
            seg_lines = [ln for a, b, ln in spans if a < end and b > start]
            has_cite = any(CITE_CMD.search(l.code) or "\\quellefehlt" in l.code for l in seg_lines)
            out.append(Sentence(seg, seg_lines, has_cite))
        start = end
    return out
