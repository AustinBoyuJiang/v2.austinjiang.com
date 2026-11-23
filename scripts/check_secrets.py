#!/usr/bin/env python3
"""Block committed credentials without printing their values."""
from pathlib import PurePosixPath
import re
import subprocess
import sys

PATTERNS = (
    re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    re.compile(rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{30,}"),
    re.compile(rb"app-[A-Za-z0-9]{20,}"),
    re.compile(rb"hf_[A-Za-z0-9]{30,}"),
)

def git(*args, input=None):
    return subprocess.check_output(["git", *args], input=input)

def private_path(name):
    leaf = PurePosixPath(name).name
    return (leaf == ".env" or leaf.startswith(".env.")) and leaf not in (".env.example", ".env.sample", ".env.template") or leaf == "runtime-config.js"

def check_data(label, data):
    for pattern in PATTERNS:
        match = pattern.search(data)
        if match:
            line = data[:match.start()].count(b"\n") + 1
            print(f"Credential detected: {label}:{line}. Use a local .env file; rotate any exposed credential.", file=sys.stderr)
            return False
    return True

def staged():
    okay = True
    for record in git("ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        mode, oid, stage = meta.split()
        name = name.decode(errors="replace")
        if private_path(name):
            print(f"Private configuration must not be tracked: {name}", file=sys.stderr)
            okay = False
        if stage != b"0":
            print(f"Resolve the unmerged index before committing: {name}", file=sys.stderr)
            okay = False
        if mode != b"160000":
            okay = check_data(name, git("cat-file", "blob", oid.decode())) and okay
    return okay

def history():
    okay = True
    # Pre-push checks the complete reachable history, so an old branch cannot
    # silently reintroduce a credential after the history rewrite.
    entries = git("rev-list", "--objects", "--all").splitlines()
    objects = {}
    for entry in entries:
        oid, _, name = entry.partition(b" ")
        objects.setdefault(oid.decode(), name.decode(errors="replace"))
    if not objects:
        return True
    info = git("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)", input=("\n".join(objects) + "\n").encode())
    proc = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for entry in info.splitlines():
        oid, kind, _ = entry.split()
        if kind != b"blob":
            continue
        oid = oid.decode()
        name = objects[oid]
        if private_path(name):
            print(f"Private configuration exists in Git history: {name}", file=sys.stderr)
            okay = False
        proc.stdin.write((oid + "\n").encode())
        proc.stdin.flush()
        header = proc.stdout.readline().split()
        data = proc.stdout.read(int(header[2]))
        proc.stdout.read(1)
        okay = check_data(name or oid, data) and okay
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("Unable to read all Git objects")
    for oid in git("rev-list", "--all").splitlines():
        okay = check_data("commit " + oid.decode(), git("cat-file", "commit", oid.decode())) and okay
    return okay

if __name__ == "__main__":
    good = history() if "--history" in sys.argv else staged()
    if good:
        print("Credential check passed.")
    sys.exit(0 if good else 1)
