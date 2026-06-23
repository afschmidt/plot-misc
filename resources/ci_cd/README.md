# Continuous integration scripts

Run and debug the GitLab pipeline locally in Docker before committing.
The pipeline is defined in `.gitlab-ci.yml`; these are its per-job commands plus
helpers to drive them locally. 
The scripts contain no Python version or image names, those live in 
`.gitlab-ci.yml`.

## Files

| File | What it does |
|------|--------------|
| `pages.sh` | The `pages` job: installs the package (`pip install ".[dev]"` — deps are baked into the image) then builds the Sphinx docs into `public/` (GitLab Pages). |
| `test.sh` | `pip install ".[dev]"` + `pytest tests`. Image-agnostic; the `unit-tests` job runs it once per Python version. |
| `run_pages.sh` / `run_tests.sh` | In-container wrappers that run `pages`/`test` for local mirroring. |
| `run_docker.sh` | Low-level: start a container from an image, copy the repo in, run one wrapper by `mode` (`pages`\|`tests`). |
| `debug_run_docker.sh` | Full local mirror: reads versions/images from `.gitlab-ci.yml` and runs the whole pipeline (`unit-tests` ×N → `pages`) in order. |

SAST is not mirrored locally (managed by GitLab; advisory anyway).

## Usage

```sh
# Whole pipeline — repo root + docs dir auto-detected, so no args needed
bash resources/ci_cd/debug_run_docker.sh

# A single job — run_docker.sh <image> <repo_root> <doc_build_dir> <mode>
bash run_docker.sh floriaan1/plot-misc:master ~/.../plot-misc /path/to/docs pages
bash run_docker.sh python:3.11-slim ~/.../plot-misc /tmp/ignore tests   # one version
```

Requires Docker, plus `python` + `pyyaml` on the host (to parse `.gitlab-ci.yml`).
