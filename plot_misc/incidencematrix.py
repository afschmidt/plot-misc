'''
A function to draw incidence matrices, creating an n by m grid of lines
populating the intersections with shapes.
'''

# importing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Any, List, Type, Union, Tuple, Dict
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    # _assign_empty_default,
)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def draw_incidencematrix(data:pd.DataFrame, fsize:Tuple[float, float]=(6,6),
                         dot_colour:List[Tuple[str, float]]=[('grey',0), ('black',1)],
                         line_colour:List[str]=['lightgrey', 'lightgrey'],
                         dot_size:List[float]=[4, 8],
                         dot_transparency:List[float]=[0.9, 1.0],
                         lw:List[float]=[0.3, 0.3],
                         tick_lab_size:List[float]=[4.5, 4.5],
                         tick_len:List[float]=[2, 2],
                         tick_wid:List[float]=[0.3, 0.3],
                         margins:Union[List[float], None]=None,
                         ax:Union[plt.Axes, None]=None,
                         break_limits:List[float] = [-np.inf, np.inf],
                         kwargs_scatter_dict:Union[Dict[Any, Any],None]=None,
                         kwargs_vline_dict:Union[Dict[Any, Any],None]=None,
                         kwargs_hline_dict:Union[Dict[Any, Any],None]=None,
                         ) -> Tuple[plt.Figure, plt.Axes]:
    '''
    Creates a `categorical heatmap`, essentially visualising an incidence
    matrix.
    
    Arguments
    ---------
    Data : pd.DataFrame
        A incidence matrix with index and column labels used as x-axis and
        y-axis tick labels. The matrix values will be plotted basd on the
        `dot_colour` breaks and colours, with a specified size and transparency.
    fsize : tuple
        A two element tuple, with the width and height in cm.
    dot_colour : list of tuples, default `[('grey',0), ('black',1)]`
        A list of arbitrary length, specifying the colour and upper bound
        the colour is applied to. Each tuple should have
        (<colour>, <upper bound>).
        
        The default: [('grey',0), ('black',1)], colours dots grey for value in
        (\\infinity, 0], and colours dots black for values in (0, 1].
    dot_size : list
        A list of length equal to `dot_colour`. specifying the size of the dots.
    dot_transparency : list
        A list of length equal to `dot_colour`, specifying the alpha of the dots.
    line_colour : list
        A two element list specifying the horizontal and vertical line
        colours.
    lw : list
        A two element list specifying the horizontal and vertical line
        size.
    tick_lab_size : list
        A two element list specifying the label size of the x-, y-axis ticks.
    tick_len : list
        A two element list specifying the length of the x-, y-axis ticks.
    tick_wid : list
        A two element list specifying the width of the x-, y-axis ticks.
    margins : list
        A two element list specifying the margins of the x-, y-axis.
    ax : plt.axes
        An optional matplotlib axis -- will otherwise make one internally
    break_limits : list
        Currently used to specify the lower bound the first colour is applied
        to. Most likely you will never need to touch this.
    kwargs_*_dict : dict, default None
        Optional arguments supplied to the various plotting functions:
            kwargs_scatter_dict        --> ax.scatter
            kwargs_vline_dict          --> ax.vline
            kwargs_hline_dict          --> ax.hline
        
    Returns
    -------
    fig: plt.Figure
    ax: plt.Axes
    '''
    
    # check inputs
    is_type(dot_size, list)
    is_type(dot_colour, list)
    is_type(dot_transparency, list)
    # map None to dict
    kwargs_scatter_dict = kwargs_scatter_dict or {}
    kwargs_vline_dict = kwargs_vline_dict or {}
    kwargs_hline_dict = kwargs_hline_dict or {}
    # kwargs_scatter_dict, kwargs_vline_dict, kwargs_hline_dict =\
    #     _assign_empty_default(
    #         [kwargs_scatter_dict, kwargs_vline_dict, kwargs_hline_dict],
    #         dict)
    # if one value is supplied, multiply the number of dot_colour elements
    ndots = len(dot_colour)
    if len(dot_size) == 1:
        dot_size = dot_size * ndots
    if len(dot_transparency) ==1:
        dot_transparency = dot_transparency * ndots
    # further tests
    if not len(dot_colour) == len(dot_size):
        raise IndexError('The number of `dot_size` entries should equal '
                         '`dot_colour`.'
                         )
    if not len(dot_colour) == len(dot_transparency):
        raise IndexError('The number of `dot_transparency` entries should '
                         'equal `dot_colour`.'
                         )
    if not isinstance(data, pd.DataFrame):
        raise ValueError('`data` should be a pd.DataFrame.')
    
    # do we need to make an axis
    if ax is None:
        cmtoinch = 0.393700787
        f, ax = plt.subplots(figsize=(fsize[0] * cmtoinch,
                                      fsize[1] * cmtoinch))
    else:
        f = ax.figure
    
    # the x and y coordinates
    M, N = data.shape
    x, y = np.meshgrid(np.arange(M), np.arange(N))
    
    ################
    # plot dots
    for it, value in enumerate(dot_colour):
        # unpack value
        col, cut = value
        # make breaks
        if it==0:
            sel = (data > break_limits[0]) & (data <= cut)
        # elif it==n:
        #     sel = (data >= cut) & (data < break_limits[1])
        #     print(sel)
        else:
            sel = (data > cut_old) & (data <= cut)
        
        # subset data
        xs = x[sel.to_numpy().T]
        ys = y[sel.to_numpy().T]
        
        # error out if there is no data.
        if xs.size == 0:
            raise ValueError('No data, for cut: `{}`.'.format(str(cut)))
        
        # plot
        new_scatter_kwargs = _update_kwargs(update_dict=kwargs_scatter_dict,
                                            edgecolor=(1, 1, 1, 0),
                                            linewidths=0.0,
                                            s=dot_size[it],
                                            alpha=dot_transparency[it],
                                            c=col, zorder=3,
                                            )
        ax.scatter(xs.flat, ys.flat, **new_scatter_kwargs)
        
        # store previous cut
        cut_old = cut
        # end loop
    ################
    
    # adding grid lines
    for xv in range(x.shape[1]):
        new_vline_kwargs = _update_kwargs(update_dict=kwargs_vline_dict,
                                          c=line_colour[0], linestyle='-',
                                          linewidth=lw[0], zorder=1,
                                          )
        ax.axvline(x=xv, **new_vline_kwargs)
    for xy in range(x.shape[0]):
        new_hline_kwargs = _update_kwargs(update_dict=kwargs_vline_dict,
                                          c=line_colour[0], linestyle='-',
                                          linewidth=lw[0], zorder=1,
                                          )
        ax.axhline(y=xy, **new_hline_kwargs)
    # ticks
    ax.set(xticks=np.arange(x.shape[1]), yticks=np.arange(x.shape[0]),
           xticklabels=data.index, yticklabels=data.columns)
    ax.tick_params(axis="x", labelsize=tick_lab_size[0], length=tick_len[0],
                   width=tick_wid[0], rotation=90)
    ax.tick_params(axis="y", labelsize=tick_lab_size[1], length=tick_len[1],
                   width=tick_wid[1])
    
    # trim margin
    if not margins is None:
        ax.margins(x=margins[0], y=margins[1])
    
    # return the figure and axes
    return f, ax
