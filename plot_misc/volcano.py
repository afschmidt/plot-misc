import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from pandas.core.frame import DataFrame
from typing import Any, List, Type, Union, Tuple, Optional, Dict


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_volcano(data:DataFrame, y_column:str, x_column:str,
                 point_labels:Union[str,None]=None, legend:bool=False,
                 fsize:Tuple[float, float]=(7,10),
                 adjust:bool=False, lim:float=1000,
                 alpha:float=0.00001,
                 col:Tuple[str, str, str]=('orangered','dimgrey','lightcoral'),
                 xlab:str='Point estimate',
                 ylab:str=r'$-log_{10}(pvalue)$',
                 ylim:Union[List[float],None]=None,
                 msize:float=10,
                 tsize:float=5,
                 transparency_ns:float=0.6,
                 text_index:Union[List[str],None]=None,
                 ax:Union[plt.Axes, None]=None,
                 **kwargs:Optional[Any],
                 ):
    '''
    Creates a volcano plots, where significant results are labeled.
    
    Arguments
    ---------
    Data : pd.DataFrame
        A pandas dataframe with -log10(pvalues) and
        effect estimates and a column the points can be labels by.
    y_column, x_column, point_labels : str
        A column name in data.
    legend : boolean
        Should the legend be returned (default: False).
    fsize : tuple
        Figure size W by H in inches.
    adjust : boolean
        Should overplotting of annotations be decreased.  Note this starts a
        (computational demanding) iterative process.
    lim : float
        The tolerance for overplotting, higher numbers indicate lower tolerance
        and increases the distance between labels; also increasing the run time.
    alpha : float
        The significance cut-off used (will be logged, internally).
    col : tuple
        A three element tuple listing the colours for:
        significant dots, non-significant dots, and the vertical line.
    xlab, ylab : str
    ylim : list
        The y-limit, by default is simply uses the data limits.
    msize : float
        Size of the dots
    tsize : float
        Size of the text size
    transparency_ns : float
        Transparency value of the non-significant results (default 0.6)
    text_index : list
        An optional list of pandas indices or booleans to subset the printed
        labels.
    ax : plt.axes
        An optional matplotlib axis. If supplied the function works on the axis
        and does not return anything.
    **kwargs : dict
        Optional arguments for `adjust_text`.
    
    Returns
    -------
    Unpacks a matplotlib figure, axes, unless `ax` is supplied an plt.axis,
    in which case nothing is returned.
    '''
    
    # raise warning
    if (adjust == True and point_labels == None):
        warnings.warn('`adjust` is ignored if `point_labels` is None',
                      SyntaxWarning)
    
    ### getting figure
    # should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=fsize)
    else:
        f = None
    ### significance level
    threshold = -1 * np.log10(alpha)
    ### setting a reference line (zorder=1; behind)
    ax.axvline(x=0, c=col[2], linestyle='--', zorder=1, linewidth=1)
    ### getting data above threshold
    above = data[data[y_column] >= threshold]
    xs = above[x_column]
    ys = above[y_column]
    ax.scatter(xs, ys, c=col[0], edgecolor=(1, 1, 1, 0), zorder=2,
               label=r'$-\log_{10}$(p-value) > ' + str(round(threshold, 2)),
               s=msize)
    ### getting data below threshold
    below = data[data[y_column] < threshold]
    xns = below[x_column]
    yns = below[y_column]
    ax.scatter(xns, yns, c=col[1], edgecolor=(1, 1, 1, 0),
               linewidths=0.0,
               label='Not Sig', zorder=2, s=msize, alpha=transparency_ns
               )
    ### adding annotations
    if legend:
        ax.legend()
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    ### do we want to set the ylim
    if not ylim is None:
        plt.ylim( ylim[0], ylim[1] )
    # adjust text only if labels are specified
    if not point_labels is None:
        # check if column is present
        if not point_labels in data.columns:
            raise IndexError('`point_label` is not present in the data.columns')
        # get text, do we want to subset
        if not text_index is None:
            text_data = data[data[point_labels].isin(text_index)]
            above = text_data[text_data[y_column] >= threshold]
            xs = above[x_column]
            ys = above[y_column]
        # getting the actual labels
        texts = []
        for x, y, l in zip(xs, ys, above[point_labels]):
            texts.append(ax.text(x, y, l, size=tsize))
        if adjust:
            # NOTE update the kwargs to a dict and add the overwrite function
            adjust_text(texts, lim=lim, zorder=3, ax=ax,
                        arrowprops=dict(arrowstyle="-", color='k', lw=0.5),
                        **kwargs)
    # return the figure and axes
    return f, ax
