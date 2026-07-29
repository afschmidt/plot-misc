<img src="https://schmidtaf.gitlab.io/plot-misc/_images/icon.png" alt="plot-misc icon" width="250"/>

# A collection of plotting functions
__version__: `2.3.0`

This repository collects plotting modules written on top of `matplotlib`.
The functions describe plotting archetypes intended to set up light-touch,
illustrations that can be customised using the standard matplotlib interface
via axes and figures.
Because the implementation is matplotlib-first, the API is consistent with
matplotlib conventions, and users already familiar with the library will find 
the learning curve minimal.

The functionality is geared towards illustrations commonly used in biomedical 
research:

* Bar charts
* Bubble charts
* Forest plots (with optional side-tables)
* Heatmaps (with optional annotations)
* Incidence matrix plots
* Machine learning plots (calibration, feature importance, net benefit)
* Pie charts
* Survival plots (with optional survival table)
* Tree/compatibility plots
* Volcano plots

Please consult the **[documentation](https://SchmidtAF.gitlab.io/plot-misc/)** 
for plot-misc.

## Citation

If you use this package in your research please cite the
**[paper](https://academic.oup.com/bioinformaticsadvances/article/6/1/vbag184/8721292)**:

```bibtex
@article{Schmidt:2026,
  author  = {Schmidt, Amand Floriaan and Hukerikar, Nikita and
             Finan, Chris and van Vugt, Marion},
  title   = {Effective visualization of biomedical data using plot-misc},
  journal = {Bioinformatics Advances},
  volume  = {6},
  number  = {1},
  pages   = {vbag184},
  doi     = {10.1093/bioadv/vbag184},
  year    = {2026}
}
```

## Installation 
The package is available on PyPI, and conda, with the latest source code 
available on gitlab. 

### Installation using PyPI

To install the package from PyPI, run:

```bash
pip install plot-misc
```

This installs the latest stable release along with its dependencies.

### Installation using conda

A Conda package is maintained in my personal Conda channel.
To install from this channel, run:

```bash
conda install afschmidt::plot-misc
```

### Installation using gitlab

If you require the latest updates, potentially not yet formally released,
you can install the package directly from GitLab.

First, clone the repository and move into its root directory:

```bash
git clone git@gitlab.com:SchmidtAF/plot-misc.git
cd plot-misc
```

Install the dependencies:

```bash
# From the root of the repository
conda env create --file ./resources/conda/envs/conda_create.yaml
```

To add to an existing environment use:

```bash
# From the root of the repository
conda env update --file ./resources/conda/envs/conda_update.yaml
```

Next the package can be installed: 

```bash
make install
```

#### Development
For development work, install the package in editable mode with Git commit 
hooks configured:

```bash
make install-dev
```
This command installs the package in editable mode and configures Git commit 
hooks, allowing you to run `git pull` to update the repository or switch 
branches without reinstalling.

Alternatively, you can install manually:
```bash
python -m pip install -e .
python .setup_git_hooks.py
```

#### Git Hooks Configuration


When setting up a development environment, the `setup-hooks` command 
configures Git hooks to enforce conventional commit message formatting and 
spell check using `codespell`.

To view the commit message format requirements, run:

```bash
./.githooks/commit-msg -help
```

For frequent use, add this function to your shell configuration (`~/.bashrc` 
or `~/.zshrc`):

```bash
commit-format-help() {
    local git_root
    git_root=$(git rev-parse --show-toplevel 2>/dev/null)
    
    if [ -z "$git_root" ]; then
        echo "Error: Not inside a git repository"
        return 1
    fi
    
    local hook_path="$git_root/.githooks/commit-msg"
    
    if [ ! -f "$hook_path" ]; then
        echo "Error: commit-msg hook not found"
        return 1
    fi
    
    "$hook_path" --help
}
```

#### Validating the package

After installing the package from GitLab, you may wish to run the test
suite to confirm everything is working as expected:

```bash
# From the root of the repository
pytest tests
```

## Usage

Please have a look at the examples in 
[resources](https://gitlab.com/SchmidtAF/plot-misc/-/tree/master/resources/examples)
for some possible recipes. 


