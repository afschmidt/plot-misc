"""Provides centralised access to example data sets that can be used in tests
and also in example code and/or jupyter notebooks.

The `skeleton_package.example_data.examples` module is very simple, this is
not really designed for editing via end users but they should call the two
public methods functions, `skeleton_package.example_data.examples.get_data()`,
`skeleton_package.example_data.examples.help()`.

Notes
-----
Data can be "added" either through functions that generate the data on the fly
or via functions that load the data from a static file located in the
``example_data`` directory. The data files being added  should be as small as
possible (i.e. kilobyte/megabyte range). The dataset functions should be
decorated with the ``@dataset`` decorator, so the example module knows about
them. If the function is loading a dataset from a file in the package, it
should look for the path in ``_ROOT_DATASETS_DIR``.

Examples
--------

Registering a function as a dataset providing function:

>>> @dataset
>>> def dummy_data(*args, **kwargs):
>>>     \"\"\"A dummy dataset function that returns a small list.
>>>
>>>     Returns
>>>     -------
>>>     data : `list`
>>>         A list of length 3 with ``['A', 'B', 'C']``
>>>
>>>     Notes
>>>     -----
>>>     This function is called ``dummy_data`` and has been decorated with a
>>>     ``@dataset`` decorator which makes it available with the
>>>     `example_data.get_data(<NAME>)` function and also
>>>     `example_data.help(<NAME>)` functions.
>>>     \"\"\"
>>>     return ['A', 'B', 'C']

The dataset can then be used as follows:

>>> from skeleton_package.example_data import examples
>>> examples.get_data('dummy_data')
>>> ['A', 'B', 'C']

A dataset function that loads a dataset from file, these functions should load
 from the ``_ROOT_DATASETS_DIR``:

>>> @dataset
>>> def dummy_load_data(*args, **kwargs):
>>>     \"\"\"A dummy dataset function that loads a string from a file.
>>>
>>>     Returns
>>>     -------
>>>     str_data : `str`
>>>         A string of data loaded from an example data file.
>>>
>>>     Notes
>>>     -----
>>>     This function is called ``dummy_data`` and has been decorated with a
>>>     ``@dataset`` decorator which makes it available with the
>>>     `example_data.get_data(<NAME>)` function and also
>>>     `example_data.help(<NAME>)` functions. The path to this dataset is
>>>     built from ``_ROOT_DATASETS_DIR``.
>>>     \"\"\"
>>>     load_path = os.path.join(_ROOT_DATASETS_DIR, "string_data.txt")
>>>     with open(load_path) as data_file:
>>>         return data_file.read().strip()

The dataset can then be used as follows:

>>> from skeleton_package.example_data import examples
>>> examples.get_data('dummy_load_data')
>>> 'an example data string'
"""
import os
import re
import pandas as pd

# The name of the example datasets directory
_EXAMPLE_DATASETS = "example_datasets"
"""The example dataset directory name (`str`)
"""

_ROOT_DATASETS_DIR = os.path.join(os.path.dirname(__file__), _EXAMPLE_DATASETS)
"""The root path to the dataset files that are available (`str`)
"""

