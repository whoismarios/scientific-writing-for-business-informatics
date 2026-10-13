#!/usr/bin/env python3
"""Checks GitHub at most once a day for a newer version of this skill and installs it on request."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = "whoismarios/scientific-writing-for-business-informatics"
BRANCH = "main"
SKILL_DIR = Path(__file__).resolve().parent.parent
TTL = 24 * 3600
DEFAULTS = {"check": True, "auto": False}


def skill_name():
    m = re.search(r"^name:\s*(\S+)", (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else SKILL_DIR.name


def version_key(v):
    return tuple(int(p) for p in re.findall(r"\d+", v or "0")[:3])


def local_version():
    path = SKILL_DIR / "VERSION"
    return path.read_text(encoding="utf-8").strip() if path.exists() else "0.0.0"


def cache_file():
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "scientific-writing-skills" / f"{skill_name()}.json"


def fetch(path):
    """Returns a file of the skill from the main branch on GitHub, or None if it cannot be reached."""
    rel = f"skills/{skill_name()}/{path}"
    try:
        url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{rel}"
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode("utf-8")
    except Exception:
        pass
    if shutil.which("gh"):
        try:
            out = subprocess.run(
                ["gh", "api", f"repos/{REPO}/contents/{rel}?ref={BRANCH}", "-H", "Accept: application/vnd.github.raw"],
                capture_output=True, text=True, timeout=6,
            )
            if out.returncode == 0:
                return out.stdout
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None


def changes_since(changelog, installed):
    """Returns the changelog entries newer than the installed version as (version, [lines])."""
    entries, current = [], None
    for line in (changelog or "").splitlines():
        m = re.match(r"^##\s+\[?(\d+\.\d+\.\d+)", line)
        if m:
            current = (m.group(1), []) if version_key(m.group(1)) > version_key(installed) else None
            if current:
                entries.append(current)
        elif current and line.strip().startswith(("-", "*")):
            current[1].append(line.strip().lstrip("-* ").strip())
    return entries


def install_kind():
    """How the skill was installed: git (a checkout), global or project (via npx skills), or copy."""
    if SKILL_DIR.parent.name == "skills" and SKILL_DIR.parent.parent.name in {".agents", ".claude", ".codex"}:
        return "global" if SKILL_DIR.parents[2] == Path.home() else "project"
    try:
        if subprocess.run(["git", "-C", str(SKILL_DIR), "rev-parse", "--is-inside-work-tree"],
                          capture_output=True, text=True).stdout.strip() == "true":
            return "git"
    except OSError:
        pass
    return "copy"


def settings(cfg=None):
    s = {**DEFAULTS, **(cfg or {})}
    if os.environ.get("SKILL_UPDATE_CHECK") == "0":
        s["check"] = False
    if os.environ.get("SKILL_AUTO_UPDATE") == "1":
        s["auto"] = True
    return s


def status(cfg=None, force=False):
    """Compares the installed version with GitHub, using a cache that is at most a day old."""
    s = settings(cfg)
    installed = local_version()
    result = {"skill": skill_name(), "installed": installed, "latest": None, "available": False,
              "changes": [], "auto": s["auto"], "install": install_kind(), "state": "off"}
    if not s["check"]:
        return result
    path = cache_file()
    cached = None
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    ttl = TTL if cached and cached.get("latest") else 3600
    if not force and cached and cached.get("installed") == installed and time.time() - cached.get("time", 0) < ttl:
        latest, changes = cached.get("latest"), cached.get("changes", [])
    else:
        remote = fetch("VERSION")
        latest = remote.strip() if remote else None
        changes = changes_since(fetch("CHANGELOG.md"), installed) if latest and version_key(latest) > version_key(installed) else []
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"time": time.time(), "installed": installed, "latest": latest, "changes": changes}),
                            encoding="utf-8")
        except OSError:
            pass
    result.update(latest=latest, changes=changes, state="unknown" if latest is None else "ok",
                  available=bool(latest) and version_key(latest) > version_key(installed))
    return result


def apply():
    """Installs the newest version through the skills CLI. Returns an exit code."""
    name, kind, before = skill_name(), install_kind(), local_version()
    if kind == "git":
        print(f"{name} runs from a Git checkout at {SKILL_DIR}. Update it there with: git pull")
        return 2
    if kind == "copy" or not shutil.which("npx"):
        print(f"{name} was not installed with npx skills. Reinstall with: npx skills add {REPO} --skill {name} --global")
        return 2
    cmd = ["npx", "--yes", "skills", "update", name, "-g" if kind == "global" else "-p", "-y"]
    cwd = SKILL_DIR.parents[2] if kind == "project" else None
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"Update failed: {e}")
        return 1
    after = local_version()
    try:
        cache_file().unlink()
    except OSError:
        pass
    if out.returncode != 0:
        print("Update failed:\n" + (out.stderr or out.stdout).strip()[-1500:])
        return 1
    print(f"{name} updated from {before} to {after}." if after != before else f"{name} is at {after}, nothing changed.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", nargs="?", choices=["status", "apply"], default="status")
    ap.add_argument("--force", action="store_true", help="ignore the cache and ask GitHub now")
    ap.add_argument("--json", action="store_true", help="print the status as JSON")
    a = ap.parse_args()
    if a.action == "apply":
        return apply()
    st = status(force=a.force)
    if a.json:
        print(json.dumps(st, ensure_ascii=False, indent=1))
    else:
        print(describe(st))
    return 0


def describe(st):
    """One line for the summary, followed by the new changelog entries."""
    if st["state"] == "off":
        return f"update: check disabled, installed {st['installed']}"
    if st["state"] == "unknown":
        return f"update: installed {st['installed']}, GitHub not reachable"
    if not st["available"]:
        return f"update: {st['installed']} is the newest version"
    lines = [f"update: {st['latest']} available, installed {st['installed']}, auto update {'on' if st['auto'] else 'off'}"
             + (", installed from a Git checkout (git pull)" if st["install"] == "git" else "")]
    for version, items in st["changes"]:
        lines += [f"  {version}: {item}" for item in items]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
