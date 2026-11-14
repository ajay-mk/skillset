#!/bin/sh
# Symlink this repo's skills into Claude Code and Codex.
# Safe to re-run: correct links are left alone, links into this repo that moved
# are updated, and anything else in the way is reported and skipped.
set -e

repo=$(cd "$(dirname "$0")" && pwd -P)
n=0

# link <source in repo> <link path>
link() {
  tool=${2#"$HOME"/}; tool=$HOME/${tool%%/*}
  [ -d "$tool" ] || return 0  # that tool is not installed
  mkdir -p "$(dirname "$2")"
  if [ "$(readlink "$2" 2>/dev/null)" = "$1" ]; then
    echo "ok    $2"
  elif case "$(readlink "$2" 2>/dev/null)" in "$repo"/*) true ;; *) false ;; esac; then
    ln -sfn "$1" "$2"
    echo "moved $2"
  elif [ -e "$2" ] || [ -L "$2" ]; then
    echo "skip  $2 already exists, pointing at $(readlink "$2" || echo 'a real file')" >&2
  else
    ln -s "$1" "$2"
    echo "link  $2"
    n=$((n + 1))
  fi
}

# skills/<group>/<skill>/SKILL.md; links are flat, named by skill
for dir in "$repo"/skills/*/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  dir=${dir%/}; name=$(basename "$dir")
  link "$dir" "$HOME/.claude/skills/$name"
  link "$dir" "$HOME/.codex/skills/$name"
done

echo "$n new link(s)"
