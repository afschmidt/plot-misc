# Changelog

## Unreleased

### Added

* `c_col` in `plot_misc.volcano` allows the user to overrule `col_nsgnd` and
  `col_sgnd`

### Changed

* `plot_misc.utils.calc_matrices` now retains the order in which the outcomes
  and exposures first appear in the input data, instead of sorting both axes
  alphabetically. Pass `sort=True` to restore the previous behaviour.
* Reworked the GitLab CI/CD pipeline: unit tests now run on every merge request
  and the default branch (decoupled from the docs deploy) and block on failure;
  the tests run across Python 3.10/3.11/3.12 on stock slim images via a matrix;
  hardened the CI shell scripts (`set -eu`) and replaced the broken custom SAST
  job with the GitLab-managed template.
* `resources/ci_cd/debug_run_docker.sh` now reads the version list and images 
  from `.gitlab-ci.yml` so it stays in sync with CI. It is portable: the repo 
  root and docs build dir are auto-detected and Docker availability is 
  pre-checked, so it runs on any machine (not just the maintainer's). 
* Simplified the `pages` docs job: the package install moved into `pages.sh`
  and the separate `before_script.sh` + its `.before_script_template` anchor
  were removed. `make` is now baked into the docs image (`PERSISTENT_DEPS`)
  instead of being re-installed via `apk add` on every run.

### Removed

* `resources/ci_cd/before_script.sh` and the `.before_script_template` anchor
  in `.gitlab-ci.yml`; the docs job now runs `pages.sh` directly (which installs
  the package then builds the docs).
* Dead bioinformatics-template leftovers from the docs Docker image
  (`resources/docker/plot-misc/master/Dockerfile`): the `libdeflate`/
  `libdeflate-dev` (cyvcf), `openssh` (only used by the removed ssh-agent), and
  commented `llvm11`/numba build dependencies. 

### Fixed

* `plot_misc.machine_learning` imported `Self` from `typing`, which only exists
  on Python 3.11+, breaking imports on the declared-supported Python 3.10. It
  now falls back to `typing_extensions.Self` on 3.10.

## 2.2.2 - 2026-06-23

### Added

* `plot_misc.heatmap.masked_heatmap`, a two-layer heatmap that draws a
  single-colour background and overlays the heatmap only on the cells flagged
  by a binary `indicator` table the same shape as `data`. 
* `examples.qc_matrix`, a dummy quality-control data set (signed standardised
  deviations plus a binary pass/fail indicator) showcasing `masked_heatmap`.
* Masked-heatmap cells added to the `resources/examples/heatmap.ipynb` and
  `resources/examples/tldr/heatmap.ipynb` notebooks.
* Example notebooks for the `plot_misc.utils.utils` helpers: a concise TLDR
  notebook `resources/examples/tldr/utils.ipynb` and a detailed worked-out
  notebook `resources/examples/utils.ipynb`.
* Corresponding `.nblink` files under `docs/source/examples/plots/` and
  `docs/source/examples/plots/tldr/`, linked into the `nbgallery` and the
  "Worked out examples" toctree in `docs/source/index.rst`.
* `calc_matrices` `symbol` argument to set the significance marker glyph to
  any text/unicode string (e.g. `'●'`, `'◆'`); previously fixed to `'★'`.
* `calc_matrices` `annotate='symbol'` option, replacing `'star'` as the
  significance-marker selector.
* `calc_matrices` p-value annotation options `'pvalues_signed'`,
  `'pvalues_unsigned'`, and `'pvalues_raw'`, controlling whether the
  annotation shows signed -log10, unsigned -log10, or the raw p-value. The
  numeric value matrix remains signed -log10 regardless.
* `MatrixHeatmapResults` now exposes two further numeric p-value tables,
  `curated_matrix_value_unsigned_log` (unsigned -log10) and
  `curated_matrix_value_raw` (raw p-values), alongside the signed -log10
  `curated_matrix_value`.

### Changed

* `calc_matrices` `annotate` now defaults to `'symbol'` (was `'star'`); the
  default output is unchanged. The `annotate` argument is now a typed
  `Literal` of the supported options.
* `_format_matrices` no longer takes a `log` argument; p-values are always
  -log10 transformed and the numeric `curated_matrix_value` is consistently
  signed -log10.
* `calc_matrices` `alpha` is now a raw p-value in (0, 1] (default `0.05`),
  consistent with `volcano`; it is converted internally to a -log10 threshold.
  Values outside (0, 1] raise `InputValidationError`.
* `calc_matrices` `ptrun` is now a raw p-value in (0, 1] (default `1e-16`),
  consistent with `alpha`; the old exponent convention was removed. Values
  outside (0, 1] raise `InputValidationError`.

### Deprecated

* `calc_matrices` `annotate='star'` is deprecated in favour of `'symbol'`.
* `calc_matrices` `annotate='pvalues'` is deprecated in favour of
  `'pvalues_signed'`.
* `calc_matrices` `without_log` is deprecated and no longer changes behaviour
  (p-values are always -log10 transformed); use `curated_matrix_value_raw`
  for raw p-values.

### Fixed

* `annotate_heatmap` no longer raises `MaskError` on masked arrays; masked
  cells (e.g. from `masked_heatmap`) are skipped so only visible cells are
  annotated.
* `masked_heatmap` now rejects a shape mismatch between `data` and `indicator`
  on the full 2D shape (previously only the row count was checked, so a column
  mismatch raised an opaque `IndexError`), and applies `background_zorder` to
  the background grid lattice.
* `segment_labelled` now rotates the midpoint label to align with the drawn
  segment. The second endpoint was transformed with the wrong x-coordinate
  (`y[0]` instead of `x[1]`), producing an incorrect text angle whenever
  `x[1] != y[0]`.
* `masked_heatmap` per-cell outlines are no longer clipped by the axes boundary
  on edge cells (outline patches now default to `clip_on=False`).

## 2.2.1 - 2026-05-30

### Added

* TLDR notebooks split into per-plot files under `resources/examples/tldr/`
  (`barcharts`, `bubblechart`, `forestplot`, `heatmap`, `incidencematrix`,
  `machine_learning`, `pychart`, `survival`, `treeplot`, `volcanoplot`),
  each with minimal self-contained examples. The original `tldr.ipynb` has
  been removed.
* Corresponding `.nblink` files added under
  `docs/source/examples/plots/tldr/` and linked in `docs/source/index.rst`.
* New `load_forest_preprocessed` dataset loader in
  `plot_misc/example_data/examples.py`, returning a plot-ready DataFrame
  with colour and shape columns attached.
* Barchart `group_positions` parameter to control bar positions within
  groups.
* Examples for saving metadata with PDFs and applying compression with TIFFs
  added to the publication-ready notebook.

### Changed

* `resources/build/inc_version.sh` improved: simplified git branch detection
  and now also updates `CHANGELOG.md` automatically on version bump.
* CI/CD: unified pip dependencies across pipeline stages and removed stale
  code and comments.

### Fixed

* Heatmap: threshold now applied to raw values instead of normalised values.
* Barchart: grouped bar charts were using the same position for every bar
  within a group.
* Function and class naming inconsistencies corrected; boolean handling
  brought in line with coding standards.

### Removed

* Redundant `conftest.py` removed from the test suite.

## v2.2.0 - 18-02-2026

### Fixed

- Fixed a `pytest.raises` error for `plot_table`.
- Added missing `test_survival` test.
- Renamed `commit-spell.sh` to `pre-commit` to comply with git hook name
  conventions.

### Added

- Git hook enforcing commit message standards.
- Added the `.githooks` directory and script.
- `codespellrc` and ignore word list.
- Makefile: generalised GitLab install and path to the git hooks
    setup script; git hook install now handled via `make install`.
- Started a publication-ready tips notebook, expanding tutorials on tick
  labels and locations.

### Changed

- Incidencematrix parameter arguments updated.
- Volcano module refactored: updated colour arguments, added
  `vline_kwargs_dict`, and updated the example notebook.
- Heatmap refactored: removed redundant tests and cleaned the example file.
- Example notebooks updated, correcting spelling mistakes and removing
  redundant help calls.
- Numerous spelling and grammar fixes across documentation.

### Deprecated

_Nothing_

### Removed

- Clustermap removed from the heatmap module, as it no longer fits the
  package aim.
- Seaborn dependency removed.

## v2.1.0 - 30-10-2025

### Fixed

- forestplot notebook. 

### Added

- Added `midpoints` parameter to `annotate_axis_midpoints` function which 
  overwrites the `gap` argument. 
- Added `survival` module and notebook supporting survival plots with bottom 
  survival table. 
- Additional colour schemes to the utils.colour module.
- `text_wrap` function in utils.formatting to automatically break a string 
 into multiple lines with optional line break character. 
- introduced x and y coordinate parameters in incidencematrix allowing the 
  user to match coordinates when creating multiple plots in for example a
  gridspec.


### Changed

- Documentation improvements.

### Deprecated

_Nothing_ 

### Removed

_Nothing_

## v2.0.4 - 14-08-2025

### Fixed

- Added missing versioning in the pyproject.toml for the required and optional packages.

### Added

_Nothing_

### Changed

- Improved the example notebooks and documentation.
- Brought the docker requirements image in line with the current software versions. 
- stack_bar now uses bar internally instead of matplotlib.Axes.bar. 
- split the requirements.txt into requirements.txt and requirements-dev.txt, updating the CI/CD scripts to pip install both. 

### Deprecated

_Nothing_ 

### Removed

_Nothing_

## v2.0.3 - 08-08-2025

### Fixed

_Nothing_

### Added

_Nothing_

### Changed

- Updated the sci_notation parameters to include both `max` and `min` windsoring. 
- `MatrixHeatmapResults` now inherits from the general `Results` class.
- Improved the documentation - added a design_philosophy.rst to explain how the design philosophy of the module and explain 
 how code contributions can best adhere to this. 
- Introduced the `Real` type hint for the `utils` code. 

### Deprecated

_Nothing_ 

### Removed

_Nothing_

## v2.0.1 - 29-07-2025

### Fixed

- Upgraded adjustText to 1.3 or higher to deal with an error where the `lim` keyword was incorrectly passed to FancyArrowPatch. 

### Added

_Nothing_. 

### Changed

- Slightly changed the pyproject.toml and meta.yaml file to handle the license correctly (changed to US spelling instead of licence). 

### Deprecated

_Nothing_. 

### Removed

_Nothing_. 

## v2.0.0 - 24-07-2025

### Fixed

- Minor bug fixes. 

### Added

- Expanded code based to publish package on conda. 
- `annotate_axis_midpoints` was added to `utils.utils`. The function adds a string placed exactly in the mid of two points. Useful to create headers in plots with lots of groups. 
- Added `Real` type hint to replace `int | float`. 
- Included further pytests for modules with low coverage (below 80%). 
- Included a `raising issues` tutorial.

### Changed

- The entire documentation has been refactored to be numpy compliant. 
- All notebooks have been updated showcasing the new functionality.
- The following modules were refactored, where needed replacing function by classes: `barchart`, `forest`, `incidencematrix`, `pychart`. 
- `assign_distance` can now deal with groups of different sizes. 
- moved much of the function and classes outside the constants module into the `errors.py` module instead. 
- The plot-table now standardise the x-axis to the `[0, 1]` range to improve alignments.

### Deprecated

_Nothing_. 

### Removed

- `assign_distance` is replaced by `set_y_coordinates`. 

## v1.1.1 - 29-03-2025

### Fixed

- Bug fixes to pychart. 
- Bug fixes to utils.utils.calc_matrix.

### Added

- Where relevant add __repr__
- Added some additional colours. 
- Added a grouped bar chart. 

### Changed

- Migrated to pyproject.toml instead of setup.py
- Where relevant ensure all functions return ax.figure if an ax is supplied. 
This replaces returning a None value.
- Document clarifications. 
- `assign_distance` can now deal with groups of different sizes. 

### Deprecated

_Nothing_

### Removed

_Nothing_

## v1.1.0 - 23-02-2024

### Fixed

_Nothing_

### Added

- A DecisionCurve class in the machine_learning.

### Changed

- Updated examples.
- Changed the default behaviour of assign_distance to not sort rows. 

### Deprecated

_Nothing_

### Removed

- Removes KD test function.
- Removes table module.

## v1.0.0 - 15-02-2024

### Fixed

_Nothing_

### Added

- Piechart module `pychart`.
- A point estimate formatting function in `utils.formatting`.
- A empirical support class to plot trees. 
- Pytest for the new functions.
- Adding sphinx documentation
- Gitlab CI/CD

### Changed

- Updated the python requirements, currently build for python 3.12.

### Deprecated

_Nothing_

### Removed

_Nothing_

## v0.3.0 - 29-06-2023

### Fixed

- Fixed documentation
- Various fixes to `forest.py`

### Added

- Expanded the number of input tests.
- Added a `_dict_string_argument` function to test the content of pd.DataFrame columns or pd.Series.
- Started a `test_constants.py` module. 
- Verbose argument to some functions.

### Changed

- volcano.py now calls `ax` instead of `plt` to set limits and labels. 

### Deprecated

_Nothing_

### Removed

_Nothing_

## v0.2.0 - 27-03-2023

### Fixed

- Updated installation instructions and removed redundancies.
- Fixed documentation


### Added

- seaborn clustermap wrapper.
- Added additional arguments for plot_forest.
- Added `plot_table` function to `forest`, including example and tests.

### Changed

_Nothing_

### Deprecated

_Nothing_

### Removed

_Nothing_


## v0.1.0 - 12-02-2023

### Fixed

- Various minor changes in the arguments, improving logic and fixing some bugs
- kwargs in nested functions can now be overwritten by simply using the kwargs_dicts using `_update_kwargs` to ensure the `kwargs_dicts` take precedence .

### Added

- Added unit tests for all plotting modules
- Added example data
- Added additional examples under resources
- Various naming objects in constants.py

### Changed

- Updated examples reflecting minor changes in the code base
- Moved colour.py to utils.
- Dependencies: matplotlib 3.5.*

### Deprecated

- Added a futurewarning warning that  plot_misc.table.layout will be moved to the module `data_clean` (outside of plot_misc).

### Removed

_Nothing_

## v0.0.1.a0 - 05-01-2023

### Fixed

_Nothing_

### Added

- Started a changelog. 

### Changed

_Nothing_

### Deprecated

_Nothing_

### Removed

_Nothing_

