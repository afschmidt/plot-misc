# Building and uploading plot_misc to conda

## Requirements

The following packages must be installed if they are not already 
available:

```sh
conda install conda-build
conda install anaconda-client
```

### Set up an Anaconda token

If needed create an Anaconda account and set up login token 
`https://anaconda.org/<USER_NAME>/settings/access`.

Add the token to your `~/.bashrc`:

```sh
export ANACONDA_API_TOKEN=<YOUR_ACTUAL_TOKEN_HERE>
```

Finally confirm the token is found by running `anaconda whoami`. 

### Required files 

To build the package for Conda we need to ensure
there is a `meta.yaml` file which describes the 
package dependencies and Python version. 

Additionally, include a `build.sh` file detailing how the package 
should be installed.

```sh
set -ex
$PYTHON -m pip install . -vv
```

## Build the conda package locally

Ensure the package environment is active, then run:

```sh
conda build build/
```

This will build your package locally. 
The output will indicate the location; look for something like
`${HOME}/miniconda/envs/<PACKAGE_NAME>/conda-bld/noarch/<PACKAGE_NAME>-<PACKAGE_VERSION>-py_<BUILD_VERSION>.conda` . 

## Upload to conda 

```sh
anaconda upload ${HOME}/miniconda/envs/<PACKAGE_NAME>/conda-bld/noarch/<PACKAGE_NAME>-<PACKAGE_VERSION>-py_<BUILD_VERSION>.conda 
```

If you want to automatically upload to Conda, skipping the step above, please
add `anaconda_upload: true` to your `~/.condarc`. 

