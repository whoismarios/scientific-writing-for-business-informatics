"""Condenses findings into a history entry, a chat summary and a self-contained HTML report."""

import html
import json
from collections import Counter
from pathlib import Path

from ruleset import RULESET, RULES, SEVERITY_RANK

WEIGHTS = {"Fehler": 5.0, "Warnung": 2.0, "Hinweis": 0.5, "Offen": 0.0}
COLOR_NAMES = {"source": "Quelle fehlt", "open": "Offen", "evidence": "Beleg", "style": "Stil", "structure": "Struktur", "none": "Bibliografie, Quelltext und Abgabe"}


def index(findings, words):
    """Weighted findings per 1,000 words. Markers and environment checks do not count."""
    s = sum(WEIGHTS.get(b.severity, 0) for b in findings if RULES.get(b.rule, {}).get("check") != "environment")
    return round(s / max(words, 1) * 1000, 1)


LEGACY_HISTORY_KEYS = {"zeit": "time", "regelwerk": "ruleset", "woerter": "words", "schwere": "severity", "regeln": "rules",
                       "agenten": "agents", "befunde": "findings", "regel": "rule", "datei": "file", "zeile": "line",
                       "meldung": "message"}


def load_history(text):
    """Parses a history entry, accepting the German keys of older versions."""
    def fix(d):
        return {LEGACY_HISTORY_KEYS.get(k, k): v for k, v in d.items()}
    entry = fix(json.loads(text))
    entry["findings"] = [fix(b) for b in entry.get("findings", [])]
    return entry


def history_entry(meta, findings, agents):
    c = Counter(b.severity for b in findings)
    return {
        "time": meta["time"],
        "ruleset": meta["ruleset"],
        "words": meta["words"],
        "index": index(findings, meta["words"]),
        "severity": dict(c),
        "rules": dict(Counter(b.rule for b in findings)),
        "agents": agents,
        "findings": [{"fp": b.fingerprint, "rule": b.rule, "file": b.file, "line": b.line, "message": b.message[:160],
                     "severity": b.severity} for b in findings],
    }


def diff(entry, prev):
    if not prev:
        return None, None
    now = {b["fp"] for b in entry["findings"]}
    before = {b["fp"]: b for b in prev["findings"]}
    added = now - set(before)
    fixed = [b for fp, b in before.items() if fp not in now]
    return added, fixed


def render_summary(meta, findings, agents, entry, prev):
    c = Counter(b.severity for b in findings)
    lines = [f"## Lektorat {meta['time'][:16].replace('T', ' ')}", "",
             f"Lektoratsindex **{entry['index']}** (gewichtete Befunde je 1.000 Wörter, niedriger ist besser)"
             + (f", vorher {prev['index']}" if prev else ""),
             f"{meta['words']} Wörter" + (f" in der Auswahl {meta['selection']}" if meta.get("selection") else f", {meta['sentences']} Sätze, {len(meta['files'])} Dateien"), "",
             "| Fehler | Warnung | Hinweis | Offen |", "|---:|---:|---:|---:|",
             f"| {c.get('Fehler', 0)} | {c.get('Warnung', 0)} | {c.get('Hinweis', 0)} | {c.get('Offen', 0)} |"]
    added, fixed = diff(entry, prev)
    if added is not None:
        lines += ["", f"Seit dem letzten Lauf: {len(fixed)} behoben, {len(added)} neu."]
    if agents:
        lines += ["", "Gutachter: " + ", ".join(f"{k} {v}" for k, v in agents.items())]
    top = Counter(b.rule for b in findings if b.severity in {"Fehler", "Warnung"}).most_common(8)
    if top:
        lines += ["", "Häufigste Fehler und Warnungen: " + ", ".join(f"`{r}` {n}×" for r, n in top)]
    return "\n".join(lines)


def _e(s):
    return html.escape(str(s or ""))


