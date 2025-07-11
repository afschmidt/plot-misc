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
from plot_misc.constants import Real

# # NOTE updates the pytests when ready.
# from plot_misc.example_data import examples
# data_w = examples.load_barchart_data()
# data = data_w.T.copy()
# label = 'labels'
# total_col = 'total'
# data[label] = data_w.T.index
# data[total_col] = data.drop(columns=[label]).sum(axis=1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bar(data:pd.DataFrame, label:str, column:str,
        error_max:str | None = None, error_min:str | None = None,
        colours:list[str]=['tab:blue', 'tab:pink'], transparancy:float=0.7,
        wd:Real=1.0, edgecolor:str='black',
        horizontal:bool = False, figsize:tuple[Real,Real] = (2,2),
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
    transparancy : `float`, default 0.7
        For the alpha of the bars.
    wd : `float` or `int`, default 1.0
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
# NOTE Update the docstring to explain how kwargs are passed to
# barchart.bar first and how we can pass kwargs to matplotlib.bar as well.
def stack_bar(data:pd.DataFrame, label:str, columns:list[str],
              colours:list[str]=['tab:blue', 'tab:pink'],
              transparancy:float=0.7, wd:Real=1.0, edgecolor:str='black',
              horizontal:bool = False, figsize:tuple[Real,Real] = (2,2),
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
    wd : `float` or `int`, default 1.0
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
            new_kwargs = _update_kwargs(update_dict=kwargs,
                                        edgecolor=edgecolor,
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
def subtotal_bar(data:pd.DataFrame, label:str, total_col:str,
                 subtotal_col: str | None = None,
                 colours:tuple[str,str]=('grey','tab:blue'),
                 transparancy:tuple[float,float]=(0.7,0.9),
                 wd:tuple[float,float]=(1,0.6),
                 edgecolor:tuple[str,str]=('black', 'black'),
                 zorder:tuple[int,int] = (2,3),
                 horizontal:bool=False,
                 figsize:tuple[Real,Real] = (2,2),
                 ax:plt.Axes | None = None,
                 total_kwargs_dict:dict[str,Any] | None = None,
                 subtotal_kwargs_dict:dict[str, Any] | None = None,
                 ) -> tuple[plt.Figure,plt.Axes]:
    '''
    A bar chart with a total column and overplotted subtotal columns.
    The first entry of each argument refers to the subtotal chart, the second
    to the total chart.
    
    Arguments
    ---------
    data : `pd.DataFrame`
        The input data.
    label : `str`
        The column name with the axes labels you want to use.
    total_col : `str`
        The column name with the (y-axis) values (floats/int) that need to be
        plotted.
    subtotal_col : `str` or `None`, default `NoneType`
        The column name with the (y-axis) values (floats/int) that need to be
        plotted. Skip total_col by setting it to None (default).
    colours : `tuple` [`str`,`str`], default ("grey", "tab:blue")
        A list of colours of the bars.
    transparancy : `tuple` [`float`,`float`], default (0.7, 0.9)
        For the alpha of the bars.
    wd : `tuple` [`real`,`real`], default (1.0, 0.6)
        The bar widths.
    edgecolor : `tuple` [`str`,`str`], default ("black", "black")
        The bar edgecolor.
    horizontal : `bool`, default `False`
        Whether plot a horizontal barchart.
    zorder : `tuple` [`int`,`int`], default (2,3)
        The order the total and subtotal bars are plotted.
    figsize : `tuple` [`float`, `float`], default (2, 2),
        The figure size in inches, when ax is set to None.
    ax : `plt.Axes` or `None`, default `None`
        The pyplot.axes object.
    *_kwargs_dict : dict, default None,
        Optional arguments supplied to the various plotting functions:
            total_kwargs_dict    --> ax.bar
            subtotal_kwargs_dict --> ax.bar
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    is_df(data)
    is_type(label, str)
    is_type(ax, (type(None), plt.Axes))
    is_type(total_col, str)
    is_type(subtotal_col, (str, type(None)))
    is_type(zorder, tuple)
    is_type(colours, tuple)
    is_type(transparancy, tuple)
    is_type(wd, tuple)
    is_type(edgecolor, tuple)
    is_type(horizontal, bool)
    is_type(total_kwargs_dict, (dict,type(None)))
    is_type(subtotal_kwargs_dict, (dict,type(None)))
    if any(data.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('data'))
    # ### should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # mapping None to empty dicts
    total_kwargs_dict = total_kwargs_dict or {}
    subtotal_kwargs_dict = subtotal_kwargs_dict or {}
    # get labels
    labels = data[label]
    # counts
    total = data[total_col]
    # #### plot total
    # checking whether something is passed to kwargs_bar
    kwargs_bar = total_kwargs_dict.pop("kwargs_bar", {})
    new_total_kwargs_bar = _update_kwargs(
        update_dict = kwargs_bar,
        zorder=zorder[0],
    )
    new_total_kwargs = _update_kwargs(
        update_dict=total_kwargs_dict,
        label=label,
        column=total_col,
        colours=[colours[0]],
        transparancy=transparancy[0],
        wd=wd[0],
        edgecolor=edgecolor[0],
        horizontal=horizontal,
        kwargs_bar = new_total_kwargs_bar,
    )
    bar(
        pd.DataFrame({total_col:total, label:labels}),
        ax=ax,
         **new_total_kwargs,
           )
    # plot subtotal
    if not subtotal_col is None:
        subtotal = data[subtotal_col]
        # updating kwargs
        kwargs_bar2 = subtotal_kwargs_dict.pop("kwargs_bar", {})
        new_subtotal_kwargs_bar = _update_kwargs(
            update_dict = kwargs_bar2,
            zorder=zorder[1],
        )
        new_subtotal_kwargs = _update_kwargs(
            update_dict=subtotal_kwargs_dict,
            label=label,
            column=subtotal_col,
            colours=[colours[1]],
            transparancy=transparancy[1],
            wd=wd[1],
            edgecolor=edgecolor[1],
            horizontal=horizontal,
            kwargs_bar = new_subtotal_kwargs_bar,
        )
        bar(
            pd.DataFrame({subtotal_col:subtotal, label:labels}),
            ax=ax,
             **new_subtotal_kwargs,
               )
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # return
    return f, ax

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

