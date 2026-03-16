"""
Heatmap drawing and annotation tools built on top of matplotlib and seaborn.

This module provides flexible functions to create and annotate heatmaps using
either `matplotlib` or `seaborn`, with extensive support for customisation and
publication-quality output.

Functions
---------
heatmap(data, row_labels, col_labels, ...)
    Draws a standard heatmap using matplotlib's `imshow`, with options for
    gridlines, tick formatting, and embedded colourbars.

annotate_heatmap(im, data=None, valfmt=None, ...)
    Adds text annotations to an existing heatmap image (AxesImage object),
    with configurable formatting and colour thresholding.

Notes
-----
The base structure of the `heatmap` and `annotate_heatmap` functions is derived
from the example published in the official matplotlib gallery [1]_.

References
----------
.. [1] Matplotlib contributors. "Creating annotated heatmaps."
Matplotlib Gallery.
https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
"""

# modules
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
)
from plot_misc.constants import Real
from typing import Any

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def heatmap(data:pd.DataFrame | np.ndarray, row_labels:list[str] | np.ndarray,
            col_labels:list[str] | np.ndarray, grid_col:str='white',
            grid_linestyle:str='-', grid_linewidth:float=3,
            cbar_bool:bool=False, cbar_label:str="",
            ax:plt.Axes | None = None,
            grid_kw:dict[Any,Any] | None = None,
            cbar_kw:dict[Any,Any] | None = None,
            **kwargs:Any,
            ) -> tuple[matplotlib.image.AxesImage,
                       matplotlib.colorbar.Colorbar]:
    """
    Plot a heatmap with row and column labels using matplotlib.
    
    This function draws a heatmap using `imshow`, with options to configure
    grid lines, colourbars, and axis labels. It accepts both NumPy arrays
    and pandas DataFrames as input.
    
    Parameters
    ----------
    data : `pd.DataFrame` or `np.array`
        A 2D array of shape (M, N) containing the values to plot.
    row_labels : `list` [`str`] or `np.ndarray`
        A list or array of length M with the labels for the rows.
    col_labels : `list` [`str`] or `np.ndarray`
        A list or array of length N with the labels for the rows.
    grid_col : `str`, default 'white'
        The colour of the grid lines
    grid_linestyle : `str`, default '-'
        The linestyle of the grid lines
    grid_linewidth : `float`, default 3
        The width of the grid lines.
    cbar_bool : `bool`, default `False`
        If `True`, add a colourbar to the figure.
    cbar_label : `str`, default " "
        The label for the colorbar.
    ax : `plt.Axes` or `None`, default None
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted. If
        not provided, use current axes or create a new one.
    grid_kw : `dict` [`str`,`any`] or `None`, default None
        A dictionary with arguments to `matplotlib.Axes.grid`.
    cbar_kw : `dict` [`str`, `any`] or `None`, default `None`
        A dictionary with arguments to `matplotlib.Figure.colorbar`.
    **kwargs : `any`
        All other arguments are forwarded to `imshow`.
    
    Returns
    -------
    im : `matplotlib.image.AxesImage`
        The heatmap image object.
    cbar : `matplotlib.colorbar.Colorbar` or `None`
        The colourbar object if `cbar_bool` is `True`, otherwise `None`.
    
    Notes
    -----
    The returned objects can be used to annotate the cells using for example
    `annotate_heatmap`.
    
    This function is adapted from the matplotlib gallery example [HM1]_.
    
    References
    ----------
    .. [HM1] Matplotlib contributors. "Creating annotated heatmaps."
            Matplotlib Gallery.
            https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
    """
    
    # create a axes if needed
    if not ax:
        ax = plt.gca()
    # check input
    if isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # copy
    row_lab = row_labels
    col_lab = col_labels
    # check additional input
    is_type(row_lab, (list, np.array))
    is_type(col_lab, (list, np.array))
    is_type(cbar_label, str)
    # map None to dict
    grid_kw = grid_kw or {}
    cbar_kw = cbar_kw or {}
    # ### Plot the heatmap
    im = ax.imshow(matrix, **kwargs)
    # Create colorbar
    if cbar_bool:
        # NOTE if the kwargs for colobar is extended use `_update_kwargs
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbar_label, rotation=-90, va="bottom")
    else:
        cbar = None
    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_xticklabels(col_lab)
    ax.set_yticks(np.arange(matrix.shape[0]))
    ax.set_yticklabels(row_lab)
    # Let the horizontal axes labeling appear on top.
    # ax.tick_params(top=True, bottom=False,
    #                labeltop=True, labelbottom=False)
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right",
             rotation_mode="anchor")
    # Turn spines off and create white grid.
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # set tick marks
    ax.set_xticks(np.arange(matrix.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(matrix.shape[0]+1)-.5, minor=True)
    # grid
    new_grid_kwargs = _update_kwargs(
        update_dict=grid_kw, which="minor", color=grid_col,
                     linestyle=grid_linestyle, linewidth=grid_linewidth,
                     )
    ax.grid(**new_grid_kwargs)
    ax.tick_params(which="minor", bottom=False, left=False)
    # return stuff
    return im, cbar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def annotate_heatmap(
    im:plt.Axes.imshow,
    data:pd.DataFrame | np.ndarray | None = None,
    valfmt:str | matplotlib.ticker.Formatter | None = None,
    textcolors:tuple[str,str] | list[str,str]=("black","white"),
    threshold: float | None = None,
    **kwargs:Any,
) -> list[plt.Text]:
    """
    Annotate each cell in a heatmap image with its value.
    
    This function adds text annotations to an existing `AxesImage` object,
    such as those created by the `heatmap` function. The text colour may
    be adjusted dynamically based on a threshold value and the image’s colour
    map.
    
    Parameters
    ----------
    im : `plt.Axes.imshow`
        The AxesImage to be labeled.
    data : `pd.DataFrame`, `np.array`, or `None`, default `Nonetype`
        A 2D numpy array of shape (M, N). If `None`, the function uses the
        array embedded in `im`.
    valfmt : `str`, `matplotlib.ticker.Formatter` or `None`, default `None`
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}" - (note the `x` is needs
        to be included to represent the numerical), or be a
        `matplotlib.ticker.Formatter`.
    textcolors : `list` or `tuple` [`str`, `str`], default `('black', 'white')`
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.
    threshold : `float` or `None`, default `None`
        The absolute value in data units according to which the colors from
        textcolors are applied.  If None (the default) uses the middle of the
        colormap as separation.
    **kwargs : `any`
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    
    Returns
    -------
    texts : `list` of `matplotlib.text.Text`
        A list of text annotation objects added to the heatmap.
    """
    
    # mapping data to matrix
    values = im.get_array()
    if data is None:
        matrix = im.get_array()
    elif isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        # this will value is matrix is a string
        try:
            threshold = im.norm(values.max())/2.
        except np.core._exceptions.UFuncTypeError:
            threshold = None
    # Set default alignment to center, but allow it to be
    # overwritten by text_kw.
    kw = _update_kwargs(update_dict=kwargs,
                        horizontalalignment="center",
                        verticalalignment="center",
                        )
    # Get the formatter in case a string is supplied
    if valfmt is not None:
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)
    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            # only run if threshold exists
            if threshold is not None:
                kw.update(color=textcolors[int(im.norm(abs(values[i, j])) > threshold)])
            # format text or not
            if valfmt is not None:
                text = im.axes.text(j, i, valfmt(matrix[i, j], None), **kw)
            else:
                text = im.axes.text(j, i, matrix[i,j], **kw)
            texts.append(text)
    # returning stuff
    return texts

