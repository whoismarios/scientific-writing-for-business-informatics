"""Lädt Regelwerk und Projektkonfiguration und stellt das Befundformat bereit."""

import hashlib
import re
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REGELWERK = tomllib.loads((SKILL_DIR / "regelwerk.toml").read_text(encoding="utf-8"))
RULES = {r["id"]: r for r in REGELWERK["regel"]}
WORTLISTEN = REGELWERK["wortlisten"]
FARBEN = REGELWERK["farben"]
ABKUERZUNGEN = set(WORTLISTEN["abkuerzungen"])
SCHWERE_RANG = {"Fehler": 0, "Offen": 1, "Warnung": 2, "Hinweis": 3}

DEFAULT_CONFIG = {
    "projekt": {"main": "src/Main.tex", "bib": [], "glossar": [], "titel": ""},
    "marker": {"quelle_fehlt": ["quellefehlt"], "offen": ["offen", "platz"]},
    "satz": {"max_woerter": 35, "max_nebensaetze": 2},
    "struktur": {"ohne_strukturpruefung": ["Anhang"]},
    "begriffe": {"verboten": {}, "varianten": [], "komposita": []},
    "schwere": {},
    "projektregeln": [],
    "ausnahmen": {"woerter": []},
}


def load_config(root, erkannt=None):
    """Liest lektorat.toml aus dem Projektwurzelverzeichnis, sonst die erkannten Werte, und ergänzt Standardwerte."""
    path = Path(root) / "lektorat.toml"
    cfg = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else (erkannt or {})
    for val in list(cfg.values()):
        if isinstance(val, dict) and "projektregeln" in val and "projektregeln" not in cfg:
            cfg["projektregeln"] = val.pop("projektregeln")
    merged = {}
    for key, default in DEFAULT_CONFIG.items():
        val = cfg.get(key, default)
        merged[key] = {**default, **val} if isinstance(default, dict) else val
    for key, val in cfg.items():
        merged.setdefault(key, val)
    return merged


def word_pattern(entries):
    """Baut aus einer Wortliste mit Platzhalter * einen Regex mit Wortgrenzen."""
    parts = []
    for e in sorted(entries, key=len, reverse=True):
        p = re.escape(e).replace(r"\*", r"\w*").replace(r"\ ", r"\s+")
        parts.append(p)
    return re.compile(r"(?<![\w-])(?:" + "|".join(parts) + r")(?![\w-])", re.IGNORECASE)


@dataclass
class Befund:
    regel: str
    schwere: str
    datei: str
    zeile: int
    meldung: str
    auszug: str = ""
    vorschlag: str = ""
    quelle: str = "linter"
    farbe: str = ""
    titel: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def fingerprint(self):
        norm = re.sub(r"\s+", " ", (self.auszug or self.meldung).lower()).strip()[:120]
        return hashlib.sha1(f"{self.regel}|{self.datei}|{norm}".encode()).hexdigest()[:16]

    def as_dict(self):
        d = asdict(self)
        d["fingerprint"] = self.fingerprint
        return d


def make(config, regel, datei, zeile, meldung, auszug="", vorschlag="", quelle="linter"):
    """Erzeugt einen Befund mit Schwere und Farbe aus dem Regelwerk, oder None wenn abgeschaltet."""
    meta = RULES.get(regel, {})
    schwere = config.get("schwere", {}).get(regel, meta.get("schwere", "Hinweis"))
    if schwere == "aus":
        return None
    return Befund(regel, schwere, datei, zeile, meldung, auszug[:240], vorschlag, quelle,
                  meta.get("farbe", "stil"), meta.get("titel", regel))


def from_dict(d, config):
    """Übernimmt einen Befund aus JSON (z.B. von einem Gutachter-Agenten) und ergänzt Metadaten."""
    regel = d.get("regel", "AGENT")
    meta = RULES.get(regel, {})
    schwere = config.get("schwere", {}).get(regel, d.get("schwere") or meta.get("schwere", "Hinweis"))
    if schwere == "aus":
        return None
    return Befund(regel, schwere, d.get("datei", ""), int(d.get("zeile") or 0), d.get("meldung", ""),
                  d.get("auszug", ""), d.get("vorschlag", ""), d.get("quelle", "agent"),
                  meta.get("farbe", d.get("farbe", "struktur")), meta.get("titel", regel))
