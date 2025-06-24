import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numbers import Real
from plot_misc.errors import (
    is_df,
    are_columns_in_df,
)
from typing import Any
from plot_misc.utils.utils import (
    adjust_labels,
    _update_kwargs,
)
from itertools import cycle


    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE add an adjustment factor for xy in annotate
# This adjustment can other be a constant or a list of tuples with floats
# arrow_start_scaling = 1.05  # slightly outside the unit circle
# xy = (cx + arrow_start_scaling * x, cy + arrow_start_scaling * y)
# probably also make xypos_scaling to accept a list of tuples with the same
# number or elements as there are rows in data.
def piechart(data: pd.DataFrame, col_values: str, col_labels:str | None = None,
             ax: plt.Axes | None = None, figsize: tuple[float, float] = (8, 4),
             fontsize: Real = 8,
             colours: list[str] = ['black', 'grey', 'lightgrey'],
             xypos_scaling: tuple[float, float] = (1.15, 1.15),
             min_dist_lables: float = 0.13,
             arrowprops: dict[str, Any] | None = None,
             bboxprops: dict[str, Any] | None = None,
             pie_kwargs:dict[Any,Any] | None = None,
             annotate_kwargs:dict[Any,Any] | None = None,
             ):
    """
    Creates a pie chart on the given Axes object,
        or a new figure if None.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        The DataFrame containing data.
    col_values : `str`
        A column name in `data` representing the size of each piechart wedge.
    col_labells : `str` or `None`, default `None`
        A column name in `data` representing the wedge labels. Set to `None`
        to generate a piechart without labels.
    ax : `plt.Axes` or `None`, default `NoneType`
        The axes object on which to plot the pie chart.  If None, a new figure
        and axes object are created.
    figsize : `tuple` [`float`, `float`], default `(8, 4)`
        Figure size in inches.
    fontsize : `float`, default 8.0
        Label font size
    colors : `list` [`str`, `str`], default [`black`, 'grey`, 'lightgrey']
        List of colours to use for pie chart segments.
    xypos_scaling : `tuple` [`float`, `float`], default (1.15, 1.15)
        The scaling factor positioning the label text in radians. The first
        values moves the text left or right, the second value up or down.
    arrowprops : `dict` [`str`, 'any`] or `None`, default `NoneType'
        keyword arguments passed to FancyArrowPatch.
    bboxprops : `dict` [`str`, `any`] or `None`, default `NoneType`
        keyword arguments passed to bbox.
    pie_kwargs : `dict`, default `NoneType`
        keyword arguments for ax.pie
    annotate_kwargs :`` dict, default `NoneType`
        keyword arguments for annotations.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The matplotlib figure containing the pie chart.
    ax : matplotlib.axes.Axes
        The axes object of the plot.
    """
    # check input
    is_df(data)
    col_list = [col_labels, col_values]
    if col_labels is None:
        col_list = [col_values]
    are_columns_in_df(data, col_list)
    # set defaults
    if bboxprops is None:
        bboxprops = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.0,
                          alpha=0.0)
    if arrowprops is None:
        arrowprops=dict(arrowstyle="-", lw=0.4)
    # map None to dict
    pie_kwargs = pie_kwargs or {}
    annotate_kwargs = annotate_kwargs or {}
    # update kwargs
    pie_kwargs = _update_kwargs(update_dict = pie_kwargs,
                                autopct = '', startangle = 135,
                                colors = colours, wedgeprops = {
                                    'alpha' : 0.5, 'edgecolor': 'k',
                                    'linewidth' : 0.5},
                                )
    # Create new ax if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    # Are there zero counts
    if (data[col_values] <= 0).sum() > 0:
        raise ValueError("Input data includes zero values.")
    # draw piechart
    wedges, _, _ = ax.pie(data[col_values], **pie_kwargs)
    # equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    # Define annotation properties
    if col_labels is not None:
        # NOTE consider making this into a separate function
        # get wedges from ax.patches
        annot_kwargs = _update_kwargs(update_dict = annotate_kwargs,
                                      arrowprops=arrowprops,
                                      bbox=bboxprops, zorder=0, va="center")
        # Create a list to store annotations for adjusting labels
        labels = data[col_labels].to_list()
        annotations = []
        for i, p in enumerate(wedges):
            # wedge center
            cx, cy = p.center
            # gets the angle of each wedge
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            # whether the alignment is right or left of the center
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            # the angle of the arrow/line
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            annot_kwargs["arrowprops"].update(
                {"connectionstyle": connectionstyle})
            # Annotate labels and store them in the list
            annot_kwargs = _update_kwargs(update_dict = annot_kwargs,
                                          fontsize=fontsize,)
            ann = ax.annotate(labels[i], xy=(cx + x, cy + y),
                              xytext=(xypos_scaling[0] * np.sign(x),
                                      xypos_scaling[1] * y),
                              horizontalalignment=horizontalalignment,
                              **annot_kwargs,)
            # add annotations
            annotations.append(ann)
        # Adjust labels
        adjust_labels(annotations, ax, min_distance=min_dist_lables)
    # return figure and axes
    return fig, ax