def sparkline(history):
    vals = [h["index"] for h in history][-30:]
    if len(vals) < 2:
        return ""
    w, h = 320, 64
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pts = [(i * (w - 16) / (len(vals) - 1) + 8, h - 10 - (v - lo) / span * (h - 22)) for i, v in enumerate(vals)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5"><title>{v}</title></circle>' for (x, y), v in zip(pts, vals))
    return f'<svg class="spark" viewBox="0 0 {w} {h}" role="img" aria-label="Verlauf des Lektoratsindex"><path d="{path}"/>{dots}</svg>'


def render_html(cfg, meta, findings, agents, history, prev):
    entry = history[-1] if history else history_entry(meta, findings, agents)
    added, fixed = diff(entry, prev)
    c = Counter(b.severity for b in findings)
    order = {f: i for i, f in enumerate(meta["files"])}
    findings = sorted(findings, key=lambda b: (order.get(b.file, 999), b.file, b.line, SEVERITY_RANK.get(b.severity, 9)))
    marker = [b for b in findings if b.severity == "Offen"]
    rest = [b for b in findings if b.severity != "Offen"]
    groups = {}
    for b in rest:
        groups.setdefault(b.file, []).append(b)

    def row(b):
        r = RULES.get(b.rule, {})
        is_new = added is not None and b.fingerprint in added
        src = "agent" if b.source.startswith("agent") else b.source
        return (
            f'<li class="f" data-s="{_e(b.severity)}" data-c="{_e(b.color)}" data-q="{_e(src)}" data-n="{int(is_new)}">'
            f'<div class="fh"><span class="sev s-{_e(b.severity)}">{_e(b.severity)}</span>'
            f'<span class="dot c-{_e(b.color)}" title="{_e(COLOR_NAMES.get(b.color, b.color))}"></span>'
            f'<code class="rid" title="{_e(r.get("why", ""))}">{_e(b.rule)}</code>'
            f'<span class="loc">Zeile {b.line}</span>'
            + (f'<span class="tag">{_e(b.source)}</span>' if b.source not in {"linter", "bib"} else "")
            + ('<span class="tag new">neu</span>' if is_new else "")
            + f'</div><p class="msg">{_e(b.message)}</p>'
            + (f'<p class="ex">{_e(b.excerpt)}</p>' if b.excerpt and b.excerpt != b.message else "")
            + (f'<p class="fix">→ {_e(b.suggestion)}</p>' if b.suggestion else "")
            + "</li>"
        )

    sections = []
    for file, items in groups.items():
        cc = Counter(b.severity for b in items)
        badge = " ".join(f'<span class="mini s-{k}">{cc[k]}</span>' for k in ("Fehler", "Warnung", "Hinweis") if cc.get(k))
        sections.append(f'<details class="grp" open><summary><span class="fn">{_e(file)}</span>{badge}</summary>'
                        f'<ul>{"".join(row(b) for b in items)}</ul></details>')

    marker_rows = "".join(
        f'<tr><td><span class="dot c-{_e(b.color)}"></span></td><td>{_e(Path(b.file).name)}:{b.line}</td><td>{_e(b.message)}</td></tr>'
        for b in marker)
    fixed_html = ""
    if fixed:
        items = "".join(f'<li><code>{_e(b["rule"])}</code> {_e(Path(b["file"]).name)}:{b["line"]} {_e(b["message"])}</li>' for b in fixed[:300])
        fixed_html = f'<details class="grp"><summary><span class="fn">Seit dem letzten Lauf behoben</span><span class="mini ok">{len(fixed)}</span></summary><ul class="plain">{items}</ul></details>'

    rule_counts = Counter(b.rule for b in rest)
    rule_rows = "".join(
        f'<tr><td><code>{_e(r)}</code></td><td>{_e(RULES.get(r, {}).get("title", ""))}</td><td>{n}</td></tr>'
        for r, n in sorted(rule_counts.items(), key=lambda kv: (SEVERITY_RANK.get(RULES.get(kv[0], {}).get("severity"), 9), -kv[1])))
    title = cfg["project"].get("title") or "Arbeit"
    delta = ""
    if prev:
        d = round(entry["index"] - prev["index"], 1)
        delta = f'<span class="delta {"good" if d < 0 else "bad" if d > 0 else ""}">{"+" if d > 0 else ""}{d}</span>'

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lektoratsbericht</title>
<style>
:root{{--bg:#f7f6f2;--card:#fff;--ink:#1d1d1b;--mute:#6b6a64;--line:#e4e2da;--sev-error:#b42318;--sev-warning:#b54708;--sev-hint:#475467;--sev-open:#c4320a;
--c-source:#d92d20;--c-open:#e8590c;--c-evidence:#c11574;--c-style:#2a5bd7;--c-structure:#7a3fc4;--c-none:#98a2b3;--good:#067647;--bad:#b42318}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151513;--card:#1e1e1b;--ink:#ecebe6;--mute:#a3a29b;--line:#33322e;--sev-error:#f97066;--sev-warning:#fdb022;--sev-hint:#98a2b3;
--c-source:#f97066;--c-open:#fd853a;--c-evidence:#ee46bc;--c-style:#6f9cf5;--c-structure:#b692f6;--good:#47cd89;--bad:#f97066}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:980px;margin:0 auto;padding:32px 16px 80px}}
h1{{font:600 28px/1.2 ui-serif,Georgia,serif;margin:0 0 4px}}h2{{font:600 18px/1.3 ui-serif,Georgia,serif;margin:36px 0 12px}}
.sub{{color:var(--mute);margin:0 0 24px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}
.kpi b{{display:block;font:600 26px/1.1 ui-serif,Georgia,serif}}.kpi span{{color:var(--mute);font-size:13px}}
.kpi.idx b{{font-size:32px}}.delta{{font-size:14px;margin-left:6px}}.delta.good{{color:var(--good)}}.delta.bad{{color:var(--bad)}}
.spark{{width:100%;height:64px;margin-top:6px}}.spark path{{fill:none;stroke:var(--ink);stroke-width:1.5}}.spark circle{{fill:var(--ink)}}
.bar{{position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;display:flex;flex-wrap:wrap;gap:6px;border-bottom:1px solid var(--line)}}
.bar button{{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:99px;padding:4px 11px;cursor:pointer}}
.bar button[aria-pressed=false]{{opacity:.45}}.bar input{{flex:1;min-width:160px;font:inherit;font-size:13px;padding:4px 10px;border:1px solid var(--line);border-radius:99px;background:var(--card);color:var(--ink)}}
.grp{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden}}
.grp summary{{padding:10px 14px;cursor:pointer;display:flex;gap:8px;align-items:center;font-weight:600}}.fn{{flex:1;overflow-wrap:anywhere}}
ul{{list-style:none;margin:0;padding:0}}.f{{border-top:1px solid var(--line);padding:10px 14px}}
.fh{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}}
.sev{{font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}}.s-Fehler{{color:var(--sev-error)}}.s-Warnung{{color:var(--sev-warning)}}.s-Hinweis{{color:var(--sev-hint)}}.s-Offen{{color:var(--sev-open)}}
.mini{{font-size:12px;border-radius:99px;padding:1px 8px;border:1px solid currentColor}}.mini.ok{{color:var(--good)}}
.dot{{width:10px;height:10px;border-radius:3px;display:inline-block}}.c-source{{background:var(--c-source)}}.c-open{{background:var(--c-open)}}.c-evidence{{background:var(--c-evidence)}}.c-style{{background:var(--c-style)}}.c-structure{{background:var(--c-structure)}}.c-none{{background:var(--c-none)}}
.rid{{font-size:12px;cursor:help}}.loc{{color:var(--mute)}}.tag{{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:0 6px;color:var(--mute)}}.tag.new{{color:var(--bad);border-color:currentColor}}
.msg{{margin:4px 0 0}}.ex{{margin:4px 0 0;color:var(--mute);font-family:ui-serif,Georgia,serif;font-style:italic;overflow-wrap:anywhere}}.fix{{margin:4px 0 0;font-size:14px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:14px}}
td,th{{padding:7px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:top}}tr:first-child td{{border-top:0}}
.plain li{{padding:6px 14px;border-top:1px solid var(--line);font-size:14px}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--mute);margin-top:10px}}
footer{{margin-top:40px;color:var(--mute);font-size:13px}}
</style></head><body><main>
<h1>Lektoratsbericht</h1>
<p class="sub">{_e(title)} · {_e(meta['time'][:16].replace('T', ' '))} · Regelwerk {_e(RULESET['meta']['version'])} · {meta['words']} Wörter in {len(meta['files'])} Dateien</p>
<div class="kpis">
<div class="kpi idx"><b>{entry['index']}{delta}</b><span>Lektoratsindex, gewichtete Befunde je 1.000 Wörter</span>{sparkline(history)}</div>
<div class="kpi"><b class="s-Fehler">{c.get('Fehler', 0)}</b><span>Fehler</span></div>
<div class="kpi"><b class="s-Warnung">{c.get('Warnung', 0)}</b><span>Warnungen</span></div>
<div class="kpi"><b class="s-Hinweis">{c.get('Hinweis', 0)}</b><span>Hinweise</span></div>
<div class="kpi"><b class="s-Offen">{c.get('Offen', 0)}</b><span>offene Marker</span></div>
</div>
<div class="legend">{''.join(f'<span><span class="dot c-{k}"></span> {v}</span>' for k, v in COLOR_NAMES.items())}</div>
<p class="sub" style="margin-top:12px">Gewichte: Fehler 5, Warnung 2, Hinweis 0,5. Marker zählen nicht. {('Gutachter: ' + ', '.join(f'{k} ({v})' for k, v in agents.items())) if agents else 'Nur mechanische Prüfung, ohne Gutachter-Agenten.'}</p>

