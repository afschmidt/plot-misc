'''
Constants used throughout the package
'''

import pandas as pd
import numpy.typing as npt
import numpy as np
from typing import Any, List, Type, Union, Tuple

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# NAMES

class TableNames(object):
    '''
    Often used strings
    '''
    phenotype_table = 'phenotype'
    outcome_format  = 'trait'
    exposure        = 'exposure'
    exposure_format = 'exposure_formatted'
    uniprot         = 'uniprot_id'
    uniprot_label   = 'uniprot_display_label'
    plot_label      = 'plot_label'
    pvalue          = 'pvalue'
    pvalue_log10    = 'pvalue_log10'
    file_name       = 'file_name'
    analysis        = 'analysis'
    index           = 'index'
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# make_heatmap
class MakeHeatmapNames(object):
    value_input    = 'curated_matrix_value'
    annot_input    = 'curated_matrix_annotation'
    annot_star     = 'matrix_star'
    annot_pval     = 'matrix_pvalue'
    annot_effect   = 'matrix_point_estimate'
    value_point    = 'curated_matrix_point_estimate_value'
    value_original = 'crude_point_estimate'
    source_data    = 'source_data'
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# CHECKING INPUTS

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# numpy typing
def as_array(a: npt.ArrayLike) -> np.ndarray:
    return np.array(a)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class InputValidationError(Exception):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_type(param: Any, types: Union[Tuple[Type], Type]) -> bool:
    """
    Checks if a given parameter matches any of the supplied types
    
    Parameters
    ----------
    param: object to test
    types: either a single type, or a tuple of types to test against.
    
    Returns
    -------
    True if the parameter is an instance of any of the given types.
    Raises InputValidationError otherwise.
    """
    if not isinstance(param, types):
        raise InputValidationError(f"Expected any of [{types}], got {type(param)}")
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_df(df: Any) -> bool:
    """
    Checks if objects is a pd.DataFrame.
    
    Parameters
    ----------
    df: object
    
    Returns
    -------
    True if the df is a pd.DataFrame. Raises InputValidationError otherwise.
    """
    return is_type(df, pd.DataFrame)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def are_columns_in_df(
    df: pd.DataFrame, expected_columns: Union[List[str], str],
    warning: bool=False
) -> bool:
    """
    Checks if all expected columns are present in a given pandas.DataFrame.
    
    Parameters
    ----------
    df: pandas.DataFrame
    expected_columns: either a single column name or a list of column names to test
    warning : bool, default False
        raises a warning instead of an error.
    
    
    Returns
    -------
    True if all expected_columns are in the df. Raises InputValidationError otherwise.
    """
    # constant
    message = "The following columns are missing from the pandas.DataFrame: {}"
    res = True
    # tests
    expected_columns_set: Set[str] = set(expected_columns) if isinstance(
        expected_columns, list
    ) else set([expected_columns])
    
    missing_columns = expected_columns_set - set(df.columns)
    # return
    if missing_columns:
        if warning == False:
            raise InputValidationError(
                message.format(missing_columns)
            )
        else:
            warnings.warn(
                message.format(missing_columns)
            )
            res = False
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# error messages
class Error_MSG(object):
    '''
    A collection of error messages.
    '''
    MISSING_DF = '`{}` contains missing values.'

