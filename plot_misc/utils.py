#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from typing import Any, List, Type, Union, Tuple
from plot_misc.constants import is_type

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def change_ticks(ax:plt.axis, ticks:list, axis='x', log:bool=False):
    '''
    Takes an axis and changes the ticks labels and location
    
    Parameters
    ----------
    ax : plot.axes
    ticks : list,
        A list of ticks marks which will be used for the position and labels
    labels : TODO,
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
    is_type(axis, str)
    is_type(log, bool)
    # set labels
    labels = ticks
    # do we need to transform the location
    if log == True:
        tick_location = np.log(ticks)
    else:
        tick_location = ticks
    # work on xaxis
    if axis == 'x':
        try:
            ax.xaxis.set_ticks(tick_location)
            ax.xaxis.set_ticklabels(labels)
        except AttributeError as e:
            raise e
    # work on yaxis
    if axis == 'y':
        try:
            ax.yaxis.set_ticks(tick_location)
            ax.yaxis.set_ticklabels(labels)
        except AttributeError as e:
            raise e
    # done

