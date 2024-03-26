import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, List, Type, Union, Tuple, Dict, ClassVar, Optional
from plot_misc.utils.utils import (
    fix_labels
)
from itertools import cycle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pychart(data: pd.DataFrame, columns: List[str],  
            title: Union[None, str] = None, ax: plt.Axes = None, 
            figsize: Tuple[float, float] = (8, 4),
            fontsize: float = 8, colors: Union[None, List[str]] = None, 
            pie_kwargs: Dict[Any, Any] = {}, 
            annotate_kwargs: Dict[Any, Any] = {}, 
            title_kwargs: Dict[Any, Any] = {}):
    """
    Creates a pie chart on the given Axes object, 
        or a new figure if None.
    
    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing data.
    title : str, default `NoneType`
        Title of the pie chart.
    columns : list of string
        List of column names to analyse in 'data'.
    ax : matplotlib.axes.Axes, optional
        The axes object on which to plot the pie chart. 
        If None, a new figure and axes are created.
    figsize : tuple of floats, default `(8, 4)`
        Figure size in inches.
    fontsize : float, default 8.0
        Label font size
    colors : list of strings, default `NoneType`
        List of colours to use for pie chart segments.  
        If not provided, a default set of colours is used.
    pie_kwargs : dict, default {}
        Additional keyword arguments for axes.pie
    annotate_kwargs : dict, default {}
        Additional keyword arguments for annotations.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The matplotlib figure containing the pie chart.
    ax : matplotlib.axes.Axes
        The axes object of the plot.
    
    Example
    -------
        >>> df = pd.DataFrame(...)
        >>> pychart(df, 'Sample Title', ['Col1', 'Col2', 'Col3'],
        pie_kwargs={'startangle': 90}, annotate_kwargs={'fontsize': 10})
    """
    
    # Create new ax if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    # Define colors for pie chart segments
    default_colors = ['#d62728', '#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd',
                      '#8c564b', '#e377c2', '#bcbd22', '#ff1493']
    color_cycle = cycle(colors if colors else default_colors)
    # Filter the DataFrame based on the condition
    
    # Calculate counts for each column in 'columns'
    counts = [data[col].sum() for col in columns]
    
    # Calculate percentages
    total = sum(counts)
    percentages = [(size / total) * 100 for size in counts]
    
    # Create custom labels with percentages
    labels_with_percentages = [f'{label} ({percentage:.1f}%)' for label,
                               percentage in zip(columns, percentages)]
    
    # Create a DataFrame for plotting
    data_for_plot = {'Mutations': columns, 'Count': counts}
    df_for_plot = pd.DataFrame(data_for_plot)
    
    # Remove rows with Count <= 0
    df_for_plot = df_for_plot[df_for_plot['Count'] > 0]
    
    # Filter labels based on the rows in 'df_for_plot'
    labels_with_percentages =\
        [labels_with_percentages[i] for i in df_for_plot.index]
    
    # Create a pie chart in the corresponding subplot
    pie_args = {'autopct': '', 'startangle': 135, 'colors': colors,
                'wedgeprops': {'alpha': 0.5, 'edgecolor':'k', 'linewidth':0.5}}
    pie_args.update(pie_kwargs)
    wedges, text, autopct = ax.pie(df_for_plot['Count'], **pie_args)
    # set title
    if title is not None:
        ax.set_title(title, **title_kwargs)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    
    # Define annotation properties
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.0,
                      alpha=0.0)
    kw = dict(arrowprops=dict(arrowstyle="-", lw=0.4),
              bbox=bbox_props, zorder=0, va="center", **annotate_kwargs)
    
    # Create a list to store annotations for adjusting labels
    annotations = []
    
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        # Annotate labels and store them in the list
        ann = ax.annotate(labels_with_percentages[i], xy=(x, y),
                            xytext=(1.15 * np.sign(x), 1.15 * y),
                            horizontalalignment=horizontalalignment,
                            fontsize=fontsize, **kw)
        
        annotations.append(ann)
    # end loop
    fix_labels(annotations, ax, min_distance=0.13)
    
    # Adjust the layout and return the figure and axes
    plt.tight_layout(pad=1.3)
    return fig, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def pychart_grid(df, strat, columns, num_columns=2, figsize=(8, 4),
                 smaller=1, colors=None, pie_kwargs={}, annotate_kwargs={},
                 title_kwargs={}, subplots_adjust_kwargs={}
                 ):
    """
    Create a grid of pie charts for each condition in 'strat' based on 
    'columns' in the DataFrame 'df'.

    Parameters:
    ----------
    df (pd.DataFrame): 
        The DataFrame containing data.
    strat (list): 
        List of conditions to create pie charts for.
    columns (list): 
        List of columns to analyze in 'df'.
    num_columns (int, optional): 
        Number of columns in the grid. Default is 2.
    figsize (tuple, optional): 
        Figure size. Default is (8, 4).
    smaller (int, optional): 
        Scaling factor for figure and labels. Default is 1.
    colors (list, optional): 
        List of colors to use for pie chart segments. If not provided, a 
        default set of colors is used.
    pie_kwargs (dict, optional): 
        Additional keyword arguments to pass to the pie chart creation 
        (e.g., wedgeprops).
    annotate_kwargs (dict, optional): 
        Additional keyword arguments to pass to the annotations 
        (e.g., arrowprops).
    title_kwargs (dict, optional): 
        Additional keyword arguments to pass to the title of the subplot.

    Returns:
    -------
    fig (matplotlib.figure.Figure): 
        The matplotlib figure containing subplots.
    axes (numpy.ndarray): 
        The array of subplots.
    """

    num_plots = len(strat)
    num_rows = (num_plots + num_columns - 1) // num_columns  

    # Calculate the number of rows
    # Create subplots based on the number of conditions in 'strat' and 'num_columns'
    fig, axes = plt.subplots(num_rows, num_columns, 
                             figsize=(figsize[0] * smaller * num_columns, 
                                      figsize[1] * smaller * num_rows))

    # Flatten the axes array if it's more than 1D
    axes = np.array(axes).flatten()

    # Adjust horizontal and vertical space between subplots
    subplots_adjust_args = {"wspace": 0.25, "hspace":0.25}
    subplots_adjust_args.update(subplots_adjust_kwargs)
    plt.subplots_adjust(**subplots_adjust_args)

    # Define colors for pie chart segments
    colors = ['#d62728', '#1f77b4', '#ff7f0e', 
              '#2ca02c', '#9467bd', '#8c564b', 
              '#e377c2', '#bcbd22', '#ff1493']

    for idx, var in enumerate(strat):
        # Filter the DataFrame based on the condition
        data = df[df[var] == 1]

        # Calculate counts for each column in 'columns'
        counts = [data[col].sum() for col in columns]

        # Calculate percentages
        total = sum(counts)
        percentages = [(size / total) * 100 for size in counts]

        # Create custom labels with percentages
        labels_with_percentages = [f'{label} ({percentage:.1f}%)' for \
                                   label, percentage in zip(columns, 
                                    percentages)]

        # Create a DataFrame for plotting
        data_for_plot = {'Mutations': columns, 'Count': counts}
        df_for_plot = pd.DataFrame(data_for_plot)

        # Remove rows with Count <= 0
        df_for_plot = df_for_plot[df_for_plot['Count'] > 0]

        # Filter labels based on the rows in 'df_for_plot'
        labels_with_percentages = [labels_with_percentages[i] for \
                                   i in df_for_plot.index]

        pie_args = {'autopct': '', 'startangle': 135, 
                    'colors': colors, 
                    'wedgeprops': {'alpha': 0.5, 
                    'edgecolor':'k', 'linewidth':0.5}}
        
        pie_args.update(pie_kwargs)
        wedges, text, autopct = axes[idx].pie(df_for_plot['Count'], **pie_args)
        
        title_args = {'fontsize': 8 * smaller, 'y': 0.85}
        title_args.update(title_kwargs)
        
        axes[idx].set_title(f'Distribution for {var}', **title_args)
        # Equal aspect ratio ensures that pie is drawn as a circle
        axes[idx].axis('equal')  

        # Define annotation properties
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", 
                          lw=0.0, alpha=0.0)
        kw = dict(arrowprops=dict(arrowstyle="-", lw=0.4*smaller),
                  bbox=bbox_props, zorder=0, va="center", **annotate_kwargs)

        # Create a list to store annotations for adjusting labels
        annotations = []
    
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})

            # Annotate labels and store them in the list
            ann = axes[idx].annotate(labels_with_percentages[i], xy=(x, y), 
                                     xytext=(1.15 * np.sign(x), 1.15 * y),
                                     horizontalalignment=horizontalalignment, 
                                     fontsize=6 * smaller, **kw)

            annotations.append(ann)
        fix_labels(annotations, axes[idx], min_distance=0.13)
    return fig, axes

