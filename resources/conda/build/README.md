# Building and uploading plot_misc to conda

## Requirements

The following packages need be installed if not already 
available:

```sh
conda install conda-build
conda install anaconda-client
```

### Set-up a anaconda token

If needed create an anaconda account and set up an anaconda login token 
`https://anaconda.org/<USER_NAME>/settings/access`.

add the token to your `~/.bashrc`:

```sh
export ANACONDA_API_TOKEN=<YOUR_ACTUAL_TOKEN_HERE>
```

and finally confirm the token is found `anaconda whoami`. 

### Required files 

To build the package for conda we need to ensure
there is a meta.yaml file which describes the 
package dependencies and python version. 

Additionally, there is a need to include a 
`build.sh` file detailing how the package 
should be installed.

```sh
set -ex
$PYTHON -m pip install . -vv
```

## Build the conda package locally

ensure the package environment is active and run:

```sh
conda build build/
```

This will build your package locally. 
The output will note the location, look for something like
`${HOME}/miniconda/envs/<PACKAGE_NAME>/conda-bld/noarch/<PACKAGE_NAME>-<PACKAGE_VERSION>-py_<BUILD_VERSION>.conda` . 

## Upload to conda 

```sh
anaconda upload ${HOME}/miniconda/envs/<PACKAGE_NAME>/conda-bld/noarch/<PACKAGE_NAME>-<PACKAGE_VERSION>-py_<BUILD_VERSION>.conda 
```

If you want to automatically upload to conda, skipping the step above, please
add `anaconda_upload: true` to your `~/.condarc`. 

