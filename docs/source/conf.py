# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', '..' )))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'plot-misc'
copyright = '2024, A. Floriaan Schmidt'
author = 'A. Floriaan Schmidt'
release = '2.0.4'
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # allows integration of markodwn notebooks
    "myst_parser",
    # allows integraton of jupyter notebooks
    "nbsphinx",
    # allows notebook inclusion through .nblink files
    "nbsphinx_link",
    # auto-gen api docs from docstrings, support directives: .. automodule::
    "sphinx.ext.autodoc",
    # allows for numpy/google style docstrings parsing into sphinx
    "sphinx.ext.napoleon",
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    # 'sphinxarg.ext',
    # 'sphinx.ext.todo',
    # "sphinx_gallery.load_style",
    # 'sphinx_changelog'
]

templates_path = ['_templates']
exclude_patterns = []

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_theme_options = {
    "display_version": True,
}

# Intersphinx, links into the STD python library
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None)
}
