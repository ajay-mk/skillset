#!/usr/bin/env python3
"""Capture a git diff snapshot and build a standalone review-helper page.

  review_helper.py capture --repo R --base B [--head H] [--untracked P ...] -o snap.json
  review_helper.py build snap.json -o page.html

capture fills the mechanical fields (paths, status, stats, exact patches,
endpoint sources, hashes). The agent then writes the narrative fields
(title, summary, groups, per-file title/group/before/after/why, annotations,
comments, checks) into the JSON. build validates that every narrative field
and every link target is present, then embeds the JSON into the template.
Stdlib only.
"""
import argparse, base64, datetime, hashlib, json, pathlib, subprocess, sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template.html"
STATUS = {"A": "added", "D": "deleted", "M": "modified", "R": "renamed", "C": "copied", "T": "modified"}


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def text(b):
    return None if b is None else b.decode("utf-8", errors="replace")


def endpoint(repo, rev, path):
    """File bytes at a revision, or in the worktree when rev is None; None if absent."""
    if rev is None:
        p = pathlib.Path(repo, path)
        return p.read_bytes() if p.is_file() else None
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def is_binary(b):
    return b is not None and b"\0" in b[:8000]


def capture_once(repo, base, head, untracked):
    rng = [base] + ([head] if head else [])
    raw = git(repo, "diff", "-M", "--name-status", "-z", *rng).split(b"\0")
    entries, i = [], 0
    while i < len(raw) and raw[i]:
        code = raw[i].decode()[0]
        if code in "RC":
            entries.append((code, raw[i + 1].decode(), raw[i + 2].decode()))
            i += 3
        else:
            entries.append((code, raw[i + 1].decode(), raw[i + 1].decode()))
            i += 2
    files = []
    for code, old_path, path in entries:
        patch = git(repo, "diff", "-M", "--binary", *rng, "--", *{old_path, path})
        old, new = endpoint(repo, base, old_path), endpoint(repo, head, path)
        files.append((STATUS.get(code, "modified"), old_path, path, patch, old, new))
    for path in untracked:
        new = endpoint(repo, None, path)
        if new is None:
            sys.exit(f"untracked file not found: {path}")
        patch = git(repo, "diff", "--no-index", "--binary", "--", "/dev/null", path, check=False)
        files.append(("added", None, path, patch, None, new))
    return files


def capture(a):
    repo = git(a.repo, "rev-parse", "--show-toplevel").decode().strip()
    base = git(repo, "rev-parse", "--verify", f"{a.base}^{{commit}}").decode().strip()
    head = git(repo, "rev-parse", "--verify", f"{a.head}^{{commit}}").decode().strip() if a.head else None
    # Recapture until two consecutive passes agree, so a file edited mid-capture
    # cannot leave patches and sources from different moments.
    for _ in range(3):
        first = capture_once(repo, base, head, a.untracked)
        second = capture_once(repo, base, head, a.untracked)
        if first == second:
            break
    else:
        sys.exit("the working tree kept changing during capture; retry when it is quiet")
    if not first:
        sys.exit("empty diff: nothing to review")

    out = []
    for status, old_path, path, patch, old, new in first:
        binary = is_binary(old) or is_binary(new)
        adds = sum(1 for l in patch.split(b"\n") if l.startswith(b"+") and not l.startswith(b"+++"))
        dels = sum(1 for l in patch.split(b"\n") if l.startswith(b"-") and not l.startswith(b"---"))
        out.append({
            "path": path, "old_path": old_path if old_path != path else None,
            "status": status, "binary": binary, "adds": adds, "deletes": dels,
            "patch64": base64.b64encode(patch).decode(),
            "sha256": hashlib.sha256(patch).hexdigest(),
            "old": None if binary else text(old), "new": None if binary else text(new),
            "title": "", "group": "", "before": "", "after": "", "why": "", "annotations": [],
        })
    whole = hashlib.sha256(b"".join(base64.b64decode(f["patch64"]) for f in out)).hexdigest()
    branch = a.head or git(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    snap = {
        "title": "", "subtitle": "", "repo": pathlib.Path(repo).name, "root": repo,
        "branch": branch, "base": base, "head": head or "working tree",
        "comparison": f"{a.base} → {a.head or 'working tree (staged + unstaged)'}",
        "captured": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "fingerprint": whole, "pr_url": "",
        "summary": {"overview": "", "changes": [], "focus": []},
        "groups": [], "files": out, "comments": [], "checks": [], "excluded": [], "notes": [],
    }
    pathlib.Path(a.output).write_text(json.dumps(snap, indent=1, ensure_ascii=False))
    print(f"captured {len(out)} files, fingerprint {whole[:12]} -> {a.output}")


def validate(s):
    errs = []
    need = lambda obj, keys, where: errs.extend(f"{where}: missing {k}" for k in keys if not obj.get(k))
    need(s, ["title", "groups"], "snapshot")
    need(s["summary"], ["overview", "changes"], "summary")
    files = {f["path"]: f for f in s["files"]}

    def target(t, where):
        f = files.get(t.get("file"))
        if not f:
            errs.append(f"{where}: unknown file {t.get('file')!r}")
            return
        line, side = t.get("line"), t.get("side", "new")
        src = f.get(side)
        if line and (src is None or not 1 <= line <= len(src.splitlines())):
            errs.append(f"{where}: {t['file']} has no {side} line {line}")

    for f in s["files"]:
        need(f, ["title", "group", "before", "after", "why"], f["path"])
        if f["group"] and f["group"] not in s["groups"]:
            errs.append(f"{f['path']}: group {f['group']!r} not in groups")
    for k in ("changes", "focus"):
        for n, t in enumerate(s["summary"].get(k, [])):
            need(t, ["text"], f"summary.{k}[{n}]")
            target(t, f"summary.{k}[{n}]")
    for c in s["comments"]:
        need(c, ["id", "concern", "disposition"], f"comment {c.get('id')}")
        for t in c.get("evidence", []):
            target(t, f"comment {c.get('id')} evidence")
    for c in s["checks"]:
        need(c, ["title", "status"], f"check {c.get('title')}")
    return errs


def build(a):
    s = json.loads(pathlib.Path(a.snapshot).read_text())
    errs = validate(s)
    if errs:
        sys.exit("snapshot incomplete:\n  " + "\n  ".join(errs))
    blob = json.dumps(s, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text().replace("/*__SNAPSHOT__*/", blob, 1)
    pathlib.Path(a.output).write_text(page)
    print(f"built {a.output} ({len(page) // 1024} KiB, {len(s['files'])} files)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--repo", default=".")
    c.add_argument("--base", required=True, help="base commit or ref (e.g. a merge-base)")
    c.add_argument("--head", help="head commit or ref; omit to compare against the working tree")
    c.add_argument("--untracked", nargs="*", default=[], help="untracked files to include, repo-relative")
    c.add_argument("-o", "--output", required=True)
    b = sub.add_parser("build")
    b.add_argument("snapshot")
    b.add_argument("-o", "--output", required=True)
    a = p.parse_args()
    capture(a) if a.cmd == "capture" else build(a)


if __name__ == "__main__":
    main()
