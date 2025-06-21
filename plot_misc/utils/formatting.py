"""
String and numeric formatting utilities for statistical output.

This module provides functions for transforming numerical results into
formatted strings for reporting and visualisation. It includes tools for
generating confidence intervals, scientific notation with superscript
exponents, and -log10 transformations of p-values for significance plotting.
Additionally, ROC curves can be formatted into structured DataFrames for
performance evaluation plots.

Functions
---------
format_estimates(point, se=None, lower=None, upper=None, alpha=0.05,
                 round=2, exp=False)
    Formats a point estimate and confidence interval into a compact string.

sci_notation(number, sig_fig=2, max=1e-100)
    Converts a float into scientific notation with superscript exponents.

format_roc(observed, predicted, **kwargs)
    Computes ROC curve data and returns it as a tidy DataFrame.

Constants
---------
MAXLOG10 : int
    Maximum -log10(p) value used for truncation of very small p-values.

"""

import numpy as np
import pandas as pd
import warnings
from scipy.stats import norm
from typing import (
    Any,
    Optional,
)
from plot_misc.constants import (
    UtilsNames,
)
from plot_misc.errors import (
    is_type,
    same_len,
)
from sklearn.metrics import (
    roc_curve,
)

# constants
MAXLOG10=20

# NOTE add more pytests
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# NOTE Add pytest also when input is zero
def _nlog10_func(p:pd.Series, max:float | int=MAXLOG10):
    """
    Compute -log10(p-values), with truncation.
    
    Parameters
    ----------
    p : `pd.Series`
        p-values.
    max : `int` or `float`, default 20
        truncate larger values to this constant.
    
    Returns
    -------
    pd.Series
        Transformed p-values with capped maximum.
    """
    # which values are rounded to zero
    notzero = p == 0
    # transform
    nlog10 = -1 * np.log10(p)
    # replacing zero
    nlog10[notzero] = max
    # truncating
    nlog10[nlog10 > max] = max
    # removing sign - note these are np.log(1) pvalues.
    nlog10[nlog10 == -0] = 0
    # returning
    return nlog10

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def format_estimates(point:float, se: float | None=None,
                     lower: float | None=None, upper: float | None=None,
                     alpha:float=0.05, round:int=2, exp:bool=False
                      ) -> str:
    """
    Format point estimates with confidence intervals into a string.
    
    Parameters
    ----------
    point : `float`
        Point estimate.
    se : `float` or `None`, default `NoneType`
        Standard error of the point estimate.
    lower : `float` or `None`, default `NoneType`
        Lower bound of the confidence interval.
    upper : `float` or `None`, default `NoneType`
        Upper bound of the confidence interval.
    alpha : `float`, default 0.05
        Significance level used to compute confidence interval if `se` is given.
    round : `int`, default 2
        Number of decimal places to round, retaining trialing zeros.
    exp : `bool`, default `False`
        If True, exponentiate the values with base e.
    
    Returns
    -------
    str
        Formatted string: "point (lower; upper)".
    
    Raises
    ------
    TypeError
        If required inputs are not supplied correctly.
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
def format_roc(observed:np.ndarray, predicted:np.ndarray,
               **kwargs:Optional[Any],
               ) -> pd.DataFrame:
    '''
    Takes a binary `observed` column vector and a continuous `predicted`
    column vector, and returns a pd.DataFrame with the columns
    `false_positive`, `sensitivity` and `threshold`.
    
    Arguments
    ---------
    observed : `np.ndarray`
        A column vector of the observed binary outcomes.
    predicted : `np.ndarray`
        A column vector of the predicted outcome (should be continuous), e.g.,
        representing the predicted probability.
    **kwargs
        Supplied to `sklearn.metrics.roc_curve`.
    
    Returns
    -------
    pd.DataFrame
        ROC curve with columns: false_positive, sensitivity, threshold.
    
    Raises
    ------
    ValueError
        If observed and predicted lengths differ.
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _superscriptinate(number:str) -> str:
    '''
    Will replace any number (0-9), separators, and addition subtraction
    symbols with a superscript equivalent expression.
    
    Parameters
    ----------
    number : `str`
        String of digits and symbols
    
    Returns
    -------
    str
        A string with superscript numbers.
    '''
    return number.replace('0','⁰').replace('1','¹').replace('2','²').\
        replace('3','³').replace('4','⁴').replace('5','⁵').replace('6','⁶')\
        .replace('7','⁷').replace('8','⁸').replace('9','⁹').replace('-','⁻')\
        .replace('+', '⁺').replace('.','·').replace(',','˒')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def sci_notation(number:float | int, sig_fig:int=2,
                 max:float=np.float_power(10, -100)) -> str:
    """
    Convert a number to scientific notation with superscript exponent.
    
    Parameters
    ----------
    number : `float` or `int`
        A number.
    sig_fig : `int`, default 2
        The number of significant digits after the decimal point.
    max `float`, default 10^{-100}
        the float value below which values get truncated to the max
        (i.e., winsorised)
    
    Returns
    -------
    str
        The number in scientific notation.
    
    Notes
    -----
    Will automatically truncates values if too small to print.
    
    Examples
    --------
    >>> sci_notation(2465640, sig_fig=4)
    '2.4656×10⁶
    """
    if number < max:
        number = max
    # getting string
    ret_string = "{0:.{1:d}e}".format(number, sig_fig)
    try:
        a,b = ret_string.split("e")
        # removed leading "+" and strips leading zeros too.
        b = int(b)
        return a + "×10" + _superscriptinate(str(b))
    except ValueError or TypeError:
        return str(np.nan)
