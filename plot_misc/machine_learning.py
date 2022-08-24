# imports
import matplotlib.pyplot as plt
from plot_misc.constants import  as_array
from plot_misc.utils import change_ticks
from typing import Any, List, Type, Union, Tuple, Dict

# #############################################################################
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
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = None
    # get index index to numeric
    index = range(values.shape[0])
    # ################### plot lines and dots
    ax.hlines(y=index, xmin=0, xmax=values, color=line_color,
              linewidth=linewidth, **kwargs_lines_dict,
              )
    ax.plot(values, index, "o", c=dot_color, markeredgecolor=dot_edge_color,
            markersize=dot_size, markeredgewidth=dot_edge_size,
            **kwargs_plot_dict,
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

