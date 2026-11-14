#!/usr/bin/env python3
"""Fetch a PR's review threads, review summaries, and conversation comments as JSON.

Usage: fetch_comments.py <pr-number-or-url> [-R owner/repo] [-o out.json]
Needs an authenticated `gh`.
"""
import argparse
import json
import subprocess
import sys

# ponytail: first 100 threads/reviews/comments and 50 comments per thread;
# add cursor pagination if a PR ever exceeds that (the output flags truncation).
QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      url title headRefOid
      reviewThreads(first: 100) {
        totalCount
        nodes {
          id isResolved isOutdated path line originalLine diffSide
          comments(first: 50) {
            totalCount
            nodes { databaseId author { login } body createdAt url }
          }
        }
      }
      reviews(first: 100) {
        totalCount
        nodes { author { login } state body submittedAt url }
      }
      comments(first: 100) {
        totalCount
        nodes { author { login } body createdAt url }
      }
    }
  }
}
"""


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


def author(node):
    return (node.get("author") or {}).get("login", "ghost")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pr")
    p.add_argument("-R", "--repo")
    p.add_argument("-o", "--out")
    a = p.parse_args()

    view = ["pr", "view", a.pr, "--json", "number,url"] + (["-R", a.repo] if a.repo else [])
    info = json.loads(gh(*view))
    owner, name = info["url"].split("/")[3:5]

    data = json.loads(gh("api", "graphql", "-f", f"query={QUERY}",
                         "-F", f"owner={owner}", "-F", f"name={name}",
                         "-F", f"number={info['number']}"))
    pr = data["data"]["repository"]["pullRequest"]
    t, rv, cm = pr["reviewThreads"], pr["reviews"], pr["comments"]

    out = {
        "url": pr["url"], "title": pr["title"], "head": pr["headRefOid"],
        "truncated": t["totalCount"] > len(t["nodes"])
        or rv["totalCount"] > len(rv["nodes"]) or cm["totalCount"] > len(cm["nodes"])
        or any(n["comments"]["totalCount"] > len(n["comments"]["nodes"]) for n in t["nodes"]),
        "threads": [{
            "thread_id": n["id"],
            "remote": "resolved" if n["isResolved"] else "open",
            "outdated": n["isOutdated"],
            "path": n["path"], "line": n["line"] or n["originalLine"], "side": n["diffSide"],
            "comments": [{"id": c["databaseId"], "author": author(c), "body": c["body"],
                          "created": c["createdAt"], "url": c["url"]}
                         for c in n["comments"]["nodes"]],
        } for n in t["nodes"]],
        "reviews": [{"author": author(r), "state": r["state"], "body": r["body"],
                     "submitted": r["submittedAt"], "url": r["url"]}
                    for r in rv["nodes"] if r["body"].strip()],
        "conversation": [{"author": author(c), "body": c["body"],
                          "created": c["createdAt"], "url": c["url"]} for c in cm["nodes"]],
    }
    text = json.dumps(out, indent=2)
    if a.out:
        open(a.out, "w").write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
