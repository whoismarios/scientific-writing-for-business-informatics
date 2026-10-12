"""Verdichtet Befunde zu Verlaufseintrag, Chat-Zusammenfassung und eigenständigem HTML-Bericht."""

import html
import json
from collections import Counter
from pathlib import Path

from regelwerk import REGELWERK, RULES, SCHWERE_RANG

GEWICHT = {"Fehler": 5.0, "Warnung": 2.0, "Hinweis": 0.5, "Offen": 0.0}
FARBNAME = {"quelle": "Quelle fehlt", "offen": "Offen", "beleg": "Beleg", "stil": "Stil", "struktur": "Struktur", "keine": "Bibliografie, Quelltext und Abgabe"}


def index(befunde, woerter):
    """Gewichtete Befunde je 1.000 Wörter. Marker und Umfeldprüfungen zählen nicht."""
    s = sum(GEWICHT.get(b.schwere, 0) for b in befunde if RULES.get(b.regel, {}).get("pruefung") != "umfeld")
    return round(s / max(woerter, 1) * 1000, 1)


def history_entry(meta, befunde, agenten):
    c = Counter(b.schwere for b in befunde)
    return {
        "zeit": meta["zeit"],
        "regelwerk": meta["regelwerk"],
        "woerter": meta["woerter"],
        "index": index(befunde, meta["woerter"]),
        "schwere": dict(c),
        "regeln": dict(Counter(b.regel for b in befunde)),
        "agenten": agenten,
        "befunde": [{"fp": b.fingerprint, "regel": b.regel, "datei": b.datei, "zeile": b.zeile, "meldung": b.meldung[:160],
                     "schwere": b.schwere} for b in befunde],
    }


def diff(entry, prev):
    if not prev:
        return None, None
    now = {b["fp"] for b in entry["befunde"]}
    before = {b["fp"]: b for b in prev["befunde"]}
    neu = now - set(before)
    behoben = [b for fp, b in before.items() if fp not in now]
    return neu, behoben


def render_summary(meta, befunde, agenten, entry, prev):
    c = Counter(b.schwere for b in befunde)
    lines = [f"## Lektorat {meta['zeit'][:16].replace('T', ' ')}", "",
             f"Lektoratsindex **{entry['index']}** (gewichtete Befunde je 1.000 Wörter, niedriger ist besser)"
             + (f", vorher {prev['index']}" if prev else ""),
             f"{meta['woerter']} Wörter" + (f" in der Auswahl {meta['auswahl']}" if meta.get("auswahl") else f", {meta['saetze']} Sätze, {len(meta['dateien'])} Dateien"), "",
             "| Fehler | Warnung | Hinweis | Offen |", "|---:|---:|---:|---:|",
             f"| {c.get('Fehler', 0)} | {c.get('Warnung', 0)} | {c.get('Hinweis', 0)} | {c.get('Offen', 0)} |"]
    neu, behoben = diff(entry, prev)
    if neu is not None:
        lines += ["", f"Seit dem letzten Lauf: {len(behoben)} behoben, {len(neu)} neu."]
    if agenten:
        lines += ["", "Gutachter: " + ", ".join(f"{k} {v}" for k, v in agenten.items())]
    top = Counter(b.regel for b in befunde if b.schwere in {"Fehler", "Warnung"}).most_common(8)
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


