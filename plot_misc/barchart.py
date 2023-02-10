"""
A collection of various bar chart functions.
"""
import matplotlib.pyplot as plt
import pandas as pd
from plot_misc.constants import Error_MSG
from plot_misc.utils.utils import _update_kwargs
from plot_misc.constants import (
    is_type,
    is_df,
)
from typing import Any, List, Type, Union, Tuple, Optional, Dict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stack_bar(df:pd.DataFrame, label:str, columns:List[str], ax:plt.Axes,
              colours:List[str]=['tab:blue', 'tab:pink'],
              transparancy:float=0.7, wd:float=1, edgecolor:str='black',
              **kwargs:Optional[Any]) -> plt.Axes:
    '''
    Function for a bar chart, remove top and left spines.
    
    Arguments
    ---------
    df : pd.DataFrame,
    label : str,
        Column lables in `df`.
    columns : list of strings,
        List of columns names in `df`.
    ax : plt.ax
    colours : list of strings,
        List with the number of colours equal to len(columns).
    transparancy : float, 0.7
        Degree of transparancy, between 0 and 1 (solid).
    wd : float
        Bar width.
    edgecolor : str of colours, default `black`.
    kwargs
        Arbitrary keyword arguments for `ax.bar`.
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    is_df(df)
    is_type(label, str)
    is_type(columns, list)
    is_type(ax, plt.Axes)
    is_type(colours, list)
    is_type(transparancy, float)
    is_type(wd, float)
    is_type(edgecolor, str)
    # should not be any missings
    # NOTE consider making this into a function
    if any(df.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('df'))
    # make sure we have sufficient colours
    if len(columns) != len(colours):
        raise AttributeError('The number of columns ({0}) does not match the '
                             'number of colours ({1}).'.format(
                                 len(columns), len(colours)))
    # get labels
    labels = df[label]
    # get columns
    fields=columns
    # actual plotting
    left = len(df) * [0]
    for idx, name in enumerate(fields):
        # updating kwargs
        new_kwargs = _update_kwargs(update_dict=kwargs, edgecolor=edgecolor,
                                    width=wd, color=colours[idx],
                                    alpha=transparancy,
                                    )
        # renning ax.bar
        ax.bar(labels, height=df[name], bottom = left, **new_kwargs,
               )
        left = left + df[name]
    # removing spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # returns
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stack_barh(df:pd.DataFrame, label:str, columns:List[str], ax:plt.Axes,
               colours:List[str]=['tab:blue', 'tab:pink'],
               transparancy:float=0.7, wd:float=1, edgecolor:str='black',
               **kwargs:Optional[Any]) -> plt.Axes:
    '''
    Function for a horizontal bar chart, removes top and left spines.
    
    Arguments
    ---------
    df : pd.DataFrame
    label : str
        Column labels in `df`.
    columns : list of strings
        List of columns names in `df`.
    ax : plt.ax
    colours : list
        List with the number of colours equal to len(columns).
    transparancy : float, 0.7
        Degree of transparancy, between 0 and 1 (solid).
    wd : float
        Bar width.
    edgecolor : str of colours, default `black`
    kwargs
        Arbitrary keyword arguments for `ax.barh`.
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    is_df(df)
    is_type(label, str)
    is_type(columns, list)
    is_type(ax, plt.Axes)
    is_type(colours, list)
    is_type(transparancy, float)
    is_type(wd, float)
    is_type(edgecolor, str)
    # should not be any missings
    if any(df.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('df'))
    # get labels
    labels = df[label]
    # get columns
    fields=columns
    # actual plotting
    left = len(df) * [0]
    for idx, name in enumerate(fields):
        # updating kwargs
        new_kwargs = _update_kwargs(update_dict=kwargs, edgecolor=edgecolor,
                                    height=wd, color=colours[idx],
                                    alpha=transparancy,
                                    )
        ax.barh(labels, width=df[name], left=left, **new_kwargs,
                )
        left = left + df[name]
    # removing spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # return ax
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def subtotal_bar(df:pd.DataFrame, label:str, subtotal_col:str, ax:plt.Axes,
              total_col:Union[str,None]=None,
              colours:List[str]=['grey', 'tab:blue'],
              transparancy:List[float]=[0.7, 0.9], wd:List[float]=[1, 0.6],
              edgecolor:List[str]=['black', 'black'],
              total_kwargs_dict:Dict[Any,Any]={},
              subtotal_kwargs_dict:Dict[Any,Any]={},
              ) -> plt.Axes:
    '''
    A bar chart with a total column and overplotted subtotal columns.
    The first entry of each argument refers to the subtotal chart, the second
    to the total chart.
    
    Arguments
    ---------
    df : pd.DataFrame,
    label : str,
        The column name with the axes labels you want to use.
    subtotal_col : str,
        The column name with the (y-axis) values (floats/int) that need to be
        plotted.
    total_col : str, default `NoneType`
        The column name with the (y-axis) values (floats/int) that need to be
        plotted. Skip total_col by setting it to None (default).
    colours : List of strings,
        A list of colours of the bars.
    transparancy : List of floats,
        For the alpha of the bars.
    wd : List of floats,
        A float to specify bar widths.
    edgecolor : List of strings
        The bar edgecolor.
    ax : plt.Axes
    *_kwargs_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            total_kwargs_dict    --> ax.bar
            subtotal_kwargs_dict --> ax.bar
    
    Returns
    -------
    plt.Axes
    '''
    # ### check input
    if any(df.isna().any()):
        raise ValueError(Error_MSG.MISSING_DF.format('df'))
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
def bar(df:pd.DataFrame, label:str, column:str, ax:plt.Axes,
        colours:List[str]=['tab:blue', 'tab:pink'], transparancy:float=0.7,
        wd:float=1, edgecolor:str='black', **kwargs:Optional[Any],
        ) -> plt.Axes:
    '''
    Plot a barchart with sequentially coloured bars.
    
    Arguments
    ---------
    df : pd.DF
    label : str
        The column name with the axes labels you want to use.
    column : str
        The column name with the (y-axis) values (floats/int) that need to be
        plotted.
    colours : list
        A list of colours, can be a single or multiple values (will get
        recycled).
    colours : str,
        A list of colours of the bars.
    transparancy : str,
        For the alpha of the bars.
    wd : str,
        A float to specify bar widths.
    edgecolor : str
        The bar edgecolor.
    ax : plt.Axes
    kwargs
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
                                width=wd, color=colours,
                                alpha=transparancy,
                                )
    # actual plotting
    ax.bar(labels,height=df[column], **new_kwargs,
           )
    # removing spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # return
    return ax

