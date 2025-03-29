#!/usr/bin/env python3
'''
A module packaging various (string) formatting functions.
'''
import numpy as np
import pandas as pd
import warnings
from scipy.stats import norm
from typing import Any, List, Type, Union, Tuple, Dict, ClassVar, Optional
from plot_misc.constants import (
    UtilsNames,
    is_type,
    as_array,
    same_len,
)
from sklearn.metrics import (
    roc_curve,
)

# constants
MAXLOG10=20

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
def format_estimates(point:float, se:Union[float,None]=None,
                      lower:Union[float, None]=None,
                      upper:Union[float, None]=None, alpha:float=0.05,
                      round:int=2, exp:bool=False
                      ) -> str:
    """
    Formats point estimates with confidence intervals
    
    Arguments
    ---------
    point, se, lower, upper : float
        Please supply either the `se` or (`lower` and `upper`) as floats.
    alpha : float, default 0.05
        The desired type 1 error rate
    round : integer, default 2
        The desired number of significant figures
    exp : boolean, default False
        Should the point estimates, lower and upper bounds be exponentiated
        with base `e`
    
    Returns
    -------
    format_string : str
        `point (lower; upper)` formatted string with appropriate rounding
    """
    # check input
    is_type(round, int)
    is_type(alpha, float)
    is_type(point, float)
    if se == None and not ( isinstance(lower, float) and isinstance(upper, float) ):
            raise TypeError('Please supply either an `se`, or both  `lower` '
                            'and `upper`.')
    if isinstance(se, float) and not ( lower == None and upper == None):
            raise TypeError('Please supply either an `se`, or both  `lower` '
                            'and `upper`.')
    if isinstance(se, float) and isinstance(lower, float) and\
    isinstance(upper, float):
            warnings.warn('Ignoring `se`.', SyntaxWarning)
    # calculate lower and upper bounds
    if (lower == None and upper == None):
        z = norm.ppf(1-alpha/2)
        lower = point - z*se
        upper = point + z*se
    if exp == True:
        point = np.exp(point)
        upper = np.exp(upper)
        lower = np.exp(lower)
    # format string
    r_format = '.{}f'.format(round)
    format_string = format(point, r_format) + ' (' + format(lower, r_format) + \
        '; ' + format(upper, r_format) + ')'
    return format_string

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def format_roc(observed:as_array, predicted:as_array,
               **kwargs:Optional[Any],
               ) -> pd.DataFrame:
    '''
    Takes a binary `observed` column vector and a continuous `predicted`
    column vector, and returns a pd.DataFrame with the columns
    `false_positive`, `sensitivity` and `threshold`.
    
    Arguments
    ---------
    observed: numpy array
        A column vector of the observed binary outcomes.
    predicted: numpy array
        A column vector of the predicted outcome (should be continuous), e.g.,
        representing the predicted probability.
    kwargs: Any
        Supplied to `sklearn.metrics.roc_curve`.
    
    Returns
    -------
    results: pd.DataFrame,
        With columns: `false_positive`, `sensitivity` and `threshold`.
    '''
    # check input
    is_type(observed, np.ndarray)
    is_type(predicted, np.ndarray)
    same_len(observed,predicted)
    # get columns
    false_positive, sensitivity, threshold = roc_curve(
        y_true=observed, y_score=predicted,
        **kwargs,
    )
    # make data frame
    results = pd.DataFrame(
        {
            UtilsNames.roc_false_positive: false_positive,
            UtilsNames.roc_sensitivity: sensitivity,
            UtilsNames.roc_threshold: threshold,
        }
    )
    # return
    return results

