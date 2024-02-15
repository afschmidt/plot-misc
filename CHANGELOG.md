# Changelog

## v1.0.0 - 15-02-2024

### Fixed

_Nothing_

### Added

- Piechart module `pychart`.
- A point estimate formatting function in `utils.formatting`.
- A emperical support class to plot trees. 
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

