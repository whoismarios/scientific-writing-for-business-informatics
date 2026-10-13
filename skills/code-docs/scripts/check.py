#!/usr/bin/env python3
"""Finds missing or stale code documentation and README facts that no longer match the project."""

import argparse
import ast
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import update  # noqa: E402

PY = "Google Python Style Guide 3.8.3"
TS = "Google TypeScript Style Guide, Comments and documentation"
RULES = {
    "DOC-MISSING": ("warning", "Public function or class without docstring or JSDoc",
                    f"{PY}, mandatory for the public API. {TS}, document all top-level exports"),
    "DOC-ARGS-MISSING": ("warning", "Multi-line docstring without Args section, or any docstring in style full",
                         f"{PY}, sections may only be left out when a one-line docstring suffices"),
    "DOC-PARAM-MISSING": ("warning", "Parameter missing from the documented parameters",
                          f"{PY}, Args lists each parameter by name"),
    "DOC-PARAM-STALE": ("error", "Documented parameter no longer exists in the signature",
                        f"{PY} and {TS}, a docstring describes the calling syntax"),
    "DOC-RETURNS-MISSING": ("hint", "Return value not documented although parameters are",
                            f"{PY}, Returns or Yields unless the summary starts with Returns or Yields"),
    "README-MISSING": ("warning", "No README in the project root", "GitHub Docs, About READMEs. Standard Readme"),
    "README-SCRIPT": ("error", "README names a script that does not exist", "Standard Readme, Install and Usage"),
    "README-PATH": ("error", "Documentation points to a path that does not exist", "code-docs convention, facts match the project"),
    "README-ENV": ("warning", "Environment variable from the example file is not documented", "Standard Readme, Usage. code-docs convention"),
    "ARCH-MISSING": ("hint", "No ARCHITECTURE.md", "Kladov (2021), ARCHITECTURE.md"),
    "ARCH-DIR": ("hint", "Top-level source folder not mentioned in ARCHITECTURE.md", "Kladov (2021), codemap"),
}

DEFAULTS = {
    "style": "google",
    "private": False,
    "min_lines": 0,
    "exclude": [],
    "architecture": "",
    "update": {"check": True, "auto": False},
}

SKIP_DIRS = {
    "node_modules", ".git", ".venv", "venv", "env", "dist", "build", ".next", "out", "coverage",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".turbo", "vendor", "site-packages",
}
DEFAULT_EXCLUDE = [
    "*/migrations/*", "*/alembic/versions/*", "*.d.ts", "*.test.*", "*.spec.*",
    "*/test_*.py", "*_test.py", "*/tests/*", "*/__tests__/*", "*/conftest.py",
]
PY_EXT = {".py"}
TS_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
REFERENCE_ONLY = {".java": "java", ".cs": "csharp", ".r": "r", ".go": "go"}
CODE_EXT = PY_EXT | TS_EXT | set(REFERENCE_ONLY) | {".kt", ".rs", ".rb", ".php", ".swift"}
DOC_SUFFIX = re.compile(
    r"\.(py|ts|tsx|js|jsx|mjs|cjs|json|toml|ya?ml|md|txt|sh|sql|css|scss|html|ini|cfg|lock|env|example|tex|bib|svg|png|jpg)$"
)
ENV_FILES = {".env.example", ".env.sample", ".env.template", ".env.local.example", "example.env"}
PM_BUILTINS = {
    "install", "i", "add", "remove", "rm", "dlx", "exec", "create", "init", "up", "update", "upgrade", "why",
    "list", "ls", "outdated", "audit", "link", "unlink", "publish", "import", "store", "setup", "env", "global",
    "config", "info", "cache", "workspace", "workspaces", "set", "dedupe", "prune", "patch",
}


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str
    message: str
    source: str = ""


def finding(file, line, rule, message):
    return Finding(file, line, rule, RULES[rule][0], message, RULES[rule][2])