def render_html(cfg, meta, befunde, agenten, history, prev):
    entry = history[-1] if history else history_entry(meta, befunde, agenten)
    neu, behoben = diff(entry, prev)
    c = Counter(b.schwere for b in befunde)
    order = {f: i for i, f in enumerate(meta["dateien"])}
    befunde = sorted(befunde, key=lambda b: (order.get(b.datei, 999), b.datei, b.zeile, SCHWERE_RANG.get(b.schwere, 9)))
    marker = [b for b in befunde if b.schwere == "Offen"]
    rest = [b for b in befunde if b.schwere != "Offen"]
    groups = {}
    for b in rest:
        groups.setdefault(b.datei, []).append(b)

    def row(b):
        r = RULES.get(b.regel, {})
        is_new = neu is not None and b.fingerprint in neu
        src = "agent" if b.quelle.startswith("agent") else b.quelle
        return (
            f'<li class="f" data-s="{_e(b.schwere)}" data-c="{_e(b.farbe)}" data-q="{_e(src)}" data-n="{int(is_new)}">'
            f'<div class="fh"><span class="sev s-{_e(b.schwere)}">{_e(b.schwere)}</span>'
            f'<span class="dot c-{_e(b.farbe)}" title="{_e(FARBNAME.get(b.farbe, b.farbe))}"></span>'
            f'<code class="rid" title="{_e(r.get("warum", ""))}">{_e(b.regel)}</code>'
            f'<span class="loc">Zeile {b.zeile}</span>'
            + (f'<span class="tag">{_e(b.quelle)}</span>' if b.quelle not in {"linter", "bib"} else "")
            + ('<span class="tag new">neu</span>' if is_new else "")
            + f'</div><p class="msg">{_e(b.meldung)}</p>'
            + (f'<p class="ex">{_e(b.auszug)}</p>' if b.auszug and b.auszug != b.meldung else "")
            + (f'<p class="fix">→ {_e(b.vorschlag)}</p>' if b.vorschlag else "")
            + "</li>"
        )

    sections = []
    for datei, items in groups.items():
        cc = Counter(b.schwere for b in items)
        badge = " ".join(f'<span class="mini s-{k}">{cc[k]}</span>' for k in ("Fehler", "Warnung", "Hinweis") if cc.get(k))
        sections.append(f'<details class="grp" open><summary><span class="fn">{_e(datei)}</span>{badge}</summary>'
                        f'<ul>{"".join(row(b) for b in items)}</ul></details>')

    marker_rows = "".join(
        f'<tr><td><span class="dot c-{_e(b.farbe)}"></span></td><td>{_e(Path(b.datei).name)}:{b.zeile}</td><td>{_e(b.meldung)}</td></tr>'
        for b in marker)
    behoben_html = ""
    if behoben:
        items = "".join(f'<li><code>{_e(b["regel"])}</code> {_e(Path(b["datei"]).name)}:{b["zeile"]} {_e(b["meldung"])}</li>' for b in behoben[:300])
        behoben_html = f'<details class="grp"><summary><span class="fn">Seit dem letzten Lauf behoben</span><span class="mini ok">{len(behoben)}</span></summary><ul class="plain">{items}</ul></details>'

    rule_counts = Counter(b.regel for b in rest)
    rule_rows = "".join(
        f'<tr><td><code>{_e(r)}</code></td><td>{_e(RULES.get(r, {}).get("titel", ""))}</td><td>{n}</td></tr>'
        for r, n in sorted(rule_counts.items(), key=lambda kv: (SCHWERE_RANG.get(RULES.get(kv[0], {}).get("schwere"), 9), -kv[1])))
    titel = cfg["projekt"].get("titel") or "Arbeit"
    delta = ""
    if prev:
        d = round(entry["index"] - prev["index"], 1)
        delta = f'<span class="delta {"good" if d < 0 else "bad" if d > 0 else ""}">{"+" if d > 0 else ""}{d}</span>'

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lektoratsbericht</title>
<style>
:root{{--bg:#f7f6f2;--card:#fff;--ink:#1d1d1b;--mute:#6b6a64;--line:#e4e2da;--fehler:#b42318;--warnung:#b54708;--hinweis:#475467;--offen:#c4320a;
--quelle:#d92d20;--c-offen:#e8590c;--beleg:#c11574;--stil:#2a5bd7;--struktur:#7a3fc4;--keine:#98a2b3;--good:#067647;--bad:#b42318}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151513;--card:#1e1e1b;--ink:#ecebe6;--mute:#a3a29b;--line:#33322e;--fehler:#f97066;--warnung:#fdb022;--hinweis:#98a2b3;
--quelle:#f97066;--c-offen:#fd853a;--beleg:#ee46bc;--stil:#6f9cf5;--struktur:#b692f6;--good:#47cd89;--bad:#f97066}}}}
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
.sev{{font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}}.s-Fehler{{color:var(--fehler)}}.s-Warnung{{color:var(--warnung)}}.s-Hinweis{{color:var(--hinweis)}}.s-Offen{{color:var(--offen)}}
.mini{{font-size:12px;border-radius:99px;padding:1px 8px;border:1px solid currentColor}}.mini.ok{{color:var(--good)}}
.dot{{width:10px;height:10px;border-radius:3px;display:inline-block}}.c-quelle{{background:var(--quelle)}}.c-offen{{background:var(--c-offen)}}.c-beleg{{background:var(--beleg)}}.c-stil{{background:var(--stil)}}.c-struktur{{background:var(--struktur)}}.c-keine{{background:var(--keine)}}
.rid{{font-size:12px;cursor:help}}.loc{{color:var(--mute)}}.tag{{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:0 6px;color:var(--mute)}}.tag.new{{color:var(--bad);border-color:currentColor}}
.msg{{margin:4px 0 0}}.ex{{margin:4px 0 0;color:var(--mute);font-family:ui-serif,Georgia,serif;font-style:italic;overflow-wrap:anywhere}}.fix{{margin:4px 0 0;font-size:14px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:14px}}
td,th{{padding:7px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:top}}tr:first-child td{{border-top:0}}
.plain li{{padding:6px 14px;border-top:1px solid var(--line);font-size:14px}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--mute);margin-top:10px}}
footer{{margin-top:40px;color:var(--mute);font-size:13px}}
</style></head><body><main>
<h1>Lektoratsbericht</h1>
<p class="sub">{_e(titel)} · {_e(meta['zeit'][:16].replace('T', ' '))} · Regelwerk {_e(REGELWERK['meta']['version'])} · {meta['woerter']} Wörter in {len(meta['dateien'])} Dateien</p>
<div class="kpis">
<div class="kpi idx"><b>{entry['index']}{delta}</b><span>Lektoratsindex, gewichtete Befunde je 1.000 Wörter</span>{sparkline(history)}</div>
<div class="kpi"><b class="s-Fehler">{c.get('Fehler', 0)}</b><span>Fehler</span></div>
<div class="kpi"><b class="s-Warnung">{c.get('Warnung', 0)}</b><span>Warnungen</span></div>
<div class="kpi"><b class="s-Hinweis">{c.get('Hinweis', 0)}</b><span>Hinweise</span></div>
<div class="kpi"><b class="s-Offen">{c.get('Offen', 0)}</b><span>offene Marker</span></div>
</div>
<div class="legend">{''.join(f'<span><span class="dot c-{k}"></span> {v}</span>' for k, v in FARBNAME.items())}</div>
<p class="sub" style="margin-top:12px">Gewichte: Fehler 5, Warnung 2, Hinweis 0,5. Marker zählen nicht. {('Gutachter: ' + ', '.join(f'{k} ({v})' for k, v in agenten.items())) if agenten else 'Nur mechanische Prüfung, ohne Gutachter-Agenten.'}</p>

