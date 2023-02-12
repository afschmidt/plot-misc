'''
Provides a function to draw and annotate volcano plots.

Dots are plotted on a Cartesian-grid with typically the -log10(p-value) on
the y-axis and a measure of magnitude on the x-axis. Different colours can be
used to identify certain key parts of the grahp.

Label overlap is addressed by sourcing `adjustText`.
'''
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from pandas.core.frame import DataFrame
from plot_misc.utils.utils import _update_kwargs
from typing import Any, List, Type, Union, Tuple, Optional, Dict


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_volcano(data:DataFrame, y_column:str, x_column:str,
                 point_label:Union[str,None]=None, legend:bool=False,
                 fsize:Union[Tuple[float, float], None]=None,
                 adjust:bool=False, lim:float=1000,
                 alpha:float=0.00001,
                 col:Tuple[str, str, str]=('orangered','dimgrey','lightcoral'),
                 xlab:str='Point estimate',
                 ylab:str=r'$-log_{10}(pvalue)$',
                 ylim:Union[List[float],None]=None,
                 msize:float=10,
                 lsize:float=5,
                 transparency_ns:float=0.6,
                 index_label:Union[List[str],None]=None,
                 ax:Union[plt.Axes, None]=None,
                 label_kwargs_dict:Dict[Any, Any]={},
                 scatter_sig_kwargs_dict:Dict[Any, Any]={},
                 scatter_nonsig_kwargs_dict:Dict[Any, Any]={},
                 ):
    '''
    Creates a volcano plots, were significant results are labeled.
    
    Arguments
    ---------
    Data : pd.DataFrame
        A pandas dataframe with -log10(pvalues) and
        effect estimates and a column the points can be labels by.
    y_column, x_column, point_label : str
        A column name in data.
    legend : boolean
        Should the legend be returned (default: False).
    fsize : tuple, default `NoneType`.
        Figure size W by H in inches. Set to `NoneType` to skip.
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
    lsize : float
        Size of the text size
    transparency_ns : float
        Transparency value of the non-significant results (default 0.6)
    index_label : list
        An optional list of pandas indices or booleans to subset the printed
        labels.
    ax : plt.axes
        An optional matplotlib axis. If supplied the function works on the axis
        and does not return anything.
    *_kwargs_dict : dict, default empty dict,
        Optional arguments supplied to the various plotting functions:
            label_kwargs_dict          --> adjust_text
            scatter_sig_kwargs_dict    --> ax.bar
            scatter_nonsig_kwargs_dict --> ax.bar
    
    Returns
    -------
    Unpacks a matplotlib figure, axes, unless `ax` is supplied an plt.axis,
    in which case nothing is returned.
    '''
    
    # raise warning
    if (adjust == True and point_label == None):
        warnings.warn('`adjust` is ignored if `point_label` is None',
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
    # kwargs
    new_sig_kwargs = _update_kwargs(
        update_dict=scatter_sig_kwargs_dict,
        edgecolor=(1, 1, 1, 0), zorder=2, c=col[0], s=msize,
    )
    ax.scatter(xs, ys, **new_sig_kwargs)
    ### getting data below threshold
    below = data[data[y_column] < threshold]
    xns = below[x_column]
    yns = below[y_column]
    # kwargs
    new_nonsig_kwargs = _update_kwargs(
        update_dict=scatter_nonsig_kwargs_dict,
        edgecolor=(1, 1, 1, 0), zorder=2, linewidths=0.0, s=msize,
        alpha=transparency_ns, c=col[1],
    )
    ax.scatter(xns, yns,  **new_nonsig_kwargs,)
    ### adding annotations
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    ### do we want to set the ylim
    if not ylim is None:
        plt.ylim( ylim[0], ylim[1] )
    # adjust text only if labels are specified
    if not point_label is None:
        # check if column is present
        if not point_label in data.columns:
            raise IndexError('`point_label` is not present in the data.columns.')
        # get text, do we want to subset
        if not index_label is None:
            text_data = data.loc[index_label]
            above = text_data[text_data[y_column] >= threshold]
            xs = above[x_column]
            ys = above[y_column]
        # getting the actual labels
        texts = []
        for x, y, l in zip(xs, ys, above[point_label]):
            texts.append(ax.text(x, y, l, size=lsize))
        if adjust:
            # NOTE update the kwargs to a dict and add the overwrite function
            new_label_kwargs = _update_kwargs(
                updaete_dict=label_kwargs_dict,
                lim=lim, zorder=3, ax=ax,
                arrowprops=dict(arrowstyle="-", color='k', lw=0.5),
            )
            adjust_text(texts, **new_label_kwargs,)
    # return the figure and axes
    return f, ax
