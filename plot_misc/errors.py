"""
Error handling for plot-misc.
"""
import inspect
import warnings
import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
from typing import Any, List, Type, Union, Tuple, Callable
from packaging import version

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# numpy typing
def as_array(a: ArrayLike) -> np.ndarray:
    return np.array(a)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class InputValidationError(Exception):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# error messages
class Error_MSG(object):
    '''
    A collection of error messages.
    '''
    MISSING_DF = '`{}` contains missing values.'
    INVALID_STRING = '`{}` should be limited to `{}`.'
    INVALID_EXACT_LENGTH = '`{}` needs to contain exactly {} elements, not {}.'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_param_name(param:Any) -> str | None:
    '''
    Gets the name of `param` or otherwise return a None.
    '''
    frame = inspect.currentframe().f_back.f_back
    param_names =\
        [name for name, value in frame.f_locals.items() if value is param]
    return param_names[0] if param_names else None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_type(param: Any, types: Union[Tuple[Type], Type],
            param_name: Union[str, None]=None) -> bool:
    """
    Checks if a given parameter matches any of the supplied types
    
    Parameters
    ----------
    param: Any
        Object to test.
    types: Type
        Either a single type, or a tuple of types to test against.
    
    Returns
    -------
    True if the parameter is an instance of any of the given types.
    Raises AttributeError otherwise.
    """
    if not isinstance(param, types):
        if param_name is None:
            param_name = get_param_name(param)
        else:
            warnings.warn('`param_name` will be depricated.',
                          DeprecationWarning,
                          stacklevel=2,
                          )
        raise InputValidationError(
            f"Expected any of [{types}], "
            f"got {type(param)}; Please see parameter: `{param_name}`."
        )
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
    warning: bool=False) -> bool:
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
def is_series_type(column: Union[pd.Series, pd.DataFrame],
                   types: Union[Tuple[Type], Type],
                   ) -> bool:
    """
    Checks if a pd.DataFrame or pd.Series contest has the supplied type.
    
    _Note_: instead of testing the dtypes, the function will look over each
        element and test this individually.
    
    Parameters
    ----------
    column: pd.Series or pd.DataFrame,
    types: a single type.
    
    Returns
    -------
    True if the column(s) match(es) the given types. Raises
    InputValidationError otherwise.
    """
    # check input
    is_type(column, (pd.DataFrame, pd.Series))
    # run tests
    if isinstance(column, pd.Series):
        [is_type(col, types) for col in column]
    elif isinstance(column, pd.DataFrame):
        if version.parse('2.0.3') <= version.parse(pd.__version__):
            # iteritems got depricated.
            column.iteritems = column.items
        for _, col in column.items():
            [is_type(co, types) for co in col]
    # return
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def same_len(object1: Any, object2: Any,
             object_names:Union[List[str], None]=None,
             ) -> bool:
    """
    Check if two object's have the same length, and otherwise raise
    `ValueError`.
    
    Arguments
    ---------
    object1, object2 : Any
        Any type of object.
    objects_names : list of strings
        The two objects the series our sourced from. Will be returned in any
        potential `IndexError` message.
        
    Returns
    -------
    True if all OK. Raises a ValueError otherwise.
    """
    n1 = len(object1)
    n2 = len(object2)
    if object_names is None:
        object_names = ['object1', 'object2']
    elif len(object_names) !=2:
        raise ValueError('`object_names` should be `NoneType` or contain '
                         'two strings')
    # the actual test
    if n1 != n2:
        raise ValueError("The length of `{0}`: {1}, does not match the length "
                         "of `{2}`: {3}.".format(object_names[0], n1,
                                               object_names[1], n2)
                         )
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def string_to_list(object:Any) -> Union[Any, List[str]]:
    '''
    Checks if `object` is a string and wraps this in a list, returns the
    original object if it is not a string.
    
    Parameters
    ----------
    object : Any
        Any object that might be a string.
    
    Returns
    -------
    string wrapped in a list or the original object type.
    '''
    if isinstance(object, str):
        return list(object)
    else:
        return object

