#!/bin/sh
# Run the unit tests. Self-contained and image-agnostic: installs the package
# with its dev extras then runs pytest. Used by the GitLab `unit-tests` job
# (on python:*-slim) and by run_tests.sh for local Docker mirroring.
# Assumed to run from the root of the repo.
set -eu
echo "[test] running in: $PWD"
python --version

# Upgrade pip, then install the package + dev/test dependencies.
# ".[dev]" resolves to requirements.txt + requirements-dev.txt via the
# dynamic optional-dependencies in pyproject.toml.
pip install --upgrade pip
pip install ".[dev]"

# Run the test suite.
pytest tests
