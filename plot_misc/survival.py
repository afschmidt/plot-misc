"""
TODO
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    is_df,
    are_columns_in_df,
    Error_MSG,
)
from typing import Any, Optional
from plot_misc.constants import Real

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_time_to_event(data: pd.DataFrame,
                            survival_col: str,
                            time_col: str | None = None,
                            lower_ci_col: str | None = None,
                            upper_ci_col: str | None = None,
                            xlim: tuple[Real,Real] | None = None,
                            line_colour: str = 'steelblue',
                            line_width: Real = 2,
                            line_style: str = '-',
                            line_colour_ci: str | None = None,
                            line_width_ci: Real | None = None,
                            line_style_ci: str | None = None,
                            figsize:tuple[Real,Real] = (2,2),
                            ax:plt.Axes | None = None,
                            margins:tuple[Real,Real] = (0,0),
                            add:bool = False,
                            kwargs_surv:dict[str,Any] | None = None,
                            kwargs_ci:dict[str,Any] | None = None,
                            ) -> tuple[plt.Figure, plt.Axes]:
    """
    Create a Kaplan-Meier survival curve plot.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        DataFrame with survival data and time as index
    survival_col : `str`
        Column name containing survival probabilities
    time_col : `str` or `None`
        The name of the time column, will default to the index if set to
        `None`.
    lower_ci_col : `str` or `None`, default `None`
        Column name containing lower confidence interval
    upper_ci_col : `str` or `None`, default `None`
        Column name containing upper confidence interval
    line_colour : `str`, default '#2E86AB'
        Colour for the survival curve
    line_width : `Real`, default 2
        Width of the survival curve line
    line_style : `str`, default '-'
        Line style for survival curve
    line_colour_ci : `str` or `None`, default `None`
        Colour for confidence interval lines
    line_width_ci : `float` or `None`, default `None`
        Width of confidence interval lines
    line_style_ci : `str` or `None`, default `None`
        Line style for confidence intervals
    ax : `plt.ax`, default `None`
        The pyplot.axes object.
    figsize : `tuple` [`Real`, `Real`], default (2, 2),
        The figure size in inches, when ax is set to None.
    xlim : `tuple` [`Real`,`Real`] or `None`, default `None`
        The x-axis limits.
    margins : `tuple` [`Real`,`Real`], default (0, 0)
        Margins for x and y axes
    add : `bool`, default `False`
        Whether to add to existing axis
        
    Returns
    -------
    plt.Figure
        The matplotlib figure object
        
    Raises
    ------
    InputValidationError
        If required columns are not found in DataFrame
    ValueError
        When setting `add` to True without supplying an `ax` object.
    """
    is_df(data)
    is_type(survival_col, str)
    is_type(time_col, (type(None), str))
    is_type(lower_ci_col, (type(None), str))
    is_type(upper_ci_col, (type(None), str))
    is_type(line_colour, (type(None), str))
    is_type(line_width, (type(None), str))
    is_type(line_style, (type(None), str))
    is_type(line_colour_ci, (type(None), str))
    is_type(line_width_ci, (type(None), str))
    is_type(line_style_ci, (type(None), str))
    is_type(ax, (type(None), plt.Axes))
    is_type(xlim, tuple)
    is_type(margins, tuple)
    is_type(add, bool)
    # Validate required columns
    are_columns_in_df(
        data, [survival_col, time_col, lower_ci_col, upper_ci_col],)
    # mapping None to empty dicts
    kwargs_surv = kwargs_surv or {}
    kwargs_ci = kwargs_ci or {}
    # ### should we create a figure and axis
    if add == False:
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
    else:
        if ax is None:
            raise ValueError('please supply an `ax` when `add` is `True`.')
        else:
            f = ax.figure
    # ### Extract data
    if time_col is None:
        time_ = data.index.values
    else:
        time_ = data[time_col].values
    # estimates
    survival = data[survival_col].values
    # ### plotting
    # Main survival curve (step function)
    new_kwargs_surv = _update_kwargs(
        update_dict=kwargs_surv,
        where='post', linewidth=line_width,
        linestyle=line_style, color=line_colour,)
    ax.step(time_, survival, **new_kwargs_surv,)
    # add confidence intervals
    if line_colour is None:
        line_colour = line_colour
    if line_style_ci is None:
        line_style_ci = line_style
    if line_width_ci is None:
        line_width_ci = line_width
    for ci_col in [lower_ci_col, upper_ci_col]:
        if ci_col is not None:
            new_kwargs_ci = _update_kwargs(
                update_dict=kwargs_ci,
                where='post', linewidth=line_width_ci,
                linestyle=line_style_ci, color=line_colour_ci,)
            ci_ = data[ci_col].values
            ax.step(time_, ci_, **new_kwargs_ci,)
    # Formatting
    if add == False:
        ax.margins(*margins)
        if xlim is not None:
            ax.set_xlim(xlim)
    return f, ax

