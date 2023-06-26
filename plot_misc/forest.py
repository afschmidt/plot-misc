'''
A module to draw forest plots and side tables.

Aside from the plotting functions the moduel contains fuctions to
appropriatly orrientate input DataFrames.
'''

# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from typing import Any, List, Type, Union, Tuple, Dict, Sequence, Optional
from plot_misc.utils.utils import _update_kwargs
from plot_misc.constants import ForestNames as FNames
from plot_misc.constants import (
    is_type,
    are_columns_in_df,
)

# #############################################################################
# functions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO write test
def order_row(data:pd.DataFrame, order_outer:Dict[str, List[str]],
              order_inner:Union[Dict[str, List[str]], None]=None
              ) -> pd.core.frame.DataFrame:
    '''
    Order a data frame by and outer and inner order, say by study and within
    study by outcome.
    
    Parameters
    ----------
    data : pd.DataFrame,
    oder_outer : dict,
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
def _assign_distance(df:pd.DataFrame, group:str, within_pad:float=2,
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
    df : pd.DataFrame,
        The dataframe that contains the `group` of interest.
    group : str,
        A string that maps to a column in df.
    strata : str, default None
        An optional df column which nests the `group` values.
    within_pad : float,
        The distance between point estimates nested within a group.
    between_pad : float,
        The distance between groups of point estimates. This is the y-axis
        distance that will be skipped between the last y-axis coordinate in the
        previous group and the starting y-axis coordinate of the current group.
    start : float, default 0,
        The starting position of the sequence.
    new_col : str, default `y_axis`
        The name of the column that will be added to `df`.
    sort_dict : dict, default None
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
    is_type(sort_dict, (type(None), dict))
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
                s_col:str='o', c_col:str='black', g_col:Union[str, None]=None,
                a_col:Union[float, str]=1, shape_size:float=40, ci_lwd:float=2,
                ci_colour:str='indianred', connect_shape:bool = False,
                connect_shape_colour:str='black', connect_shape_lwd:float=1,
                span:bool = True, span_colour:List[str] = ['white', 'lightgrey'],
                ax:Union[plt.Axes, None]=None, figsize:tuple=(10, 10),
                reverse_y:bool=True,
                verbose:bool=False,
                kwargs_scatter_dict:Dict[Any, Any]={},
                kwargs_plot_ci_dict:Dict[Any, Any]={},
                kwargs_connect_segments_dict:Dict[Any, Any]={},
                kwargs_span_dict:Dict[Any, Any]={}
                ) -> Tuple[plt.Figure, plt.Axes]:
    """
    A forest plot function, that allows for grouping of estimates by `group`.
    Related if there are estimates with the same `y_col` value these get
    depicted as a horizontal sequence linked by a line segement.
    
    Arguments
    ---------
    df : pd.DataFrame,
    x_col : str,
        The column name of the x-axis values (typically point estimates).
    lb_col : str, default None,
        The column name of the lower bound of an confidence interval.
    ub_col : str, default None,
        The column name of the upper bound of an confidence interval.
    y_col : str, default 'y_axis',
        The column name of the y-axis values used to differentiate
        estimates/studies.
    s_col : str, default 'o',
        The column name of the shape indicators. If string is not found in `df`
        the string value will be added to an `s_col` column.
    c_col : str, default 'black',
        The column name of the shape colour indicators. If string is not found
        in `df` the string value will be added to an `c_col` column.
    a_col : float or str, default 1,
        The column name of the alpha value for each point. If the string is not
        found in `df`, the float will be added to an `a_col` column.
    g_col : str, default None,
        The column name of the group indicator; often the outcome or study
        indicators. If None, a column with a unique value for each row will be
        added - so there are no groups. This column will also be used to
        provide y-axis ticklabels.
    shape_size : float, default 40,
        The shape size.
    ci_lwd : float, default 1,
        The line width of the confidence intervals.
    ci_colour : float, default 'indianred'
        The line colour of the confidence intervals
    connect_shape : boolean, default False,
        If the point estimates should be connected with a line. Only relevant
        when estimates have the same y-axis.
    connect_shape_colour : str, default `grey`,
        The line colour.
    connect_shape_lwd : float, default 1,
        The line width.
    span : boolean, default True,
        Whether an colour-interchanging horizontal background segment should
        be added
    span_colour : list of two string, default ['white', 'lightgrey'],
        The colours of the span.
    ax : plt.axes, default None
        An optional matplotlib axis. If supplied the function works on the axis.
    figsize : tuple of two floats, default (10, 10),
        The figure size, when ax==None.
    reverse_y : boolean, default True,
        inverts the y-axis.
    kwargs_*_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            kwargs_scatter_dict          --> ax.scatter
            kwargs_plot_ci_dict          --> ax.plot
            kwargs_connect_segments_dict --> ax.plot
            kwargs_span_dict             --> ax.axhspan
    
    Returns
    -------
    Unpacks a matplotlib figure, axes.
    f : plt.Figure.
    x : plt.Axes.
    
    Examples
    --------
    Additional characteristics can be mapped through the various kwargs_*_dict,
    calling the `row` object which represents a row of the `df` through
    `df.iterrows()`:
    
    >>> plot_forest(df,
    >>>             ...,
    >>>             kwargs_scatter_dict={'linewidths': row[lw_col_name]},
    >>>            )
    >>>
    
    """
    # ################### do check and set defaults
    is_type(x_col, str)
    is_type(lb_col, (type(None), str))
    is_type(ub_col, (type(None), str))
    is_type(y_col, str)
    is_type(s_col, str)
    is_type(c_col, str)
    is_type(g_col, str)
    is_type(a_col, (int, float, str))
    is_type(shape_size, (int, float))
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
    if not isinstance(df, pd.DataFrame):
        raise TypeError('`df` should be a pd.DataFrame.')
    if not df[x_col].dtype.kind in 'iufc':
        raise TypeError('`x_col` should be numeric')
    if not df[ub_col].dtype.kind in 'iufc':
        raise TypeError('`ub_col` should be numeric')
    if not df[lb_col].dtype.kind in 'iufc':
        raise TypeError('`lb_col` should be numeric')
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
        new_scatter_kwargs = _update_kwargs(update_dict=kwargs_scatter_dict,
                                            s=shape_size,
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
        new_plot_ci_kwargs = _update_kwargs(update_dict=kwargs_plot_ci_dict,
                                            c=ci_colour, linewidth=ci_lwd,
                                            alpha=row[a_col_name],
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
    # add the starting and endpoints
    y_mid.insert(0, y_locations.iloc[0][FNames.min])
    y_mid[-1] = ax.get_ylim()[1] # replace with y-axis limit
    # ################### Add horizontal segments
    if span ==True:
        # add segments
        for t in range(len(y_mid)-1):
            ymin = y_mid[t]
            # stop if t is too large
            try:
                ymax = y_mid[t+1]
            except IndexError:
                ymax = y_mid[t]
                pass
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
            ax.axhspan(ymin, ymax, **new_span_kwargs,
                       )
    # ################### adjust y margins
    new_margins = [ax.get_ylim()[0], ax.get_ylim()[1]]
    new_margins[1] = y_mid[-1]
    ax.set_ylim(new_margins)
    # ################### add y-axis labels
    ax.set_yticks(y_locations[FNames.mean])
    ax.set_yticklabels(y_locations.index)
    # ################### invert y-axis
    if reverse_y == True:
        ax.invert_yaxis()
    # ################### return the figure and axis
    return f, ax

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
    kwargs_text_dict:Dict[Any, Any]={},
    kwargs_header_dict:Dict[Any, Any]={},
    kwargs_yticklabel_dict:Dict[Any, Any]={},
) -> plt.Axes:
    """
    Plots a side-table using `ax.text` and supplied `plt.Axes`.
    
    ----------
    dataframe (pandas.core.frame.DataFrame)
            Pandas DataFrame containg `string_col` that should be plotted.
            margin of error, etc.
    y_col : str, default 'y_axis',
        The column name of the y-axis values used to identify rows.
    string_col : str,
            The the column name that should be plotted. Should contain a
            `string` value.
    annoteheaders : str, default `NoneType`
        string to annotate the table column.
    pad : float, default 1
        Multiplication factor for the x-coordinate location:
        `mean(ax.get_xlim())`.
    negative_padding : float, default 1.0
        determines the y-coordinate of the table header as:
        `ax.get_ylim()[1] - ngative_padding`
    size_text : float, default 10
        The font size for the table text.
    size_header : float, default 10
        The font size for the table header.
    yticklabel : list of strings,
        A list of string containing the y-axis labels. Should match the length
        of `ytickloc`.
    ytickloc : list of floats,
        A list of floats defining the y-axis locations for the ticks.
    [l|r]_yticklab_pad: str,
        An optional string to use as a prefix or suffic of the y-axis labels.
    ax : plt.axes,
            Axes to operate on.
    kwargs_*_dict : dict, default empty dict,
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
    is_type(annoteheader, str)
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
    # ################### return
    return ax
