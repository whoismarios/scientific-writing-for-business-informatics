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


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#161b26;--mute:#5f6777;--faint:#8a92a1;--line:#e3e6eb;--soft:#f0f2f5;--acc:#3b4cca;--accbg:#eef0fb;--red:#b42318;--redbg:#fdf2f1;--redline:#f3cfcb;--onacc:#fff;--shadow:0 1px 2px rgba(22,27,38,.04),0 2px 8px rgba(22,27,38,.04);
--c-source:#c4473c;--c-open:#c98a3a;--c-evidence:#a8578f;--c-style:#5470c6;--c-structure:#7d68b8;--c-none:#a3aab5;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0f1218;--card:#161a22;--ink:#e6e8ec;--mute:#a0a7b4;--faint:#727a88;--line:#272c36;--soft:#1d222b;--acc:#9aa6ff;--accbg:#1f2440;--red:#f4877d;--redbg:#2a1715;--redline:#4a2622;--onacc:#0f1218;--shadow:none;
--c-source:#e07d73;--c-open:#d9a865;--c-evidence:#c98bb6;--c-style:#8aa0e6;--c-structure:#a796d6;--c-none:#6f7684;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
h1,h2,button,summary,.kpi,.lbl,.sev,.mini,.count,.eyebrow{font-family:Montserrat,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:40px 16px 96px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:0 0 4px}
h1{font-size:28px;line-height:1.2;font-weight:700;letter-spacing:-.01em;margin:0 0 6px}
h2{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:700;margin:40px 0 14px}
h2 .cnt{font-size:12px;font-weight:600;color:var(--mute);background:var(--soft);border-radius:99px;padding:2px 9px}
.sub{color:var(--mute);margin:0 0 24px}.note{color:var(--mute);font-size:13px;margin:12px 0 0}
.kpis{display:grid;grid-template-columns:2fr repeat(4,1fr);gap:12px;align-items:start}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}
.kpi b{display:block;font-size:28px;line-height:1;font-weight:700;font-variant-numeric:tabular-nums}.kpi span{display:block;color:var(--mute);font-size:13px;font-weight:500;margin-top:6px}
.kpi.idx b{font-size:34px}.kpi.alert b{color:var(--red)}
.kpi .delta{display:inline;font-size:14px;font-weight:600;margin-left:8px;color:var(--mute)}.delta.bad{color:var(--red)}
.spark{width:100%;height:56px;margin-top:10px}.spark path{fill:none;stroke:var(--acc);stroke-width:1.6}.spark circle{fill:var(--acc)}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--mute);margin-top:14px}.legend>span{display:inline-flex;align-items:center;gap:6px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}.c-source{background:var(--c-source)}.c-open{background:var(--c-open)}.c-evidence{background:var(--c-evidence)}.c-style{background:var(--c-style)}.c-structure{background:var(--c-structure)}.c-none{background:var(--c-none)}
.bar{position:sticky;top:0;z-index:2;margin:0 -16px;padding:12px 16px;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center}
.grpb{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.lbl{font-size:11px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--faint);margin-right:2px}
.bar button{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:6px 11px;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.bar button:hover{border-color:var(--faint)}.bar button:focus-visible,.bar input:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.bar button[aria-pressed=true]{background:var(--accbg);border-color:transparent;color:var(--acc)}
.bar button[aria-pressed=false]{background:transparent;color:var(--faint);text-decoration:line-through}
.bar button.toggle[aria-pressed=false]{text-decoration:none;color:var(--ink);background:var(--card);border-color:var(--line)}.bar button.toggle[aria-pressed=true]{background:var(--acc);color:var(--onacc)}
.bar input{flex:1;min-width:180px;font:inherit;font-size:13px;padding:7px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
.count{margin-left:auto;font-size:13px;font-weight:600;color:var(--mute);font-variant-numeric:tabular-nums}
.grp{background:var(--card);border:1px solid var(--line);border-radius:14px;margin:12px 0;overflow:hidden;box-shadow:var(--shadow)}
.grp>summary{padding:12px 18px;cursor:pointer;display:flex;gap:8px;align-items:center;font-weight:600;font-size:14px;list-style:none}.grp>summary::-webkit-details-marker{display:none}
.grp>summary:after{content:"";width:7px;height:7px;border-right:2px solid var(--faint);border-bottom:2px solid var(--faint);transform:rotate(45deg);margin:0 4px 3px 6px;transition:transform .2s}.grp[open]>summary:after{transform:rotate(-135deg);margin-bottom:-3px}
.fn{flex:1;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
ul{list-style:none;margin:0;padding:0}.f{border-top:1px solid var(--line);padding:12px 18px}
.fh{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}
.sev{display:inline-flex;align-items:center;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;border-radius:6px;padding:3px 7px;border:1px solid var(--line);color:var(--mute)}
.sev.s-Fehler{background:var(--redbg);border-color:var(--redline);color:var(--red)}.sev.s-Warnung{color:var(--ink)}.sev.s-Hinweis{border-color:transparent;background:var(--soft)}.sev.s-Offen{border-style:dashed}
.mini{font-size:12px;font-weight:600;border-radius:6px;padding:2px 7px;background:var(--soft);color:var(--mute)}.mini.s-Fehler{background:var(--redbg);color:var(--red)}.mini.s-Warnung{color:var(--ink)}
.rid{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mute);cursor:help}.loc{color:var(--faint)}
.tag{font-size:11px;font-weight:600;border:1px solid var(--line);border-radius:6px;padding:1px 6px;color:var(--mute)}.tag.new{color:var(--acc);border-color:var(--acc)}
.msg{margin:6px 0 0}.ex{margin:4px 0 0;color:var(--mute);font-style:italic;overflow-wrap:anywhere}.fix{margin:6px 0 0;font-size:14px;color:var(--mute)}.fix b{color:var(--acc);font-weight:600}
table{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;font-size:14px;box-shadow:var(--shadow)}
td,th{padding:9px 14px;border-top:1px solid var(--line);text-align:left;vertical-align:top}tr:first-child td{border-top:0}td code{font-size:12px;color:var(--mute)}td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
.plain li{padding:8px 18px;border-top:1px solid var(--line);font-size:14px;color:var(--mute)}
footer{margin-top:48px;color:var(--faint);font-size:13px}
@media (max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.kpi.idx{grid-column:1/-1}.bar{position:static}.count{margin-left:0}h1{font-size:23px}}
@media print{body{background:#fff}.bar{display:none}.grp,.kpi,table{box-shadow:none;break-inside:avoid}}
"""

JS = """
const st={s:new Set(["Fehler","Warnung","Hinweis"]),c:new Set(["evidence","style","structure","none"]),q:true,n:false};
const q=document.getElementById("q"),count=document.getElementById("count"),all=document.querySelectorAll(".f:not(.m)");
function apply(){const t=q.value.toLowerCase();let n=0;all.forEach(e=>{
const ok=st.s.has(e.dataset.s)&&st.c.has(e.dataset.c)&&(st.q||e.dataset.q!=="agent")&&(!st.n||e.dataset.n==="1")&&(!t||e.textContent.toLowerCase().includes(t));
e.style.display=ok?"":"none";n+=ok;});
document.querySelectorAll("details.grp").forEach(g=>{if(g.querySelector(".f"))g.style.display=[...g.querySelectorAll(".f")].some(e=>e.style.display!=="none")?"":"none";});
count.textContent=n+" von "+all.length+" Befunden";}
document.querySelectorAll("#bar button").forEach(b=>b.addEventListener("click",()=>{const on=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",on);
const f=b.dataset.f,v=b.dataset.v;if(f==="s"||f==="c"){on?st[f].add(v):st[f].delete(v);}else{st[f]=on;}apply();}));
q.addEventListener("input",apply);apply();
"""

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
            + (f'<p class="fix"><b>Vorschlag:</b> {_e(b.suggestion)}</p>' if b.suggestion else "")
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
        fixed_html = f'<details class="grp"><summary><span class="fn">Seit dem letzten Lauf behoben</span><span class="mini">{len(fixed)}</span></summary><ul class="plain">{items}</ul></details>'

    rule_counts = Counter(b.rule for b in rest)
    rule_rows = "".join(
        f'<tr><td><code>{_e(r)}</code></td><td>{_e(RULES.get(r, {}).get("title", ""))}</td><td class="num">{n}</td></tr>'
        for r, n in sorted(rule_counts.items(), key=lambda kv: (SEVERITY_RANK.get(RULES.get(kv[0], {}).get("severity"), 9), -kv[1])))
    title = cfg["project"].get("title") or "Arbeit"
    delta = ""
    if prev:
        d = round(entry["index"] - prev["index"], 1)
        delta = f'<span class="delta{" bad" if d > 0 else ""}">{"+" if d > 0 else ""}{d}</span>'

    sev = lambda k: f'<span class="sev s-{k}">{k}</span>'
    btn = lambda f, v, label, on="true", cls="": f'<button data-f="{f}" data-v="{v}" aria-pressed="{on}"{f' class="{cls}"' if cls else ""}>{label}</button>'
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lektoratsbericht</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap">
<style>{CSS}</style></head><body><main>
<p class="eyebrow">thesis-editor</p>
<h1>Lektoratsbericht</h1>
<p class="sub">{_e(title)} · {_e(meta['time'][:16].replace('T', ' '))} · Regelwerk {_e(RULESET['meta']['version'])} · {meta['words']} Wörter in {len(meta['files'])} Dateien</p>
<div class="kpis">
<div class="kpi idx"><b>{entry['index']}{delta}</b><span>Lektoratsindex, gewichtete Befunde je 1.000 Wörter, niedriger ist besser</span>{sparkline(history)}</div>
<div class="kpi{" alert" if c.get('Fehler') else ""}"><b>{c.get('Fehler', 0)}</b><span>Fehler</span></div>
<div class="kpi"><b>{c.get('Warnung', 0)}</b><span>Warnungen</span></div>
<div class="kpi"><b>{c.get('Hinweis', 0)}</b><span>Hinweise</span></div>
<div class="kpi"><b>{c.get('Offen', 0)}</b><span>offene Marker</span></div>
</div>
<div class="legend"><span class="lbl">Farben im PDF</span>{''.join(f'<span><span class="dot c-{k}"></span>{v}</span>' for k, v in COLOR_NAMES.items())}</div>
<p class="note">Gewichte: Fehler 5, Warnung 2, Hinweis 0,5. Marker zählen nicht. {('Gutachter: ' + ', '.join(f'{k} ({v})' for k, v in agents.items())) if agents else 'Nur mechanische Prüfung, ohne Gutachter-Agenten.'}</p>

<h2>Offene Marker<span class="cnt">{len(marker)}</span></h2>
<table>{marker_rows or '<tr><td>Keine offenen Marker.</td></tr>'}</table>

<h2>Befunde<span class="cnt">{len(rest)}</span></h2>
<div class="bar" id="bar">
<div class="grpb"><span class="lbl">Schwere</span>{btn("s", "Fehler", "Fehler")}{btn("s", "Warnung", "Warnung")}{btn("s", "Hinweis", "Hinweis")}</div>
<div class="grpb"><span class="lbl">Art</span>{btn("c", "evidence", "Beleg")}{btn("c", "style", "Stil")}{btn("c", "structure", "Struktur")}{btn("c", "none", "Bibliografie")}</div>
<div class="grpb"><span class="lbl">Quelle</span>{btn("q", "agent", "Gutachter")}{btn("n", "1", "nur neue", "false", "toggle")}</div>
<input type="search" id="q" placeholder="Suche in Befunden"><span class="count" id="count" aria-live="polite"></span>
</div>
{fixed_html}
{''.join(sections)}

<h2>Befunde je Regel</h2>
<table>{rule_rows}</table>
<footer>Erzeugt mit thesis-editor. Regel-IDs zeigen beim Überfahren die Begründung. Ausnahmen im Quelltext mit <code>% thesis-editor: ignore REGEL-ID</code>.</footer>
</main>
<script>{JS}</script></body></html>"""
