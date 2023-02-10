
'''
A module to draw and annotate heatmaps using matplotlib.

Code addapted from:
    <https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html>
'''

# modules
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from plot_misc.constants import is_type, as_array
from typing import Any, List, Type, Union, Tuple, Optional, Dict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def heatmap(data:Union[pd.DataFrame, as_array],
            row_labels:Union[List[str], as_array],
            col_labels:Union[List[str], as_array],
            grid_col:str='white', grid_linestyle:str='-',
            grid_linewidth:float=3,
            grid_kw:Dict[Any, Any]={},
            cbar_bool:bool=False,
            cbar_label:str="",
            cbar_kw:Dict[Any, Any]={},
            ax:Union[plt.Axes, None]=None,
            **kwargs:Optional[Any]) -> Tuple[matplotlib.image.AxesImage,
                                             matplotlib.colorbar.Colorbar]:
    """
    Create a heatmap from a numpy array and two lists of labels.
    
    Parameters
    ----------
    data : pd.DataFrame or np.array
        A 2D numpy array of shape (M, N).
    row_labels : list or np.array
        A list or array of length M with the labels for the rows.
    col_labels : list or np.array
        A list or array of length N with the labels for the rows.
    grid_col : str, default 'white'
        The colour of the grid lines
    grid_linestyle : str, default '-'
        The linestyle of the grid lines
    grid_linewidth : float, default 3
        The grid lines width.
    grid_kw : dict
        A dictionary with arguments to `matplotlib.Axes.grid`. Optional.
    cbar_bool : boolean, default False
        Set to True to add a colour bar.
    cbar_label : str
        The label for the colorbar.  Optional.
    cbar_kw : dict
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    ax : plt.Axes, default NoneType
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    
    Returns
    -------
    mpl.image.AxesImage, mpl.colorbar.Colorbar
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
    # ### Plot the heatmap
    im = ax.imshow(matrix, **kwargs)
    # Create colorbar
    if cbar_bool == True:
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
    ax.grid(which="minor", color=grid_col, linestyle=grid_linestyle,
            linewidth=grid_linewidth, **grid_kw)
    ax.tick_params(which="minor", bottom=False, left=False)
    # return stuff
    return im, cbar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def annotate_heatmap(im:plt.Axes.imshow,
                     data:Union[pd.DataFrame, as_array, None]=None,
                     valfmt:Union[str, matplotlib.ticker.Formatter, None]=None,
                     textcolors:Union[Tuple[str], List[str]]=("black", "white"),
                     threshold:Union[float,None]=None, **text_kw:Optional[Any],
                     ) -> List[plt.Text]:
    """
    A function to annotate a heatmap.
    
    Parameters
    ----------
    im : `plt.Axes.imshow`
        The AxesImage to be labeled.
    data : pd.DataFrame or np.array, default Nonetype
        A 2D numpy array of shape (M, N). Optional.
    valfmt : str or `matplotlib.ticker.Formatter`, default NoneType
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors: list of tuple of string, default ('black', 'white')
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold float, default NoneType
        The absolute value in data units according to which the colors from
        textcolors are applied.  If None (the default) uses the middle of the
        colormap as separation.  Optional.
    **text_kw
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    
    Returns
    -------
    List of plt.text.Text:
        The plt.text.Text objects contain `tuple`-like objects with the
        Cartesian-coordinates and the text for each coordinate.
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
    # kw will act as kwargs for im.axes.text
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(text_kw)
    # Get the formatter in case a string is supplied
    if not valfmt is None:
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)
    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            # only run if threshold exists
            if not threshold is None:
                kw.update(color=textcolors[int(im.norm(abs(values[i, j])) > threshold)])
            # format text or not
            if not valfmt is None:
                text = im.axes.text(j, i, valfmt(matrix[i, j], None), **kw)
            else:
                text = im.axes.text(j, i, matrix[i,j], **kw)
            texts.append(text)
    # returning stuff
    return texts
