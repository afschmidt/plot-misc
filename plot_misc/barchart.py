"""
A collection of various bar chart functions, based on matplotlib.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    is_df,
    Error_MSG,
)
from typing import Any, Optional

# NOTE updates the pytests when ready.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bar(data:pd.DataFrame, label:str, column:str,
        error_max:str | None = None, error_min:str | None = None,
        colours:list[str]=['tab:blue', 'tab:pink'], transparancy:float=0.7,
        wd:float=1.0, edgecolor:str='black',
        horizontal:bool = False, figsize:tuple = (2,2),
        ax:plt.Axes | None = None,
        kwargs_bar:dict[str, Any] | None = None,
        kwargs_error:dict[str, Any] | None = None,
        ) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plot a barchart with sequentially coloured bars.
    
    Arguments
    ---------
    data : `pd.DataFrame`
        A table containing columns for the bar heights and bar labels.
    label : `str`
        The column name with the axes labels you want to use.
    column : `str`
        The column name containing the bar height values.
    error_max : `str`, default `NoneType`
        column name for the upper value of the error segement.
    error_min : ``str` default `NoneType`
        column name for the lower value of the error segement.
    colours : `list` [`str`]
        A list of colours, can be a single or multiple values. The colours will
        get recycled if there are fewer than the number of bars.
    transparancy : `str`, default 0.7
        For the alpha of the bars.
    wd : `str`, default 1.0
        A float to specify bar widths.
    edgecolor : `str`, default `black`
        The bar edgecolor.
    horizontal : `bool`, default `False`
        Whether plot a horizontal barchart.
    ax : `plt.ax`, default `NoneType`
        The pyplot.axes object.
    figsize : `tuple` [`float`, `float`], default (2, 2),
        The figure size in inches, when ax is set to None.
    kwargs_bar : `any`
        Arbitrary keyword arguments for `ax.bar` or `ax.barh`.
    kwargs_error : `any`
        Arbitrary keyword arguments for `ax.hlines` or `ax.vlines`.
    
    Returns
    -------
    fig : plt.Figure
    ax : plt.Axes
    '''
    is_df(data)
    is_type(label, str)
    is_type(column, str)
    is_type(colours, list)
    is_type(transparancy, float)
    is_type(wd, (float, int))
    is_type(edgecolor, str)
    is_type(horizontal, bool)
    is_type(ax, (type(None), plt.Axes))
    is_type(error_min, (type(None), str))
    is_type(error_max, (type(None), str))
    is_type(kwargs_bar, (type(None), dict))
    is_type(kwargs_error, (type(None), dict))
    # ### should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # mapping None to empty dicts
    kwargs_bar = kwargs_bar or {}
    kwargs_error = kwargs_error or {}
    # ### check input
    if any(data.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('data'))
    # ### get labels
    labels = data[label]
    # ### plotting
    if horizontal == False:
        # plotting vertical bar chart
        new_kwargs = _update_kwargs(update_dict=kwargs_bar,
                                    edgecolor=edgecolor,
                                    width=wd, color=colours,
                                    alpha=transparancy,
                                    zorder=2,
                                    )
        bars = ax.bar(labels, height=data[column], **new_kwargs,
                      )
    else:
        # plotting horizontal bar chart
        new_kwargs = _update_kwargs(update_dict=kwargs_bar,
                                    edgecolor=edgecolor,
                                    height=wd, color=colours,
                                    alpha=transparancy,
                                    zorder=2,
                                    )
        bars = ax.barh(labels, width=data[column], **new_kwargs,
                       )
    # do we need to plot error bars
    if error_min is not None or error_max is not None:
        # finding the mid points of the bars and
        # initialising the bounds, allowing for one-sided limits.
        if horizontal == False:
            min_l = [b.get_y() + b.get_height() for b in bars]
            max_l = min_l.copy()
        else:
            min_l = [b.get_x() + b.get_width() for b in bars]
            max_l = min_l.copy()
        # setting columns values
        try:
            min_l = data[error_min].to_list()
        except KeyError:
            pass
        try:
            max_l = data[error_max].to_list()
        except KeyError:
            pass
        # the actual plotting
        new_kwargs_error = _update_kwargs(update_dict=kwargs_error,
                                    color='black',
                                    zorder=1,
                                    )
        if horizontal == False:
            mids = [b.get_x() + b.get_width() / 2 for b in bars]
            ax.vlines(mids, min_l, max_l, **new_kwargs_error,)
        else:
            mids = [b.get_y() + b.get_height() / 2 for b in bars]
            ax.hlines(mids, min_l, max_l, **new_kwargs_error,)
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # return
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stack_bar(data:pd.DataFrame, label:str, columns:list[str],
              colours:list[str]=['tab:blue', 'tab:pink'],
              transparancy:float=0.7, wd:float=1.0, edgecolor:str='black',
              horizontal:bool = False, figsize:tuple = (2,2),
              ax:plt.Axes | None = None, **kwargs:Optional[Any],
              ) -> tuple[plt.Figure, plt.Axes]:
    '''
    Function for a bar chart, removes top and left spines.
    
    Arguments
    ---------
    data : `pd.DataFrame`
        A table containing columns for the bar heights and bar labels.
    label : `str`
        The column name of the axis labels.
    columns : `list` [`str`]
        The column names of the bar heights.
        List of column names in `data`.
    colours : `list` [`str`]
        List with the number of colours equal to len(columns).
    transparancy : `float`, default 0.7
        Degree of transparancy, between 0 and 1 (solid).
    wd : `float`, default 1.0
        Bar width.
    edgecolor : `str`, default `black`
        The colour of the bar edge line.
    horizontal : `bool`, default `False`
        Whether plot a horizontal barchart.
    ax : `plt.ax`, default `NoneType`
        The pyplot.axes object.
    figsize : `tuple` [`float`, `float`], default (2, 2),
        The figure size in inches, when ax is set to None.
    kwargs : `any`
        Arbitrary keyword arguments for `ax.bar` or `ax.barh`.
    
    Returns
    -------
    fig : plt.Figure
    ax : plt.Axes
    '''
    # ### check input
    is_df(data)
    is_type(label, str)
    is_type(columns, list)
    is_type(colours, list)
    is_type(transparancy, float)
    is_type(wd, (float, int))
    is_type(edgecolor, str)
    is_type(horizontal, bool)
    is_type(ax, (type(None), plt.Axes))
    # ### should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # ### should not be any missings
    # NOTE consider making this into a function
    if any(data.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('data'))
    # make sure we have sufficient colours
    if len(columns) != len(colours):
        raise AttributeError('The number of columns ({0}) does not match the '
                             'number of colours ({1}).'.format(
                                 len(columns), len(colours)))
    # get labels
    labels = data[label]
    # get columns
    fields=columns
    # actual plotting
    left = len(data) * [0]
    for idx, name in enumerate(fields):
        if horizontal == False:
            # plotting vertical bar chart
            new_kwargs = _update_kwargs(update_dict=kwargs, edgecolor=edgecolor,
                                        width=wd, color=colours[idx],
                                        alpha=transparancy,
                                        )
            ax.bar(labels, height=data[name], bottom=left, **new_kwargs,
                   )
        else:
            # horizontal bar chart
            new_kwargs = _update_kwargs(update_dict=kwargs, edgecolor=edgecolor,
                                        height=wd, color=colours[idx],
                                        alpha=transparancy,
                                        )
            ax.barh(labels, width=data[name], left=left, **new_kwargs,
                    )
        # update the locations
        left = left + data[name]
    # removing spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # returns
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def subtotal_bar(df:pd.DataFrame, label:str, subtotal_col:str, ax:plt.Axes,
                 total_col: str | None = None,
                 colours:list[str]=['grey', 'tab:blue'],
                 transparancy:list[float]=[0.7, 0.9], wd:list[float]=[1, 0.6],
                 edgecolor:list[str]=['black', 'black'],
                 total_kwargs_dict:dict[str,Any] | None = None,
                 subtotal_kwargs_dict:dict[str, Any] | None = None,
                 ) -> plt.Axes:
    '''
    A bar chart with a total column and overplotted subtotal columns.
    The first entry of each argument refers to the subtotal chart, the second
    to the total chart.
    
    Arguments
    ---------
    df : pd.DataFrame
    label : str
        The column name with the axes labels you want to use.
    subtotal_col : str
        The column name with the (y-axis) values (floats/int) that need to be
        plotted.
    total_col : str, default `NoneType`
        The column name with the (y-axis) values (floats/int) that need to be
        plotted. Skip total_col by setting it to None (default).
    colours : List of strings
        A list of colours of the bars.
    transparancy : List of floats
        For the alpha of the bars.
    wd : List of floats
        A float to specify bar widths.
    edgecolor : List of strings
        The bar edgecolor.
    ax : plt.Axes
        The pyplot.axes objct.
    *_kwargs_dict : dict, default None,
        Optional arguments supplied to the various plotting functions:
            total_kwargs_dict    --> ax.bar
            subtotal_kwargs_dict --> ax.bar
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    is_df(df)
    is_type(ax, plt.Axes, 'ax')
    is_type(label, str, 'label')
    is_type(subtotal_col, str, 'subtotal_col')
    is_type(total_col, (str, type(None)), 'total_col')
    is_type(colours, list, 'colours')
    is_type(transparancy, list, 'transparancy')
    is_type(wd, list, 'wd')
    is_type(edgecolor, list, 'edgecolor')
    is_type(total_kwargs_dict, (dict,type(None)), 'total_kwargs_dict')
    is_type(subtotal_kwargs_dict, (dict,type(None)), 'subtotal_kwargs_dict')
    if any(df.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('df'))
    # mapping None to empty dicts
    total_kwargs_dict = total_kwargs_dict or {}
    subtotal_kwargs_dict = subtotal_kwargs_dict or {}
    # get labels
    labels = df[label]
    # counts
    subtotal = df[subtotal_col]
    # plot subtotal
    new_subtotal_kwargs = _update_kwargs(
        update_dict=subtotal_kwargs_dict, edgecolor=edgecolor[0], width=wd[0],
        color=colours[0], alpha=transparancy[0],
    )
    ax.bar(labels, height=subtotal, **new_subtotal_kwargs,
           )
    # plot total
    if not total_col is None:
        total = df[total_col]
        # updating kwargs
        new_total_kwargs = _update_kwargs(
            update_dict=total_kwargs_dict,
            edgecolor=edgecolor[1], width=wd[1], color=colours[1],
            alpha=transparancy[1],
        )
        # running ax.bar
        ax.bar(labels,height=total, **new_total_kwargs,
               )
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # return
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def group_bar(df:pd.DataFrame, label:str, columns:list[str],
        ax:plt.Axes, errors:list[str]=None, csiz:float=2,
        colours:list[str]=['tab:blue', 'tab:pink'], transparancy:float=0.7,
        wd:float=1, edgecolor:str='black', **kwargs:Optional[Any],
        ) -> plt.Axes:
    '''
    Plot a barchart with sequentially coloured bars.
    
    Arguments
    ---------
    df : pd.DF
    label : str
        The column name with the axes labels you want to use.
    columns : list
        The column names with the (y-axis) values (floats/int) that need to be
        plotted.
    errors : list
        The column names with the (y-axis) values (floats/int) of the
        error-bars.
    colours : list
        A list of colours, can be a single or multiple values (will get
        recycled).
    colours : str
        A list of colours of the bars.
    transparancy : str, default 0.7
        For the alpha of the bars.
    wd : str, default 1.0
        A float to specify bar widths.
    edgecolor : str, default `black`
        The bar edgecolor.
    ax : plt.Axes
        The pyplot.axes objct.
    kwargs : any
        Arbitrary keyword arguments for `ax.bar`.
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    if any(df.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('df'))
    # get labels
    labels = df[label]
    # updating kwargs
    new_kwargs = _update_kwargs(update_dict=kwargs, edgecolor=edgecolor,
                                width=wd, alpha=transparancy, capsize=csiz,
                                )
    # set x-axis
    x_ax = np.arange(df.shape[0])
    xtic = np.arange(df.shape[0])
    for i in range(len(columns)):
        # identify column and color
        column = columns[i]
        color = colours[i]
        if errors is not None:
            error = errors[i]
            # actual plotting
            ax.bar(x_ax,height=df[column],color=color,yerr=df[error],
                    **new_kwargs,
                   )
        else:
            # actual plotting
            ax.bar(x_ax,height=df[column],color=color,**new_kwargs,
                   )
        # update middle of bars
        if i > 0:
            xtic = [x + (wd / 2) for x in xtic]
        # update x-axis
        x_ax = [x + wd for x in x_ax]
    # define x-axis ticks in the middle
    ax.set_xticks(xtic)
    # add x-axis labels
    ax.set_xticklabels(labels)
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # return
    return ax

