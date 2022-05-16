'''
Formatting tables
'''
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# import
import os
import warnings
import pandas as pd
import numpy as np
from types import FunctionType
from typing import Any, List, Type, Union, Tuple
from plot_misc.constants import (
    TableNames,
    is_type,
    is_df,
    are_columns_in_df
)

# constants
MAXLOG10=20

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _nlog10_func(p, max=MAXLOG10):
    """
    computes negative log10 p-value
    
    Parameters
    ----------
    p : pandas.Series
        p-values.
    max : int, optional
        cutoff which replaces 0. The default is 16.
    
    Returns
    -------
    pandas.Series
    
    """
    # which values are rounded to zero
    notzero = p == 0
    # transform
    nlog10 = -1 * np.log10(p)
    # replacing zero
    nlog10[notzero] = max
    # truncating
    nlog10[nlog10 > max] = max
    # removing sign
    nlog10[nlog10 == -0] = 0
    # returning
    return(nlog10)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Formatting function

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _apply_and_rename(data:pd.DataFrame, original_columns:list,
                      new_columns:Union[list, type(None)]=None,
                      drop_original:bool=False,
                      func:Union[FunctionType, type(None)]=None):
    '''
    Applies a function across a subset of pandas DataFrame columns and assigns
    these columns to either the same or a different set of column names.
    
    Parameters
    ----------
    data : pd.DataFrame,
    original_columns : list,
        The column names that need to be manipulated
    new_columns : list, default NoneType,
        The new column names
    drop_original : bool, default False,
        Should the original column names be dropped. Only works when
        `new_columns` names are supplied.
    func : function, default NoneType
        The function that should be applied to each column
    
    Returns
    -------
    pd.DataFrame
    '''
    # check input
    is_df(data)
    is_type(original_columns, (list, type(None)))
    is_type(new_columns, (list, type(None)))
    is_type(drop_original, bool)
    is_type(func,(FunctionType, type(None)))
    # ### check format
    are_columns_in_df(data, original_columns)
    if not new_columns is None:
        if len(original_columns) != len(new_columns):
            raise ValueError('`original_columns` and `new_columns` have a different'
                             ' number of elements'
                             )
    if drop_original == True and new_columns is None:
        raise ValueError('Please supply `new_columns')
    # ### the actual work
    if new_columns is None:
        new_columns = original_columns
    # run the for loop
    if func is None:
        for ocol, ncol in zip(original_columns, new_columns):
            data[ncol] = data[ocol]
    else:
        for ocol, ncol in zip(original_columns, new_columns):
            data[ncol] = func(data[ocol])
    # do we want to drop the original columns
    if drop_original == True:
        data.drop(original_columns, axis=1, inplace=True)
    # return stuff
    return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def formatting(data, strip_columns:list=None, replace_string_columns:dict=None,
               log10_columns:list=None, rename_columns:dict=None,
               drop_original:bool=True, rename_column_values:dict=None,
               order_columns:list=None, ):
    '''
    Formats a table using the following optionals:
        - Stripping white space from string columns
        - Substituting strings
        - -1*log10 transformations on numerical columns
        - Moves columns towards the front,
        - Renames column (either retaining or dropping the original columns)
    
    Returns the same input data if none of the optional arguments are supplied!
    
    Parameters
    ----------
    data : pd.DataFrame,
    strip_columns : list of strings, default Nonetype
        The column names which should be stripped.
    replace_string_columns : dict, default Nonetype
        A dictionary wit the column names as keys and a two element list
        for the original string and replacement string (in that order!).
    log10_columns : list of strings, default Nonetype
        Applies a -1 * log10 transformation.
    rename_columns : dict, default Nonetype
        A dictionary with the original names as keys, and the new names as
        values.
    rename_column_values : dict of dicts, default Nonetype
        A dictionary with the column as key, and a dictionary{old:new} as
        value.
    drop_original : bool, default True,
        Removes the original names in `rename_columns`.
    order_columns : list of string, default Nonetype,
        Columns moved to the front of the dataframe.
    
    Returns
    -------
    pd.DataFrame
    '''
    # ### check input
    is_df(data)
    is_type(strip_columns, (list, type(None)))
    is_type(log10_columns, (list, type(None)))
    is_type(order_columns, (list, type(None)))
    is_type(replace_string_columns, (dict, type(None)))
    is_type(rename_columns, (dict, type(None)))
    is_type(rename_column_values, (dict, type(None)))
    is_type(drop_original, bool)
    # ### copy()
    frame = data.copy()
    # ### renaming
    if not rename_columns is None:
        frame=_apply_and_rename(
            frame.copy(),
            original_columns=list(rename_columns.keys()),
            new_columns=list(rename_columns.values()),
            drop_original=drop_original,
        )
    # ### renaming column values
    if not rename_column_values is None:
        for key, value in rename_column_values.items():
            frame[key] = frame[key].map(value)
    # ### strip strings
    if not strip_columns is None:
        # do we need to strip the index
        if TableNames.index in strip_columns:
            frame.index = frame.index.str.strip()
            # remove index from strop_columns
            strip_columns2 = [s for s in strip_columns if s !=TableNames.index]
        else:
            strip_columns2 = strip_columns
        # strip the remaining
        if len(strip_columns2) > 0:
            for col in strip_columns2:
                frame[col] = frame[col].str.strip()
    # ### string replacements
    if not replace_string_columns is None:
        for key, value in replace_string_columns.items():
            # check if list
            is_type(value, list)
            if len(value) != 2:
                # check if it has two elements
                raise ValueError('All of the `replace_string_columns` '
                                 'dictionary values should be a list with two '
                                 'entries')
            # replace
            frame[key] = frame[key].str.replace(value[0], value[1])
    # ### which columns should be log10 transformed
    if not log10_columns is None:
        frame=_apply_and_rename(
            frame.copy(),
            original_columns=log10_columns,
            func=_nlog10_func
        )
    # ### Moving columns to the front
    if not order_columns is None:
        # looing over the reverse order of the list
        for p in order_columns[::-1]:
            frame.insert(0, p, frame.pop(p))
    # ### return
    return frame

