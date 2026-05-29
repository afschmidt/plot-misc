#!/bin/sh
# This is assumed to be running from the root of the repo
echo "[before] running in: $PWD"
# For debugging
echo $CI_COMMIT_BRANCH
echo $CI_DEFAULT_BRANCH
python --version
git branch

# Needed for Sphinx (make in build-base) and pysam (build-base + others)
apk add build-base bzip2-dev zlib-dev xz-dev openblas-dev linux-headers openssh

# start ssh-agent
eval `ssh-agent -s`
# ssh-add -l

# Upgrade pip first
pip install --upgrade pip

# Package requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package being built/tested
pip install .

# Run all the tests
pytest tests
