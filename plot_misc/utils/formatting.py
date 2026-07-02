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
format_estimates(point, se=None, lower=None, upper=None, alpha=0.05, ...)
    Formats a point estimate and confidence interval into a compact string.

sci_notation(number, sig_fig=2, ...)
    Converts a float into scientific notation with superscript exponents.

format_roc(observed, predicted, ...)
    Computes ROC curve data and returns it as a tidy DataFrame.

string_interval(limits, int_notation, middle, lower_lim, inq_space, sep)
    Maps a lists of intervals to string interval notation.

Constants
---------
MAXLOG10 : int
    Maximum -log10(p) value used for truncation of very small p-values.

"""

import numpy as np
import pandas as pd
import warnings
from scipy.stats import norm
from typing import Any
from plot_misc.constants import (
    UtilsNames,
    Real,
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

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def _nlog10_func(p:pd.Series, max:Real=MAXLOG10):
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
def format_estimates(point:Real, se: float | None=None,
                     lower: Real | None=None, upper: Real | None=None,
                     alpha:float=0.05, round:int=2, exp:bool=False
                      ) -> str:
    """
    Format point estimates with confidence intervals into a string.
    
    Parameters
    ----------
    point : `float` or `int`
        Point estimate.
    se : `float` or `None`, default `None`
        Standard error of the point estimate.
    lower : `float`, `int` or `None`, default `None`
        Lower bound of the confidence interval.
    upper : `float`, `int` or `None`, default `None`
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
    if se is None and not (isinstance(lower, float) and isinstance(upper, float)):
            raise TypeError('Please supply either an `se`, or both  `lower` '
                            'and `upper`.')
    if isinstance(se, float) and not (lower is None and upper is None):
            raise TypeError('Please supply either an `se`, or both  `lower` '
                            'and `upper`.')
    if isinstance(se, float) and isinstance(lower, float) and\
    isinstance(upper, float):
            warnings.warn('Ignoring `se`.', SyntaxWarning)
    # calculate lower and upper bounds
    if lower is None and upper is None:
        z = norm.ppf(1-alpha/2)
        lower = point - z*se
        upper = point + z*se
    if exp:
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
               **kwargs:Any,
               ) -> pd.DataFrame:
    """
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
    """
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
    """
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
    """
    return number.replace('0','⁰').replace('1','¹').replace('2','²').\
        replace('3','³').replace('4','⁴').replace('5','⁵').replace('6','⁶')\
        .replace('7','⁷').replace('8','⁸').replace('9','⁹').replace('-','⁻')\
        .replace('+', '⁺').replace('.','·').replace(',','˒')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def sci_notation(number: Real, sig_fig:int=2,
                 max:Real | None = None, min:Real | None = None,
                 ) -> str:
    """
    Convert a number to scientific notation with superscript exponent.
    
    Parameters
    ----------
    number : `float` or `int`
        A number.
    sig_fig : `int`, default 2
        The number of significant digits after the decimal point.
    max `float`, `int` or `None`, default `None`.
        the float value below which values get truncated to the supplied maximum
        value (i.e., winsorised)
    min `float`, `int` or `None`, default `None`.
        the float value below which values get truncated to the supplied minimum
        value (i.e., winsorised)
    
    Returns
    -------
    str
        The number in scientific notation.
    
    Notes
    -----
    Will truncates values if too small/large to print.
    
    Examples
    --------
    >>> sci_notation(2465640, sig_fig=4)
    '2.4656×10⁶
    """
    # check input
    is_type(number, Real)
    is_type(min, (type(None), Real))
    is_type(max, (type(None), Real))
    if min is not None and number < min:
        number = min
    if max is not None and number > max:
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def wrap_text(text: str, max_n: int, break_char:str='') -> str:
    """
    If the `text` string is longer than `max_n`, insert a linebreak at a white
    space before `max_n`.
     
    Parameters
    ----------
    text : `str`
        A string which should be truncated if too long.
    max_n : `int`
        The truncation length.
    break_char : `str`,
        The character to insert before a newline when a word must be
        split (a hard break). Defaults to an empty string.
        
    Return
    ------
    str
        The truncated string, with additional linebreak if needed.
    """
    #  ####check input
    is_type(text, str)
    is_type(max_n, int)
    # #### remove any leading white space
    text = text.lstrip()
    # #### check string
    # The string it already short enough!
    if len(text) <= max_n:
        return text
    text_cut = text.rfind(" ", 0, max_n)
    # If there is no white space apply a hard break
    if text_cut == -1:
        text_cut = max_n
        line_ending = break_char + "\n"
    else:
        line_ending = "\n"
    first_part = text[:text_cut] + line_ending
    #  get the remainder
    if text_cut == max_n:
        # hard break
        remainder = text[text_cut:]
    else:
        # soft break
        remainder = text[text_cut + 1 :]
    # Recursive step, will stop when len(text)<=max_n
    return first_part + wrap_text(remainder, max_n, break_char)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def string_interval(limits:list[Real], int_notation:bool=False,
                    middle:bool=False, lower_lim:Real | None = None,
                    inq_space:str = ' ', sep:str = ', ',
                    ) -> list[str]:
    """
    Generate string labels for numeric intervals using midpoint, inequality, or
    interval notation.
    
    Parameters
    ----------
    limits : `list` [`real`]
        A list of numeric values (floats or integers) defining the upper bounds
        of each interval.
    int_notation : `bool`, default `False`
        If True, return intervals using mathematical interval notation
        (e.g., "(a, b]"). Cannot be used together with `middle=True`.
    middle : `bool`, default `False`
        If True, return the midpoint of each interval instead of the full
        bounds.  If the interval is open-ended (i.e., includes ±inf), it falls
        back to inequality notation.
    lower_lim : `real` or `None`, default `None`
        Left-most bound of the first interval. If not provided, assumed to be
        negative infinity.
    inq_space : `str`, default ' '
        Space between inequality symbols and numbers (e.g., "< 0.5" vs "<0.5").
    sep : `str`, default ', '
        Separator for interval notation (e.g., "(a, b]").
    
    Return
    ------
    list of str
        A list of interval descriptions as strings, formatted according to the
        selected output style.
    
    Examples
    --------
    >>> string_sets([0.2, 0.5, 1.0], lower_lim=0.0, middle=True)
    ['0.1', '0.35', '0.75']
    
    >>> string_sets([0.5, 1.0], lower_lim=0.0, sep=' p ')
    ['0.0 < p ≤ 0.5', '< 1.0']
    """
    # check input
    is_type(limits, list)
    is_type(int_notation, bool)
    is_type(middle, bool)
    is_type(lower_lim, (type(None), Real))
    is_type(sep, str)
    is_type(inq_space, str)
    # what should be plotted
    vals = []
    limits = sorted(limits)
    if middle:
        # combine lower limit with limits to form intervals
        edges = [lower_lim if lower_lim is not None else -np.inf] + limits
        for i in range(len(limits)):
            lo = edges[i]
            hi = edges[i + 1]
            if np.isinf(lo) or np.isinf(hi):
                # still include an inequality for inf
                if np.isinf(lo):
                    # if the left value is inf use the value to the right
                    vals.append("≤" + inq_space + str(hi))
                else:
                    # if the last value is inf use the value to the left
                    vals.append(">" + inq_space + str(lo))
            else:
                # otherwise just plot the mid point
                vals.append(str((lo + hi) / 2))
    else:
        # not mid-points, just inq or intervals
        for k in  range(len(limits)):
            if int_notation:
                if k == 0 and lower_lim is not None:
                    vals.append("(" + str(lower_lim) + sep +\
                                str(limits[k]) + ']')
                elif k == 0:
                    vals.append("(" + str(-np.inf) + sep +\
                                str(limits[k]) + ']')
                elif limits[k] == limits[-1] and np.isinf(limits[-1]):
                    vals.append("(" + str(limits[k - 1]) + sep +\
                                str(limits[k]) + ')')
                else:
                    vals.append("(" + str(limits[k - 1]) + sep +\
                                str(limits[k]) + ']')
            else:
                if limits[k] == limits[0] or limits[k] == limits[-1]:
                    if limits[k] == limits[0] and lower_lim is not None:
                        vals.append(
                            str(lower_lim) + inq_space + "<" + sep + "≤" +
                            inq_space + str(limits[k])
                        )
                    else:
                        vals.append("≤" + inq_space + str(limits[k]))
                else:
                    vals.append("<" + inq_space + str(limits[k]))
    # return
    return vals