def load_config(root):
    cfg = dict(DEFAULTS)
    path = root / "code-docs.toml"
    if path.exists():
        user = tomllib.loads(path.read_text(encoding="utf-8"))
        cfg.update({k: {**DEFAULTS[k], **v} if isinstance(DEFAULTS.get(k), dict) else v for k, v in user.items()})
    cfg["exclude"] = DEFAULT_EXCLUDE + list(cfg["exclude"])
    return cfg


def project_files(root, cfg):
    """Lists project files relative to root, honoring .gitignore when the project is a Git repository."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.splitlines()
        rels = [Path(p) for p in out]
    except (OSError, subprocess.CalledProcessError):
        rels = [p.relative_to(root) for p in root.rglob("*") if p.is_file()]
    result = []
    for rel in rels:
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if any(fnmatch.fnmatch("/" + rel.as_posix(), pat) for pat in cfg["exclude"]):
            continue
        if (root / rel).is_file():
            result.append(rel)
    return sorted(result)


def changed_files(root, rev):
    run = lambda *args: subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout
    names = run("diff", "--name-only", "--relative", rev).splitlines()
    names += run("ls-files", "--others", "--exclude-standard").splitlines()
    return {Path(n) for n in names}


# Python

SECTION = re.compile(
    r"^(Args|Arguments|Parameters|Returns|Return|Yields|Yield|Raises|Attributes|Examples?|Notes?|Todo|See Also|Warnings?):\s*$"
)
SKIP_DECORATORS = {"overload", "override"}
PROPERTY_DECORATORS = {"property", "cached_property", "setter", "getter", "deleter"}


def sections(doc):
    out, current = {}, None
    for line in doc.splitlines():
        m = SECTION.match(line)
        if m:
            current = m.group(1)
            out[current] = []
        elif current:
            out[current].append(line)
    return out


def documented_names(lines):
    names, indent = set(), None
    for line in lines:
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip())
        indent = depth if indent is None else indent
        if depth == indent:
            m = re.match(r"\s*\*{0,2}(\w+)\s*(?:\([^)]*\))?\s*:", line)
            if m:
                names.add(m.group(1))
    return names


def decorator_names(node):
    names = set()
    for d in node.decorator_list:
        d = d.func if isinstance(d, ast.Call) else d
        if isinstance(d, ast.Attribute):
            names.add(d.attr)
        elif isinstance(d, ast.Name):
            names.add(d.id)
    return names


def own_nodes(fn):
    stack = list(fn.body)
    while stack:
        node = stack.pop()
        yield node
        stack.extend(
            c for c in ast.iter_child_nodes(node)
            if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda))
        )


def returns_value(fn):
    ann = fn.returns
    if ann is not None:
        if isinstance(ann, ast.Constant) and ann.value is None:
            return False
        return not (isinstance(ann, ast.Name) and ann.id in {"None", "NoReturn", "Never"})
    return any(
        (isinstance(n, ast.Return) and n.value is not None and not (isinstance(n.value, ast.Constant) and n.value.value is None))
        or isinstance(n, (ast.Yield, ast.YieldFrom))
        for n in own_nodes(fn)
    )


def body_lines(node):
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if not body:
        return 0
    return body[-1].end_lineno - body[0].lineno + 1


def check_python_signature(rel, fn, doc, in_class, style):
    out = []
    args = fn.args
    params = [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]
    if args.vararg:
        params.append(args.vararg.arg)
    if args.kwarg:
        params.append(args.kwarg.arg)
    if in_class and params and params[0] in {"self", "cls"}:
        params = params[1:]
    params = [p for p in params if p != "_"]
    secs = sections(doc)
    arg_lines = secs.get("Args") or secs.get("Arguments") or secs.get("Parameters")
    one_line = len(doc.strip().splitlines()) == 1
    strict = style == "full" or (style == "google" and not one_line)
    if arg_lines is None:
        if params and strict:
            out.append(finding(rel, fn.lineno, "DOC-ARGS-MISSING", f"{fn.name}: no Args section for {', '.join(params)}"))
    else:
        named = documented_names(arg_lines)
        for p in params:
            if p not in named and style != "summary":
                out.append(finding(rel, fn.lineno, "DOC-PARAM-MISSING", f"{fn.name}: {p} not in Args"))
        for n in sorted(named - set(params)):
            out.append(finding(rel, fn.lineno, "DOC-PARAM-STALE", f"{fn.name}: Args lists {n}, which is not a parameter"))
    summary = doc.strip().splitlines()[0] if doc.strip() else ""
    has_returns = any(k in secs for k in ("Returns", "Return", "Yields", "Yield"))
    if strict and returns_value(fn) and not has_returns and not re.match(r"(Returns?|Yields?)\b", summary):
        out.append(finding(rel, fn.lineno, "DOC-RETURNS-MISSING", f"{fn.name}: no Returns section"))
    return out


def python_findings(root, rel, cfg):
    try:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=str(rel))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return []
    out = []
    file = rel.as_posix()

    def visit(node, private, in_class):
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            name = child.name
            if name.startswith("__") and name.endswith("__"):
                continue
            decos = decorator_names(child)
            if decos & SKIP_DECORATORS:
                continue
            is_private = private or name.startswith("_")
            is_class = isinstance(child, ast.ClassDef)
            if is_class:
                visit(child, is_private, True)
            if is_private and not cfg["private"]:
                continue
            doc = ast.get_docstring(child)
            if doc is None:
                if body_lines(child) >= cfg["min_lines"]:
                    kind = "class" if is_class else "function"
                    out.append(finding(file, child.lineno, "DOC-MISSING", f"{kind} {name}"))
                continue
            if not is_class and not decos & PROPERTY_DECORATORS:
                out.extend(check_python_signature(file, child, doc, in_class, cfg["style"]))

    visit(tree, False, False)
    return out


# TypeScript and JavaScript

TS_DECL = re.compile(
    r"^[ \t]*export\s+(?:default\s+)?(?:declare\s+)?"
    r"(?:(?:abstract\s+)?class\s+(?P<cls>[\w$]+)"
    r"|(?:async\s+)?function\s*\*?\s*(?P<fn>[\w$]*)"
    r"|const\s+(?P<const>[\w$]+)\s*(?::[^=\n]+)?=\s*(?:async\s+)?(?=function\b|\(|<|[\w$]+\s*=>))",
    re.M,
)
JSDOC_PARAM = re.compile(r"@param\s+(?:\{[^}]*\}\s+)?\[?([\w$]+)")
NO_RETURN_TYPE = re.compile(r"^(void|never|undefined|Promise<\s*void\s*>)$")
OPEN, CLOSE = "([{<", ")]}>"


def matching(text, start):
    """Returns the index after the bracket that closes the one at start, or -1."""
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c in OPEN:
            depth += 1
        elif c in CLOSE and not (c == ">" and text[i - 1] == "="):
            depth -= 1
            if depth == 0:
                return i + 1
    return -1


def split_params(text):
    parts, depth, cur = [], 0, ""
    for i, c in enumerate(text):
        if c in OPEN:
            depth += 1
        elif c in CLOSE and not (c == ">" and i and text[i - 1] == "="):
            depth -= 1
        if c == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def jsdoc_above(lines, idx):
    i = idx - 1
    while i >= 0 and lines[i].strip().startswith("@"):
        i -= 1
    if i < 0 or not lines[i].rstrip().endswith("*/"):
        return None
    end = i
    while i >= 0 and "/**" not in lines[i]:
        if "/*" in lines[i] and "/**" not in lines[i]:
            return None
        i -= 1
    return "\n".join(lines[i:end + 1]) if i >= 0 else None


def jsdoc_summary(doc):
    for line in doc.splitlines():
        text = line.strip().removeprefix("/**").removesuffix("*/").strip().lstrip("*").strip()
        if text and not text.startswith("@"):
            return text
    return ""


def ts_findings(root, rel, cfg):
    try:
        text = (root / rel).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    lines = text.splitlines()
    file = rel.as_posix()
    out = []
    for m in TS_DECL.finditer(text):
        no = text.count("\n", 0, m.start()) + 1
        name = m.group("cls") or m.group("fn") or m.group("const") or "default"
        is_class = m.group("cls") is not None
        doc = jsdoc_above(lines, no - 1)
        params_text, ret_type, body = None, None, 1
        bare = re.match(r"([\w$]+)\s*=>", text[m.end():]) if m.group("const") else None
        if bare:
            params_text = bare.group(1)
        elif not is_class:
            open_at = text.find("(", m.end())
            close_at = matching(text, open_at) if open_at >= 0 else -1
            if close_at > 0:
                params_text = text[open_at + 1:close_at - 1]
                rest = text[close_at:close_at + 400]
                rt = re.match(r"\s*:\s*(.+?)\s*(?:\{|=>)", rest, re.S)
                ret_type = rt.group(1).strip() if rt else None
                brace = text.find("{", close_at)
                arrow_expr = re.match(r"\s*(?::[^=]+)?=>\s*[^{\s]", rest)
                if brace >= 0 and not arrow_expr:
                    end = matching(text, brace)
                    if end > 0:
                        body = text.count("\n", brace, end) + 1
        else:
            brace = text.find("{", m.end())
            end = matching(text, brace) if brace >= 0 else -1
            body = text.count("\n", brace, end) + 1 if end > 0 else 1
        if doc is None:
            if body >= cfg["min_lines"]:
                out.append(finding(file, no, "DOC-MISSING", f"{'class' if is_class else 'function'} {name}"))
            continue
        if is_class or params_text is None:
            continue
        style = cfg["style"]
        params, destructured = [], False
        for p in split_params(params_text):
            p = re.sub(r"^(?:\.\.\.|readonly\s+|public\s+|private\s+|protected\s+)+", "", p)
            if p[:1] in "{[":
                destructured = True
                continue
            pm = re.match(r"[\w$]+", p)
            if pm and pm.group(0) != "this":
                params.append(pm.group(0))
        named = set(JSDOC_PARAM.findall(doc))
        if not named and (params or destructured):
            if style == "full":
                out.append(finding(file, no, "DOC-ARGS-MISSING", f"{name}: no @param tags"))
        elif named:
            for p in params:
                if p not in named and style != "summary":
                    out.append(finding(file, no, "DOC-PARAM-MISSING", f"{name}: {p} has no @param"))
            if not destructured:
                for n in sorted(named - set(params)):
                    out.append(finding(file, no, "DOC-PARAM-STALE", f"{name}: @param {n} is not a parameter"))
        has_returns = re.search(r"@returns?\b", doc)
        strict = style == "full" or (style == "google" and named)
        if strict and ret_type and not NO_RETURN_TYPE.match(ret_type) and not has_returns and not re.match(r"Returns?\b", jsdoc_summary(doc)):
            out.append(finding(file, no, "DOC-RETURNS-MISSING", f"{name}: no @returns"))
    return out


# README and ARCHITECTURE

def doc_files(files):
    return [f for f in files if re.fullmatch(r"(readme|architecture)(\.[a-z_-]+)?\.md", f.name.lower())]


def package_scripts(root, files):
    scripts, found = set(), False
    for f in files:
        if f.name == "package.json":
            found = True
            try:
                scripts |= set(json.loads((root / f).read_text(encoding="utf-8")).get("scripts", {}))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    return scripts if found else None


def make_targets(root, files):
    targets, found = set(), False
    for f in files:
        if f.name in {"Makefile", "makefile", "GNUmakefile"}:
            found = True
            targets |= set(re.findall(r"^([\w.-]+)\s*:(?!=)", (root / f).read_text(encoding="utf-8"), re.M))
    return targets if found else None


SCRIPT_CALL = re.compile(
    r"\b(?:npm|bun)\s+run\s+([\w:.-]+)|\bnpm\s+(start|test)\b|\b(?:pnpm|yarn)\s+(?:run\s+)?([\w:.-]+)|\bmake\s+([\w.-]+)"
)


def script_findings(root, files, docs):
    out = []
    scripts, targets = package_scripts(root, files), make_targets(root, files)
    for d in docs:
        for no, line in enumerate((root / d).read_text(encoding="utf-8").splitlines(), 1):
            for m in SCRIPT_CALL.finditer(line):
                npm = m.group(1) or m.group(2) or m.group(3)
                if npm and scripts is not None and npm not in scripts and npm not in PM_BUILTINS and not npm.startswith("-"):
                    out.append(finding(d.as_posix(), no, "README-SCRIPT", f"script {npm} not in any package.json"))
                if m.group(4) and targets is not None and m.group(4) not in targets:
                    out.append(finding(d.as_posix(), no, "README-SCRIPT", f"make target {m.group(4)} not in Makefile"))
    return out


def env_findings(root, files, docs):
    documented = "\n".join((root / d).read_text(encoding="utf-8") for d in docs)
    out = []
    for f in files:
        if f.name not in ENV_FILES:
            continue
        for no, line in enumerate((root / f).read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=", line)
            if m and not re.search(rf"\b{m.group(1)}\b", documented):
                out.append(finding(f.as_posix(), no, "README-ENV", f"{m.group(1)} not mentioned in README or ARCHITECTURE"))
    return out


def path_like(token, link):
    if not token or any(c in token for c in " <>{}$*~|\"'`,;()") or "://" in token:
        return False
    if token.startswith(("#", "mailto:", "/", "-", "@", "http")):
        return False
    if link:
        return True
    if "/" not in token.rstrip("/"):
        return False
    return token.startswith(("./", "../")) or token.endswith("/") or bool(DOC_SUFFIX.search(token))


def local_only(root, rel, names):
    """Whether a path is a file each person creates locally, such as .env next to .env.example."""
    stem, dot, ext = rel.name.partition(".") if not rel.name.startswith(".") else (rel.name, "", "")
    variants = {f"{rel.name}.{s}" for s in ("example", "sample", "template", "dist")}
    variants |= {f"{stem}.{s}.{ext}" for s in ("example", "sample", "template")} if dot else set()
    if variants & names:
        return True
    try:
        return subprocess.run(["git", "check-ignore", "-q", rel.as_posix()], cwd=root).returncode == 0
    except OSError:
        return False


def path_findings(root, files, docs):
    names = {f.name for f in files} | {p.name for f in files for p in f.parents}
    out = []
    for d in docs:
        fenced = False
        for no, line in enumerate((root / d).read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
                continue
            if fenced:
                continue
            tokens = [(t, False) for t in re.findall(r"`([^`]+)`", line)]
            tokens += [(t, True) for t in re.findall(r"\]\(([^)\s]+)\)", line)]
            for token, link in tokens:
                token = token.split("#")[0].split("?")[0]
                if not path_like(token, link):
                    continue
                target = token.rstrip("/")
                bases = [root / d.parent, root]
                if any((b / target).exists() for b in bases) or (not link and "/" not in target and target in names):
                    continue
                head = target.removeprefix("./").split("/")[0]
                if not link and not target.startswith("../") and not any((b / head).exists() for b in bases):
                    continue
                if local_only(root, d.parent / target, names):
                    continue
                out.append(finding(d.as_posix(), no, "README-PATH", f"{token} does not exist"))
    return out


def architecture_findings(root, files, cfg):
    candidates = [Path(cfg["architecture"])] if cfg["architecture"] else [
        f for f in files if f.name.lower() == "architecture.md" and len(f.parts) <= 2
    ]
    arch = next((c for c in candidates if (root / c).exists()), None)
    if arch is None:
        return [finding("ARCHITECTURE.md", 0, "ARCH-MISSING", "no overview of modules and data flow")]
    text = (root / arch).read_text(encoding="utf-8")
    dirs = sorted({f.parts[0] for f in files if len(f.parts) > 1 and f.suffix.lower() in CODE_EXT and not f.parts[0].startswith(".")})
    return [
        finding(arch.as_posix(), 1, "ARCH-DIR", f"{d}/ not mentioned")
        for d in dirs if not re.search(rf"(?<![\w-]){re.escape(d)}(?![\w-])", text)
    ]


def run_checks(root, only=None, since=None, overrides=None):
    root = root.resolve()
    cfg = {**load_config(root), **(overrides or {})}
    files = project_files(root, cfg)
    scope = changed_files(root, since) if since else None
    areas = set(only or ["code", "readme", "arch"])
    findings = []
    if "code" in areas:
        for f in files:
            if scope is not None and f not in scope:
                continue
            if f.suffix in PY_EXT:
                findings += python_findings(root, f, cfg)
            elif f.suffix in TS_EXT:
                findings += ts_findings(root, f, cfg)
    docs = doc_files(files)
    if "readme" in areas:
        if not any(f.name.lower() == "readme.md" and len(f.parts) == 1 for f in files):
            findings.append(finding("README.md", 0, "README-MISSING", "add a README with purpose, setup and usage"))
        findings += script_findings(root, files, docs) + env_findings(root, files, docs) + path_findings(root, files, docs)
    if "arch" in areas:
        findings += architecture_findings(root, files, cfg)
    order = {"error": 0, "warning": 1, "hint": 2}
    findings.sort(key=lambda f: (order[f.severity], f.file, f.line, f.rule))
    return cfg, files, findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".", help="project root, default is the current directory")
    ap.add_argument("--only", help="comma-separated areas: code, readme, arch")
    ap.add_argument("--since", help="limit code findings to files changed since this Git revision")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--rules", action="store_true", help="list rule IDs with severity and title")
    a = ap.parse_args()
    if a.rules:
        for rule, (sev, title, source) in RULES.items():
            print(f"{rule:<20} {sev:<8} {title}\n{'':<29} {source}")
        return
    root = Path(a.root)
    cfg, files, findings = run_checks(root, a.only.split(",") if a.only else None, a.since)
    st = update.status(cfg["update"])
    unchecked = {}
    for f in files:
        ext = f.suffix.lower()
        if ext in CODE_EXT - PY_EXT - TS_EXT:
            unchecked[ext] = unchecked.get(ext, 0) + 1
    if a.json:
        print(json.dumps({"config": {k: cfg[k] for k in ("style", "private", "min_lines")}, "update": st,
                          "unchecked": {e: {"files": n, "reference": REFERENCE_ONLY.get(e)} for e, n in unchecked.items()},
                          "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=1))
        return
    counts = {s: sum(f.severity == s for f in findings) for s in ("error", "warning", "hint")}
    print(f"code-docs: {len(files)} files, style {cfg['style']}, "
          f"{counts['error']} errors, {counts['warning']} warnings, {counts['hint']} hints")
    for f in findings:
        print(f"{f.severity:<8} {f.rule:<20} {f.file}:{f.line}  {f.message}")
    if unchecked:
        print("not checked mechanically: " + ", ".join(
            f"{n} {e}" + (f" (see references/{REFERENCE_ONLY[e]}.md)" if e in REFERENCE_ONLY else " (no reference)")
            for e, n in sorted(unchecked.items())))
    print(update.describe(st))


if __name__ == "__main__":
    sys.exit(main())
