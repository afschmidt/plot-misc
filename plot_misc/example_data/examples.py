"""Provides centralised access to example data sets that can be used in tests
and also in example code and/or jupyter notebooks.

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
import numpy as np
from plot_misc.constants import (
    UtilsNames,
    ForestNames,
)

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
def dummy_data():
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
def dummy_load_data():
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
def load_forest_data(**kwargs):
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
        sep='\t', index_col=0, **kwargs,
    )
    # add y-axis
    df[ForestNames.y_col] = \
        [
            0.0, 2.0, 4.0, 0.0, 2.0, 4.0, 0.0, 2.0, 4.0, 10.0, 12.0,
            14.0, 10.0, 12.0, 14.0, 10.0, 12.0, 14.0, 20.0, 22.0, 24.0,
            20.0, 22.0, 24.0, 20.0, 22.0, 24.0, 30.0, 32.0, 34.0, 30.0,
            32.0, 34.0, 30.0, 32.0, 34.0, 40.0, 42.0, 44.0, 40.0, 42.0,
            44.0, 40.0, 42.0, 44.0, 50.0, 52.0, 54.0, 50.0, 52.0, 54.0,
            50.0, 52.0, 54.0
        ]
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_barchart_data(**kwargs):
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
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_heatmap_data(**kwargs):
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
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_lollipop_data(**kwargs):
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
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_net_benefit_data(**kwargs):
    """
    Loads a table containing the predicted probabilities for two models, as
    well as the outcome data. Can be used to test the `machine_learning` module.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'net_benefit.tsv.gz'),
        sep='\t', index_col=False, **kwargs,
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def heatmap_data(**kwargs):
    """
    Creates a dummy results pd.DF object to test the `make_heatmap` program.
    """
    data = pd.DataFrame({
        UtilsNames.mat_index: [
            'ldlc_glgc', 'hdlc_glgc', 'ldlc_glgc', 'hdlc_glgc', 'ldlc_glgc',
            'hdlc_glgc', 'ldlc_glgc', 'hdlc_glgc'
        ],
        UtilsNames.mat_exposure: [
            'SCF', 'SCF', 'TRAIL', 'TRAIL', 'IP10', 'IP10', 'IL2ra', 'IL2ra'
        ],
        UtilsNames.mat_outcome: [
            'LDL-C', 'HDL-C', 'LDL-C', 'HDL-C', 'LDL-C', 'HDL-C', 'LDL-C',
            'HDL-C'
        ],
        UtilsNames.mat_point: [
            np.nan, 0.0278005, np.nan,  -0.15723944, 0.0321544, -0.02524,
            -0.2353, 0.023522
        ],
        UtilsNames.mat_pvalue: [
            np.nan, 0.000534346, np.nan, 0.20464, 0.0001, 0.95426, 0.0052353,
            0.25353
        ]
    }, **kwargs)
    data.index = data[UtilsNames.mat_index]; data.index.name = 'index'
    return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def heatmap_point_matrix(**kwargs):
    """
    Creates a dummy results pd.DF object to test the `make_heatmap` program.
    Includes point estimates.
    """
    data = pd.DataFrame({
        UtilsNames.mat_exposure_list[0]: [
            0.023522, -0.233500,
        ],
        UtilsNames.mat_exposure_list[1]: [
            -0.025240, 0.032154,
        ],
        UtilsNames.mat_exposure_list[2]: [
            np.nan, np.nan,
        ],
        UtilsNames.mat_exposure_list[3]: [
            -0.0157239, 0.027800
        ],
    }, **kwargs)
    data.index = UtilsNames.mat_outcome_list
    data.index.name = UtilsNames.mat_outcome
    return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def heatmap_pvalue_matrix(**kwargs):
    """
    Creates a dummy results pd.DF object to test the `make_heatmap` program.
    Includes p-values.
    """
    data = pd.DataFrame({
        UtilsNames.mat_exposure_list[0]: [
            0.253530, 0.005235,
        ],
        UtilsNames.mat_exposure_list[1]: [
            0.95426, 0.00010,
        ],
        UtilsNames.mat_exposure_list[2]: [
            np.nan, np.nan,
        ],
        UtilsNames.mat_exposure_list[3]: [
            0.204640, 0.000534,
        ],
    }, **kwargs)
    data.index = UtilsNames.mat_outcome_list
    data.index.name = UtilsNames.mat_outcome
    return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_calibration_data(**kwargs):
    """
    Loads a table with binary outcomes and predicted risk. Can be used to test
    the `machine_learning.calibration` function.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'calibration_data.tsv.gz'),
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_calibration_bins(**kwargs):
    """
    Loads a table with observed and predicted risk in 6 equally sized bins,
    with lower and upper 95% confidence intervals for the observed risk. Can
    be used to test the `machine_learning.calibration` function.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'calibration_bins.tsv.gz'),
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_incidence_matrix_data(**kwargs):
    """
    Loads a table linking genes to traits, represented by a `1` with a `0`
    for genes and traits without a potential assocaition.
    
    Returns
    -------
    pd.DataFrame
    """
    # files
    df = pd.read_csv(
        os.path.join(_ROOT_DATASETS_DIR, 'incidence_matrix_data.tsv.gz'),
        sep='\t', index_col=0, **kwargs,
    )
    # return
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataset
def load_pychart_data(**kwargs):
        # List of genes
    genes = ['PKP2', 'MYL2', 'JUP', 'DSC2', 'DSG2', 'TTN', 'DES', 'DSP', 'PLN', 'RBM20', 'BAG3']
    # Initialize data with zeros for genes
    data = np.zeros((100, len(genes)), dtype=int)
    # Assign each patient one gene
    np.random.seed(0)  # For reproducibility
    for row in data:
        row[np.random.randint(len(genes))] = 1
    # Create DataFrame
    df = pd.DataFrame(data, columns=genes)

    df['HCM'] = np.random.choice([0, 1], 100)
    df['DCM'] = 1 - df['HCM']
    return df

