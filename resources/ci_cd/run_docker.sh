#!/bin/bash
# Run a test build using docker on local PC, this can be used to debug CI/CD
# gitlab builds without repeated commits. The documentation is uploaded to
# pCloud static web pages for viewing.
# This will create a container called plot-misc and do the build before closing
# and removing the container. The container will also be removed on error.
# Usage
# ./run_docker.sh <image name> <repo_root> <doc_build_dir> [mode]
#   mode: "pages" (default) mirrors the docs build job; "tests" mirrors the
#         unit-test job. Only "pages" needs doc_build_dir (pass any placeholder
#         for "tests").
container_name="plot-misc"
init_dir="$PWD"
temp_dir=$(mktemp -d)

stop_docker() {
    echo "[info] stopping container..."
    docker stop "$container_name"
    echo "[info] removing container..."
    docker rm "$container_name"
    rm -r "$temp_dir"
    cd "$init_dir"
}
trap stop_docker EXIT INT SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM ERR
set -eu

# The docker image to use is the first argument and the repository root is
# the second
image="$1"
# `cd ... && pwd -P` rather than `readlink -f` so this resolves on macOS (BSD
# readlink has no -f).
repo_root="$(cd "$2" && pwd -P)"
repo_base="$(basename "$repo_root")"

# Optional 4th arg selects which CI script to mirror inside the container:
# "pages" (default) runs the docs build, "tests" runs the unit-test job.
mode="${4:-pages}"
case "$mode" in
    pages) run_script="resources/ci_cd/run_pages.sh" ;;
    tests) run_script="resources/ci_cd/run_tests.sh" ;;
    *) echo "[error] unknown mode '$mode' (expected 'pages' or 'tests')" >&2
       exit 1 ;;
esac

# The documentation build dir is only required when mirroring the docs build.
build_dir="${3:-}"
if [ "$mode" = "pages" ]; then
    : "${build_dir:?Error: doc_build_dir (arg 3) required in pages mode}"
    mkdir -p "$build_dir"
fi

# This will be the working directory in the docker image, this corresponds to
# the repository root
workdir="/tests"
echo "[info] starting directory: $PWD"
echo "[info] repo root: $repo_root"

echo "[info] starting container..."
docker run \
       -w "$workdir" \
       --name "$container_name" \
       -dit "$image" /bin/sh

echo "[info] copying repo to docker..."
docker container cp "$repo_root" "$container_name":"$workdir"/
echo "[info] executing ${mode} run (${run_script})..."
docker exec --workdir "${workdir}"/"$repo_base" "$container_name" \
       /bin/sh "${workdir}"/"$repo_base"/"$run_script"

# Only the docs build produces output to copy back out of the container.
if [ "$mode" = "pages" ]; then
    echo "[info] copying from docker..."
    docker container cp "$container_name":"${workdir}"/"$repo_base"/public "$temp_dir"
    cd "$repo_root"
    rsync -avz "$temp_dir"/public/* "$build_dir"
fi
echo "*** END ***"
