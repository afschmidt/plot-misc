#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import stats as ss
from typing import Any, List, Type, Union, Tuple, Dict, ClassVar
from plot_misc.constants import (
    is_type,
    MakeHeatmapNames as MHnames
)
from plot_misc.table.layout import _nlog10_func

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MatrixHeatmapResults(object):
    '''
    The `calc_matrices` results objects
    '''
    SET_ARGS = [MHnames.value_input,
                MHnames.annot_input,
                MHnames.annot_star,
                MHnames.annot_pval,
                MHnames.annot_effect,
                MHnames.value_original,
                MHnames.value_point,
                MHnames.source_data,
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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Functions
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
        ks_res[c] = ss.kstest(temp[np.isnan(temp) == False], 'uniform')
        # print(c + ' KS p-value: ' + str(ks_res[c][1]))
    # return
    return ks_res

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE transition this function over from merit_helper, integrate the Names
# class into constants, change the defaults and add tests (for this entire
# module).
def extract(data:pd.DataFrame, exposures:list, phenotypes:list,
            exposures_col:str, phenotypes_col:str,
            point_col:str=Names.point_estimate,
            pvalue_col:str=Names.pvalue):
    """
    Will extract p-values, and point-estimates from the `--file`, and subset
    it on the subplied exposures and outcomes.
    
    Parameters
    ----------
    data:       ;pd.DataFrame
        a pd.DataFrame with columns names[uniq_id], Names.phenotype,
        Names.pvalue, Names.point_estimate.
    exposures:  :list
        a list of uniqily defined row indices that map to `data` exposure_col.
    phenotypes:   :list
        a list of uniquely defined phenotypes that map to `data` phenotypes_col.
    *_col: str,
        The column names for `data`. Here the exposures_col, phenotypes_col,
        are used as labels for the pd.DataFrame
        
    Returns
    -------
    point_mat : pd.DataFrame, with point estimates
    pvalue_mat : pd.DataFrame, with p-values,
    source_data : pd.DataFrame, source data
    
    """
    ### subsetting
    # making sure we do not change the original `data`
    data = data.copy()
    # checking if index should be added to the data
    if phenotypes_col == MHnames.index:
        data.reset_index()
        data[MHnames.index] = data.index
        data.index.name = ''
    if exposures_col == MHnames.index:
        data.reset_index()
        data[MHnames.index] = data.index
        data.index.name = ''
    # cheking phenotypes are all available
    missing_p = set(phenotypes).difference(data[phenotypes_col].tolist())
    if not len(list(missing_p)) == 0:
        raise KeyError("Some of the phenotypes are not present in the"
                       "supplied data. The following names were not found: "
                       "\n".join(map(str ,missing_p)))
    else:
        slice1 = data[data[phenotypes_col].isin(phenotypes)]
    # cheking the exposures are present
    missing = set(exposures).difference(slice1[exposures_col].tolist())
    if not len(list(missing)) == 0:
        raise KeyError("Some of the exposures are not present in the"
                       "supplied data. The following names were not found: "
                       "\n".join(map(str ,missing)))
    else:
        slice2 = slice1[slice1[exposures_col].isin(exposures)]
    ### getting estimates
    point = slice2[[point_col, exposures_col, phenotypes_col]].copy()
    pvalue = slice2[[pvalue_col, exposures_col, phenotypes_col]].copy()
    ### ordering Rows
    sorterRows = dict(zip(phenotypes, range(len(phenotypes))))
    point['sort_rows'] = point.index.map(sorterRows)
    point.sort_values(by = 'sort_rows', ascending = True, inplace=True)
    order_rows = point[phenotypes_col].unique().tolist()
    ### ordering cols
    sorterCols = dict(zip(exposures, range(len(exposures))))
    point['sort_cols'] = point.index.map(sorterCols)
    point.sort_values(by = 'sort_cols', ascending = True, inplace=True)
    order_cols = point[exposures_col].unique().tolist()
    ### matrix
    point_mat = point.pivot_table(index=[phenotypes_col],
                      columns = exposures_col,
                      values = point_col
                      ).reindex(index = order_rows, columns = order_cols)
    pvalue_mat = pvalue.pivot_table(index=[phenotypes_col],
                      columns = exposures_col,
                      values = pvalue_col
                      ).reindex(index = order_rows, columns = order_cols)
    ### check the shape are correct
    if not point_mat.shape == pvalue_mat.shape:
        raise ValueError('P-value and point estimate matrices have different'
                         'shapes')
    else:
        return point_mat, pvalue_mat, slice2

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def format_matrices(effect, pval, sig, log=True, ptrun=16, digits='3',
                    symbol='★'):
    """
    Simple function that
        - log10s the p-values
        - rounds to 4 dp
        - scales p-values times direction
        - masks non-significant point estimates
    Parameters
    ----------
    effect, p-value: pd.DataFrame
        Matrices of the same size with the effect estimates and p-values as
        numerical/float entries.
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
    four pd.dataframes:
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
                  exposures_col:str,
                  phenotypes_col:str,
                  point_col:str='point',
                  pvalue_col:str='pvalue',
                  alpha:float=-1*np.log10(0.05),
                  sig_numbers:int=2,
                  ptrun:float=16,
                  annotate:str='stars',
                  without_log:bool=False,
                  mask_na:bool=True,
                  mapper:pd.DataFrame=pd.DataFrame(),
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
    data : pd.DataFrame
    *_col : str,
        Column names in `data`
    alpha  : float, default 0.05
        The significance cut-off.
    sig_numbers : int, default 2
        The number of significant numbers the cell annotations should have.
    ptrun : float, default=16,
        P-values above this value will be truncated.
    annotate : str, default `starts`
        The cell annotation: 'stars', 'pvalues', 'pointestimates', 'None'
    without_log : boolean, default False,
        If the p-value should _NOT_ be -log10 converted.
    mask_na : boolean, default True,
        If you want to mask missing results (e.g., replacing NAs by 0 or 1)
    mapper : pd.DataFrame, default = an empty pd.DataFrame,
    
    Returns
    -------
    res : :obj:`MatrixHeatmapResults`
        Includes two curated matrix ready to use in a plotting function
        as well as matrices useful for custom jobs or checking output.
        The objects are pd.DataFrame with values as `floats` for plotting
        or, as `strings` for annotations.
    """
    #### check input
    # TODO
    ### Decide which data to extract
    exposures, phenotypes = _mapper_format(mapper, data,
                                           phenotypes_col=phenotypes_col,
                                           exposures_col=exposures_col)
    ### subsetting data
    point_mat, pvalue_mat, source_data = extract(data, exposures=exposures,
                                                 phenotypes=phenotypes,
                                                 exposures_col=exposures_col,
                                                 phenotypes_col=phenotypes_col,
                                                 point_col=point_col,
                                                 pvalue_col=pvalue_col)
    ### formatting data
    values, annot_effect, annot_star, annot_pval, values_point =\
    format_matrices(point_mat, pvalue_mat, sig=alpha,
                    ptrun=ptrun, digits=str(sig_numbers),
                    log=without_log == False)
    
    ### selecting the annotation to use
    if annotate == 'stars':
        annot = annot_star
    elif annotate == 'pvalues':
        annot = annot_pval
    elif annotate == 'pointestimates':
        annot = annot_effect
    elif annotate == 'None':
        annot = pd.DataFrame().reindex_like(values)
        annot.fillna('', inplace=True)
    else:
        raise ValueError('Incorrect `annotate` value supplied '
                         'Please use: {}'.\
                         format(['stars','pvalues', 'pointestimates', 'None']))
    
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
    res = {MHnames.value_input: values_input,
           MHnames.annot_input: annot_input,
           MHnames.annot_star: annot_star,
           MHnames.annot_pval: annot_pval,
           MHnames.annot_effect: annot_effect,
           MHnames.value_original: values,
           MHnames.value_point: values_point,
           MHnames.source_data: source_data,
           }
    return MatrixHeatmapResults(**res)

