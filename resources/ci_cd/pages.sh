#!/bin/sh
# Build the Sphinx docs for the GitLab `pages` job. The docs image bakes in the
# dependencies + Sphinx/pandoc, but not plot_misc itself, so install the package
# (deps resolve as already-satisfied) before building. Assumed to run from the
# root of the repo.
set -eu
echo "[pages] running in: $PWD"

# Install plot_misc (+ dev extras) so Sphinx autodoc can import it.
pip install --upgrade pip
pip install ".[dev]"

# Ensure the documentation build directory is present
mkdir -p ./docs/build

cd docs
make html
cd ..
echo "[pages] removing public"
if [ -e public ]; then
    rm -r public
fi
echo "[pages] creating public"
mkdir -p public
echo "[pages] moving HTML to public"
mv docs/build/html/* public/
echo "[pages] PWD: $PWD"
echo "[pages] contents of public"
ls "$PWD"/public
