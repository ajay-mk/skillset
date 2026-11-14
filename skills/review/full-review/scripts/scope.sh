#!/bin/sh
# Print the full-review scope block. Usage: scope.sh [PR number | ref | range]
# Exits non-zero on a bad ref or an empty scope, before any pass launches.
set -e
arg=$1
untracked="" body="" checkout=""

if [ -n "$arg" ] && [ -z "$(printf %s "$arg" | tr -d 0-9)" ]; then
  diff="gh pr diff $arg"
  files=$(gh pr view "$arg" --json files --jq '.files[].path')
  log=$(gh pr view "$arg" --json commits --jq '.commits[] | .oid[0:7] + " " + .messageHeadline + "\n" + .messageBody')
  base=$(gh pr view "$arg" --json baseRefName --jq .baseRefName)
  body=$(gh pr view "$arg" --json body --jq .body)
  head=$(gh pr view "$arg" --json headRefOid --jq .headRefOid)
  [ "$head" = "$(git rev-parse HEAD)" ] && checkout=ok || checkout=mismatch
elif [ -n "$arg" ]; then
  case $arg in
    *..*) range=$arg; logrange=$arg ;;
    *) git rev-parse -q --verify "$arg^{commit}" >/dev/null || { echo "bad ref: $arg" >&2; exit 1; }
       range="$arg...HEAD"; logrange="$arg..HEAD" ;;
  esac
  diff="git diff $range"
  base=$arg
  log=$(git log --format='%h %B' "$logrange")
else
  base=""
  for b in main master "$(git symbolic-ref -q --short refs/remotes/origin/HEAD || true)"; do
    [ -n "$b" ] && git rev-parse -q --verify "$b^{commit}" >/dev/null || continue
    base=$(git merge-base HEAD "$b") && break
  done
  if [ -n "$base" ] && [ "$base" != "$(git rev-parse HEAD)" ]; then
    diff="git diff $base"  # includes uncommitted edits
    log=$(git log --format='%h %B' "$base..HEAD")
  else
    diff="git diff HEAD"
    base=""
    log=""
  fi
  untracked=$(git ls-files --others --exclude-standard)
fi

case $diff in git*) files=$($diff --name-only) ;; esac
if [ -z "$files" ] && [ -z "$untracked" ]; then
  echo "empty scope: $diff has no changes" >&2
  exit 1
fi

cat <<EOF
diff: $diff
base: ${base:-none}
commits:
${log:-  (none)}
${body:+pr-body:
$body
}${checkout:+checkout: $checkout
}files:
$files
untracked:
${untracked:-  (none)}
status-before:
$(git status --porcelain)
EOF
