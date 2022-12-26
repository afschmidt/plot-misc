# imports
from matplotlib.colorbar import colorbar_factory
import matplotlib.pyplot as plt
import pandas as pd
from plot_misc.constants import (
    as_array,
    is_type,
    is_df,
    are_columns_in_df,
    same_len,
    InputValidationError,
    string_to_list,
)
from plot_misc.utils import (
    change_ticks,
    _update_kwargs,
)
from typing import Any, List, Type, Union, Tuple, Dict, Optional

# #############################################################################

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lollipop(values:as_array, labels:as_array,
             line_color:str='tab:orange', dot_color:str='deeppink',
             linewidth:float=1, dot_edge_color:str='black', dot_size:float=4,
             dot_edge_size:float=0.5, figsize:tuple=(6, 6),
             xmargin:Union[float, None]=0, reverse_y:bool=False,
             xlimit:Union[Tuple[float, float], None]=None,
             ax:Union[plt.Axes, None]=None,
             kwargs_lines_dict:Dict[Any, Any]={},
             kwargs_plot_dict:Dict[Any, Any]={},
             ) -> Tuple[plt.Axes, plt.Figure]:
    '''
    Essentially a bar chart, where the bar is replaced by a line with a dot for
    the bar endpoint. Currently the plotting assumes we want to plot a line
    from zero to the`max_col`.
    
    Parameters
    ----------
    max_col : np.ndarray,
        The column with line endpoints
    lab_col : np.ndarray,
        The column with tick labels.
    line_color: str, default `tab:orange`
        The line colour.
    linewidth : float, default 1,
        The line width.
    dot_color : str, default `deeppink`
        The dot colour.
    dot_edge_color : str, default `black`
        The dot edge colour.
    dot_size : float, default 4
        The side of the dot.
    dot_edge_size : float, default 0.5
        The line size of the edge.
    xmargin : float, default 0
        The x margins, set to `NoneType` to keep default.
    xlimit : tuple of float, default `NoneType`
        The x-axis limits.
    ax : plt.Axes, default `NoneType`
        A `matplotlib.axes.Axes` instance to which the figure is plotted. If
        not provided, use current axes or create a new one.  Optional.
    figsize : tuple of two floats, default (10, 10),
        The figure size, when ax==None.
    reverse_y : boolean, default False,
        inverts the y-axis.
    kwargs_*_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            kwargs_lines_dict -- > ax.hlines
            kwargs_plot_dict  -- > ax.plot
    
    Returns
    -------
    tuple: figure, axes
    '''
    # ################### Check input
    
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = None
    # get index index to numeric
    index = range(values.shape[0])
    # ################### plot lines and dots, first updating the kwargs
    new_lines_dict = _update_kwargs(kwargs_lines_dict, color=line_color,
                                    linewidth=linewidth)
    ax.hlines(y=index, xmin=0, xmax=values, **new_lines_dict,
              )
    new_plot_dict = _update_kwargs(kwargs_plot_dict,
                                   marker='o',
                                   linestyle='None',
                                   c=dot_color,
                                   markeredgecolor=dot_edge_color,
                                   markersize=dot_size,
                                   markeredgewidth=dot_edge_size,
                                   )
    ax.plot(values, index, **new_plot_dict,
            )
    # ################### tick labels
    change_ticks(ax=ax, ticks=list(index), labels=list(labels), axis='y')
    # ################### hide spines
    try:
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    except AttributeError:
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
    # ################### margins
    xlim = ax.get_xlim()
    if not xmargin is None:
        ax.margins(x=xmargin)
    if xlimit is None:
        ax.set_xlim(0, xlim[1]*1.05)
    # ################### invert y-axis
    if reverse_y == True:
        ax.invert_yaxis()
    # ################### return the figure and axis
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE add LOESS functionality
# NOTE add strings to constants.py
def calibration(data:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                observed:str, predicted:str,
                lower_observed:Union[None, str]=None,
                upper_observed:Union[None, str]=None,
                ci_colour:Union[str, List[str], None]=['lightcoral'],
                ci_linewidth:Union[str, List[float], None]=[0.5],
                dot_marker:Union[str, List[str]]=['o'],
                dot_colour:Union[str, List[str]]=['lightcoral'],
                line_colour:Union[str, List[str]]=['lightcoral'],
                line_linewidth:Union[str, List[float]]=[0.7],
                line_linestyle:Union[str, List[str]]=['--'],
                figsize:Tuple[float, float]=(6, 6),
                diagonal_colour:str='black',
                diagonal_linewdith:float=0.5,
                diagonal_linestyle:str='-',
                margins:Tuple[float, float]=(0.01, 0.01),
                ax:Union[plt.Axes, None]=None,
                kwargs_ci_dict:Dict[Any, Any]={},
                kwargs_dot_dict:Dict[Any, Any]={},
                kwargs_line_dict:Dict[Any,Any]={},
                kwargs_diagonal_dict:Dict[Any,Any]={},
                ) -> Tuple[plt.Axes, plt.Figure]:
    '''
    Provides a basic template for a calibration plot, comparing the observed
    and predicted risk. Here the observed risk will be based on some grouping
    based on the predicted risk, and the average event rate within each group.
    Hence optional confidence intervals can be included for the observed risk.
    
    Can plot multiple lines (representing distinct prediction models),
    although this can quickly become crowded and one might consider a
    multi panel plot.
    
    Parameters
    ----------
    data : pd.DataFrame or dict of pd.DataFrame
        When multiple DataFrame's are provided, care should be given to ensure
        all have the same column names.
    observed : str
        A column name in `data` representing the observed risk
        (between 0 and 1).
    predicted : str
        A column name in `data` representing the predicted risk
        (between 0 and 1).
    lower_observed : str, default `NoneType`
        An optional column name in `data` representing the lower bound of
        the observed risk.
    upper_observed : str, default `NoneType`
        An optional column name in `data` representing the upper bound of
        the observed risk.
    ci_colour : string or list of strings,
        The colours that the (optional) confidence intervals should have.
    ci_linewdith : string or list of strings,
        The linewdith of the (optional) confidence intervals.
    dot_colour : string or list of string,
        The marker colour.
    dot_marker : string or list of strings,
        The marker for the average agreement between observed and predicted
        risk.
    line_colour : string or list of strings,
        The colour of the line connecting the dots.
    line_linestyle : string or list of strings,
        The linestyle of the line(s) connecting the dots.
    line_linewidth : string or list of floats,
        The linewidth of the line(s) connecting the dots.
    diagonal_colour : str,
        The colour of the diagonal line.
    diagonal_linestyle : str
        The linestyle of the diagonal line.
    diagonal_linewdith : float
        The width of the diagonal line.
    ax : plt.Axes, default `NoneType`
        A `matplotlib.axes.Axes` instance to which the figure is plotted. If
        not provided, use current axes or create a new one.  Optional.
    figsize : tuple of two floats, default (6, 6),
        The figure size, when ax==None.
    kwargs_*_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            kwargs_ci_dict       --> ax.plot
            kwargs_dot_dict   --> ax.scatter
            kwargs_line_dict     --> ax.plot
            kwargs_diagonal_dict --> ax.axline
    '''
    # ################### check input
    is_type(data, (dict, pd.DataFrame))
    is_type(observed, str)
    is_type(predicted, str)
    is_type(ax, (plt.Axes, type(None)))
    is_type(lower_observed, (str, type(None)))
    is_type(upper_observed, (str, type(None)))
    is_type(ci_colour, (str,list, type(None)))
    is_type(ci_linewidth, (str, list, type(None)))
    is_type(dot_marker,(str, list))
    is_type(dot_colour, (str, list))
    is_type(line_colour, (str, list))
    is_type(line_linewidth, (str, list))
    is_type(line_linestyle, (str, list))
    is_type(figsize, tuple)
    is_type(diagonal_linewdith, float)
    is_type(diagonal_colour, str)
    is_type(diagonal_linestyle, str)
    is_type(margins, tuple)
    # combined the columns
    columns = [predicted, observed]
    if not lower_observed is None:
        columns = columns + [lower_observed]
    if not upper_observed is None:
        columns = columns + [upper_observed]
    # creating a dictionary if needed
    if not isinstance(data, dict):
        data = {'dataset1': data}
    # testing column content
    [are_columns_in_df(d, columns) for d in data.values()]
    # compare plt params to dict len
    # NOTE if None simply repeat for the number of datasets
    if not ci_colour is None:
        same_len(data, ci_colour, ['data', 'ci_colour'])
    else:
        ci_colour = [None] * len(data)
    # NOTE if None simply repeat for the number of datasets
    if not ci_linewidth is None:
        same_len(data, ci_linewidth, ['data', 'ci_linewdith'])
    else:
        ci_linewidth = [None] * len(data)
    same_len(data, dot_colour, ['data', 'dot_colour'])
    same_len(data, dot_marker, ['data', 'dot_marker'])
    same_len(data, line_colour, ['data', 'line_colour'])
    same_len(data, line_linewidth, ['data', 'line_linewidth'])
    same_len(data, line_linestyle, ['data', 'line_linestyle'])
    # ################### making lists
    ci_linewidth = string_to_list(ci_linewidth)
    ci_colour = string_to_list(ci_colour)
    dot_marker = string_to_list(dot_marker)
    dot_colour = string_to_list(dot_colour)
    line_colour = string_to_list(line_colour)
    line_linewidth = string_to_list(line_linewidth)
    line_linestyle = string_to_list(line_linestyle)
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = None
    # ################### loop over dict
    for idx, (key, val) in enumerate(data.items()):
        # unpack data
        x_bin = val[predicted]
        y_bin = val[observed]
        # set lb and ub to the same y-values, and update based on avail data
        y_bin_lb = val[observed]
        y_bin_ub = val[observed]
        if not lower_observed is None:
            y_bin_lb = val[lower_observed]
        if not upper_observed is None:
            y_bin_ub = val[upper_observed]
        # set confidence intervals
        y_ci = [y_bin_lb, y_bin_ub]
        x_ci = [x_bin, x_bin]
        # Add the diagonal line, first updating the kwargs
        new_diagonal_dict =\
            _update_kwargs(kwargs_diagonal_dict, lw=diagonal_linewdith,
                           ls=diagonal_linestyle, c=diagonal_colour)
        ax.axline(xy1=(0, 0), slope=1, **new_diagonal_dict,
                  )
        # add line connecting the dots, first updating the kwargs
        new_line_dict =\
            _update_kwargs(kwargs_line_dict, c=line_colour[idx],
                           linewidth=line_linewidth[idx],
                           linestyle=line_linestyle[idx],
                           )
        ax.plot(x_bin, y_bin, **new_line_dict,
                )
        # plot confidence interval, first updating the kwargs
        new_ci_dict =\
            _update_kwargs(kwargs_ci_dict, c=ci_colour[idx],
                           linewidth=ci_linewidth[idx],
                           )
        ax.plot(x_ci, y_ci, **new_ci_dict,
                )
        # plot dots, first updating the kwargs
        new_dot_dict =\
            _update_kwargs(kwargs_dot_dict, c=dot_colour[idx],
                           marker=dot_marker[idx],
                           )
        ax.scatter(x_bin, y_bin, **new_dot_dict,
                   )
        # NOTE can expand this to include an optional loess curve
        # NOTE need to add an entry point for individual level data
    # ################### set the plot params
    # making sure the axis is square
    # axes_min = min(ax.get_xlim()[0], ax.get_ylim()[0])
    # NOTE this is slightly opinionated thinking that the lower limit should
    # always start at zero.
    axes_max = max(ax.get_xlim()[1], ax.get_ylim()[1])
    ax.set_xlim(0, axes_max)
    ax.set_ylim(0, axes_max)
    # hide the right and top spines
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    # margins around the both x and y
    ax.margins(margins[0], margins[1])
    # ################### return the figure and axis
    return f, ax
