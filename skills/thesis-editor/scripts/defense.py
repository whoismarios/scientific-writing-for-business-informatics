"""Turns the examiner's question catalogue into a self-contained practice page for the oral defense."""

import html
import json
from collections import Counter
from datetime import datetime

CATEGORIES = ["Beitrag", "Theorie", "Methodik", "Formeln", "Implementierung", "Ergebnisse", "Limitationen", "Ausblick"]
LEVELS = ["Einstieg", "Vertiefung", "kritisch"]


def load(run_dir):
    """All questions from .thesis-editor/run/defense/*.json, sorted by category and difficulty."""
    questions = []
    for f in sorted((run_dir / "defense").glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Übersprungen, kein gültiges JSON: {f.name} ({e})")
            continue
        for q in data.get("questions", data) if isinstance(data, dict) else data:
            if isinstance(q, dict) and q.get("question"):
                questions.append(q)
    order = {c: i for i, c in enumerate(CATEGORIES)}
    level = {d: i for i, d in enumerate(LEVELS)}
    questions.sort(key=lambda q: (order.get(q.get("category"), 99), level.get(q.get("difficulty"), 9)))
    return questions


def summary(questions):
    cats = Counter(q.get("category", "Sonstiges") for q in questions)
    gaps = sum(1 for q in questions if q.get("gap"))
    lines = [f"{len(questions)} Fragen, davon {gaps} mit Lücke in der Arbeit",
             "Kategorien: " + ", ".join(f"{c} {n}" for c, n in sorted(cats.items(), key=lambda kv: CATEGORIES.index(kv[0]) if kv[0] in CATEGORIES else 99))]
    return "\n".join(lines)


def _e(s):
    return html.escape(str(s or ""))


def render(questions, title):
    gaps = [q for q in questions if q.get("gap")]
    cats = [c for c in CATEGORIES if any(q.get("category") == c for q in questions)]
    cats += sorted({q.get("category", "Sonstiges") for q in questions} - set(cats))
    cards = []
    for i, q in enumerate(questions, 1):
        loc = f'{_e(q.get("file", ""))}:{_e(q.get("line", ""))}' if q.get("file") else ""
        answer = "".join(f"<li>{_e(a)}</li>" for a in q.get("answer", []))
        gap = f'<p class="gap"><b>Lücke in der Arbeit:</b> {_e(q["gap"])}</p>' if q.get("gap") else ""
        follow = f'<p class="follow"><b>Mögliche Nachfrage:</b> {_e(q["followup"])}</p>' if q.get("followup") else ""
        cards.append(f'''<article class="q" data-c="{_e(q.get("category", "Sonstiges"))}" data-d="{_e(q.get("difficulty", ""))}" data-g="{1 if q.get("gap") else 0}">
<div class="qh"><span class="n">{i}</span><span class="tag">{_e(q.get("category", ""))}</span><span class="tag d-{_e(q.get("difficulty", ""))}">{_e(q.get("difficulty", ""))}</span><span class="by">{_e(q.get("asked_by", ""))}</span>{'<span class="tag gapt">Lücke</span>' if q.get("gap") else ""}</div>
<h3>{_e(q["question"])}</h3>
<details><summary>Antwort zeigen</summary>
<p class="why">{_e(q.get("why", ""))}</p><ul>{answer}</ul>{gap}{follow}<p class="loc">{loc}</p>
</details></article>''')
    gap_list = "".join(f'<li><b>{_e(q["question"])}</b><br>{_e(q["gap"])} <span class="loc">{_e(q.get("file", ""))}:{_e(q.get("line", ""))}</span></li>' for q in gaps)
    buttons = "".join(f'<button data-f="c" data-v="{_e(c)}" aria-pressed="true">{_e(c)}</button>' for c in cats)
    buttons += "".join(f'<button data-f="d" data-v="{d}" aria-pressed="true">{d}</button>' for d in LEVELS)
    stamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kolloquium</title>
<style>
:root{{--bg:#f7f6f2;--card:#fff;--ink:#1d1d1b;--mute:#6b6a64;--line:#e4e2da;--gap:#b42318;--gapbg:#fef3f2;--easy:#067647;--mid:#b54708;--hard:#b42318}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151513;--card:#1e1e1b;--ink:#ecebe6;--mute:#a3a29b;--line:#33322e;--gap:#f97066;--gapbg:#2a1715;--easy:#47cd89;--mid:#fdb022;--hard:#f97066}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:880px;margin:0 auto;padding:32px 16px 80px}}
h1{{font:600 28px/1.2 ui-serif,Georgia,serif;margin:0 0 4px}}h2{{font:600 18px/1.3 ui-serif,Georgia,serif;margin:32px 0 12px}}
.sub{{color:var(--mute);margin:0 0 20px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}.kpi b{{display:block;font:600 26px/1.1 ui-serif,Georgia,serif}}.kpi span{{color:var(--mute);font-size:13px}}
.gaps{{background:var(--gapbg);border:1px solid var(--gap);border-radius:10px;padding:12px 16px}}.gaps li{{margin:8px 0}}
.bar{{position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;display:flex;flex-wrap:wrap;gap:6px;border-bottom:1px solid var(--line)}}
.bar button{{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:99px;padding:4px 11px;cursor:pointer}}
.bar button[aria-pressed=false]{{opacity:.45}}.bar .act{{font-weight:600}}
.q{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:12px 16px}}
.qh{{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--mute)}}.n{{font-weight:600;color:var(--ink)}}
.tag{{border:1px solid var(--line);border-radius:99px;padding:0 8px}}.d-Einstieg{{color:var(--easy)}}.d-Vertiefung{{color:var(--mid)}}.d-kritisch{{color:var(--hard)}}.gapt{{color:var(--gap);border-color:var(--gap)}}
h3{{font:600 17px/1.4 ui-serif,Georgia,serif;margin:8px 0}}
details summary{{cursor:pointer;color:var(--mute);font-size:13px}}.why{{color:var(--mute);font-style:italic}}
.gap{{color:var(--gap)}}.loc{{color:var(--mute);font:12px ui-monospace,Menlo,monospace}}ul{{margin:6px 0;padding-left:20px}}
.hidden{{display:none}}
@media print{{.bar{{display:none}}details{{display:block}}details>*{{display:block}}.q{{break-inside:avoid}}}}
</style></head><body><main>
<h1>Vorbereitung auf das Kolloquium</h1>
<p class="sub">{_e(title)} · erstellt {stamp} mit thesis-editor. Erst laut antworten, dann aufklappen.</p>
<div class="kpis"><div class="kpi"><b>{len(questions)}</b><span>Fragen</span></div>
<div class="kpi"><b>{sum(1 for q in questions if q.get("difficulty") == "kritisch")}</b><span>kritische Fragen</span></div>
<div class="kpi"><b>{len(gaps)}</b><span>Lücken in der Arbeit</span></div></div>
{f'<h2>Offene Flanken</h2><div class="gaps"><p>Zu diesen Fragen liefert die Arbeit noch keine gute Antwort. Vorher klären oder eine Antwort vorbereiten.</p><ul>{gap_list}</ul></div>' if gaps else ""}
<h2>Fragen</h2>
<div class="bar">{buttons}<button class="act" id="shuffle">Zufällige Reihenfolge</button><button class="act" id="open">Alle Antworten</button><button class="act" id="gaponly" aria-pressed="false">Nur Lücken</button></div>
<div id="list">{"".join(cards)}</div>
</main>
<script>
const st={{c:new Set(),d:new Set(),g:false}};
document.querySelectorAll('.bar button[data-f]').forEach(b=>st[b.dataset.f].add(b.dataset.v));
function apply(){{document.querySelectorAll('.q').forEach(q=>q.classList.toggle('hidden',!(st.c.has(q.dataset.c)&&(st.d.has(q.dataset.d)||!q.dataset.d)&&(!st.g||q.dataset.g==='1'))))}}
document.querySelectorAll('.bar button[data-f]').forEach(b=>b.onclick=()=>{{const s=st[b.dataset.f];s.has(b.dataset.v)?s.delete(b.dataset.v):s.add(b.dataset.v);b.setAttribute('aria-pressed',s.has(b.dataset.v));apply()}});
document.getElementById('gaponly').onclick=e=>{{st.g=!st.g;e.target.setAttribute('aria-pressed',st.g);apply()}};
document.getElementById('shuffle').onclick=()=>{{const l=document.getElementById('list');[...l.children].map(x=>[Math.random(),x]).sort((a,b)=>a[0]-b[0]).forEach(([,x])=>l.appendChild(x))}};
let open=false;document.getElementById('open').onclick=e=>{{open=!open;document.querySelectorAll('details').forEach(d=>d.open=open);e.target.textContent=open?'Antworten verbergen':'Alle Antworten'}};
</script></body></html>"""