<h2>Offene Marker ({len(marker)})</h2>
<table>{marker_rows or '<tr><td>Keine offenen Marker.</td></tr>'}</table>

<h2>Befunde ({len(rest)})</h2>
<div class="bar" id="bar">
<button data-f="s" data-v="Fehler" aria-pressed="true">Fehler</button><button data-f="s" data-v="Warnung" aria-pressed="true">Warnung</button><button data-f="s" data-v="Hinweis" aria-pressed="true">Hinweis</button>
<button data-f="c" data-v="beleg" aria-pressed="true">Beleg</button><button data-f="c" data-v="stil" aria-pressed="true">Stil</button><button data-f="c" data-v="struktur" aria-pressed="true">Struktur</button><button data-f="c" data-v="keine" aria-pressed="true">Bibliografie</button>
<button data-f="q" data-v="agent" aria-pressed="true">Gutachter</button><button data-f="n" data-v="1" aria-pressed="false">nur neue</button>
<input type="search" id="q" placeholder="Suche in Befunden">
</div>
{behoben_html}
{''.join(sections)}

<h2>Befunde je Regel</h2>
<table>{rule_rows}</table>
<footer>Erzeugt mit thesis-lektor. Regel-IDs zeigen beim Überfahren die Begründung. Ausnahmen im Quelltext mit <code>% lektorat: ignore REGEL-ID</code>.</footer>
</main>
<script>
const st={{s:new Set(["Fehler","Warnung","Hinweis"]),c:new Set(["beleg","stil","struktur","keine"]),q:true,n:false}};
const q=document.getElementById("q");
function apply(){{const t=q.value.toLowerCase();document.querySelectorAll(".f").forEach(e=>{{
const ok=st.s.has(e.dataset.s)&&st.c.has(e.dataset.c)&&(st.q||e.dataset.q!=="agent")&&(!st.n||e.dataset.n==="1")&&(!t||e.textContent.toLowerCase().includes(t));
e.style.display=ok?"":"none";}});
document.querySelectorAll("details.grp").forEach(g=>{{const any=[...g.querySelectorAll(".f")].some(e=>e.style.display!=="none");if(g.querySelector(".f"))g.style.display=any?"":"none";}});}}
document.querySelectorAll("#bar button").forEach(b=>b.addEventListener("click",()=>{{const on=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",on);
const f=b.dataset.f,v=b.dataset.v;if(f==="s"||f==="c"){{on?st[f].add(v):st[f].delete(v);}}else{{st[f]=on;}}apply();}}));
q.addEventListener("input",apply);
</script></body></html>"""
