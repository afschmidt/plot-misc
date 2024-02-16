'''
A module to draw forest plots and side tables, as well as related illustrations
such as tree plots.

Aside from the plotting functions the module contains functions to
appropriately orientated input DataFrames.
'''

# imports
# from matplotlib._api.deprecation import deprecated
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import warnings
from scipy.stats import norm
from typing import Any, List, Type, Union, Tuple, Dict, Sequence, Optional
from plot_misc.utils.utils import (
    _update_kwargs,
    _dict_string_argument,
    plot_span,
    segment_labelled,
)
from plot_misc.constants import ForestNames as FNames
from plot_misc.constants import (
    is_type,
    is_df,
    is_series_type,
    are_columns_in_df,
    InputValidationError,
    Error_MSG,
)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class PlotForestResults(object):
    '''
    The results object for `plot_forest`.
    '''
    SET_ARGS = [
        FNames.span,
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
    # /////////////////////////////////////////////////////////////////////////
    def __str__(self):
        return f"A `PlotForestResults` class."

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class EmpericalSupportPlotResults(PlotForestResults):
    '''
    Results class for the EmpericalSupport.plot function, inherits from
    the `PlotForestResults` class.
    '''
    SET_ARGS = [
        FNames.ESTIMATE,
        FNames.data_table,
    ]
    # /////////////////////////////////////////////////////////////////////////
    def __str__(self):
        return f"An `EmpericalSupport` class."

# #############################################################################
# functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def order_row(data:pd.DataFrame, order_outer:Dict[str, List[str]],
              order_inner:Union[Dict[str, List[str]], None]=None
              ) -> pd.core.frame.DataFrame:
    '''
    Order a data frame by and outer and inner order, say by study and within
    study by outcome.
    
    Parameters
    ----------
    data : pd.DataFrame
    oder_outer : dict
        The dictionary key will be used to select the `data` column, and the
        dictionary value should contain a list of string to order the column.
    order_inner : dict, default `NoneType`
        The dictionary key will be used to select the `data` column, and the
        dictionary value should contain a list of string to order the column.
        Set to `NoneType` to skip and only order by `oder_outer`.
    
    Returns
    -------
    order_data : pd.DataFrame.
    '''
    # check input
    AE_MSG = 'Please supply a `dict` of length one.'
    is_type(data, pd.DataFrame)
    is_type(order_outer, dict)
    is_type(order_inner, (type(None), dict))
    if len(order_outer) > 1:
        raise AttributeError(AE_MSG)
    if not order_inner is None:
        if len(order_inner) > 1:
            raise AttributeError(AE_MSG)
    # ### algorithm
    size_in = data.shape
    outer_col = list(order_outer.keys())[0]
    outer_lst = list(order_outer.values())[0]
    order_data = pd.DataFrame()
    # loop over outer order
    for sel_outer in outer_lst:
        slice_outer = data.loc[data[outer_col] == sel_outer]
        # do we have an inner order
        if not order_inner is None:
            inner_col = list(order_inner.keys())[0]
            inner_lst = list(order_inner.values())[0]
            inner_data = pd.DataFrame()
            for sel_inner in inner_lst:
                slice_inner = slice_outer.loc[
                    slice_outer[inner_col] == sel_inner]
                inner_data = pd.concat([inner_data, slice_inner])
                #end loop
            slice_outer = inner_data
            # end inner
        order_data = pd.concat([order_data, slice_outer])
    # ### check output
    if order_data.shape != size_in:
        IndexError('Input and output shape are distinct!')
    # return
    return order_data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def assign_distance(df:pd.DataFrame, group:str, within_pad:float=2,
                     between_pad:float=4, start:float=1, new_col:str='y_axis',
                     sort_dict:Union[Dict[str,int], None, str]=None,
                     strata:Union[str, None]=None,
                     ) -> pd.core.frame.DataFrame:
    """
    A helper function that adds a `y-axis` column (useful for Cartesian graphs)
    to a dataframe based on group membership. The within_pad arguments
    determines the spacing `between` groups with the same value, while
    between_pad sets the spacing `between` distinct groups.
    
    Arguments
    ---------
    df : pd.DataFrame
        The dataframe that contains the `group` of interest.
    group : str
        A string that maps to a column in df.
    strata : str, default `NoneType`
        An optional df column which nests the `group` values.
    within_pad : float, default 2.0
        The distance between point estimates nested within a group.
    between_pad : float, default 4.0
        The distance between groups of point estimates. This is the y-axis
        distance that will be skipped between the last y-axis coordinate in the
        previous group and the starting y-axis coordinate of the current group.
    start : float, default 0
        The starting position of the sequence.
    new_col : str, default `y_axis`
        The name of the column that will be added to `df`.
    sort_dict : dict, default `NoneType`
        Supply a key:value-float combination dictionary to sort the rows on
        `group` membership. Set to `NoneType` to order rows by
        `[order, strata]`. Set to `skip` to do nothing.
    
    Returns
    -------
    df : pd.DataFrame
    """
    df = df.copy()
    # check input
    is_type(df, pd.DataFrame)
    is_type(group, str)
    is_type(new_col, str)
    is_type(strata, (type(None), str))
    is_type(within_pad, (int, float))
    is_type(between_pad, (int, float))
    is_type(sort_dict, (type(None), dict, str))
    are_columns_in_df(df, expected_columns=[group])
    # if not group in df.columns:
    #     raise KeyError('`df` does not contain column {0}.'.format(group))
    if strata is None:
        # use a place-holder strata
        strata=FNames.strata_del
        df[strata]=1
    # sort index to group column values together
    if sort_dict is None:
        # sort by group value
        df.sort_values(by=[group, strata], inplace=True)
    elif sort_dict == 'skip':
        # do nothing
        pass
    else:
        # sort by custom order
        order=FNames.order_col
        df[order] = df[group].map(sort_dict)
        df.sort_values(by=[order, strata], inplace=True)
        del df[order]
    # number of groups and number of rows
    n_strat = len(df[strata].unique())
    n_group = len(df[group].unique())
    l_group = df[group].value_counts().unique()/n_strat
    if l_group.shape[0] != 1:
        raise ValueError('The number of group elements is not unique: {}.'.\
                         format(l_group.shape[0]))
    else:
        l_group = l_group[0]
    # getting spacing
    y_axis = []
    i = 0
    while i < n_group:
        # within group sequence
        chunk = np.arange(start, stop=start+within_pad*l_group, step=within_pad)
        y_axis = y_axis + chunk.tolist()
        # between group space
        start = y_axis[-1] + between_pad
        # incrementing
        i+=1
    # loop over the strata
    df[new_col] = np.nan
    for strat in df[strata].unique():
        df.loc[df[strata] == strat, new_col] = y_axis
    # return stuff
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_forest(df:pd.DataFrame, x_col:str, lb_col:Union[str, None]=None,
                ub_col:Union[str, None]=None, y_col:str='y_axis',
                s_size_col:Union[str,float,None]=None,
                s_col:str='o', c_col:str='black', g_col:Union[str, None]=None,
                a_col:Union[float, str]=1, shape_size:Union[float, None]=None,
                ci_lwd:float=2, ci_colour:str='indianred',
                connect_shape:bool = False, connect_shape_colour:str='black',
                connect_shape_lwd:float=1, span:bool = True,
                span_return:bool = False,
                span_colour:List[str] = ['white', 'lightgrey'],
                ax:Union[plt.Axes, None]=None, figsize:tuple=(10, 10),
                reverse_y:bool=True,
                verbose:bool=False,
                ylim:Union[Tuple[float, float], None]=None,
                kwargs_scatter_dict:Dict[Any, Any]={},
                kwargs_plot_ci_dict:Dict[Any, Any]={},
                kwargs_connect_segments_dict:Dict[Any, Any]={},
                kwargs_span_dict:Dict[Any, Any]={}
                ) -> Tuple[plt.Figure, plt.Axes, PlotForestResults]:
    """
    Plots points based on their `x_col` and `y_col` values on a Cartesian
    coordinate system. By including indicators of precision as lower and
    upper bounds (e.g., representing a confidencen interval), this plot is
    often referred to as a forest plot.
    
    The plotting functions allows for grouping of estimates by `group`.
    Related, if there are estimates with the same `y_col` value these get
    depicted as a horizontal sequence linked by an optional line segement
    (`connect_shaep`).
    
    Parameters
    ----------
    df : pd.DataFrame
    x_col : str
        The column name of the x-axis values (typically point estimates).
    lb_col : str, default None
        The column name of the lower bound of an confidence interval.
    ub_col : str, default None
        The column name of the upper bound of an confidence interval.
    y_col : str, default `y_axis`
        The column name of the y-axis values used to differentiate
        estimates/studies.Should contain `int` or `float` values representing
        the cartesian y-coordinate for each point.
    s_col : str, default `o`
        The column name of the shape indicators. If string is not found in `df`
        the string value will be added to an `s_col` column.
    c_col : str, default `black`
        The column name of the shape colour indicators. If string is not found
        in `df` the string value will be added to an `c_col` column.
    a_col : float or str, default 1
        The column name of the alpha value for each point. If the string is not
        found in `df`, the float will be added to an `a_col` column.
    g_col : str, default `NoneType`
        The column name of the group indicator; often the outcome or study
        indicators. If None, a column with a unique value for each row will be
        added - so there are no groups. This column will also be used to
        provide y-axis ticklabels.
    s_size_col : str, float, default 40
        The column name of the `shape size` value for each point. Can also
        simply supply a `float` for a uniform shape. Supplying a `NoneType`
        will default to 40.
    ci_lwd : float, default 1
        The line width of the confidence intervals.
    ci_colour : float, default 'indianred'
        The line colour of the confidence intervals
    connect_shape : boolean, default `False`
        If the point estimates should be connected with a line. Only relevant
        when estimates have the same y-axis.
    connect_shape_colour : str, default `grey`
        The line colour.
    connect_shape_lwd : float, default 1.0
        The line width.
    span : boolean, default `True`
        Whether an colour-interchanging horizontal background segment should
        be added
    span_return : boolean, default `False`
        Whether to return a dictionary with the span coordinates and kwargs to
        ``ax.axhspan``.
    span_colour : list of two string, default ['white', 'lightgrey']
        The colours of the span.
    ylim : tuple of floats, `NoneType`
        Overwrite the default y-limits if not set to `NoneType`.
    ax : plt.axes, default `NoneType`
        An optional matplotlib axis. If supplied the function works on the axis.
    figsize : tuple of two floats, default (10, 10),
        The figure size, when ax is set to None.
    reverse_y : boolean, default `True`
        inverts the y-axis.
    kwargs_*_dict : dict, default empty dict
        Optional arguments supplied to the various plotting functions:
            kwargs_scatter_dict          --> ax.scatter
            kwargs_plot_ci_dict          --> ax.plot
            kwargs_connect_segments_dict --> ax.plot
            kwargs_span_dict             --> ax.axhspan
    
    Returns
    -------
    figure : plt.Figure
        This will default to `NoneType` unless the figure is internally created.
        That is when an `ax` argument is supplied.
    axes : plt.Axes
    results : PlotForestResults class
        Unpacks matplotlib figure, axes, class
    
    Examples
    --------
    Additional control over the dots and confidence intervals characteristics
    can be leveraged by accessing `kwargs_scatter_dict` or
    `kwargs_scatter_dict`, and assigning a 'row[col_name]` value to a keyword
    argument. Here `row` represents a row of the `df` accessed through
    `df.iterrows()`. The string value will be evaluated and assigned
    internally:
    
    >>> plot_forest(df,
    >>>             ...,
    >>>             kwargs_scatter_dict={'linewidths': 'row[lw_col_name]'},
    >>>            )
    >>>
    
    """
    # ################### internal constants
    ROW = 'row'
    # ################### do check and set defaults
    is_type(x_col, str)
    is_type(lb_col, (type(None), str))
    is_type(ub_col, (type(None), str))
    is_type(y_col, str)
    is_type(s_col, str)
    is_type(c_col, str)
    is_type(g_col, (type(None),str))
    is_type(a_col, (int, float, str))
    is_type(shape_size, (str,int, float, type(None)))
    is_type(s_size_col, (str,int, float, type(None)))
    is_type(ci_lwd, (int, float))
    is_type(ci_colour, str)
    is_type(connect_shape, bool)
    is_type(span, bool)
    is_type(connect_shape_lwd, (int, float))
    is_type(connect_shape_colour, str)
    is_type(span_colour, list)
    is_type(ax, (type(None), plt.Axes))
    is_type(figsize, tuple)
    is_type(reverse_y, bool)
    is_df(df)
    is_type(ylim, (type(None), tuple))
    is_series_type(df[x_col], (float, int))
    try:
        is_series_type(df[y_col], (float, int))
    except InputValidationError:
        raise InputValidationError(
            '`y_col` should refer to a column containing '
            'integers or floats. These are used to as '
            'y-value in a Cartesian coordinates system. '
            'Please refer to: '
            'https://en.wikipedia.org/wiki/Cartesian_coordinate_system .'
        )
    if (ub_col is not None) and (lb_col is not None):
        is_series_type(df[[ub_col, lb_col]], (float, int))
    # set default shape and colour and alpha
    s_col_name = s_col
    c_col_name = c_col
    a_col_name = a_col
    if s_col_name not in df.columns:
        s_col_name = FNames.s_col
        df[s_col_name] = s_col
        if verbose == True:
            warnings.warn('`{0}` not found in `df`, creating `s_col` column '
                          'with value {1}.'.format(s_col_name, s_col),
                          RuntimeWarning)
        del s_col
    if c_col not in df.columns:
        c_col_name = FNames.c_col
        df[c_col_name] = c_col
        if verbose == True:
            warnings.warn('`{0}` not found in `df`, creating `c_col` column '
                          'with value {1}.'.format(c_col_name, c_col),
                          RuntimeWarning)
        del c_col
    if a_col not in df.columns:
        a_col_name = FNames.a_col
        df[a_col_name] = a_col
        if verbose == True:
            warnings.warn('`{0}` not found in `df`, creating `a_col` column '
                          'with value {1}.'.format(a_col_name, a_col),
                          RuntimeWarning)
        del a_col
    if g_col is None:
        g_col = FNames.g_col
        df[g_col] = range(df.shape[0])
    # Handel shape size
    if not shape_size is None:
        warnings.warn('`shape_size` will be deprecated in future, please use '
                      '`s_size_col` instead. Note that s_size_col takes '
                      'precedence over `shape_size` without further warning.',
                      FutureWarning)
    if isinstance(shape_size, str):
        shape_size_name = shape_size
    elif isinstance(shape_size, (float, int)):
        shape_size_name = 'shape_size'
        df[shape_size_name] = shape_size
    # Use s_size_col
    if isinstance(s_size_col, str):
        shape_size_name = shape_size
    elif isinstance(s_size_col, (float, int)):
        shape_size_name = 'shape_size'
        df[shape_size_name] = s_size_col
    elif shape_size is None:
        # use default
        shape_size_name = 'shape_size'
        df[shape_size_name] = 40
    # logic checks
    if (span_return == True) and (span == False):
        warnings.warn('`span_return` will be ingored when `span` is set to '
                      '`False`.')
    # ################## should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = None
    # ################## plot points and errors
    for _, row in df.iterrows():
        # coordinates
        xs = row[x_col]
        ys = row[y_col]
        # add points
        # checking if there are string values containing `row` which need to
        # be evaluated.
        kwargs_scatter_dict = \
            _dict_string_argument(ROW, kwargs_scatter_dict, locals())
        # updating kwargs dict
        new_scatter_kwargs = _update_kwargs(update_dict=kwargs_scatter_dict,
                                            s=row[shape_size_name],
                                            marker=row[s_col_name],
                                            c=row[c_col_name],
                                            alpha=row[a_col_name],
                                            zorder=2,
                                            )
        ax.scatter(x=xs, y=ys, **new_scatter_kwargs,
                   )
        # add confidene intervals
        # if none replace with the point estimate
        if lb_col is None:
            lb = xs
        else:
            lb = row[lb_col]
        if ub_col is None:
            ub = xs
        else:
            ub = row[ub_col]
        # plot
        x_values = [lb, ub]
        y_values = [ys, ys]
        # checking if there are string values containing `row` which need to
        # be evaluated.
        kwargs_plot_ci_dict = \
            _dict_string_argument(ROW, kwargs_plot_ci_dict, locals())
        # updating kwargs dict
        new_plot_ci_kwargs = _update_kwargs(update_dict=kwargs_plot_ci_dict,
                                            c=ci_colour, linewidth=ci_lwd,
                                            )
        ax.plot(x_values, y_values, **new_plot_ci_kwargs,
                )
    # ################## aggregate coordinates
    # NOTE define min, max, mean as constants at the start
    group_y = df.groupby(y_col).agg({x_col: {FNames.min,FNames.max}})
    y_locations = df.groupby(g_col).agg({y_col: {
        FNames.mean,FNames.min, FNames.max
    }})
    # ################## segments between points
    if connect_shape ==True:
        xg_value = [ [min, max] for min, max in zip(group_y[x_col,FNames.min],
                                                    group_y[x_col,FNames.max])]
        yg_value = [ [yval, yval] for yval in  group_y.index]
        for xg, yg in zip(xg_value, yg_value):
            # only add segments if there are two distinct x-values
            if np.unique(xg).shape[0] == 2:
                new_connect_segments_kwargs = _update_kwargs(
                    update_dict=kwargs_connect_segments_dict,
                    c=connect_shape_colour, linewidth=connect_shape_lwd,
                    zorder=1
                )
                ax.plot(xg, yg, **new_connect_segments_kwargs,
                        )
            else:
                warnings.warn('The line segments have the same x-axis value, '
                              'the line plotting will be skipped.',
                              RuntimeWarning)
    # ################### calculate y-axis mid points
    y_locations = y_locations[y_col].sort_values(FNames.min)
    y_mid = []
    for r in range(y_locations.shape[0]):
        maxy = y_locations.iloc[r][FNames.max]
        try:
            miny = y_locations.iloc[r+1][FNames.min]
        except IndexError:
            miny = np.nan
        # get mid
        y_mid.append(np.nanmean([maxy, miny]))
    # ################### adjust y margins
    # adjust margin
    mima = list(df.sort_values(y_col)[y_col])[:2]
    diff = mima[1] - mima[0]
    new_margins = [min(df[y_col]) - diff/2, max(df[y_col]) + diff/2]
    if ylim is not None:
        ax.set_ylim(ylim)
    else:
        ax.set_ylim(new_margins)
    # add the starting and endpoints
    y_mid.insert(0, y_locations.iloc[0][FNames.min])
    y_mid[-1] = ax.get_ylim()[1] # replace with y-axis limit
    # ################### Add horizontal segments
    if span ==True:
        # to store the span y-axis coordiniates, colours
        span_dict = {}
        # add segments
        for t in range(len(y_mid)-1):
            ymin = y_mid[t]
            # # skipp if first or last (too tired to find an actual solution!)
            # if (t == 0) or (t == (len(y_mid)-1)):
            #     continue
            # stop if t is too large
            try:
                ymax = y_mid[t+1]
            except IndexError:
                ymax = y_mid[t]
            # change every second step
            if t % 2 == 0:
                col = span_colour[0]
            else:
                col = span_colour[1]
            # plot
            new_span_kwargs = _update_kwargs(
                update_dict=kwargs_span_dict,
                color=col, zorder=0
            )
            plot_span(ymin, ymax, ax=ax,
                      **new_span_kwargs,
                       )
            if span_return == True:
                span_dict[t] = {FNames.min:ymin, FNames.max:ymax,
                                FNames.kwargs:new_span_kwargs,
                                }
    # ################### add y-axis labels
    ax.set_yticks(y_locations[FNames.mean])
    ax.set_yticklabels(y_locations.index)
    # ################### invert y-axis
    if reverse_y == True:
        ax.invert_yaxis()
    # ################### return the figure, axis, and other
    other = {
        FNames.span: {},
    }
    if span_return == True:
        other = {FNames.span: span_dict}
    return f, ax, PlotForestResults(**other)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_table(
    dataframe: pd.core.frame.DataFrame,
    ax: plt.Axes, string_col: str, pad:float=1.0, pad_header:float=1.0,
    halignment_text:str="center", halignment_header:str="center",
    valignment_text:str="center", valignment_header:str="center",
    negative_padding:float=1.0, size_text:float=10,
    size_header:float=10, size_yticklabel:float=10, y_col:str='y_axis',
    yticklabel:Optional[Union[Sequence[str], None]]=None,
    ytickloc:Optional[Union[Sequence[float], None]]=None,
    l_yticklab_pad:Optional[Union[str, None]]=None,
    r_yticklab_pad:Optional[Union[str, None]]=None,
    annoteheader: Optional[Union[str, None]]=None,
    span:Optional[Union[dict, None]]=None,
    span_start:str='min',
    span_stop:str='max',
    span_kwargs:str='kwargs',
    kwargs_text_dict:Dict[Any, Any]={},
    kwargs_header_dict:Dict[Any, Any]={},
    kwargs_yticklabel_dict:Dict[Any, Any]={},
) -> plt.Axes:
    """
    Plots a side-table using `ax.text` and supplied `plt.Axes`.
    
    Parameters
    ----------
    dataframe : pd.DataFrame
            Pandas DataFrame containg `string_col` that should be plotted.
            margin of error, etc.
    y_col : str, default 'y_axis'
        The column name of the y-axis values used to identify rows.
    string_col : str,
            The the column name that should be plotted. Should contain a
            `string` value.
    annoteheaders : str, default `NoneType`
        string to annotate the table column.
    pad: float, default 1.0
        Multiplication factor for the x-coordinate location:
        `mean(ax.get_xlim())`.
    pad_header: float, default 1.0
        Same as `pad`.
    negative_padding : float, default 1.0
        determines the y-coordinate of the table header as:
        `ax.get_ylim()[1] - ngative_padding`
    size_text : float, default 10
        The font size for the table text.
    size_header : float, default 10
        The font size for the table header.
    yticklabel : list of strings
        A list of string containing the y-axis labels. Should match the length
        of `ytickloc`.
    ytickloc : list of floats
        A list of floats defining the y-axis locations for the ticks.
    [l|r]_yticklab_pad: str
        An optional string to use as a prefix or suffic of the y-axis labels.
    span : dict, default `NoneType`
        Whether you want to add an optional span. Supply a dictionary with
        k many unique keys and a dictionary value containing `span_start`,
        `span_stop` and `span_kwargs`. This will all be supplied to
        `merit_helper.utils.utils.plot_span`.
    ax : plt.axes
            Axes to operate on.
    kwargs_*_dict : dict, default empty dict
        Optional arguments supplied to the various plotting functions:
            kwargs_text_dict            --> ax.text
            kwargs_header_dict          --> ax.text
            kwargs_yticklabel_dict      --> ax.yaxis.set_ticklabels
    Returns
    -------
    ax : plt.axes,
        a matplotlib axes.
    """
    # ################### do check and set defaults
    is_type(y_col, str)
    is_type(ax, plt.Axes)
    is_type(string_col, str)
    is_type(pad, (float, int))
    is_type(annoteheader, (type(None), str))
    is_type(halignment_text, str)
    is_type(valignment_text, str)
    is_type(halignment_header, str)
    is_type(valignment_header, str)
    is_type(size_header, (float, int))
    is_type(size_text, (int, float))
    is_type(negative_padding, (float, int))
    is_type(l_yticklab_pad, (type(None), float, int))
    is_type(r_yticklab_pad, (type(None), float, int))
    is_type(yticklabel, (type(None), list))
    is_type(ytickloc, (type(None), list))
    is_type(span, (type(None), dict))
    # check if columns are in dataframe
    are_columns_in_df(dataframe, expected_columns=[string_col, y_col])
    # ################### remove spines
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    # remove lables
    ax.xaxis.set_ticklabels([])
    # remove ticks
    ax.set_xticks([])
    # ################### add y-labels
    if (not yticklabel is None) and (ytickloc is None):
        ValueError('`ytickloc` should be supplied if `yticklabel` is defined.')
    if (yticklabel is None) and (not ytickloc is None):
        ValueError('`yticklabel` should be supplied if `ytickloc` is defined.')
    if (not yticklabel is None) and (not ytickloc is None):
        if len(yticklabel) != len(ytickloc):
            IndexError('`yticklabel` and `ytickloc` containts distinct values.')
        # add optional label padding
        if not l_yticklab_pad is None:
            yticklabel = [l_yticklab_pad + str(s) for s in yticklabel]
        if not r_yticklab_pad is None:
            yticklabel = [str(s) + r_yticklab_pad for s in yticklabel]
        # plot y-tick labels
        ax.set_yticks(ytickloc)
        # update kwargs for labels
        new_yticklabel_kwargs = _update_kwargs(
            update_dict=kwargs_yticklabel_dict,
            weight=FNames.fontweight,
            size=size_yticklabel,
        )
        ax.yaxis.set_ticklabels(yticklabel,
                                **new_yticklabel_kwargs,
                                )
        # remove the actual tick
        ax.tick_params(left=False)
    else:
        # remove y ticks
        ax.yaxis.set_ticklabels([])
        ax.set_yticks([])
    # ################### plot string column
    # x location
    xloc = np.mean(ax.get_xlim()) * pad
    xloc_header = np.mean(ax.get_xlim()) * pad_header
    # tick labels
    for _, row in dataframe.iterrows():
        yticklabel1 = row[y_col]
        yticklabel2 = row[string_col]
        if pd.isna(yticklabel2):
            yticklabel2 = ""
        # update the kwargs
        new_text_kwargs = _update_kwargs(
            update_dict=kwargs_text_dict,
            size=size_text,
            horizontalalignment=halignment_text,
            verticalalignment=valignment_text,
        )
        # plotting table text
        ax.text(
            x=xloc,
            y=yticklabel1,
            s=yticklabel2,
            **new_text_kwargs,
        )
    # ################### add header
    if annoteheader is not None:
        # update the kwargs
        new_header_kwargs = _update_kwargs(
            update_dict=kwargs_header_dict,
            size=size_header,
            horizontalalignment=halignment_header,
            verticalalignment=valignment_header,
            fontweight=FNames.fontweight,
        )
        t = ax.text(
            x=xloc_header,
            y=ax.get_ylim()[1] - negative_padding,
            s=annoteheader,
            **new_header_kwargs,
        )
    # ################### add optional span
    if span is not None:
        for s in span:
            plot_span(span[s][span_start],
                      span[s][span_stop],
                      ax=ax,
                      **span[s][span_kwargs],
                      )
    # ################### return
    return ax

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Supported parameter space
class EmpericalSupport(object):
    '''
    A class to calculate and plot a somewhat historic empirical support plot
    that essentially plots all the possible confidence intervals to show
    the parameter space that is support by the data for a given coverage level,
    or equivalently `compatibility` based on the p-value.
    
    References
    ----------
    This is (partially) inspired based on the following
    `publication <https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-01105-9>`_.
    
    Parameters
    ----------
    estimate: float
        The estimated point estimate.
    standard_error: float
        The standard error of the point estimate.
    alpha: list of floats
        A list of alpha's (i.e., type 1 error rate) between 0 and 1.
        Typically should be around a 1000 values, for example generated
        using np.linspace.
    '''
    
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self,
                 estimate:float, standard_error:float, alpha:List[float],
                 ):
        '''
        Setting up kwargs for `calc_empirical_support` and
        `plot_empirical_support`.
        '''
        # confirm input
        is_type(estimate, (int, float))
        is_type(standard_error, (int, float))
        is_type(alpha, (list, np.ndarray))
        # asign
        self.estimate=estimate
        self.standard_error=standard_error
        self.alpha=alpha
   # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __str__(self):
        return (
            "A class to calculate and plot the parameter space supported "
            "the available data."
        )
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def calc_empirical_support(
        estimate:float, standard_error:float, alpha:List[float],
                          ) -> pd.DataFrame:
        '''
        Takes an point `estimate` (e.g., a mean difference or log-transformed
        odds ratio), its `standard_error`, and a list of `alpha's` between 0
        and 1. This will be used to calculate the empirical support for a
        parameter range centered around `estimates`. The empirical support will
        be calculated in the form of the p-values and confidence intervals, but
        reflecting to what extent the parameter space is compatibility to the
        `estimate`.
        
        Parameters
        ----------
        estimate: float,
            The estimated point estimate.
        standard_error: float,
            The standard error of the point estimate.
        alpha: list of floats,
            A list of alpha's (i.e., type 1 error rate) between 0 and 1.
            Typically should be around a 1000 values, for example generated
            using np.linspace.
        
        Returns
        -------
        table: pd.DataFrame
            Returns a table with the lower and upper bounds of the confidence
            interval, as well as the p-value and confidence interval coverage.
        '''
        # check input
        ERROR='`{}` should not {} {}, current {}: {}.'
        is_type(estimate, (int,float))
        is_type(standard_error, (int, float))
        is_type(alpha, (list, np.ndarray))
        is_series_type(pd.Series(alpha), float)
        if max(alpha) > 1:
            raise ValueError(
                ERROR.format('alpha', 'exceed', '1', 'maximum', str(max(alpha)))
            )
        if min(alpha) < 0:
            raise ValueError(
                ERROR.format('alpha', 'be smaller than', '0', 'minimum',
                             str(min(alpha)))
            )
        # coverage
        lb, ub = ( [] for _ in range(2) )
        for a in alpha:
            lb.append(estimate - standard_error*norm.ppf(1-a/2))
            ub.append(estimate + standard_error*norm.ppf(1-a/2))
        # table
        n = len(lb)
        table = pd.DataFrame({
            FNames.ESTIMATE : [estimate] * n,
            FNames.LOWER_BOUND: lb,
            FNames.UPPER_BOUND: ub,
            FNames.PVALUE: alpha,
            FNames.CI: [1-a for a in alpha],
        })
        # return
        return table
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def plot_empirical_support(
        data:pd.DataFrame, lb_col:str, ub_col:str, support_col:str,
        line_c:str='black', linewidth:float=1, linestyle:str='-',
        estimate:Union[float,None]=None, estimate_size:float=40,
        estimate_shape:Union[str, mpath.Path]=mpath.Path.unit_circle(),
        estimate_c:str='orangered',
        area_c:Union[str, None]=None, area_a:float=0.7,
        ax:Union[plt.Axes, None]=None, figsize:Tuple[float, float]=(10, 10),
        reverse_y:bool=False,
        kwargs_plot:Dict[Any,Any]={},
        kwargs_dot:Dict[Any,Any]={},
        kwargs_fill:Dict[Any,Any]={},
    ) -> Tuple[plt.Figure, plt.Axes]:
        '''
        Creates a Empirical support plot, which identifies the parameter space
        compatible with `estimate` given desired certainty. Essentially this
        plots all possible confidence intervals across a range of coverage
        probabilities between 0 and 1.
        
        Parameters
        ----------
        data: pd.DataFrame
            A pandas DataFrame containing the lower and upper bounds, as well
            as indicator of support (plotted on the y-axis).
        lb_col: str
            The column name of the lower bound.
        ub_col: str
            The column name of the upper bound.
        support_col: str
            The column name of the support values. Typically this will
            be a column with confidence interval floats, or a column of
            p-values/alpha's.
        line_c: str, default `black`
            The colour of the confidence interval curves.
        linewidth: float, default `1.0`
            The size of the confidence interval curves.
        linestyle: str, default `-`
            The linestyle of the confidence interval curves.
        estimate: float, default `NoneType`
            Provide this to plot the estimate as a marker on top of the graph.
            Set to `NoneType` to skip.
        estimate_size: float, default `1.0`
            The size of the estimate marker.
        estimate_shape: str, default `o`
            The estimate marker.
        estimate_c: str, default `orangered`
            The color of the estimate marker.
        area_c: str, default `NoneType`
            The colour of the area between the confidence intervals. This
            is mapped to the facecolor parameter. Set to `NoneType` to skip.
        area_a: float, default `0.7`
            The proportion of opacity of the area between the curves.
        ax : plt.axes, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis, otherwise the function will create an axis object internally.
        figsize : tuple of two floats, default (10, 10),
            The figure size, when ax==None.
        reverse_y : boolean, default `True`
            inverts the y-axis.
        kwargs_*_dict : dict, default empty dict
            Optional arguments supplied to the various plotting functions:
                kwargs_plot --> ax.plot
                kwargs_dot  --> ax.scatter
                kwargs_fill --> ax.fill_betweenx
        
        Returns
        -------
        Unpacks a matplotlib figure and axis.
        '''
        # ################## check input
        is_df(data)
        is_type(lb_col, str, 'lb_col')
        is_type(ub_col, str, 'ub_col')
        is_type(support_col, (str, type(None)), 'support_col')
        is_type(line_c, str, 'line_c')
        is_type(linewidth, (int, float), 'linewidth')
        is_type(linestyle, str, 'linestyle')
        is_type(estimate, (int, float, type(None)), 'estimate')
        is_type(estimate_size, (int, float), 'estimate_size')
        is_type(estimate_c, str, 'estimate_c')
        is_type(area_c, (type(None),str), 'area_c')
        is_type(area_a, (int, float), 'area_a')
        is_type(ax, (type(None), plt.Axes), 'ax')
        is_type(figsize, tuple, 'figsize')
        is_type(reverse_y, bool, 'reverse_y')
        # ################## should we create a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = None
        # ################## annotate point
        if estimate is not None:
            # find location where lb == ub
            center=data[data[lb_col] == data[ub_col]][support_col].to_list()[0]
            new_dot_kwargs = _update_kwargs(update_dict=kwargs_dot,
                                            c=estimate_c,
                                            s=estimate_size,
                                            marker=estimate_shape,
                                            zorder=2,
                                            )
            ax.scatter(y=center, x=estimate,
                       **new_dot_kwargs)
        # ################## plots lines
        new_plot_kwargs = _update_kwargs(update_dict=kwargs_plot,
                                         c=line_c,
                                         linewidth=linewidth,
                                         linestyle=linestyle,
                                         zorder=1,
                                         )
        yval=data[support_col].to_numpy()
        for xval in [lb_col, ub_col]:
            x = data[xval].to_numpy()
            ax.plot(x, yval,
                    **new_plot_kwargs)
        # ################### colour the area
        if area_c is not None:
            new_fill_kwargs = _update_kwargs(update_dict=kwargs_fill,
                                             facecolor=area_c,
                                             alpha=area_a,
                                             zorder=0,
                                             )
            ylimits=np.linspace(1,0, data.shape[0])
            # create the xaxis limits
            xleft=data[lb_col].to_numpy(); xright=data[ub_col].to_numpy()
            ax.fill_betweenx(ylimits, xleft, xright,
                             **new_fill_kwargs)
        # ################### invert y-axis
        if reverse_y == True:
            ax.invert_yaxis()
        # ################### return the figure, and axis
        return f, ax
    # /////////////////////////////////////////////////////////////////////////
    # main function
    def plot_tree(self,
             support:str='coverage', annotate_estimate:bool=False,
             annotate_ci:Union[None,List[float]]=None,
             line_c:str='black', linewidth:float=0.5, linestyle:str='-',
             estimate_size:float=20, estimate_c:str='orangered',
             estimate_shape:str=mpath.Path.unit_circle(),
             area_c:Union[str, None]=None, area_a:float=1.0,
             reverse_y:Union[None,bool]=None,
             ax:Union[plt.Axes, None]=None,
             figsize:Tuple[float, float]=(10, 10),
             kwargs_plot:Dict[Any,Any]={},
             kwargs_dot:Dict[Any,Any]={},
             kwargs_fill:Dict[Any,Any]={},
             kwargs_xlabel:Dict[Any,Any]={},
             kwargs_ylabel:Dict[Any,Any]={},
             kwargs_segment:Dict[Any,Any]={},
             kwargs_text:Dict[Any, Any]={},
             )-> Tuple[plt.Figure, plt.Axes, EmpericalSupportPlotResults]:
        '''
        Plots an Emperical Support graph based on either `coverage` (iterating
        the confidence interval coverage percentage), or `compatibility`
        (iterating the p-value). Due to its Christmas tree like shape I am
        refering to this as a `tree plot`.
        
        Parameters
        ----------
        support: str, default `coverage`
            Plots the confidence interval percentage on the y-axis from 0 to 1,
            or for `compatible` plots the p-value from 1 to 0.
        annotate_estimate: bool, default `False`
            Should the estimate be added as a dot.
        annotate_ci: list of floats, default `NoneType`
            Will add a horizontal line segment at each float position using
            `merit_helper.utils.utils.segment_labelled`.
        line_c: str, default `black`
            The colour of the confidence interval curves.
        linewidth: float, default `1.0`
            The size of the confidence interval curves.
        linestyle: str, default `-`
            The linestyle of the confidence interval curves.
        estimate: float, default `NoneType`
            Provide this to plot the estimate as a marker on top of the graph.
            Set to `NoneType` to skip.
        estimate_size: float, default `1.0`
            The size of the estimate marker.
        estimate_shape: str, default `o`
            The estimate marker.
        estimate_c: str, default `orangered`
            The color of the estimate marker.
        area_c: str, default `NoneType`
            The colour of the area between the confidence intervals. This
            is mapped to the facecolor parameter. Set to `NoneType` to skip.
        area_a: float, default `0.7`
            The proportion of opacity of the area between the curves.
        ax : plt.axes, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis, otherwise the function will create an axis object internally.
        reverse_y : boolean, default `NoneType`
            Inverts the y-axis.  Set to `False` or `True` to overwrite internal
            behaviour.
        kwargs_*_dict : dict, default empty dict
            Optional arguments supplied to the various plotting functions:
                kwargs_plot    --> ax.plot
                kwargs_dot     --> ax.scatter
                kwargs_fill    --> ax.fill_betweenx
                kwargs_ylabel  --> ax.set_ylabel
                kwargs_xlabel  --> ax.set_xlabel
                kwargs_segment --> ax.plot (merit_helper.utils.utils.segment_labelled)
                kwargs_text    --> ax.text (merit_helper.utils.utils.segment_labelled)
        
        Returns
        -------
        f: plt.Figure
            This will default to `NoneType` unless the figure is internally created.
            That is when an `ax` argument is supplied.
        axes: plt.Axes
        results: EmpericalSupportPlotResults
        
        Unpacks a matplotlib figure, axes, and a EmpericalSupportPlotResults
        class containing the internally used data.
        '''
        # ################### input
        is_type(support, str)
        is_type(annotate_estimate, bool)
        is_type(annotate_ci, (type(None), list))
        if (support != FNames.EmpericalSupport_Coverage) &\
                (support != FNames.EmpericalSupport_Compatability):
            raise InputValidationError(
                Error_MSG.INVALID_STRING.format(
                    'support', FNames.EmpericalSupport_Coverage + ' or ' +
                    FNames.EmpericalSupport_Compatability
                )
            )
        # ################### calculate support
        self.table = self.calc_empirical_support(
            estimate=self.estimate, standard_error=self.standard_error,
            alpha=self.alpha,
        )
        # ################### plot support
        # do we need a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = None
        if support == FNames.EmpericalSupport_Coverage:
            self.support_col = FNames.CI
            self.ylabel = 'Coverage'
            self.table =self.table.sort_values(
                by=[self.support_col], ascending=False)
            self.reverse_y=True
        else:
            self.support_col = FNames.PVALUE
            self.ylabel = 'Compatibility\n(p-value)'
            self.reverse_y=False
        if reverse_y is not None:
            self.reverse_y=reverse_y
        # do we annotate the point
        if annotate_estimate == True:
            plot_estimate=self.estimate
        else:
            plot_estimate=None
        # ################### plot
        f, ax = self.plot_empirical_support(
            data=self.table, support_col=self.support_col,
            lb_col=FNames.LOWER_BOUND, ub_col=FNames.UPPER_BOUND,
            estimate=plot_estimate, estimate_size=estimate_size,
            estimate_shape=estimate_shape, estimate_c=estimate_c,
            line_c=line_c, linewidth=linewidth, linestyle=linestyle,
            area_c=area_c, area_a=area_a,
            ax=ax, figsize=figsize,
            reverse_y=self.reverse_y,
            kwargs_plot=kwargs_plot,
            kwargs_dot=kwargs_dot,
            kwargs_fill=kwargs_fill,
        )
        # ################### add ci annotations
        if annotate_ci is not None:
            for val in annotate_ci:
                # finding the CI with the smallest difference compared to val
                idx = (self.table[FNames.CI]-val).abs().argsort().iloc[1]
                # getting the x and y values
                x_seg = self.table.iloc[idx][[FNames.LOWER_BOUND,
                                         FNames.UPPER_BOUND]].to_list()
                # which y_value to use
                if support == FNames.EmpericalSupport_Coverage:
                    Y_COL = FNames.CI
                else:
                    Y_COL = FNames.PVALUE
                y_seg = self.table.iloc[idx][[Y_COL]].to_list()*2
                # getting the string
                val_str="{:.2f}".format(np.round(val, 2))
                segment_labelled(x=x_seg, y=y_seg, label=val_str,
                                 ax=ax,
                                 # will be a line
                                 overrule_angle=0,
                                 kwargs_segment=kwargs_segment,
                                 kwargs_text=kwargs_text,
                                 )
        # set label
        ax.set_xlabel('Point estimate', **kwargs_xlabel)
        ax.set_ylabel(self.ylabel, **kwargs_ylabel)
        # ################### return
        results_dict={FNames.ESTIMATE   : self.estimate,
                      FNames.data_table : self.table,
                      }
        return f, ax, EmpericalSupportPlotResults(**results_dict)

