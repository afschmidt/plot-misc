#!/bin/bash
# A script to run the unit-test job inside the docker container. This is the
# test-job counterpart to run_pages.sh: it is not run by GitLab, but lets you
# locally mirror the CI `unit-tests` job (install + pytest) inside a container.
# It sources test.sh, which is pip-only and image-agnostic, so it works on the
# stock python:*-slim images used by CI as well as the custom docs image.
# It is assumed that you are in the repo mounted as the working directory.

# This is the directory where all the CI/CD scripts are located
ci_cd="resources/ci_cd"

# Run in the root of the repo
root_dir=$(basename "$PWD")
echo "[run_tests] root_dir=$root_dir"

# Make sure git likes our mounted tests dir
git config --global --add safe.directory "$PWD"

# Now run the test script
. "$ci_cd"/test.sh

echo "*** END run_tests.sh ***"
