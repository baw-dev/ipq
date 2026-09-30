#!/bin/sh
# install.sh: install the shared skill for Claude Code or local ChatGPT/Codex.
#
# Usage: install.sh [claude|chatgpt] [--check] [--project DIR]
# The target defaults to claude. --check compares without copying.
#
# claude:  ~/.claude/skills/ipq, or DIR/.claude/skills/ipq with --project.
# chatgpt: ~/.agents/skills/ipq, or DIR/.agents/skills/ipq with --project.
# Either way it copies SKILL.md, templates/, and tools/, and touches nothing else.
# Then it prints the sha256 of each installed file beside this checkout's.
# Exit status: 0 if every file matches, else 1.

set -eu

usage() { echo "usage: install.sh [claude|chatgpt] [--check] [--project DIR]" >&2; exit 1; }

REPO=$(cd "$(dirname "$0")" && pwd)
SRC="$REPO/skill"
MODE=install
PROJECT=
TARGET=claude
case "${1:-}" in
    claude|chatgpt) TARGET=$1; shift ;;
esac
case "$TARGET" in
    claude) SKILL_DIR=.claude ;;
    chatgpt) SKILL_DIR=.agents ;;
esac

while [ $# -gt 0 ]; do
    case "$1" in
        --check) [ "$MODE" = install ] || usage; MODE=check ;;
        --project)
            [ $# -ge 2 ] && [ -z "$PROJECT" ] && [ -n "$2" ] || usage
            case "$2" in -*) usage ;; esac
            PROJECT=$2; shift ;;
        -h|--help) [ $# -eq 1 ] || usage; sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) usage ;;
    esac
    shift
done

if [ -n "$PROJECT" ]; then
    [ -d "$PROJECT" ] || { echo "no such directory: $PROJECT" >&2; exit 1; }
    PROJECT=$(cd "$PROJECT" && pwd)
    [ "$PROJECT" != "$REPO" ] || { echo "that is this checkout; give the repository to install into" >&2; exit 1; }
    DEST="$PROJECT/$SKILL_DIR/skills/ipq"
else
    DEST="$HOME/$SKILL_DIR/skills/ipq"
fi

echo "target: $TARGET"
echo "destination: $DEST"

sum() {  # sum FILE: its sha256, or the word missing
    if [ ! -f "$1" ]; then
        echo missing
    elif command -v sha256sum > /dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

files() {  # files DIR: every file under DIR, relative, sorted
    (cd "$1" && find . -type f ! -name .DS_Store ! -name '*.pyc' | sed 's|^\./||' | sort)
}

if [ "$MODE" = install ]; then
    case "$DEST" in */skills/ipq) ;; *) echo "refusing to replace $DEST" >&2; exit 1 ;; esac
    rm -rf "$DEST"
    mkdir -p "$DEST"
    (cd "$SRC" && files . | while read -r f; do
        mkdir -p "$DEST/$(dirname "$f")"
        cp "$f" "$DEST/$f"
    done)
fi

status=0
for f in $( (files "$SRC"; [ -d "$DEST" ] && files "$DEST") | sort -u); do
    here=$(sum "$SRC/$f")
    there=$(sum "$DEST/$f")
    if [ "$here" = "$there" ]; then
        printf 'same     %s  %s\n' "$there" "$f"
    else
        printf 'DIFFERS  %s  %s  (this checkout: %s)\n' "$there" "$f" "$here"
        status=1
    fi
done

if [ "$MODE" = install ]; then
    echo
    echo "installed to $DEST"
    echo "run the tool with:  python3 \"$DEST/tools/ipq.py\" --help"
    if [ -n "$PROJECT" ]; then
        echo "commit $DEST with the repository so everyone gets the same version"
    fi
fi
exit $status
