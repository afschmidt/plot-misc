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

masked_heatmap(data, indicator, row_labels, col_labels, ...)
    Draws a two-layer heatmap: a single-colour background and, on top of it,
    the heatmap restricted to the cells flagged by a binary indicator table.

annotate_heatmap(im, data=None, valfmt=None, ...)
    Adds text annotations to an existing heatmap image (AxesImage object),
    with configurable formatting and colour thresholding.

Notes
-----
The base structure of the `heatmap` and `annotate_heatmap` functions is derived
from the example published in the official matplotlib gallery [1]_.

References
----------
.. [1] Matplotlib contributors. "Creating annotated heatmaps." Matplotlib
   Gallery. https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
"""

# modules
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    is_df,
    InputValidationError,
)
from plot_misc.constants import Real
from typing import Any

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def heatmap(data:pd.DataFrame | np.ndarray, row_labels:list[str] | np.ndarray,
            col_labels:list[str] | np.ndarray, grid_col:str='white',
            grid_linestyle:str='-', grid_linewidth:float=3,
            cbar_bool:bool=False, cbar_label:str="",
            ax:plt.Axes | None = None,
            figsize:tuple[float,float] | None = None,
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
    figsize : `tuple` [`float`, `float`] or `None`, default `None`
        Figure size in inches (width, height). Ignored if `ax` is provided.
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
    # check in put
    is_type(data, (pd.DataFrame, np.ndarray))
    is_type(row_labels, (list, np.ndarray))
    is_type(col_labels, (list, np.ndarray))
    is_type(grid_col, str)
    is_type(grid_linestyle, str)
    is_type(grid_linewidth, Real)
    is_type(cbar_bool, bool)
    is_type(cbar_label, str)
    # create a axes if needed
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # check input
    if isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # copy
    row_lab = row_labels
    col_lab = col_labels
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
                     clip_on=False,)
    ax.grid(**new_grid_kwargs)
    ax.tick_params(which="minor", bottom=False, left=False)
    # return stuff
    return im, cbar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def masked_heatmap(data:pd.DataFrame | np.ndarray,
                   indicator:pd.DataFrame | np.ndarray,
                   row_labels:list[str] | np.ndarray,
                   col_labels:list[str] | np.ndarray,
                   background_col:str='white', background_gridcol:str='white',
                   background_linestyle:str='-', background_linewidth:float=0.5,
                   background_zorder:Real = 1,
                   outline_col:str='black', outline_linestyle:str='-',
                   outline_linewidth:float=1.5, outline_zorder:Real = 2,
                   frame: bool=False,
                   cbar_bool:bool=False, cbar_label:str="",
                   ax:plt.Axes | None = None,
                   figsize:tuple[float,float] | None = None,
                   grid_kw:dict[Any,Any] | None = None,
                   cbar_kw:dict[Any,Any] | None = None,
                   background_kw:dict[Any,Any] | None = None,
                   outline_kw:dict[Any,Any] | None = None,
                   **kwargs: Any,
                   ) -> tuple[matplotlib.image.AxesImage,
                              matplotlib.colorbar.Colorbar]:
    """
    Plot a two-layer heatmap masked by a binary indicator table.
    
    The function draws two layers. First a single-colour background covering
    every cell (carrying an optional grid lattice). Second, the heatmap of
    `data`, restricted to the cells where `indicator` equals 1.
    
    Parameters
    ----------
    data : `pd.DataFrame` or `np.ndarray`
        A 2D array of shape (M, N) containing the values to plot.
    indicator : `pd.DataFrame` or `np.ndarray`
        A binary (0/1, booleans accepted) array of the same shape as `data`.
        Only cells equal to 1 are drawn and outlined.
    row_labels : `list` [`str`] or `np.ndarray`
        A list or array of length M with the labels for the rows.
    col_labels : `list` [`str`] or `np.ndarray`
        A list or array of length N with the labels for the columns.
    background_col : `str`, default 'white'
        The fill colour of the background layer.
    background_gridcol : `str`, default 'white'
        The colour of the background grid lattice lines.
    background_linestyle : `str`, default '-'
        The linestyle of the background grid lattice.
    background_linewidth : `float`, default 0.5
        The width of the background grid lattice. Set to 0 to suppress it.
    background_zorder : `int`, `float` default `1`
        The draw order of the background grid lattice.
    outline_col : `str`, default 'black'
        The edge colour of the per-cell outlines drawn on `indicator == 1`
        cells.
    outline_linestyle : `str`, default '-'
        The linestyle of the per-cell outlines.
    outline_linewidth : `float`, default 1.5
        The width of the per-cell outlines. Set to 0 to suppress them.
    outline_zorder : `int`, `float`, default `2`
        The draw order of the per-cell outlines.
    frame : `bool`, default `False`
        Whether to plot the spines.
    cbar_bool : `bool`, default `False`
        If `True`, add a colourbar (built from the masked heatmap layer).
    cbar_label : `str`, default ""
        The label for the colourbar.
    ax : `plt.Axes` or `None`, default `None`
        A `matplotlib.axes.Axes` instance to draw on. If `None`, a new figure
        and axes are created.
    figsize : `tuple` [`float`, `float`] or `None`, default `None`
        Figure size in inches (width, height). Ignored if `ax` is provided.
    grid_kw : `dict` [`str`, `any`] or `None`, default `None`
        Additional arguments forwarded to `matplotlib.Axes.grid` for the
        background lattice.
    outline_kw : `dict` [`str`, `any`] or `None`, default `None`
        Additional arguments forwarded to each `matplotlib.patches.Rectangle`
        outline. Outlines default to `clip_on=False` so the borders of cells on
        the matrix boundary are not clipped by the axes edge; pass
        `{'clip_on': True}` to restore clipping.
    cbar_kw : `dict` [`str`, `any`] or `None`, default `None`
        A dictionary with arguments to `matplotlib.Figure.colorbar`.
    background_kw : `dict` [`str`, `any`] or `None`, default `None`,
        A dictionary with arguments to `heatmap.heatmap`.
    **kwargs : `any`,
        All other arguments passed to `masking ax.imshow`.
    
    Returns
    -------
    im : `matplotlib.image.AxesImage`
        The masked (foreground) heatmap image object.
    cbar : `matplotlib.colorbar.Colorbar` or `None`
        The colourbar object if `cbar_bool` is `True`, otherwise `None`.
    
    Notes
    -----
    The masking is achieved by a separate imshow call setting the cells to
    transparent, revealing the background.
    
    The returned `im` mirrors the contract of `heatmap` and can therefore be
    annotated using `annotate_heatmap`.
    """
    # create an axes if needed
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # check input types
    is_type(data, (pd.DataFrame, np.ndarray))
    is_type(indicator, (pd.DataFrame, np.ndarray))
    _ = [is_type(k, (dict, type(None))) for k in\
         (grid_kw, cbar_kw, outline_kw, background_kw)]
    # the indicator must match the data shape exactly (full 2D shape, not just
    # the row count)
    if np.shape(data) != np.shape(indicator):
        raise InputValidationError(
            f"`indicator` shape {np.shape(indicator)} does not match `data` "
            f"shape {np.shape(data)}."
        )
    # coerce the data and indicator to numpy arrays
    if isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    if isinstance(indicator, pd.DataFrame):
        flag = indicator.copy().to_numpy()
    else:
        flag = indicator
    # flag should only contain 0 and 1
    unique_flags = set(np.unique(flag).tolist())
    if not unique_flags.issubset({0, 1}):
        raise InputValidationError(
            f"`indicator` must only contain binary (0/1) values, got "
            f"{sorted(unique_flags)}."
        )
    # setup the kwargs None to dict
    background_kw = background_kw or {}
    # masking_kw = masking_kw or {}
    grid_kw = grid_kw or {}
    cbar_kw = cbar_kw or {}
    outline_kw = outline_kw or {}
    outline_kw = _update_kwargs(update_dict=outline_kw,
                                zorder=outline_zorder)
    # the background grid lattice carries the background draw order
    grid_kw = _update_kwargs(update_dict=grid_kw, zorder=background_zorder)
    # ### Layer 1: a single-colour background covering every cell. Reusing
    # `heatmap` keeps a single source of truth for the tick, label, spine and
    # grid (lattice) cosmetics.
    background = np.zeros_like(matrix, dtype=float)
    layer1_kwargs = _update_kwargs(
         update_dict=background_kw,
         data=background, row_labels=row_labels, col_labels=col_labels,
         grid_col=background_gridcol, grid_linestyle=background_linestyle,
         grid_linewidth=background_linewidth, cbar_bool=False, ax=ax,
         grid_kw=grid_kw, cmap=ListedColormap([background_col]),
    )
    heatmap(**layer1_kwargs, )
    # ### Layer 2: the heatmap, masked so only `indicator == 1` cells are drawn.
    masked = np.ma.masked_where(flag == 0, matrix)
    # creating an alpha matrix.
    # user_alpha = masking_kw.pop('alpha', 1.0)
    user_alpha = kwargs.pop('alpha', 1.0)
    alpha = (flag == 1).astype(float) * np.asarray(user_alpha, dtype=float)
    layer2_kwargs = _update_kwargs(
        update_dict=kwargs, alpha=alpha,
    )
    im = ax.imshow(masked, **layer2_kwargs)
    # Create colorbar from the foreground (masked) layer
    if cbar_bool:
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbar_label, rotation=-90, va="bottom")
    else:
        cbar = None
    # ### Outline each `indicator == 1` cell. Zero cells get no patch, so they
    # carry no outline; a zero `outline_linewidth` hides the borders.
    rect_kw = _update_kwargs(update_dict=outline_kw, facecolor='none',
                             edgecolor=outline_col,
                             linestyle=outline_linestyle,
                             linewidth=outline_linewidth,
                             clip_on=False,
                             )
    rows, cols = np.where(flag == 1)
    # NOTE the 0.5 and 1.0 are imshow fixed convention and should be hardcoded
    for i, j in zip(rows, cols):
        ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, **rect_kw))
    # Show the spines
    if frame:
        for spine in ax.spines.values():
            spine.set_visible(True)
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
    # masked cells (e.g. from `masked_heatmap`) are not drawn and must not be
    # annotated; `getmaskarray` yields a full boolean mask for masked arrays and
    # an all-False mask for plain arrays, leaving the unmasked path unchanged
    mask = np.ma.getmaskarray(values)
    if data is None:
        matrix = im.get_array()
    elif isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # Compare raw data values against the raw threshold
    # This bypases any kind of value normalisation - which we should skip
    # because the string are not normalised only the values
    if threshold is None:
        try:
            threshold = values.max() / 2.
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
            # skip masked cells, which carry no drawn value to annotate
            if mask[i, j]:
                continue
            # only run if threshold exists
            if threshold is not None:
                kw.update(color=textcolors[int(abs(values[i, j]) >= threshold)])
            # format text or not
            if valfmt is not None:
                # NOTE text takes x, y - whereas values takes rows (y), col (x)
                text = im.axes.text(j, i, valfmt(matrix[i, j], None), **kw)
            else:
                text = im.axes.text(j, i, matrix[i,j], **kw)
            texts.append(text)
    # returning stuff
    return texts

