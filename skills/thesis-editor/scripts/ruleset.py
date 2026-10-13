"""Loads the rule set and the project configuration and defines the finding format."""

import hashlib
import re
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
RULESET = tomllib.loads((SKILL_DIR / "rules.toml").read_text(encoding="utf-8"))
RULES = {r["id"]: r for r in RULESET["rule"]}
WORDLISTS = RULESET["wordlists"]
COLORS = RULESET["colors"]
ABBREVIATIONS = set(WORDLISTS["abbreviations"])
SEVERITY_RANK = {"Fehler": 0, "Offen": 1, "Warnung": 2, "Hinweis": 3}
OUT_DIR = ".thesis-editor"
CONFIG_NAMES = ("thesis-editor.toml", "thesis-lektor.toml", "lektorat.toml")

DEFAULT_CONFIG = {
    "project": {"main": "src/Main.tex", "bib": [], "glossary": [], "title": ""},
    "markers": {"missing_source": ["quellefehlt"], "open": ["offen"]},
    "sentences": {"max_words": 35, "max_clauses": 2},
    "structure": {"skip_sections": ["Anhang"]},
    "terms": {"forbidden": {}, "variants": [], "compounds": []},
    "severity": {},
    "project_rules": [],
    "exceptions": {"words": []},
}


LEGACY_KEYS = {
    "projekt": ("project", {"titel": "title", "glossar": "glossary"}),
    "marker": ("markers", {"quelle_fehlt": "missing_source", "offen": "open"}),
    "satz": ("sentences", {"max_woerter": "max_words", "max_nebensaetze": "max_clauses"}),
    "struktur": ("structure", {"ohne_strukturpruefung": "skip_sections"}),
    "begriffe": ("terms", {"verboten": "forbidden", "varianten": "variants", "komposita": "compounds"}),
    "schwere": ("severity", {}),
    "ausnahmen": ("exceptions", {"woerter": "words"}),
    "forschungsfragen": ("research_questions", {}),
    "git": ("git", {"pruefen": "enabled", "sichtbarkeit_pruefen": "check_visibility"}),
}


def _normalize(cfg):
    """Accepts the German keys of older configs and moves a misplaced project_rules key to the top level."""
    out = {}
    for key, val in cfg.items():
        name, sub = LEGACY_KEYS.get(key, (key, {}))
        if isinstance(val, dict):
            val = {sub.get(k, k): v for k, v in val.items()}
            for k in ("project_rules", "projektregeln"):
                if k in val:
                    out.setdefault("project_rules", val.pop(k))
        out["project_rules" if name == "projektregeln" else name] = val
    if isinstance(out.get("severity"), dict):
        out["severity"] = {k: ("off" if str(v).lower() in {"off", "aus"} else v) for k, v in out["severity"].items()}
    return out


def config_path(root):
    """Path of the project config, or None."""
    return next((Path(root) / n for n in CONFIG_NAMES if (Path(root) / n).exists()), None)


def load_config(root, detected=None):
    """Reads thesis-editor.toml from the project root, otherwise the detected values, and fills in defaults."""
    path = config_path(root)
    cfg = _normalize(tomllib.loads(path.read_text(encoding="utf-8"))) if path else (detected or {})
    merged = {}
    for key, default in DEFAULT_CONFIG.items():
        val = cfg.get(key, default)
        merged[key] = {**default, **val} if isinstance(default, dict) else val
    for key, val in cfg.items():
        merged.setdefault(key, val)
    return merged


def word_pattern(entries):
    """Builds a regex with word boundaries from a word list with * wildcards."""
    parts = []
    for e in sorted(entries, key=len, reverse=True):
        p = re.escape(e).replace(r"\*", r"\w*").replace(r"\ ", r"\s+")
        parts.append(p)
    return re.compile(r"(?<![\w-])(?:" + "|".join(parts) + r")(?![\w-])", re.IGNORECASE)


LEGACY_FINDING_KEYS = {"regel": "rule", "schwere": "severity", "datei": "file", "zeile": "line", "meldung": "message",
                       "auszug": "excerpt", "vorschlag": "suggestion", "quelle": "source", "farbe": "color", "titel": "title"}
SEVERITY_ALIASES = {"error": "Fehler", "warning": "Warnung", "info": "Hinweis", "hint": "Hinweis", "open": "Offen"}


@dataclass
class Finding:
    rule: str
    severity: str
    file: str
    line: int
    message: str
    excerpt: str = ""
    suggestion: str = ""
    source: str = "linter"
    color: str = ""
    title: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def fingerprint(self):
        norm = re.sub(r"\s+", " ", (self.excerpt or self.message).lower()).strip()[:120]
        return hashlib.sha1(f"{self.rule}|{self.file}|{norm}".encode()).hexdigest()[:16]

    def as_dict(self):
        d = asdict(self)
        d["fingerprint"] = self.fingerprint
        return d


def make(config, rule, file, line, message, excerpt="", suggestion="", source="linter"):
    """Creates a finding with severity and color from the rule set, or None if the rule is turned off."""
    meta = RULES.get(rule, {})
    severity = config.get("severity", {}).get(rule, meta.get("severity", "Hinweis"))
    if severity == "off":
        return None
    return Finding(rule, severity, file, line, message, excerpt[:240], suggestion, source,
                  meta.get("color", "style"), meta.get("title", rule))


def from_dict(d, config):
    """Reads a finding from JSON (for example from a reviewer agent) and adds metadata. Accepts English and legacy German keys."""
    d = {LEGACY_FINDING_KEYS.get(k, k): v for k, v in d.items()}
    rule = d.get("rule", "AGENT")
    meta = RULES.get(rule, {})
    severity = SEVERITY_ALIASES.get(str(d.get("severity", "")).lower(), d.get("severity"))
    severity = config.get("severity", {}).get(rule, severity or meta.get("severity", "Hinweis"))
    if severity == "off":
        return None
    return Finding(rule, severity, d.get("file", ""), int(d.get("line") or 0), d.get("message", ""),
                  d.get("excerpt", ""), d.get("suggestion", ""), d.get("source", "agent"),
                  meta.get("color", d.get("color", "structure")), meta.get("title", rule))
