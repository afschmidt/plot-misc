'''
A collection of general utility functions not belonging to a single type of
plot.
'''

import re
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from typing import (
    Any,
    Literal,
    Optional,
    Union, Tuple, Dict, List,
)

from plot_misc.constants import (
    UtilsNames,
)
from plot_misc.errors import (
    is_type,
    InputValidationError,
    Error_MSG,
)
from plot_misc.utils.formatting import _nlog10_func

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MatrixHeatmapResults(object):
    '''
    The `calc_matrices` results objects.
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
def _update_kwargs(update_dict:dict[Any, Any], **kwargs:Optional[Any],
            ) -> dict[Any, Any]:
    '''
    This function will take any number of `kwargs` and add them to an
    `update_dict`. If there are any duplicate values in the `kwargs` and the
    `update_dict`, the entries in the `update_dict` will take precedence.
    
    Parameters
    ----------
    update_dict : `dict` [`any`, `any`]
        A dictionary with key - value pairs that should be combined with any
        of the supplied kwargs.
    kwargs : `Any`
        Arbitrary keyword arguments.
    
    Returns
    -------
    dict:
        A dictionary with the update_dict and kwargs combined, where duplicate
        entries from update_dict overwrite those in kwargs.
    
    Examples
    --------
    The function is particularly useful to overwrite `kwargs` that are
    supplied to a nested function, say:
        
        >>> _update_kwargs(update_dict={'c': 'black'}, c='red',
                         alpha = 0.5)
        >>> {'c': 'black', 'alpha': 0.5}
    '''
    new_dict = {**kwargs, **update_dict}
    # returns
    return new_dict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dict_string_argument(partial_match:str, dict_string:dict[Any, str],
                          context=dict[Any,Any],
                          ) -> dict[Any,Any]:
    '''
    Will perform an `re.match(dict_string, value)` on all the values of
    `dict_string`. If a match is found it will evaluate the value and asign
    it to the correct dictionary key: `dict_string[key] = eval(value)`.
    This function is handy if an object is only internally defined after a
    function is innitiated.
    
    Parameters
    ----------
    partial_match : str
        A regex string which will be used to find partial matches in the values
        of `dict_string`.
    dict_string : dict
        A dictionary with some string values which one wants to evaluate and
        asign back to the correct dictionary key entry.
    context : dict
        The environment to look for `value` - should contain values as a
        dictionary containing the string key word, with assigned objects.
    
    Returns
    -------
    dict:
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
def plot_span(start_span:float, stop_span:float, ax: plt.Axes,
              horizontal:bool=True, **kwargs:Optional[Any],
              ):
    '''
    Adds an horizontal or vertical span to an `ax` supplied `plt.Axes` object.
    
    Parameters
    ----------
    start_span: float
        The y-coordinate to start the span. Represents the x-axis coordinates
        when horizontal is `False`.
    stop_span: float
        The y-coordinate to end the span. Represents the x-axis coordinates
        when horizontal is `False`.
    ax : plt.Axes
            Axes to operate on.
    horizontal : Boolean, default `True`
        Whether to use axhspan or axvspan.
    **kwargs : Any
        Optional arguments supplied to axhspan or axvspan depending on
        `horizontal`
    
    Returns
    -------
    `NoneType`
    '''
    is_type(start_span, (int, float))
    is_type(stop_span, (int, float))
    is_type(ax, plt.Axes)
    is_type(horizontal, bool)
    # horizontal or vertical
    if horizontal == True:
        span = ax.axhspan
    else:
        span = ax.axvspan
    # plot
    span(start_span, stop_span, **kwargs)
    # return
    return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def change_ticks(ax:plt.Axes, ticks:List[str], labels:Union[List[str],None]=None,
                 axis:str='x', log:bool=False):
    '''
    Takes an axis and changes the ticks labels and location. If `labels` is
    set to `None`, it will use `ticks` for both the location and the labels.
    
    Can internally log-transformed `ticks`, and plot the `labels` at these
    locations.
    
    Parameters
    ----------
    ax : plt.Axes
    ticks : list
        A list of ticks marks which will be used for the position and labels
    labels : list
        If supplied use these labels instead of re-using `ticks`, need to check
        for len(ticks) == len(labels)
    log: bool, default `False`
        Should the `ticks` locations be np.log transformed. Does not affect the
        `ticklabels`.
    
    Returns
    -------
    `NoneType`
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
    *_col: str
        The column names for `data`.
    dropna: bool, default `False`
        Set to `True` to remove columns with any missing data.
    **kwargs: any
        All other arguments are forwarded to `pivot_table`.
        
    Returns
    -------
    point_mat : pd.DataFrame
        Table with point estimates.
    pvalue_mat : pd.DataFrame
        Table with p-values.
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
    pval : pd.DataFrame
        Direction times pvalue matrix; floats
    effect : pd.DataFrame
        An effect estimate matrix masking non-significant results; str
    star : pd.DataFrame
        An star matrix masking non-significant results; str
    pvalstring : pd.DataFrame
        P-value matrix masking non-significant results; str
    effect_float : pd.DataFrame
        An effect esimate matrix without masking: floats
    """
    
    # checking input
    if len(digits) > 1:
        digits=digits[0]
        # warnings
        warnings.warn("`digits` has length '{0}' "
                      "taking the first value".format(len(digits)))
    # taking the log10
    if log == True:
        pval_full = _nlog10_func(pval, ptrun)
    else:
        pval_full = pval.copy()
    # rounding
    dig = '{:.'+digits+'f}'
    pval = pval_full.round(int(float(digits)))
    dir = np.sign(effect)
    # simply stoaring the float matrix
    effect_float = effect.copy()
    # formatting
    if pd.__version__ < '2.1.0':
        effect = effect.applymap(dig.format).copy()
    else:
        effect = effect.map(dig.format).copy()
    # scaling
    pval = dir * pval
    # if log == True use larger than
    if log == True:
        # if not significant set to empty
        effect[pval_full < sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[pval_full >= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[pval_full >= sig] = pval[pval_full >= sig].astype('str')
        # if log != True use smaller than
    else:
        # if not significant set to empty
        effect[pval_full > sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[pval_full <= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[pval_full <= sig] = pval[pval_full <= sig].astype('str')
    
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
    exposure_col: str
        Column names in `data`
    outcome_col: str
        Column names in `data`
    point_col: str
        Column names in `data`
    alpha: float, default 0.05
        The significance cut-off.
    sig_numbers: int, default 2
        The number of significant numbers the cell annotations should have.
    ptrun: float, default 16
        P-values above this value will be truncated.
    annotate: str, default 'star'
        The cell annotation: 'star', 'pvalues', 'pointestimates',
        'None'. Set to `NoneType` to simply return the
        -log10(p-values) times effect direction
    without_log: boolean, default `False`
        If the p-value should `NOT` be -log10 converted.
    mask_na: boolean, default `True`
        If you want to mask missing results (e.g., replacing NAs by 0 or 1)
    **kwargs: any
        All other arguments are forwarded to `_extract`.
    
    Returns
    -------
    results: MatrixHeatmapResults
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
def fix_labels(annotations:List, axis:plt.Axes,
               min_distance:float=0.1):
    """
    Adjust the positions of annotations to prevent overlap.
    
    Parameters
    ----------
    annotations: list
        List of matplotlib ax.annotate objects.
    axis: matplotlib.axes.Axes
        The axis where the annotations are displayed.
    min_distance: float, default 0.1
        Minimum vertical distance between annotations.
    
    Returns
    -------
    `NoneType`
    """
    
    for i, ann1 in enumerate(annotations):
        for j, ann2 in enumerate(annotations):
            if i != j:
                # Get positions of annotations
                pos1 = axis.transData.inverted().transform(
                    axis.transData.transform(ann1.get_position())
                )
                pos2 = axis.transData.inverted().transform(
                    axis.transData.transform(ann2.get_position())
                )
                # Calculate distance between annotations
                vertical_distance = abs(pos1[1] - pos2[1])
                horizontal_distance = abs(pos1[0] - pos2[0])
                # Adjust positions if annotations overlap
                if vertical_distance < min_distance and\
                        horizontal_distance < min_distance:
                    if pos1[1] < pos2[1]:
                        pos1 = (pos1[0], pos2[1] - min_distance)
                    else:
                        pos2 = (pos2[0], pos1[1] - min_distance)
                    ann1.set_position(pos1)
                    ann2.set_position(pos2)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_mid_point(x:Union[List[float],Tuple[float, float]],
                   y:Union[List[float],Tuple[float, float]],
                   ) -> Tuple[float, float]:
    '''
    Takes two points and returns the Cartesian coordinates of the point in
    the middle of these two points.
    
    Parameters
    ----------
    x: list or tuple of two floats
        The x-coordinates of the two points.
    y: list or tuple of two floats
        The y-coordinates of the two points.
    
    Returns
    -------
    mid_point: tuple of two floats
        returns coordinate of the point between `x` and `y`.
    '''
    # input
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # calculates the mid point
    x_mid = sum(x)/2
    y_mid = sum(y)/2
    # return
    return x_mid, y_mid

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_angle_points(x:Union[List[float],Tuple[float, float]],
                      y:Union[List[float],Tuple[float, float]],
                      radians:bool=False,
                      ) -> float:
    '''
    Calculate the angle between two points, returns an angle between 0 and
    360 degrees.
    
    Parameters
    ----------
    x: list or tuple of two floats
        The x-coordinates of the two points.
    y: list or tuple of two floats
        The y-coordinates of the two points.
    radians:bool, default `False`
        set to `True` to return the angle in radians, instead of degrees.
    
    Returns
    -------
    angle: float
        returns an angle between 0 and 360 degrees.
    '''
    # input
    is_type(radians, bool)
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # get the angle
    delta_x = x[1] - x[0]
    delta_y = y[1] - y[0]
    slope=delta_y/delta_x
    angle_radians = np.arctan(slope)
    # convert radians to degrees
    angle_degrees_original = np.degrees(angle_radians)
    # ensure the angle is between 0 and 360 degrees
    angle = (angle_degrees_original + 360) % 360
    # get the principal angle
    if radians == True:
        angle = np.radians(angle)
    # return
    return angle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def segment_labelled(
    x:Tuple[float, float], y:Tuple[float, float], ax:plt.Axes,
    label:Union[None,str]=None,
    endpoints_marker:Union[mpath.Path,str]=mpath.Path.unit_circle(),
    endpoints_size:float=8, endpoints_c:str='orangered', segment_c='black',
    label_fontsize:float=10, label_background_c='white',
    overrule_angle:Union[None, float]=None,
    calc_angle_after_trans:bool=True,
    kwargs_segment:Dict[Any, Any]={},
    kwargs_text:Dict[Any, Any]={},
) -> plt.Axes:
    '''
    Plots a line segment between two points, and annotates the middle point
    with a `label` string.
    
    Parameters
    ----------
    x: list or tuple of two floats
        The x-coordinates of the two points.
    y: list or tuple of two floats
        The y-coordinates of the two points.
    label: str
        The string which be plotted on top of the line segment. Set to
        `NoneType` to not plot anything.
    endpoints_marker: str, default `unit_circle`
        The marker of the line segment endpoints.
    endpoints_size: float, default 30
        The marker size.
    endpoints_c: str, default `orangered`
        The marker colour.
    segment_c: str, default `black`
        The segment line colour
    label_fontsize: float, default 20
        The label font size.
    label_background_c: str, default `white`
        The label background colour.
    overrule_angle: float, default `NoneType`
        Use this to overrule the internally calculated angle against which the
        label will be plotted.
    calc_angle_after_trans: bool, default `True`
        Whether to apply a `ax.transData.transform_point` transformation before
        calculating the angle the text needs to be plotted on.
    ax: plt.axes,
        The matplotlib axis.
    kwargs_*_dict : dict, default empty dict
        Optional arguments supplied to the various plotting functions:
            kwargs_segment --> ax.plot
            kwargs_text    --> ax.text
    '''
    # ################### input
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    is_type(ax, plt.Axes)
    is_type(label, (type(None),str))
    # is_type(endpoints_marker, str)
    is_type(endpoints_size, (int, float))
    is_type(endpoints_c, str)
    is_type(label_fontsize, (int, float))
    is_type(label_background_c, str)
    is_type(overrule_angle, (type(None), float, int))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # ################### get mid point and angle
    mid_coordinates=calc_mid_point(x=x, y=y)
    if overrule_angle is None:
        # do we need to apply a transformation first
        if calc_angle_after_trans == True:
            p1 = list(ax.transData.transform_point((x[0], y[0])))
            p2 = list(ax.transData.transform_point((y[0], y[1])))
            x_trans=[p1[0], p2[0]]
            y_trans=[p1[1], p2[1]]
        else:
            x_trans = x
            y_trans = y
        text_angle=calc_angle_points(x=x_trans, y=y_trans)
    else:
        text_angle=overrule_angle
    # ################### plot line segment
    new_segment_kwargs = _update_kwargs(update_dict=kwargs_segment,
                                        c=segment_c,
                                        markersize=endpoints_size,
                                        marker=endpoints_marker,
                                        markerfacecolor=endpoints_c,
                                        linestyle='-'
                                        )
    ax.plot(x, y,
            **new_segment_kwargs)
    # ################### plot label
    if label is not None:
        new_label_kwargs = _update_kwargs(update_dict=kwargs_text,
                                          va='center', ha='center',
                                          backgroundcolor=label_background_c,
                                          fontsize=label_fontsize,
                                          rotation=text_angle,
                                          )
        ax.text(mid_coordinates[0], mid_coordinates[1], label,
                **new_label_kwargs,
                )
    # ################### return
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _extract_text_props(text_obj):
    """
    Extracts visible properties from a matplotlib.text.Text object
    by calling all safe `get_*` methods.
    
    Parameters
    ----------
    text_obj : `matplotlib.text.Text`
        The tick label from which to extract visual properties.
    
    Returns
    -------
    dict
        Dictionary of properties suitable for ax.text().
    """
    props = {}
    for name in dir(text_obj):
        if not name.startswith("get_"):
            continue
        method = getattr(text_obj, name)
        if not callable(method):
            continue
        try:
            props[name[4:]] = method()
        except TypeError:
            # Method requires an argument (e.g., get_window_extent)
            continue
        except (AttributeError, ValueError):
            # If there is not getter (AttributeError), or there is an internal
            # issue with the returned value (ValueError).
            continue
    return props

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE Update the calls to ax.text to simply accept a **kwargs
# NOTE depending on axis = x or y update the kwargs using _update_kwargs,
def annotate_axis_midpoints(ax:plt.Axes, labels:list[str],
                            axis:Literal['x','y']='y',
                            gap:int | float=6,
                            offset:float | None = None,
                            start_label:dict[str, float] | None = None,
                            end_label:dict[str, float] | None = None,
                            extra_text_props:dict[str, any] | None = None,
                            ):
    """
    Identifies gaps between axes label positions and annotates the midpoints
    with user supplied labels.
    
    Parameters
    ----------
    ax : `plt.Axes`
        The axis to annotate.
    labels : `list` [`str`]
        A list of labels for each midpoint.
    axis : {'x', 'y'}, default 'y'
        Which axis to analyse and annotate.
    gap : `int` or `float`, default 6
        The exact space between tick values to trigger annotation.
    offset : float, default `NoneType`
        The position of the label **orthogonal to the axis**, given in **axes
        coordinates** (0 = bottom/left of axis, 1 = top/right). Negative values
        place the label outside the axis bounds. Defaults to:
            - -0.01 for `axis='y'` (left of y-axis)
            - -0.02 for `axis='x'` (below x-axis)
    start_label : `dict` [`str`, `float`], default `NoneType`
        Optional label before the first detected gap. Format should be:
        `{"label text": position}` where position is the coordinate orthogonal
        to the axis (in axes coordinates).
    end_label : `dict` [`str`, `float`], default `NoneType`
        Optional label after the last detected gap. Same format as `start_label`.
    extra_text_props : `dict` [`str`, `any`]
        Extra keyword arguments for `ax.text()` (e.g. fontweight).
    """
    # ### check input
    is_type(ax, plt.Axes)
    is_type(axis, str)
    is_type(labels, list)
    is_type(gap, (int, float))
    is_type(offset, (type(None), int, float))
    is_type(start_label, (type(None), dict))
    is_type(end_label, (type(None), dict))
    if axis in ['y', 'x'] == False:
        raise ValueError('`axis` is limited to `x` or `y`.')
    # setting defaults
    if offset is None:
        offset = -0.01 if axis == 'y' else -0.02
    # initialise empty dict
    extra_text_props = extra_text_props or {}
    # #### Extract tick positions and labels from the chosen axis, and define
    # a label placement function with appropriate axis transform
    if axis == 'y':
        ticks = ax.get_yticks()
        ticklabels = ax.get_yticklabels()
        # make sure the axis y-axis is mapped to 0-1 range instead of the
        # original units, the x-axis is unaffected..
        transform = ax.get_yaxis_transform()
        place_text = lambda pos, spine_coord, label, props: ax.text(
            x=spine_coord, y=pos, s=label, transform=transform,
            ha='right',
            **props
        )
    else:
        ticks = ax.get_xticks()
        ticklabels = ax.get_xticklabels()
        # same as above.
        transform = ax.get_xaxis_transform()
        place_text = lambda pos, spine_coord, label, props: ax.text(
            x=pos, y=spine_coord, s=label, transform=transform,
            va='top',
            **props
        )
    #  #### Identify exact-sized gaps
    gap_indices = [
        i for i in range(len(ticks) - 1)
        if abs(ticks[i + 1] - ticks[i]) == gap
    ]
    n_expected = len(gap_indices)
    if isinstance(labels, list) and len(labels) != n_expected:
        raise IndexError(
            f"Expected {n_expected} labels for gaps == {gap}, "
            f"but received {len(labels)}."
        )
    # #### Base label style, extracted from the current tick labels.
    # NOTE this is rather fragile - leading to multiple KeyError/TypeError
    # first_label = next((lbl for lbl in ticklabels if lbl.get_text().strip()),
    #                    ticklabels[0])
    # base_props = _extract_text_props(first_label)
    # base_props.update(extra_text_props)
    # # to prevent TypeError if it is already present
    # for key in ("transform", "text", "x", "y", "font", "font_properties"):
    #     base_props.pop(key, None)
    base_props = extra_text_props.copy()
    # #### Adding optional start label
    if start_label and gap_indices:
        i = gap_indices[0]
        mid = (ticks[0] + ticks[i]) / 2
        label_str, spine_coord = list(start_label.items())[0]
        place_text(mid, spine_coord, label_str, base_props)
    # ##### Midpoint labels
    for j, i in enumerate(gap_indices):
        mid = (ticks[i] + ticks[i + 1]) / 2
        label_text = labels(j) if callable(labels) else labels[j]
        place_text(mid, offset, label_text, base_props)
    # #### Adding optional end label
    if end_label and gap_indices:
        i = gap_indices[-1]
        mid = (ticks[i + 1] + ticks[-1]) / 2
        label_str, spine_coord = list(end_label.items())[0]
        place_text(mid, spine_coord, label_str, base_props)

