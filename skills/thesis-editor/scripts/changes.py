"""Determines which source lines changed since a Git revision, widened to whole paragraphs."""

import re
import subprocess
from pathlib import Path

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout, r.stderr.strip()


def _paragraph(lines, no):
    """Line numbers of the paragraph around line no, delimited by blank lines."""
    start = end = no
    while start > 1 and lines[start - 2].strip():
        start -= 1
    while end < len(lines) and lines[end].strip():
        end += 1
    return range(start, end + 1)


def changed_lines(root, rev, paths):
    """Maps project-relative paths to changed line numbers since rev. Untracked files count as fully changed."""
    root = Path(root).resolve()
    code, _, err = _git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    if code != 0:
        raise SystemExit(f"Unbekannte Git-Revision: {rev}. Beispiele: HEAD~1, main, ein Commit-Hash.")
    _, diff, _ = _git(root, "diff", "--relative", "--unified=0", "--no-color", "--no-ext-diff", rev, "--", *paths)
    changed, current = {}, None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            name = line[4:].strip()
            current = None if name == "/dev/null" else name.removeprefix("b/")
        elif current and (m := HUNK.match(line)):
            start, count = int(m.group(1)), int(m.group(2) or 1)
            changed.setdefault(current, set()).update(range(start, start + count) if count else {start})
    _, untracked, _ = _git(root, "ls-files", "--others", "--exclude-standard", "--", *paths)
    for name in untracked.splitlines():
        text = (root / name).read_text(encoding="utf-8", errors="replace")
        changed[name] = set(range(1, text.count("\n") + 2))
    widened = {}
    for name, nos in changed.items():
        path = root / name
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        widened[name] = {n for no in nos if 1 <= no <= len(lines) and lines[no - 1].strip() for n in _paragraph(lines, no)}
    return widened