_DATASETS = dict()
"""This will hold the registered dataset functions (`dict`)
"""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dataset(func):
    """Register a dataset generating function. This function should be used as
    a decorator.
    
    Parameters
    ----------
    func : `function`
        The function to register as a dataset. It is registered as under the
        function name.
    
    Returns
    -------
    func : `function`
        The function that has been registered.

    Raises
    ------
    KeyError
        If a function of the same name has already been registered.

    Notes
    -----
    The dataset function should accept ``*args`` and ``**kwargs`` and should be
    decorated with the ``@dataset`` decorator.

    Examples
    --------
    Create a dataset function that returns a dictionary.

    >>> @dataset
    >>> def get_dict(*args, **kwargs):
    >>>     \"\"\"A dictionary to test or use as an example.
    >>>
    >>>     Returns
    >>>     -------
    >>>     test_dict : `dict`
    >>>         A small dictionary of string keys and numeric values
    >>>     \"\"\"
    >>>     return {'A': 1, 'B': 2, 'C': 3}
    >>>

    The dataset can then be used as follows:

    >>> from skeleton_package.example_data import examples
    >>> examples.get_data('get_dict')
    >>> {'A': 1, 'B': 2, 'C': 3}

    """
    try:
        _DATASETS[func.__name__]
        raise KeyError("function already registered")
    except KeyError:
        pass

    _DATASETS[func.__name__] = func
    return func


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_data(name, *args, **kwargs):
    """Central point to get the datasets.

    Parameters
    ----------
    name : `str`
        A name for the dataset that should correspond to a registered
        dataset function.
    *args
        Arguments to the data generating functions
    **kwargs
        Keyword arguments to the data generating functions

    Returns
    -------
    dataset : `Any`
        The requested datasets
    """
    try:
        return _DATASETS[name](*args, **kwargs)
    except KeyError as e:
        raise KeyError("dataset not available: {0}".format(name)) from e


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_datasets():
    """List all the registered datasets.

    Returns
    -------
    datasets : `list` of `tuple`
        The registered datasets. Element [0] for each tuple is the dataset name
        and element [1] is a short description captured from the docstring.
    """
    datasets = []
    for d in _DATASETS.keys():
        desc = re.sub(
            r'(Parameters|Returns).*$', '', _DATASETS[d].__doc__.replace(
                '\n', ' '
            )
        ).strip()
        datasets.append((d, desc))
    return datasets


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def help(name):
    """Central point to get help for the datasets.

    Parameters
    ----------
    name : `str`
        A name for the dataset that should correspond to a unique key in the
        DATASETS module level dictionary.

    Returns
    -------
    help : `str`
        The docstring for the function
    """
    docs = ["Dataset: {0}\n{1}\n\n".format(name, "-" * (len(name) + 9))]
    try:
        docs.extend(
            ["{0}\n".format(re.sub(r"^\s{4}", "", i))
             for i in _DATASETS[name].__doc__.split("\n")]
        )
        return "".join(docs)
    except KeyError as e:
        raise KeyError("dataset not available: {0}".format(name)) from e


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def dummy_data(*args, **kwargs):
    """A dummy dataset function that returns a small list.

    Returns
    -------
    data : `list`
        A list of length 3 with ``['A', 'B', 'C']``

    Notes
    -----
    This function is called ``dummy_data`` and has been decorated with a
    ``@dataset`` decorator which makes it available with the
    `example_data.get_data(<NAME>)` function and also
    `example_data.help(<NAME>)` functions.
    """
    return ['A', 'B', 'C']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def dummy_load_data(*args, **kwargs):
    """A dummy dataset function that loads a string from a file.

    Returns
    -------
    str_data : `str`
        A string of data loaded from an example data file.

    Notes
    -----
    This function is called ``dummy_data`` and has been decorated with a
    ``@dataset`` decorator which makes it available with the
    `example_data.get_data(<NAME>)` function and also
    `example_data.help(<NAME>)` functions. The path to this dataset is built
    from ``_ROOT_DATASETS_DIR``.
    """
    load_path = os.path.join(_ROOT_DATASETS_DIR, "string_data.txt")
    with open(load_path) as data_file:
        return data_file.read().strip()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_forest_data(*args, **kwargs):
    """
    Loads data on the test performance of a number of polygenics scores.
    Estimates represent c-statistics with confidence intervals.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'forest_data.tsv.gz'),
        sep='\t', index_col=0
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_barchart_data(*args, **kwargs):
    """
    Loads data counting the number of associations between cardiac chambers
    (`LV`, `RV`, `LA`) and cardiac outcomes.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'barchart.tsv.gz'),
        sep='\t', index_col=0,
        **kwargs
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_heatmap_data(*args, **kwargs):
    """
    Loads data representing pvalue times direction of exposures (columns)
    effects on outcomes (rows).
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'heatmap_data.tsv.gz'),
        sep='\t', index_col=0,
        **kwargs
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_table_data(*args, **kwargs):
    """
    Loads MR data for a SAP against many outcomes. Can be used as testing
    data for table manipulations.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'table_data.tsv.gz'),
        sep='\t', index_col=0
    )
    # return
    return df


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_lollipop_data(*args, **kwargs):
    """
    Loads a feature importance table. Can be used to test the
    `machine_learning` module.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'lollipop_data.tsv.gz'),
        sep='\t', index_col=0
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_volcano_data(**kwargs):
    """
    Loads a table with effect estimates and p-values. Can be used to test the
    `volcano` module.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'volcano.tsv.gz'),
        sep='\t', index_col=0, **kwargs
    )
    # return
    return df
