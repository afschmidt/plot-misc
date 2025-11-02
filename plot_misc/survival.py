"""
Survival analysis plotting tools using matplotlib.

This module provides specialised plotting functions for survival analysis
results. The functions are designed to handle common survival analysis tasks
including step-wise survival curves (e.g., Kaplan-Meier or other non-parametric
estimators), follow-up data extraction, and risk table annotations beneath
survival plots.

Functions
---------
plot_step_wise(data, estimate_col, time_col, ...)
    Create step-wise plots for survival estimates, cumulative hazard functions,
    or other piecewise constant estimators with optional confidence intervals
    and customisable styling.

extract_follow_up(data, at_risk_col, time_col, ...)
    Extract at-risk counts at specified time points for creating follow-up
    tables or "Numbers at Risk" annotations commonly displayed beneath
    survival plots.

plot_table(data, ax, string_col, ...)
    Create table-like annotations beneath plots using matplotlib's coordinate
    transforms, allowing precise alignment between plot data and tabular
    information such as risk tables or summary statistics.
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    is_df,
    are_columns_in_df,
)
from typing import Any, Optional
from plot_misc.constants import (
    ForestNames as FNames,
    Real,
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_step_wise(data: pd.DataFrame,
                   estimate_col: str,
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
                   fill:bool = False,
                   fill_alpha:float = 0.8,
                   fill_colour: str | None = None,
                   figsize:tuple[Real,Real] = (2,2),
                   ax:plt.Axes | None = None,
                   margins:tuple[Real,Real] = (0.01,0.01),
                   add:bool = False,
                   kwargs_est:dict[str,Any] | None = None,
                   kwargs_ci:dict[str,Any] | None = None,
                   kwargs_fill:dict[str,Any] | None = None,
                   ) -> tuple[plt.Figure, plt.Axes]:
    """
    Create a step-wise plot for estimation functions such as survival
    curves or cumulative hazard functions.
    
    A step-wise function is a piecewise constant function that maintains
    a constant value over intervals and changes value only at specific
    time points, creating a characteristic "step" appearance. This is
    particularly useful in survival analysis where estimates like the
    Kaplan-Meier survival function remain constant between observed
    event times and only change (step down) when events occur.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        dataFrame with survival data and time as index
    estimate_col : `str`
        column name containing the estimates (e.g., survival probabilities,
        cumulative hazard rates, or other step functions).
    time_col : `str` or `None`
        the name of the time column, will default to the index if set to
        `None`.
    lower_ci_col : `str` or `None`, default `None`
        column name containing lower confidence interval
    upper_ci_col : `str` or `None`, default `None`
        column name containing upper confidence interval
    line_colour : `str`, default `steelblue`
        colour for the step-wise line.
    line_width : `Real`, default 2
        width of the line
    line_style : `str`, default '-'
        Line style of the line
    line_colour_ci : `str` or `None`, default `None`
        colour for confidence interval lines
    line_width_ci : `float` or `None`, default `None`
        width of confidence interval lines
    line_style_ci : `str` or `None`, default `None`
        Line style for confidence intervals
    fill : `bool`, default `False`
        whether to fill the area between confidence intervals or the main line
        if only one side of the confidence interval is supplied.
    fill_alpha : `float`, default 0.8
        the ransparency value for the filled confidence interval
        area, where 0 is fully transparent and 1 is fully opaque.
    fill_colour : `str` or `None`, default `None`
        colour for the filled confidence interval area. If None, uses
        the same colour as the main line.
    ax : `plt.Axes`, default `None`
        The pyplot.axes object.
    figsize : `tuple` [`Real`, `Real`], default (2, 2),
        The figure size in inches, when ax is set to None.
    xlim : `tuple` [`Real`,`Real`] or `None`, default `None`
        The x-axis limits.
    margins : `tuple` [`Real`,`Real`], default (0.01,0.01)
        Fractional margins for x and y axes as (x_margin, y_margin).
        Only applied when add is False.
    add : `bool`, default `False`
        whether to add the plot to an existing axes without modifying
        axis properties like margins and limits. Requires ax to be
        provided.
    kwargs_est : `dict` or `None`, default `None`
        additional keyword arguments passed to `ax.step` function for the
        the main line plotting function.
    kwargs_ci : `dict` or `None`, default `None`
        additional keyword arguments passed to `ax.step` function for the
        confidence interval line plotting function.
    kwargs_fill : `dict` or `None`, default `None`
        additional keyword arguments passed to `ax.fill` function plotting the
        area between the confidence intervals.
    
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
    is_type(estimate_col, str)
    is_type(time_col, (type(None), str))
    is_type(lower_ci_col, (type(None), str))
    is_type(upper_ci_col, (type(None), str))
    is_type(line_colour, (type(None), str))
    is_type(line_width, (type(None), float, int))
    is_type(line_style, (type(None), str))
    is_type(line_colour_ci, (type(None), str))
    is_type(line_width_ci, (type(None), float, int))
    is_type(line_style_ci, (type(None), str))
    is_type(fill, bool)
    is_type(fill_colour, (type(None), str))
    is_type(fill_alpha, (type(None), float))
    is_type(ax, (type(None), plt.Axes))
    is_type(xlim, (type(None), tuple))
    is_type(margins, tuple)
    is_type(add, bool)
    is_type(figsize, tuple)
    is_type(kwargs_ci, (type(None), dict))
    is_type(kwargs_est, (type(None), dict))
    is_type(kwargs_fill, (type(None), dict))
    # Validate required columns
    are_columns_in_df(
        data, [estimate_col, time_col, lower_ci_col, upper_ci_col],)
    # mapping None to empty dicts
    kwargs_est = kwargs_est or {}
    kwargs_ci = kwargs_ci or {}
    kwargs_fill = kwargs_fill or {}
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
    estimate = data[estimate_col].values
    # ### plotting
    # Main survival curve (step function)
    new_kwargs_est = _update_kwargs(
        update_dict=kwargs_est,
        where='post', linewidth=line_width,
        linestyle=line_style, color=line_colour,
        zorder=10,)
    ax.step(time_, estimate, **new_kwargs_est,)
    # add confidence intervals
    if line_colour_ci is None:
        line_colour_ci = line_colour
    if line_style_ci is None:
        line_style_ci = line_style
    if line_width_ci is None:
        line_width_ci = line_width
    for ci_col in [lower_ci_col, upper_ci_col]:
        if ci_col is not None:
            new_kwargs_ci = _update_kwargs(
                update_dict=kwargs_ci,
                where='post', linewidth=line_width_ci,
                linestyle=line_style_ci, color=line_colour_ci,
                zorder=10,)
            ci_ = data[ci_col].values
            ax.step(time_, ci_, **new_kwargs_ci,)
    # add shaded area between limits
    if fill == True:
        if fill_colour is None:
            fill_colour = line_colour
        fill_lims = [estimate, estimate]
        if lower_ci_col is not None:
            fill_lims[0] = data[lower_ci_col].values
        if upper_ci_col is not None:
            fill_lims[1] = data[upper_ci_col].values
        # only plot the fill if the limits are different
        if not np.array_equal(fill_lims[0], fill_lims[1]):
            new_kwargs_fill = _update_kwargs(
                update_dict=kwargs_fill,
                step='post', alpha=fill_alpha, color=fill_colour,
                zorder=1,
            )
            ax.fill_between(time_, fill_lims[0], fill_lims[1],
                            **new_kwargs_fill,)
        else:
            warnings.warn("`fill` is `True`, but the supplied confidence "
                          "intervals are all None type."
                          )
    # Formatting
    if add == False:
        ax.margins(*margins)
        if xlim is not None:
            ax.set_xlim(xlim)
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def extract_follow_up(data: pd.DataFrame,
                      at_risk_col: str,
                      time_col: str | None = None,
                      points: int | list[Real] = 3,
                      output_col: str = 'group_1',
                      thousands_sep: str = ',',
                      ) -> pd.DataFrame:
    """
    Extract follow-up data for specific time points from survival analysis
    data.
    
    This function extracts at-risk counts at specified time points from
    survival data, commonly used for creating "Numbers at Risk" tables
    beneath (for example) Kaplan-Meier plots or for summarising follow-up data
    at key time intervals (e.g., 1, 3, 5-year follow-up).
    
    Parameters
    ----------
    data : `pd.DataFrame`
        DataFrame with survival data. Time values should be in the index or
        a specified column.
    at_risk_col : `str`
        Column name containing number at risk values.
    time_col : `str` or `None`, default `None`
        Column name containing time values. If None, uses the DataFrame index
        as time values.
    points : int or list[float], default 3
        Specification of time points to extract:
        
        - If int: Number of evenly spaced time points to extract from the
          data's time range. For example, points=4 with data spanning 0-100
          would extract at times [0, 33, 67, 100].
        - If list: Specific time points to query. Values can extend beyond
          the data's time range (returns 0 at-risk for future times).
    output_col : `str`, default `group_1`
        Prefix for output column names. Creates columns named
        ``{output_col}_at_risk``, ``{output_col}_at_risk_format``, etc.
    thousands_sep : `str`, default `,`
        Thousands separator character for formatting at-risk numbers in the
        formatted output column.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with the following columns:
        - 'time': Requested time points (as integers)
        - '{output_col}_at_risk': Number at risk at each time point
        - '{output_col}_at_risk_format': Formatted at-risk numbers with
          thousands separator
        - '{output_col}_raw_time': Actual time values from data corresponding
          to each requested time point
        
    Raises
    ------
    ValueError
        If any requested time point is before the first observation in the
        data. Time points beyond the maximum follow-up are handled by setting
        at-risk to zero rather than raising an error.
    InputValidationError
        If required columns are not found in DataFrame or if input types
        are invalid.
    
    Notes
    -----
    The function uses a "floor" approach for time matching: for each requested
    time point, it finds the latest available time that is ≤ the requested
    time. Time points beyond the study's maximum follow-up time return
    zero at-risk counts.
    
    Examples
    --------
    >>> # Create sample survival data
    >>> import pandas as pd
    >>> import numpy as np
    >>> time_points = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
    >>> at_risk_counts = [1000, 950, 890, 820, 740, 650, 540, 420, 280, 120]
    >>> data = pd.DataFrame({'at_risk': at_risk_counts}, index=time_points)
    
    >>> result = extract_follow_up_data(data, 'at_risk', points=5)
    >>> print(result)
       time  group_1_at_risk group_1_at_risk_format  group_1_raw_time
    0     0             1000                  1,000                 0
    1    24              890                    890                24
    2    48              740                    740                48
    3    72              540                    540                72
    4   108              120                    120               108
    """
    is_df(data)
    is_type(at_risk_col, str)
    is_type(time_col, (type(None), str))
    is_type(points, (list, int))
    is_type(output_col, str)
    is_type(thousands_sep, str)
    # check columns are present
    are_columns_in_df(data, [at_risk_col, time_col])
    # ## extract data
    if time_col is None:
        time_ = data.index.values
    else:
        time_ = data[time_col].values
    max_time = time_.max()
    at_risk = data[at_risk_col].values
    # time points
    if isinstance(points, int):
        if len(time_) <= points:
            time_points = time_
            at_risk_points = at_risk
        else:
            # Select evenly spaced points
            indices = np.linspace(0, len(time_) - 1, points, dtype=int)
            time_points = time_[indices]
            closest_times = time_points
            at_risk_points = at_risk[indices]
    else:
        # is a list, should not be empty
        if len(points) == 0:
            raise ValueError("points list cannot be empty")
        # list of specific time points
        time_points = np.array(points)
        closest_times = np.zeros_like(time_points, dtype=float)
        at_risk_points = np.zeros_like(time_points, dtype=int)
        for i, point in enumerate(time_points):
            if point > max_time:
                # set at risk to zero if larger than max follow-up
                closest_times[i] = point
                at_risk_points[i] = 0
            else:
                # find closest time <= point
                valid_indices = np.where(time_ <= point)[0]
                if len(valid_indices) > 0:
                    closest_idx = valid_indices[-1]
                    closest_times[i] = time_[closest_idx]
                    at_risk_points[i] = at_risk[closest_idx]
                else:
                    # Point is before first time point - raise error
                    min_time = time_.min()
                    raise ValueError(
                        f"Requested time point {point} is before the first "
                        f"observation at time {min_time}. Valid time range is "
                        f"[{min_time}, {max_time}]."
                    )
    # ### format and store in table
    at_risk_format = [f"{int(n):{thousands_sep}}" for n in at_risk_points]
    time_points = [int(t) for t in time_points]
    res = pd.DataFrame({
            'time': time_points,
            f'{output_col}_at_risk': at_risk_points,
            f'{output_col}_at_risk_format': at_risk_format,
            f'{output_col}_raw_time': closest_times,
        })
    # return
    return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_table(
    data:pd.core.frame.DataFrame,
    ax: plt.Axes, string_col: str | list[str],
    x_col:str='time', yloc:Real | list[Real] | None=None,
    halignment_text:str="center",
    valignment_text:str="center",
    size_text:Real=10,
    size_xticklabel:Real=10,
    yticklabel: str | list[str] | None = None,
    xticklabel: list[str] | None = None,
    xtickloc: list[Real] | None = None,
    pad_first:Real = 0.0,
    pad_last:Real = 0.0,
    pad_all:Real = 0.0,
    kwargs_text_dict:dict[Any,Any] | None = None,
    kwargs_xticklabel_dict:dict[Any,Any] | None = None,
) -> plt.Axes:
    """
    Create a table-like annotation beneath a plot.
    
    The table is positioned using data coordinates for x-axis alignment and
    axis coordinates for y-axis positioning, allowing precise alignment with
    plot elements above.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        DataFrame containing `string_col` that should be plotted.
    ax : `plt.Axes`
        Matplotlib Axes object where the table will be plotted.
    string_col : `str` or `list` [`str`],
        Column name(s) containing the values to display in the table.
        Each column becomes a row in the resulting table. Values should
        be strings or convertible to strings for display.
    x_col : `str`, default 'time'
        Column in `dataframe` containing the x-axis coordinates.
    yloc : `Real`, `list` [`Real`] or `None`, default `None`
        y-axis positions for table rows in axes coordinates (0-1 range).
        The list must match the length of string_col. If None, rows are evenly
        spaced vertically.
    halignment_text : `str`, default "center"
        Horizontal alignment of the table text (`left`, `center`, `right`).
    valignment_text : `str`, default "center"
        Vertical alignment of the table text (`top`, `center`, `bottom`).
    size_text : `real`, default 10
        The font size for the table text.
    size_xticklabel : `Real`, default 10
        Font size of the x-axis tick labels (if used).
    yticklabel : `str`, `list` [`str`] or  `None`, default `None`
        Labels for table rows (y-axis tick labels). If provided, must
        match the length of string_col. Typically contains group names
        or row descriptions.
    xticklabel : `list` [`str`] or `None`, default `None`
        A list of string containing the x-axis labels. Should match the length
        of `xtickloc`.
    xtickloc : `list` [`real`] or `None`, default `None`
        A list of real values defining the x-axis locations for the ticks.
    pad_first : `Real`, default 0.0
        Horizontal padding applied to first string.
    pad_last : `Real`, default 0.0
        Horizontal padding applied to the last string.
    pad_all : `Real`, default 0.0
        Horizontal padding applied to all the strings. Note this will be added
        on top of any `pad_last` or `pad_first` padding as a sum.
    kwargs_text_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional keyword arguments passed to ax.text() for table entries.
        Allows fine-tuning of text appearance (colour, weight, etc.).
    kwargs_xticklabel_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional keyword arguments passed to ax.set_xticklabels() for
        x-axis labels.
    
    Returns
    -------
    plt.Axes
        The axis object with the table rendered.
    
    Raises
    ------
    ValueError
        If yticklabel and string_col have different lengths, if yloc and
        string_col have different lengths, if xticklabel and xtickloc
        have different lengths, if xticklabel is provided without xtickloc
        or vice versa.
    InputValidationError
        If required columns are not found in the DataFrame or input types
        are invalid.
    
    Notes
    -----
    The function uses matplotlib's axis transforms to position text:
    - X-coordinates use data coordinates (matching the main plot)
    - Y-coordinates use axes coordinates (0-1 range for consistent spacing)
    
    This hybrid coordinate system allows the table to align with plot data
    while maintaining consistent vertical spacing regardless of
    data values.
    """
    # ################### do check and set defaults
    is_df(data)
    is_type(x_col, str)
    is_type(ax, plt.Axes)
    is_type(string_col, (list,str))
    is_type(yloc, (list, float, int, type(None)))
    is_type(halignment_text, str)
    is_type(valignment_text, str)
    is_type(size_text, (int, float))
    is_type(xticklabel, (type(None), list))
    is_type(xtickloc, (type(None), list))
    is_type(yticklabel, (str, list, type(None)))
    is_type(size_xticklabel, Real)
    is_type(pad_first, Real)
    is_type(pad_last, Real)
    # check if columns are in dataframe
    if isinstance(string_col, str):
        string_col = [string_col]
    are_columns_in_df(data, expected_columns=string_col + [x_col])
    # set None to dict
    kwargs_text_dict = kwargs_text_dict or {}
    kwargs_xticklabel_dict = kwargs_xticklabel_dict or {}
    # ################### remove spines
    ax.spines[['top', 'right']].set_visible(False)
    # remove labels
    ax.yaxis.set_ticklabels([])
    # remove ticks
    ax.set_yticks([])
    # set the y-axis to start exactly at zero
    # ax.set_ylim(bottom=0)
    # ################### y-tick labels
    if yticklabel is not None:
        if isinstance(yticklabel, str):
            yticklabel = [yticklabel]
        if len(yticklabel) != len(string_col):
            raise ValueError(
                "`yticklabel` and `string_col` should have the "
                "same number of elements."
            )
    if yloc is not None:
        if isinstance(yloc, Real):
            yloc = [yloc]
        else:
            # inverting it to get the proper order
            yloc = yloc[::-1]
        if len(yloc) != len(string_col):
            raise ValueError(
                "`yloc` and `string_col` should have the "
                "same number of elements."
            )
    # ################### x-tick labels
    if (not xticklabel is None) and (xtickloc is None):
        raise ValueError('`xtickloc` should be supplied if `xticklabel` is used.')
    if (xticklabel is None) and (not xtickloc is None):
        raise ValueError('`xticklabel` should be supplied if `xtickloc` is used.')
    if (xticklabel is not None) and (xtickloc is not None):
        if len(xticklabel) != len(xtickloc):
            raise ValueError('`xticklabel` and `xtickloc` contain distinct '
                             'values.')
        # plot x-tick labels
        ax.set_xticks(xtickloc)
        # update kwargs for labels
        new_xticklabel_kwargs = _update_kwargs(
            update_dict=kwargs_xticklabel_dict,
            size=size_xticklabel,
        )
        ax.xaxis.set_ticklabels(xticklabel,
                                **new_xticklabel_kwargs,
                                )
        # # remove the actual tick
        # ax.tick_params(left=False)
    else:
        # remove x ticks
        ax.xaxis.set_ticklabels([])
        ax.set_xticks([])
    # ################### plot string column
    # mapping the x-axis to the 0 and 1 range.
    # NOTE get_xaxis_transform maps the y-axis to [0, 1] and the
    # y-axis to the data coordinate system.
    transform = ax.get_xaxis_transform()
    # get y-coordinates between 0 and 1, excluding the endpoints
    ycoords = np.linspace(1, 0, len(string_col) + 2)[1:-1]
    # tick labels
    ylabs, ylocs = ([] for _ in range(2))
    for j, string_col_j in enumerate(string_col):
        # internal or user supplied ylocations
        if yloc is None:
            yloc_ = ycoords[j]
        else:
            yloc_ = yloc[j]
        for k, row in data.iterrows():
            xticklabel1 = row[x_col]
            xticklabel2 = row[string_col_j]
            if pd.isna(xticklabel2):
                xticklabel2 = ""
            # update the kwargs
            new_text_kwargs = _update_kwargs(
                update_dict=kwargs_text_dict,
                size=size_text,
                horizontalalignment=halignment_text,
                verticalalignment=valignment_text,
            )
            # adding text padding
            if k == 0:
                xticklabel1 = xticklabel1 + pad_first
            elif k == data.shape[0]-1:
                xticklabel1 = xticklabel1 + pad_last
            xticklabel1 = xticklabel1 + pad_all
            # plotting table text
            ax.text(
                y=yloc_,
                x=xticklabel1,
                s=xticklabel2,
                transform=transform,
                **new_text_kwargs,
            )
        # adding tick labels
        ylocs = ylocs + [yloc_]
        if yticklabel is not None:
            ylabs = ylabs + [yticklabel[j]]
    if yticklabel is not None:
        ax.set_yticks(ylocs)
        ax.set_yticklabels(ylabs)
    # ################### return
    return ax


