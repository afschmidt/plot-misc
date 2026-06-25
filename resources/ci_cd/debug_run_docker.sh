#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# debug_run_docker.sh – run the whole GitLab pipeline locally in Docker.
#
# Mirrors the runner end to end, in GitLab stage order:
#   test    -> unit-tests matrix    (one container per Python version)
#   deploy  -> pages docs build     (only if the test stage passed)
#
# Portable: the repo root is auto-detected from this script's location and the
# Python versions + images are read from <repo>/.gitlab-ci.yml, so it works on
# any machine. SAST is not mirrored (managed by GitLab; advisory anyway).
#
# Usage:
#   bash resources/ci_cd/debug_run_docker.sh [repo_root] [doc_build_dir]
#
# Defaults:
#   repo_root      auto-detected (two levels up from this script)
#   doc_build_dir  ${HOME}/google_drive/Research/ci_docs_builds/<repo> when that
#                  parent exists, else /tmp/<repo>-docs
#
# Options:
#   -h, --help   Show this help
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    sed -n '2,/^# ---/p' "$0" | sed '$d' | sed 's/^# \?//'
    exit 0
fi
set -uo pipefail

readonly PREFERRED_BUILD_PARENT="${HOME}/google_drive/Research/ci_docs_builds"
readonly DOCKER_INSTALL_URL="https://docs.docker.com/engine/install/"
readonly DOCKER_GET_URL="https://docs.docker.com/get-docker/"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
run_docker="${script_dir}/run_docker.sh"

# Repo root: explicit arg, else auto-detected two levels up (this script lives
# in <repo>/resources/ci_cd). Uses `pwd -P`, not `readlink -f`, so it also
# works on macOS.
if [[ -n "${1:-}" ]]; then
    repo_root="$(cd "${1}" && pwd -P)"
else
    repo_root="$(cd "${script_dir}/../.." && pwd -P)"
fi
repo_base="$(basename "${repo_root}")"
gitlab_ci="${repo_root}/.gitlab-ci.yml"

# Docs build dir: explicit arg, else the maintainer's layout when present, else
# a /tmp fallback so it works on any machine.
if [[ -n "${2:-}" ]]; then
    doc_build_dir="${2}"
elif [[ -d "${PREFERRED_BUILD_PARENT}" ]]; then
    doc_build_dir="${PREFERRED_BUILD_PARENT}/${repo_base}"
else
    doc_build_dir="/tmp/${repo_base}-docs"
fi

if [[ ! -f "${gitlab_ci}" ]]; then
    echo "[error] .gitlab-ci.yml not found at ${gitlab_ci}" >&2
    exit 1
fi

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Verify docker is installed and the daemon is reachable; print OS-aware hints
# and exit non-zero otherwise.
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "[error] Docker is not installed (no 'docker' on PATH)." >&2
        case "$(uname -s)" in
            Linux)  echo "[error] Install Docker Engine: ${DOCKER_INSTALL_URL}" >&2
                    echo "[error] then: sudo usermod -aG docker \"\$USER\" && newgrp docker" >&2 ;;
            Darwin) echo "[error] Install Docker Desktop (brew install --cask docker), or ${DOCKER_GET_URL}" >&2 ;;
            *)      echo "[error] Install Docker: ${DOCKER_GET_URL}" >&2 ;;
        esac
        exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
        echo "[error] Docker is installed but the daemon is not reachable." >&2
        echo "[error] Start it (e.g. 'sudo systemctl start docker'), ensure your" >&2
        echo "[error] user is in the 'docker' group, or re-run with sudo." >&2
        exit 1
    fi
}
check_docker

# Need python + pyyaml on the host to read the pipeline definition.
py="$(command -v python3 || command -v python || true)"
if [[ -z "${py}" ]]; then
    echo "[error] python (with pyyaml) is required to parse .gitlab-ci.yml" >&2
    exit 1
fi

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read the unit-tests matrix versions + the per-job images straight from
# .gitlab-ci.yml so local mirroring can never drift from CI.
versions=()
images=()
docs_img=""
while read -r kind a b; do
    case "${kind}" in
        VER)  versions+=("${a}"); images+=("${b}") ;;
        DOCS) docs_img="${a}" ;;
    esac
done < <("${py}" - "${gitlab_ci}" <<'PY'
import sys, yaml
d = yaml.safe_load(open(sys.argv[1]))
ut = d["unit-tests"]
pat = ut["image"]
for v in ut["parallel"]["matrix"][0]["PY_VERSION"]:
    print("VER", v, pat.replace("${PY_VERSION}", str(v)))
print("DOCS", d["image"]["name"].strip())
PY
)

if [[ ${#versions[@]} -eq 0 || -z "${docs_img}" ]]; then
    echo "[error] failed to parse jobs/versions from ${gitlab_ci}" >&2
    echo "        (is pyyaml installed? does the unit-tests matrix exist?)" >&2
    exit 1
fi

echo "[info] repo root:      ${repo_root}"
echo "[info] doc build dir:  ${doc_build_dir}"
echo "[info] test versions:  ${versions[*]}"
echo "[info] docs img:       ${docs_img}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run a single containerised job via run_docker.sh and capture its exit code.
#
# Parameters
# ----------
#   $1 - image : Docker image to run in.
#   $2 - mode  : run_docker.sh mode (tests|pages).
#
# Returns
# -------
#   The exit code of run_docker.sh.
# ---------------------------------------------------------------------------
run_job() {
    local image="${1}"
    local mode="${2}"
    bash "${run_docker}" "${image}" "${repo_root}" "${doc_build_dir}" "${mode}"
}

summary=()
overall_rc=0

# --- test stage (blocking, all legs run) -----------------------------------
test_failed=0
for idx in "${!versions[@]}"; do
    ver="${versions[$idx]}"
    img="${images[$idx]}"
    echo
    echo "===== test: unit-tests py${ver} (${img}) ====="
    rc=0
    run_job "${img}" tests || rc=$?
    if [[ ${rc} -eq 0 ]]; then
        summary+=("PASS  test/unit-tests py${ver} (${img})")
    else
        summary+=("FAIL  test/unit-tests py${ver} (${img}) [rc=${rc}]")
        test_failed=1
        overall_rc=1
    fi
done

# --- deploy stage (only if test stage passed, mirroring GitLab) ------------
echo
if [[ ${test_failed} -eq 0 ]]; then
    echo "===== deploy: pages (${docs_img}) ====="
    rc=0
    run_job "${docs_img}" pages || rc=$?
    if [[ ${rc} -eq 0 ]]; then
        summary+=("PASS  deploy/pages (${docs_img})")
    else
        summary+=("FAIL  deploy/pages (${docs_img}) [rc=${rc}]")
        overall_rc=1
    fi
else
    echo "===== deploy: pages SKIPPED (test stage failed, as GitLab would) ====="
    summary+=("SKIP  deploy/pages (test stage failed)")
fi

# --- summary ---------------------------------------------------------------
echo
echo "================== local pipeline summary =================="
for line in "${summary[@]}"; do
    echo "  ${line}"
done
echo "============================================================"
if [[ ${overall_rc} -eq 0 ]]; then
    echo "[info] pipeline PASSED"
else
    echo "[error] pipeline FAILED"
fi
exit ${overall_rc}
