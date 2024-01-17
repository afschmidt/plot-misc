'''
A collection of general utility functions not belonging to a single type of
plot.
'''

import re
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import stats as ss
from typing import Any, List, Type, Union, Tuple, Dict, ClassVar, Optional
from plot_misc.constants import (
    is_type,
    UtilsNames,
)
from plot_misc.table.layout import _nlog10_func

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MatrixHeatmapResults(object):
    '''
    The `calc_matrices` results objects
    '''
    SET_ARGS = [
        UtilsNames.value_input,
        UtilsNames.annot_input,
        UtilsNames.annot_star,
        UtilsNames.annot_pval,
        UtilsNames.annot_effect,
        UtilsNames.value_original,
        UtilsNames.value_point,
        UtilsNames.source_data,
    ]
    # Initiation the class
    def __init__(self, **kwargs):
        """
        Initialise
        """
        for k in kwargs.keys():
            if k not in self.__class__.SET_ARGS:
                raise AttributeError("unrecognised argument '{0}'".format(k))
        # Loops over `SET_ARGS`, assigns the kwargs content to name `s`.
        for s in self.__class__.SET_ARGS:
            try:
                setattr(self, s, kwargs[s])
            except KeyError:
                warnings.warn("argument '{0}' is set to 'None'".format(s))
                setattr(self, s, None)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MidpointNormalize(mpl.colors.Normalize):
    '''
    Class to help renomralize the color scale.
    '''
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        super().__init__(vmin, vmax, clip)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        # Note also that we must extrapolate beyond vmin/vmax
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1.]
        return np.ma.masked_array(np.interp(value, x, y,
                                            left=-np.inf, right=np.inf))
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def inverse(self, value):
        y, x = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.interp(value, x, y, left=-np.inf, right=np.inf)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Functions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _update_kwargs(update_dict:Dict[Any, Any], **kwargs:Optional[Any],
            ) -> Dict[Any, Any]:
    '''
    This function will take any number of `kwargs` and add them to an
    `update_dict`. If there are any duplicate values in the `kwargs` and the
    `update_dict`, the entries in the `update_dict` will take precedence.
    
    Parameters
    ----------
    update_dict : dict,
        A dictionary with key - value pairs that should be combined with any
        of the supplied kwargs.
    kwargs :
        Arbitrary keyword arguments.
    
    Returns
    -------
    dict
        A dictionary with the update_dict and kwargs combined, where duplicate
        entries from update_dict overwrite those in kwargs.
    
    Examples
    --------
        The function is particularly useful to overwrite `kwargs` that are
        supplied to a nested function say
        
        >>> _update_kwargs(update_dict={'c': 'black'}, c='red',
                         alpha = 0.5)
        >>> {'c': 'black', 'alpha': 0.5}
    '''
    new_dict = {**kwargs, **update_dict}
    # returns
    return new_dict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dict_string_argument(partial_match:str, dict_string:Dict[Any, str],
                          context=Dict[Any,Any],
                          ) -> Dict[Any,Any]:
    '''
    Will perform an `re.match(dict_string, value)` on all the values of
    `dict_string`. If a match is found it will evaluate the value and asign
    it to the correct dictionary key: `dict_string[key] = eval(value)`.
    This function is handy if an object is only internally defined after a
    function is innitiated.
    
    Parameters
    ----------
    partial_match : str,
        A regex string which will be used to find partial matches in the values
        of `dict_string`.
    dict_string : dict,
        A dictionary with some string values which one wants to evaluate and
        asign back to the correct dictionary key entry.
    context : dict,
        The environment to look for `value` - should contain values as a
        dictionary containing the string key word, with assigned objects.
    
    Returns
    -------
    dict
        A dictionary with the update_dict and kwargs combined, where duplicate
        entries from update_dict overwrite those in kwargs.
    
    Examples
    --------
        >>> row=[1, 2]
        >>> dict_string={'obj1': 'row[0]', 'obj2' : 2}
        >>> new_dict = _dict_string_argument('row', dict_string,
                                             context={'row':row})
        >>> # returns
        >>> {'obj1': 1, 'obj2': 2}
    '''
    # testing input
    is_type(partial_match, str)
    is_type(dict_string, dict)
    # evaluting object
    for key, value in dict_string.items():
        if isinstance(value, str):
            if re.match(partial_match, value):
                dict_string[key] = eval(value, context)
    # return stuf
    return dict_string

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def change_ticks(ax:plt.Axes, ticks:List[str], labels:Union[List[str],None]=None,
                 axis:str='x', log:bool=False):
    '''
    Takes an axis and changes the ticks labels and location
    
    Parameters
    ----------
    ax : plot.axes
    ticks : list,
        A list of ticks marks which will be used for the position and labels
    labels : list,
        If supplied use these labels instead of re-using `ticks`, need to check
        for len(ticks) == len(labels)
    log: bool, default False
        Should the `ticks` locations be np.log transformed. Does not affect the
        `ticklabels`.
    
    Returns
    -------
    Does not return anything
    '''
    # check input
    is_type(ticks, list)
    is_type(labels, (list, type(None)))
    is_type(axis, str)
    is_type(log, bool)
    # set labels
    if isinstance(labels, list):
        if not len(labels) == len(ticks):
            raise ValueError('`labels` and `ticks` have distinct number of '
                             'entries.')
        # set the actual labels
        tick_labels = labels
    else:
        tick_labels = ticks
    # do we need to transform the location
    if log == True:
        tick_location = np.log(ticks)
    else:
        tick_location = ticks
    # work on xaxis
    if axis == 'x':
        try:
            ax.xaxis.set_ticks(tick_location)
            ax.xaxis.set_ticklabels(tick_labels)
        except AttributeError as e:
            raise e
    # work on yaxis
    if axis == 'y':
        try:
            ax.yaxis.set_ticks(tick_location)
            ax.yaxis.set_ticklabels(tick_labels)
        except AttributeError as e:
            raise e
    # done

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ks_test(data:pd.DataFrame, group:str, values:str,
            nulldistribution:str='uniform') -> Dict[str, str]:
    '''
    Will loop over the unique `group` values to perform overall null-hypothesis
    tests comparing sets of values against a null-distribution using the
    Kolmogorov-Smirnoff test.
    
    Parameters
    ----------
    data : pd.DataFrame
    group : str,
        A column name in `data` which will be used to group the `values`.
    values : str,
        A column name in `data` to which you want to apply the
        Kolmogorov-Smirnoff test to.
    nulldistribution : str, default `uniform`
        The null-distribution the `values` should be compared against. This
        maps to the `Scipy.stats` avalable distributions.
    
    
    Returns
    -------
    A dictionary with `group` values and a `KstestResults` class a items.
    '''
    ks_res = {}
    for c in data[group].unique():
        temp = data[data[group] == c][values]
        ks_res[c] = ss.kstest(temp[np.isnan(temp) == False], nulldistribution)
    # return
    return ks_res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _extract(data:pd.DataFrame,
            exposure_col:str,
            outcome_col:str,
            point_col:str,
            pvalue_col:str,
            dropna:bool=False,
            **kwargs:Optional[Any],
            ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Will extract p-values, and point-estimates from a `data` pd.DataFrame, and
    create matrices with the exposure and outcome value on the margings.
    
    Parameters
    ----------
    data: pd.DataFrame
        with columns that map to the `.*_col`.
    *_col: str,
        The column names for `data`.
    dropna: bool, default `False`
        Set to `True` to remove columns with any missing data.
    **kwargs
        All other arguments are forwarded to `pivot_table`.
        
    Returns
    -------
    point_mat : pd.DataFrame, with point estimates
    pvalue_mat : pd.DataFrame, with p-values,
    """
    ### subsetting
    # making sure we do not change the original `data`
    data = data.copy()
    ### getting estimates
    point = data[[point_col, exposure_col, outcome_col]].copy()
    pvalue = data[[pvalue_col, exposure_col, outcome_col]].copy()
    ### matrix
    point_mat = point.pivot_table(index=[outcome_col],
                      columns = exposure_col,
                      values = point_col,
                      dropna=dropna,
                      **kwargs,
                      )
    pvalue_mat = pvalue.pivot_table(index=[outcome_col],
                      columns = exposure_col,
                      values = pvalue_col,
                      dropna=dropna,
                      **kwargs,
                      )
    ### check the shape are correct
    if not point_mat.shape == pvalue_mat.shape:
        raise ValueError('P-value and point estimate matrices have different'
                         'shapes')
    else:
        return point_mat, pvalue_mat

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _format_matrices(effect:pd.DataFrame, pval:pd.DataFrame, sig:float,
                    log:bool=True, ptrun:float=16, digits:str='3',
                    symbol:str='★') -> Tuple[  pd.DataFrame,
                                               pd.DataFrame,
                                               pd.DataFrame,
                                               pd.DataFrame,
                                               pd.DataFrame,
                                               ]:
    """
    Takes two matrices of point-estimates and p-values to:
        - log10s the p-values
        - rounds to `digits` dp
        - scales p-values times direction
        - masks non-significant point estimates
    
    The function will return multiple matrices either as floats or as strings.
    The float matrices can be used to colour matplotlib figures for example.
    The string matrices can be used to annotate figures, for example to
    indicate significances.
    
    Parameters
    ----------
    effect, p-value: pd.DataFrame
        Matrices of the same size with the effect estimates and p-values as
        floats.
    sig: float
        The significance p-value cut-off either bounded between 0 and 1,
        or -log10 transformed.
    log: Boolean
        should the `pval` matrix be -log10 transformed; default=True.
    ptrun: float
        the p-value truncation value.
    digits: str
        the number of significant digits the effect matrix should be rounded;
        default = '3'.
    symbol: str
        the unicode symbol used to flag significant findings; default = '★'.
    
    Returns
    -------
    five pd.dataframes:
        1. direction times pvalue matrix; floats
        2. an effect estimate matrix masking non-significant results; str
        3. an star matrix masking non-significant results; str
        4. an p-value matrix masking non-significant results; str
        5. an effect esimate matrix without masking: floats
        
    """
    # checking input
    if len(digits) > 1:
        digits=digits[0]
        # warnings
        warnings.warn("`digits` has length '{0}' "
                      "taking the first value".format(len(digits)))
    # taking the log10
    if log == True:
        pval = _nlog10_func(pval, ptrun)
    # rounding
    dig = '{:.'+digits+'f}'
    pval = pval.round(int(float(digits)))
    dir = np.sign(effect)
    # simply stoaring the float matrix
    effect_float = effect.copy()
    # formatting
    effect = effect.applymap(dig.format).copy()
    # scaling
    pval = dir * pval
    # if log == True use larger than
    if log == True:
        # if not significant set to empty
        effect[np.abs(pval) < sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[np.abs(pval) >= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[np.abs(pval) >= sig] = pval[np.abs(pval) >= sig].astype('str')
        # if log != True use smaller than
    else:
        # if not significant set to empty
        effect[np.abs(pval) > sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[np.abs(pval) <= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[np.abs(pval) <= sig] = pval[np.abs(pval) <= sig].astype('str')
    
    # returning
    return pval, effect, star, pvalstring, effect_float

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_matrices(data:pd.DataFrame,
                  exposure_col:str,
                  outcome_col:str,
                  point_col:str='point',
                  pvalue_col:str='pvalue',
                  alpha:float=-1*np.log10(0.05),
                  sig_numbers:int=2,
                  ptrun:float=16,
                  annotate:Union[str,None]='star',
                  without_log:bool=False,
                  mask_na:bool=True,
                  **kwargs:Optional[Any],
                  ) -> MatrixHeatmapResults:
    """
    Getting matrices for the cluster heatmap. Note the p-values are expected
    to range between 0 and 1.
    
    Will return two matrices: a value matrix with the -log_10(p-values) multiplied
    by the effect direction (e.g. based on the sign of `point`), and an
    annotation matrix, where significant finding are annotated as by
    `annotate`.
    
    Arguments
    ---------
    data: pd.DataFrame
    *_col: str,
        Column names in `data`
    alpha: float, default 0.05
        The significance cut-off.
    sig_numbers: int, default 2
        The number of significant numbers the cell annotations should have.
    ptrun: float, default=16,
        P-values above this value will be truncated.
    annotate: str, default 'star'
        The cell annotation: 'star', 'pvalues', 'pointestimates',
        'None'. Set to `NoneType` to simply return the
        -log10(p-values) times effect direction
    without_log: boolean, default `False`,
        If the p-value should _NOT_ be -log10 converted.
    mask_na: boolean, default `True`,
        If you want to mask missing results (e.g., replacing NAs by 0 or 1)
    **kwargs
        All other arguments are forwarded to `_extract`.
    
    Returns
    -------
    res: `MatrixHeatmapResults`
        Includes two `curated` matrix ready to use in a plotting function
        with exact content dependent on the `annotate` argument.
        
        Additionally, returns matrices useful for custom jobs or checking
        output.
        
        The objects are pd.DataFrame with values as `floats` for plotting
        or, as `strings` for annotations.
    """
    #### check input
    is_type(data, pd.DataFrame)
    is_type(exposure_col, str)
    is_type(outcome_col, str)
    is_type(point_col, str)
    is_type(pvalue_col, str)
    is_type(alpha, float)
    is_type(sig_numbers, (float, int))
    is_type(without_log, bool)
    is_type(mask_na, bool)
    ### subsetting data
    point_mat, pvalue_mat = _extract(data,
                                     exposure_col=exposure_col,
                                     outcome_col=outcome_col,
                                     point_col=point_col,
                                     pvalue_col=pvalue_col,
                                     **kwargs,
                                     )
    ### formatting data
    values, annot_effect, annot_star, annot_pval, values_point =\
        _format_matrices(
            point_mat, pvalue_mat, sig=alpha,
            ptrun=ptrun, digits=str(sig_numbers),
            log=without_log == False,
        )
    ### selecting the annotation to use
    if annotate == UtilsNames.mat_annot_star:
        annot = annot_star
    elif annotate == UtilsNames.mat_annot_pval:
        annot = annot_pval
    elif annotate == UtilsNames.mat_annot_point:
        annot = annot_effect
    elif annotate is None:
        annot = pd.DataFrame().reindex_like(values)
        annot.fillna('', inplace=True)
    else:
        raise ValueError('Incorrect `annotate` value supplied '
                         'Please use: {}'.\
                         format([UtilsNames.mat_annot_star,
                                 UtilsNames.mat_annot_pval,
                                 UtilsNames.mat_annot_point,
                                 UtilsNames.mat_annot_none,
                                 ]
                                ))
    ### drop or mask NAs
    if mask_na == False:
        drop_c = values.isna().any(axis = 0) == False
        drop_r = values.isna().any(axis = 1) == False
        values_input = values.loc[drop_r, drop_c]
        annot_input = annot.loc[drop_r, drop_c]
        # Mask with zero if logged
    elif without_log == False:
        values_input = values.fillna(0, inplace=False)
        annot_input = annot.fillna('.', inplace=False)
        annot_input[annot_input == 'nan'] = '.'
        # Mask with one if not
    else:
        values_input = values.fillna(1, inplace=False)
        annot_input = annot.fillna('.', inplace=False)
        annot_input[annot_input == 'nan'] = '.'
    ### Return
    res = {UtilsNames.value_input: values_input,
           UtilsNames.annot_input: annot_input,
           UtilsNames.annot_star: annot_star,
           UtilsNames.annot_pval: annot_pval,
           UtilsNames.annot_effect: annot_effect,
           UtilsNames.value_original: values,
           UtilsNames.value_point: values_point,
           UtilsNames.source_data: data,
           }
    return MatrixHeatmapResults(**res)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fix_labels(annotations, axis, min_distance=0.1):
    """
    Adjust the positions of annotations to prevent overlap.

    Parameters:
        annotations (list): List of matplotlib annotations to adjust.
        axis (matplotlib.axes.Axes): The axis where the annotations are displayed.
        min_distance (float, optional): Minimum vertical distance between annotations. Default is 0.1.
    """
    for i, ann1 in enumerate(annotations):
        for j, ann2 in enumerate(annotations):
            if i != j:
                # Get positions of annotations
                pos1 = axis.transData.inverted().transform(axis.transData.transform(ann1.get_position()))
                pos2 = axis.transData.inverted().transform(axis.transData.transform(ann2.get_position()))

                # Calculate distance between annotations
                vertical_distance = abs(pos1[1] - pos2[1])
                horizontal_distance = abs(pos1[0] - pos2[0])

                # Adjust positions if annotations overlap
                if vertical_distance < min_distance and horizontal_distance < min_distance:
                    if pos1[1] < pos2[1]:
                        pos1 = (pos1[0], pos2[1] - min_distance)
                    else:
                        pos2 = (pos2[0], pos1[1] - min_distance)

                    ann1.set_position(pos1)
                    ann2.set_position(pos2)