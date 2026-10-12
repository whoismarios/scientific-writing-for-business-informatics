#!/usr/bin/env python3
"""Misst Trefferquote und Fehlalarme der mechanischen Prüfung am Testkorpus mit Erwartungskommentaren."""

import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from lektorat import run_checks  # noqa: E402
from regelwerk import RULES  # noqa: E402

ERWARTET = re.compile(r"%\s*erwartet(\+1)?:\s*([A-Z0-9, -]+)")


def expectations(root):
    exp = set()
    for path in root.rglob("*"):
        if path.suffix not in {".tex", ".bib"}:
            continue
        rel = str(path.relative_to(root))
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = ERWARTET.search(line)
            if m:
                target = no + 1 if m.group(1) else no
                for rule in m.group(2).split(","):
                    if rule.strip():
                        exp.add((rel, target, rule.strip()))
    return exp


def main():
    root = HERE / "fixture"
    _, _, befunde, _ = run_checks(root)
    found = {(b.datei, b.zeile, b.regel) for b in befunde}
    exp = expectations(root)
    tp, fn, fp = found & exp, exp - found, found - exp
    per_rule = defaultdict(lambda: [0, 0, 0])
    for _, _, r in tp:
        per_rule[r][0] += 1
    for _, _, r in fn:
        per_rule[r][1] += 1
    for _, _, r in fp:
        per_rule[r][2] += 1
    mech = [r for r, m in RULES.items() if m["pruefung"] in {"linter", "bib"}]
    untested = [r for r in mech if r not in {e[2] for e in exp}]
    print(f"{'Regel':<26} Treffer  verfehlt  Fehlalarm")
    for r in sorted(per_rule):
        t, n, p = per_rule[r]
        print(f"{r:<26} {t:>7}  {n:>8}  {p:>9}")
    recall = len(tp) / max(len(exp), 1)
    precision = len(tp) / max(len(found), 1)
    print(f"\nTrefferquote {recall:.0%} ({len(tp)}/{len(exp)})   Genauigkeit {precision:.0%} ({len(tp)}/{len(found)})")
    print(f"Abgedeckte mechanische Regeln: {len(mech) - len(untested)}/{len(mech)}")
    if untested:
        print("Ohne Testfall: " + ", ".join(untested))
    for d, z, r in sorted(fn):
        print(f"  verfehlt   {r} {d}:{z}")
    for d, z, r in sorted(fp):
        print(f"  Fehlalarm  {r} {d}:{z}")
    sys.exit(0 if not fn and not fp else 1)


if __name__ == "__main__":
    main()