<h2>Offene Marker ({len(marker)})</h2>
<table>{marker_rows or '<tr><td>Keine offenen Marker.</td></tr>'}</table>

<h2>Befunde ({len(rest)})</h2>
<div class="bar" id="bar">
<button data-f="s" data-v="Fehler" aria-pressed="true">Fehler</button><button data-f="s" data-v="Warnung" aria-pressed="true">Warnung</button><button data-f="s" data-v="Hinweis" aria-pressed="true">Hinweis</button>
<button data-f="c" data-v="evidence" aria-pressed="true">Beleg</button><button data-f="c" data-v="style" aria-pressed="true">Stil</button><button data-f="c" data-v="structure" aria-pressed="true">Struktur</button><button data-f="c" data-v="none" aria-pressed="true">Bibliografie</button>
<button data-f="q" data-v="agent" aria-pressed="true">Gutachter</button><button data-f="n" data-v="1" aria-pressed="false">nur neue</button>
<input type="search" id="q" placeholder="Suche in Befunden">
</div>
{fixed_html}
{''.join(sections)}

<h2>Befunde je Regel</h2>
<table>{rule_rows}</table>
<footer>Erzeugt mit thesis-editor. Regel-IDs zeigen beim Überfahren die Begründung. Ausnahmen im Quelltext mit <code>% thesis-editor: ignore REGEL-ID</code>.</footer>
</main>
<script>
const st={{s:new Set(["Fehler","Warnung","Hinweis"]),c:new Set(["evidence","style","structure","none"]),q:true,n:false}};
const q=document.getElementById("q");
function apply(){{const t=q.value.toLowerCase();document.querySelectorAll(".f").forEach(e=>{{
const ok=st.s.has(e.dataset.s)&&st.c.has(e.dataset.c)&&(st.q||e.dataset.q!=="agent")&&(!st.n||e.dataset.n==="1")&&(!t||e.textContent.toLowerCase().includes(t));
e.style.display=ok?"":"none";}});
document.querySelectorAll("details.grp").forEach(g=>{{const any=[...g.querySelectorAll(".f")].some(e=>e.style.display!=="none");if(g.querySelector(".f"))g.style.display=any?"":"none";}});}}
document.querySelectorAll("#bar button").forEach(b=>b.addEventListener("click",()=>{{const on=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",on);
const f=b.dataset.f,v=b.dataset.v;if(f==="s"||f==="c"){{on?st[f].add(v):st[f].delete(v);}}else{{st[f]=on;}}apply();}}));
q.addEventListener("input",apply);
</script></body></html>"""
