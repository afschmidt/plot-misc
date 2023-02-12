#!/bin/bash
# Run from the build directory which should be directoly below the root with
# the .bumpversion.cfg in it
set -eu
curdir="$PWD"
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'
}

abort() {
    echo "[info] aborting..." 1>&2
    cd "$curdir"
    exit 1
}

trap 'abort' SIGINT

git_branch="$(parse_git_branch)"

# Version should be major, minor, patch, release, build
VERSION="$1"

# Do a dry from
curdir="$PWD"
cd ..
bumpversion --list --dry-run "${VERSION}"

# Now ask the user if that is ok
echo "[${git_branch}] Do you want to increment the version? Press [ENTER] to increment or [CTRL-C] to quit? "
read GO

if [[ "$GO" == "" ]]; then
    echo "[${git_branch}] bumping version number..."
    bumpversion "${VERSION}"
    echo "[${git_branch}] pushing..."
    git push origin "$git_branch" --follow-tags
    # Not sure if this is needed? - need to test
    # git push --tags
fi

cd "$curdir"
echo "*** END ***"
