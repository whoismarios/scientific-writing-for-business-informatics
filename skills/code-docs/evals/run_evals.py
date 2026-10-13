#!/usr/bin/env python3
"""Compares the findings of check.py on the fixture with the expect comments in it."""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from check import RULES, run_checks  # noqa: E402

EXPECTED = re.compile(r"(?:#|//|<!--)\s*expect(-full)?:\s*([A-Z0-9-]+(?:\s*,\s*[A-Z0-9-]+)*)")


def expectations(root, style):
    """Expectations for one style. expect applies to google and full, expect-full only to full."""
    exp = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = EXPECTED.search(line)
            if m and (not m.group(1) or style == "full"):
                exp |= {(rel, no, r.strip()) for r in m.group(2).split(",") if r.strip()}
    return exp


def main():
    root = HERE / "fixture"
    failed = False
    for style in ("google", "full"):
        _, _, findings = run_checks(root, overrides={"style": style})
        found = {(f.file, f.line, f.rule) for f in findings if f.line}
        exp = expectations(root, style)
        missed, unexpected = exp - found, found - exp
        untested = sorted(set(RULES) - {r for _, _, r in exp} - {"README-MISSING", "ARCH-MISSING"})
        print(f"style {style}: {len(found & exp)} of {len(exp)} expected findings, {len(unexpected)} unexpected")
        if untested:
            print("  Rules without a test case: " + ", ".join(untested))
        for f, n, r in sorted(missed):
            print(f"  missed      {r} {f}:{n}")
        for f, n, r in sorted(unexpected):
            print(f"  unexpected  {r} {f}:{n}")
        failed |= bool(missed or unexpected)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
