"""
TODO
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
from typing import Any, Optional, Sequence
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
                   ) -> tuple[plt.Figure, plt.Axes]:
    """
    Provides a step-wise illustration of an esimation function such as
    the survival function or the cummulative hazard.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        DataFrame with survival data and time as index
    estimate_col : `str`
        Column name containing estimates.
    time_col : `str` or `None`
        The name of the time column, will default to the index if set to
        `None`.
    lower_ci_col : `str` or `None`, default `None`
        Column name containing lower confidence interval
    upper_ci_col : `str` or `None`, default `None`
        Column name containing upper confidence interval
    line_colour : `str`, default '#2E86AB'
        Colour for the step-wise line.
    line_width : `Real`, default 2
        Width of the line
    line_style : `str`, default '-'
        Line style of the line
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
    margins : `tuple` [`Real`,`Real`], default (0.01,0.01)
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
    # Validate required columns
    are_columns_in_df(
        data, [estimate_col, time_col, lower_ci_col, upper_ci_col],)
    # mapping None to empty dicts
    kwargs_est = kwargs_est or {}
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
            ax.fill_between(time_, fill_lims[0], fill_lims[1],
                            step='post', alpha=fill_alpha, color=fill_colour,
                            zorder=1,
                            )
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
# import plot_misc.example_data.examples as examples
# surv_table = examples.create_survival_data(nrows=24)
# surv_table = examples.create_survival_data(nrows=20)
# extract_follow_up_data(surv_table, at_risk_col='at_risk', points=4)
# extract_follow_up_data(surv_table, at_risk_col='at_risk', points=[0, 20, 40, 80, 100, 120])
def extract_follow_up(data: pd.DataFrame,
                           at_risk_col: str,
                           time_col: str | None = None,
                           points: int | list[float] = 3,
                           output_col: str = 'group_1',
                           thousands_sep: str = ',',
                           ) -> pd.DataFrame:
    """
    Extract follow-up data for specific time points from survival analysis
    data.
    
    For each requested time point, finds the closest available time point that
    is less than or equal to the requested time and extracts the corresponding
    at-risk count. Time points beyond the study's maximum follow-up time return
    zero at-risk counts.
    
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
        Either an integer specifying the number of evenly spaced time points
        to extract, or a list of specific time points to query.
    output_col : `str`, default `group_1`
        Prefix for output column names. Creates columns named
        '{output_col}_at_risk', '{output_col}_at_risk_format', etc.
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
        
    Examples
    --------
    >>> # Create sample survival data
    >>> import pandas as pd
    >>> import numpy as np
    >>> time_points = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
    >>> at_risk_counts = [1000, 950, 890, 820, 740, 650, 540, 420, 280, 120]
    >>> data = pd.DataFrame({'at_risk': at_risk_counts}, index=time_points)
    
    >>> # Extract 5 evenly spaced time points
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

# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# surv_table = pd.DataFrame(
#     {
#     'time': [0, 365, 730, 1095, 1461, 1826, 2191, 2556, 2922, 3287,
#              3652, 4017, 4383, 4748, 5113, 5478],
#     'Not Discordant': ['268,196', '263,426', '258,484', '254,009',
#                        '249,315', '244,907', '240,562', '236,574',
#                        '233,347', '230,368', '227,648', '224,916',
#                        '222,169', '172,545', '95,987', '15,280'],
#     'Apo-B discordant': ['5,749', '5,629', '5,494', '5,374',
#                          '5,245', '5,129', '5,029', '4,935',
#                          '4,863', '4,777', '4,714', '4,634',
#                          '4,558', '3,586', '2,030', '346'],
#     'time_format': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
# }
# )

def plot_table(
    data:pd.core.frame.DataFrame,
    ax: plt.Axes, string_col: str | list[str],
    x_col:str='time', yloc:Real | list[Real] | None=None,
    yticklabel: str | list[str] | None = None,
    halignment_text:str="center",
    valignment_text:str="center",
    size_text:Real=10,
    size_xticklabel:Real=10,
    xticklabel: Sequence[str] | None = None,
    xtickloc: Sequence[Real] | None = None,
    pad_first:Real = 0.0,
    pad_last:Real = 0.0,
    l_xticklab_pad:str | None = None,
    r_xticklab_pad:str | None = None,
    kwargs_text_dict:dict[Any,Any] | None = None,
    kwargs_xticklabel_dict:dict[Any,Any] | None = None,
) -> plt.Axes:
    """
    Plot a bottom-aligned annotation table alongside a survival plot or similar
    structured figure, using `ax.text` and x-axis coordinates.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        Pandas DataFrame containg `string_col` that should be plotted.
        margin of error, etc.
    ax : plt.axes
            Axes to operate on.
    string_col : `str` or `list` [`str`],
            The the column name that should be plotted. Should contain a
            `string` value.
    y_col : `str`, default 'y_axis'
        Column in `dataframe` containing the vertical coordinates.
    xloc: `real`, default 0.5
        The position of the text **orthogonal to the axis**, given in **axes
        coordinates** (0 = bottom/left of axis, 1 = top/right). Negative values
        place the label outside the axis bounds.
    halignment_text : `str`, default "center"
        Horizontal alignment of the table text (`left`, `center`, `right`).
    valignment_text : `str`, default "center"
        Vertical alignment of the table text (`top`, `center`, `bottom`).
    size_text : `real`, default 10
        The font size for the table text.
    size_yticklabel : `real`, default 10
        Font size of the y-axis tick labels (if used).
    yticklabel : `list` [`str`] or `None`, default `None`
        A list of string containing the y-axis labels. Should match the length
        of `ytickloc`.
    ytickloc : `list` [`real`] or `None`, default `None`
        A list of real values defining the y-axis locations for the ticks.
    l_yticklab_pad : str or `None`, default `None`
        Optional prefix to be added to each y-axis label.
    r_yticklab_pad : str or `None`, default `None`
        Optional suffix to be added to each y-axis label.
    span : `dict` [`int`, `dict` [`str`, `any`]] or `None`, default `NoneType`
        Whether you want to add an optional span. Supply a dictionary with
        k many unique keys and next dictionaries containing `min` and
        `max` coordinates and `kwargs`. This will all be supplied to
        `merit_helper.utils.utils.plot_span`.
    kwargs_text_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional arguments passed to `ax.text` for table entries.
    kwargs_yticklabel_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional arguments passed to `ax.set_yticklabels`.
    
    Returns
    -------
    plt.Axes
        The axis object with the table rendered.
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
    is_type(l_xticklab_pad, (type(None), str))
    is_type(r_xticklab_pad, (type(None), str))
    is_type(xticklabel, (type(None), list))
    is_type(xtickloc, (type(None), list))
    # check if columns are in dataframe
    if isinstance(string_col, str):
        string_col = [string_col]
    are_columns_in_df(data, expected_columns=string_col + [x_col])
    # set None to dict
    kwargs_text_dict = kwargs_text_dict or {}
    kwargs_xticklabel_dict = kwargs_xticklabel_dict or {}
    # ################### remove spines
    ax.spines[['top', 'right']].set_visible(False)
    # remove lables
    ax.yaxis.set_ticklabels([])
    # remove ticks
    ax.set_yticks([])
    # set the y-axis to start exactly at zero
    # ax.set_ylim(bottom=0)
    # ################### y-tick lables
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
    if (not xticklabel is None) and (not xtickloc is None):
        if len(xticklabel) != len(xtickloc):
            raise IndexError('`xticklabel` and `xtickloc` containts distinct '
                             'values.')
        # add optional label padding
        if not l_xticklab_pad is None:
            xticklabel = [l_xticklab_pad + str(s) for s in xticklabel]
        if not r_xticklab_pad is None:
            xticklabel = [str(s) + r_xticklab_pad for s in xticklabel]
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
            if k == 0:
                xticklabel1 = xticklabel1 + pad_first
            elif k == data.shape[0]-1:
                xticklabel1 = xticklabel1 + pad_last
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
        ylabs = ylabs + [yticklabel[j]]
    ax.set_yticks(ylocs)
    ax.set_yticklabels(ylabs)
    # ################### return
    return ax


