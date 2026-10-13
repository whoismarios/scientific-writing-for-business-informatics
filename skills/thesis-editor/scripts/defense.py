"""Turns the examiner's question catalogue into a self-contained practice page for the oral defense."""

import html
import json
from collections import Counter
from datetime import datetime

CATEGORIES = ["Beitrag", "Theorie", "Methodik", "Formeln", "Implementierung", "Ergebnisse", "Limitationen", "Ausblick"]
LEVELS = ["Einstieg", "Vertiefung", "kritisch"]
SIGNAL = {"Einstieg": "s1", "Vertiefung": "s2", "kritisch": "s3"}


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


ICONS = {
    "cap": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "s1": '<path d="M2 20h.01"/><path d="M7 20v-4"/>',
    "s2": '<path d="M2 20h.01"/><path d="M7 20v-4"/><path d="M12 20v-8"/>',
    "s3": '<path d="M2 20h.01"/><path d="M7 20v-4"/><path d="M12 20v-8"/><path d="M17 20V8"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "shuffle": '<path d="m18 14 4 4-4 4"/><path d="m18 2 4 4-4 4"/><path d="M2 18h1.973a4 4 0 0 0 3.3-1.7l5.454-7.6a4 4 0 0 1 3.3-1.7H22"/><path d="M2 6h1.972a4 4 0 0 1 3.289 1.723l.517.737"/><path d="M22 18h-6.041a4 4 0 0 1-3.3-1.8l-.359-.45"/>',
    "eye": '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
    "follow": '<polyline points="15 10 20 15 15 20"/><path d="M4 4v7a4 4 0 0 0 4 4h12"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
}

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#161b26;--mute:#5f6777;--faint:#8a92a1;--line:#e3e6eb;--soft:#f0f2f5;--acc:#3b4cca;--accbg:#eef0fb;--red:#b42318;--redbg:#fdf2f1;--redline:#f3cfcb;--onacc:#fff;--shadow:0 1px 2px rgba(22,27,38,.04),0 2px 8px rgba(22,27,38,.04);color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0f1218;--card:#161a22;--ink:#e6e8ec;--mute:#a0a7b4;--faint:#727a88;--line:#272c36;--soft:#1d222b;--acc:#9aa6ff;--accbg:#1f2440;--red:#f4877d;--redbg:#2a1715;--redline:#4a2622;--onacc:#0f1218;--shadow:none;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
h1,h2,h3,button,summary,.badge,.kpi,.lbl,.n,.eyebrow,.count{font-family:Montserrat,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:900px;margin:0 auto;padding:40px 16px 96px}
.i{width:16px;height:16px;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
header{display:flex;gap:16px;align-items:flex-start;margin-bottom:24px}
.logo{display:grid;place-items:center;width:48px;height:48px;border-radius:14px;background:var(--accbg);color:var(--acc);flex:none}.logo .i{width:26px;height:26px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:2px 0 4px}
h1{font-size:28px;line-height:1.2;font-weight:700;letter-spacing:-.01em;margin:0 0 6px}
h2{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:700;margin:40px 0 14px}
h2 .cnt{font-size:12px;font-weight:600;color:var(--mute);background:var(--soft);border-radius:99px;padding:2px 9px}
.sub{color:var(--mute);margin:0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.kpi{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}
.kpi .ic{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;flex:none;background:var(--soft);color:var(--mute)}.kpi .ic .i{width:20px;height:20px}
.kpi b{display:block;font-size:28px;line-height:1;font-weight:700;font-variant-numeric:tabular-nums}.kpi span{display:block;color:var(--mute);font-size:13px;font-weight:500;margin-top:4px}
.k-h .ic{background:var(--redbg);color:var(--red)}.k-h b{color:var(--red)}
.badge{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;line-height:1;border-radius:6px;padding:5px 8px;border:1px solid var(--line);background:var(--card);color:var(--mute);white-space:nowrap}.badge .i{width:13px;height:13px}
.cat{background:var(--soft);border-color:transparent;color:var(--ink)}
.d-Einstieg{color:var(--faint)}.d-Vertiefung{color:var(--mute)}.d-kritisch{color:var(--red);border-color:var(--redline);background:var(--redbg)}
.gapt{color:var(--red);border-color:var(--redline)}
.by{border-color:transparent;background:transparent;color:var(--faint);font-weight:500;padding-left:2px}
.gaps{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);overflow:hidden}
.gaps>summary{display:flex;align-items:center;gap:12px;padding:14px 18px;color:var(--ink);font-size:14px;font-weight:500;line-height:1.45}
.gaps>summary>.i:first-child{width:20px;height:20px;color:var(--red)}
.gaps[open]>summary{border-bottom:1px solid var(--line)}
.glist{list-style:none;margin:0;padding:6px 18px;display:grid}
.glist li{padding:14px 0 14px 14px;border-bottom:1px solid var(--line);border-left:2px solid var(--line)}.glist li:last-child{border-bottom:0}
.glist li[data-d=kritisch]{border-left-color:var(--red)}
.glist .q-t{display:block;font-weight:600;margin:8px 0 4px;line-height:1.45}.glist p{margin:0 0 6px;color:var(--mute);font-size:14px}
summary{cursor:pointer;list-style:none}summary::-webkit-details-marker{display:none}
summary .chev{margin-left:auto;transition:transform .2s;color:var(--mute)}details[open]>summary .chev{transform:rotate(180deg)}
.bar{position:sticky;top:0;z-index:2;margin:0 -16px;padding:12px 16px;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center}
.grp{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.lbl{font-size:11px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--faint);margin-right:2px}
.bar button{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:6px 11px;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.bar button:hover{border-color:var(--faint)}.bar button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.bar button[data-f][aria-pressed=true]{background:var(--accbg);border-color:transparent;color:var(--acc)}
.bar button[data-f][aria-pressed=false]{background:transparent;color:var(--faint);text-decoration:line-through}
.bar .act[aria-pressed=true]{background:var(--acc);color:var(--onacc);border-color:var(--acc)}
.count{margin-left:auto;font-size:13px;font-weight:600;color:var(--mute);font-variant-numeric:tabular-nums}
.q{background:var(--card);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:18px 20px 16px;box-shadow:var(--shadow)}
.q.flash{animation:flash .6s ease}@keyframes flash{from{border-color:var(--acc)}to{border-color:var(--line)}}
.qh{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.n{display:grid;place-items:center;min-width:28px;height:28px;padding:0 6px;border-radius:8px;background:var(--ink);color:var(--card);font-size:13px;font-weight:700;margin-right:4px}
h3{font-size:17px;line-height:1.45;font-weight:600;margin:12px 0 14px}
.q>details>summary{display:inline-flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:var(--acc);border-radius:8px;padding:6px 0}
.q>details>summary .chev{margin-left:2px;color:inherit}.q>details[open]>summary{margin-bottom:10px}
.why{display:flex;gap:8px;color:var(--mute);font-size:14px;font-style:italic;margin:0 0 8px}.why .i{margin-top:3px}
.ans{list-style:none;margin:0 0 12px;padding:0}.ans li{position:relative;padding-left:18px;margin:6px 0}.ans li:before{content:"";position:absolute;left:4px;top:.7em;width:5px;height:5px;border-radius:50%;background:var(--faint)}
.call{display:flex;gap:10px;border-radius:10px;padding:10px 14px;margin:8px 0;font-size:14px}.call .i{margin-top:3px}.call b{display:block;font-family:Montserrat,ui-sans-serif,system-ui,sans-serif;font-size:12px;letter-spacing:.03em;margin-bottom:2px}
.gap{background:var(--redbg);border:1px solid var(--redline)}.gap .i,.gap b{color:var(--red)}
.follow{background:var(--soft)}.follow .i,.follow b{color:var(--mute)}
.loc{display:inline-flex;align-items:center;gap:6px;color:var(--faint);font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all}.loc .i{width:13px;height:13px}
.q .loc{margin-top:6px}
.hidden{display:none}
@media (max-width:640px){main{padding-top:24px}h1{font-size:23px}.logo{width:40px;height:40px}.bar{position:static}.q{padding:16px}.kpi{padding:14px}h3{font-size:16px}.count{margin-left:0}}
@media print{body{background:#fff;color:#000}.bar,.chev,.q>details>summary{display:none}.q,.kpi,.gaps{box-shadow:none;break-inside:avoid}details::details-content{content-visibility:visible;display:block}details>*{display:block}.call,.loc{display:flex}}
"""

JS = """
const st={c:new Set(),d:new Set(),g:false},list=document.getElementById('list'),count=document.getElementById('count'),total=list.children.length;
document.querySelectorAll('.bar button[data-f]').forEach(b=>st[b.dataset.f].add(b.dataset.v));
function apply(note){let n=0;list.querySelectorAll('.q').forEach(q=>{const show=st.c.has(q.dataset.c)&&(st.d.has(q.dataset.d)||!q.dataset.d)&&(!st.g||q.dataset.g==='1');q.classList.toggle('hidden',!show);n+=show});count.textContent=n+' von '+total+' Fragen'+(note?' · '+note:'')}
document.querySelectorAll('.bar button[data-f]').forEach(b=>b.onclick=()=>{const s=st[b.dataset.f];s.has(b.dataset.v)?s.delete(b.dataset.v):s.add(b.dataset.v);b.setAttribute('aria-pressed',s.has(b.dataset.v));apply()});
document.getElementById('gaponly').onclick=e=>{st.g=!st.g;e.currentTarget.setAttribute('aria-pressed',st.g);apply()};
document.getElementById('shuffle').onclick=()=>{[...list.children].map(x=>[Math.random(),x]).sort((a,b)=>a[0]-b[0]).forEach(([,x])=>{list.appendChild(x);x.classList.remove('flash');void x.offsetWidth;x.classList.add('flash')});apply('neu gemischt');list.scrollIntoView({behavior:'smooth',block:'start'})};
let open=false;document.getElementById('open').onclick=e=>{open=!open;list.querySelectorAll('details').forEach(d=>d.open=open);e.currentTarget.setAttribute('aria-pressed',open);e.currentTarget.querySelector('span').textContent=open?'Antworten verbergen':'Alle Antworten'};
apply();
"""


def _e(s):
    return html.escape(str(s or ""))


def _i(name):
    return f'<svg class="i" aria-hidden="true"><use href="#i-{name}"/></svg>'


def _diff(d):
    return f'<span class="badge d-{_e(d)}">{_i(SIGNAL[d])}{_e(d)}</span>' if d in SIGNAL else (f'<span class="badge by">{_e(d)}</span>' if d else "")


def _loc(q):
    return f'<span class="loc">{_i("file")}{_e(q["file"])}:{_e(q.get("line", ""))}</span>' if q.get("file") else ""


def render(questions, title):
    gaps = sorted((q for q in questions if q.get("gap")), key=lambda q: LEVELS[::-1].index(q["difficulty"]) if q.get("difficulty") in LEVELS else 9)
    cats = [c for c in CATEGORIES if any(q.get("category") == c for q in questions)]
    cats += sorted({q.get("category", "Sonstiges") for q in questions} - set(cats))
    cards = []
    for i, q in enumerate(questions, 1):
        c = q.get("category", "Sonstiges")
        answer = "".join(f"<li>{_e(a)}</li>" for a in q.get("answer", []))
        why = f'<p class="why">{_i("bulb")}<span>{_e(q["why"])}</span></p>' if q.get("why") else ""
        gap = f'<div class="call gap">{_i("alert")}<div><b>Lücke in der Arbeit</b>{_e(q["gap"])}</div></div>' if q.get("gap") else ""
        follow = f'<div class="call follow">{_i("follow")}<div><b>Mögliche Nachfrage</b>{_e(q["followup"])}</div></div>' if q.get("followup") else ""
        by = f'<span class="badge by">{_i("user")}{_e(q["asked_by"])}</span>' if q.get("asked_by") else ""
        cards.append(f'''<article class="q" data-c="{_e(c)}" data-d="{_e(q.get("difficulty", ""))}" data-g="{1 if q.get("gap") else 0}">
<div class="qh"><span class="n">{i}</span><span class="badge cat">{_e(q.get("category", ""))}</span>{_diff(q.get("difficulty"))}{f'<span class="badge gapt">{_i("alert")}Lücke</span>' if q.get("gap") else ""}{by}</div>
<h3>{_e(q["question"])}</h3>
<details><summary>Antwort zeigen{_i("chev").replace('class="i"', 'class="i chev"')}</summary>
{why}<ul class="ans">{answer}</ul>{gap}{follow}{_loc(q)}
</details></article>''')
    gap_list = "".join(f'<li data-d="{_e(q.get("difficulty", ""))}"><div class="qh">{_diff(q.get("difficulty"))}</div><span class="q-t">{_e(q["question"])}</span><p>{_e(q["gap"])}</p>{_loc(q)}</li>' for q in gaps)
    chev = _i("chev").replace('class="i"', 'class="i chev"')
    cbtn = "".join(f'<button data-f="c" data-v="{_e(c)}" aria-pressed="true">{_e(c)}</button>' for c in cats)
    dbtn = "".join(f'<button data-f="d" data-v="{d}" aria-pressed="true">{d}</button>' for d in LEVELS)
    sprite = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    stamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kolloquium</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap">
<style>{CSS}</style></head><body>
<!-- Icons: Lucide (lucide.dev), ISC License -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true">{sprite}</svg>
<main>
<header><div class="logo">{_i("cap")}</div><div><p class="eyebrow">Kolloquium</p><h1>Vorbereitung auf das Kolloquium</h1>
<p class="sub">{_e(title)} · erstellt {stamp} mit thesis-editor. Erst laut antworten, dann aufklappen.</p></div></header>
<div class="kpis"><div class="kpi k-q"><div class="ic">{_i("help")}</div><div><b>{len(questions)}</b><span>Fragen</span></div></div>
<div class="kpi k-h"><div class="ic">{_i("flame")}</div><div><b>{sum(1 for q in questions if q.get("difficulty") == "kritisch")}</b><span>kritische Fragen</span></div></div>
<div class="kpi k-g"><div class="ic">{_i("alert")}</div><div><b>{len(gaps)}</b><span>Lücken in der Arbeit</span></div></div></div>
{f'<h2>Offene Flanken<span class="cnt">{len(gaps)}</span></h2><details class="gaps"{" open" if len(gaps) <= 5 else ""}><summary>{_i("alert")}<span>{len(gaps)} Fragen, zu denen die Arbeit noch keine gute Antwort liefert, kritische zuerst. Vorher klären oder eine Antwort vorbereiten.</span>{chev}</summary><ul class="glist">{gap_list}</ul></details>' if gaps else ""}
<h2>Fragen<span class="cnt">{len(questions)}</span></h2>
<div class="bar"><div class="grp"><span class="lbl">Kategorie</span>{cbtn}</div><div class="grp"><span class="lbl">Schwierigkeit</span>{dbtn}</div>
<div class="grp"><span class="lbl">Aktionen</span><button class="act" id="gaponly" aria-pressed="false">{_i("alert")}<span>Nur Lücken</span></button><button class="act" id="shuffle">{_i("shuffle")}<span>Zufällige Reihenfolge</span></button><button class="act" id="open" aria-pressed="false">{_i("eye")}<span>Alle Antworten</span></button></div><span class="count" id="count" aria-live="polite"></span></div>
<div id="list">{"".join(cards)}</div>
</main>
<script>{JS}</script></body></html>"""
