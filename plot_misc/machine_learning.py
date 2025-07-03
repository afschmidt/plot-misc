"""
Figure templates for visualising performance and interpretability of
machine learning models.

This module provides reusable plotting utilities for common visualisations in
machine learning workflows, including lollipop charts for feature importance,
calibration plots for model reliability assessment, and decision curve
analysis (DCA) plots for evaluating clinical utility.

Functions
---------
lollipop(values, labels, ...)
    Draws a line-and-dot chart as a visual alternative to bar plots.

calibration(data, observed, predicted, ...)
    Creates calibration plots comparing observed and predicted risks with
    optional confidence intervals.

Classes
-------
DecisionCurve
    A class to compute and plot decision curves, quantifying net benefit
    across varying risk thresholds.

"""

# imports
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib as mpl
from plot_misc.constants import (
    NamesDecisionCurves as NamesDC,
    NamesMachineLearnig as NamesML,
)
from plot_misc.errors import (
    is_type,
    is_df,
    are_columns_in_df,
    same_len,
    InputValidationError,
    string_to_list,
)
from plot_misc.utils.utils import (
    change_ticks,
    _update_kwargs,
)
from typing import (
    Any,
    Callable,
    List,
    Union,
    Tuple,
    Dict,
)
from statsmodels.nonparametric.smoothers_lowess import lowess
# from packaging import version
# if version.parse('3.4.0') < version.parse(mpl._version.version):
#     from matplotlib.colorbar import Colorbar as colorbar_factory
# else:
#     from matplotlib.colorbar import colorbar_factory

# #############################################################################

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lollipop(values:np.ndarray, labels:np.ndarray,
             line_color:str='tab:orange', dot_color:str='deeppink',
             linewidth:float=1, dot_edge_color:str='black', dot_size:float=4,
             dot_edge_size:float=0.5,
             importance_margin:float | None =0,
             importance_limit:tuple[float,float] | None=None,
             reverse_feature_order:bool=False,
             vertical:bool=False,
             figsize:tuple=(6, 6),
             ax:plt.Axes | None=None,
             kwargs_lines_dict:dict[Any,Any] | None=None,
             kwargs_plot_dict:dict[Any,Any] | None=None,
             ) -> tuple[plt.Axes, plt.Figure]:
    '''
    Plots a lollipop chart.
    
    A visual alternative to a bar chart, drawing a horizontal line for each
    observation and ending in a dot. Primarily used for ranked feature
    importance, effect sizes, or similar vector-valued summaries.
    
    Parameters
    ----------
    values : `np.ndarray`
        Values determining the length of each line.
    labels : `np.ndarray`
        Labels for each feature.
    line_color: `str`, default `tab:orange`
        The line colour.
    linewidth : `float`, default 1
        The linewidth.
    dot_color : `str`, default `deeppink`
        The dot colour.
    dot_edge_color : `str`, default `black`
        Colour of the dot edges.
    dot_size : `float`, default 4
        The size of the dot.
    dot_edge_size : `float`, default 0.5
        Width of the dot edge outline.
    reverse_feature_order : `bool`, default `False`
        Plots the features in opposite order.
    importance_margin : `float`, default 0
        Padding on the axis representing the feature importance value.
        Set to `None` to use matplotlib defaults.
    importance_limit : `tuple` [`float`,`float`], default `NoneType`
        Explicit x-axis limits. If None, inferred automatically.
    vertical : `bool`, default `True`
        If True, draws vertical lines with feature labels on the y-axis.
        If False, draws horizontal lines with feature labels on the x-axis.
        This effectively transposes the chart orientation and can be used
        to better accommodate long labels or large feature sets.
    ax : `plt.Axes`, default `NoneType`
        Matplotlib Axes to plot on. If None, a new figure and axes are created.
    figsize : `tuple` [`float`,`float`], default `(10, 10)`
        The figure size in inches when ax is `NoneType`.
    kwargs_lines_dict : `dict` [`str`, `any`] or `None`, default `None`
        Additional keyword arguments passed to `ax.hlines`.
    kwargs_plot_dict : `dict` [`str`, `any`] or `None`, default `None`
        Additional keyword arguments passed to `ax.plot` for dot rendering.
    
    Returns
    -------
    figure : `matplotlib.figure.Figure`
        The matplotlib Figure object.
    ax : `matplotlib.axes.Axes`
        The matplotlib Axes object with the plot drawn on.
    '''
    
    # ################### Check input
    is_type(ax, (type(None), plt.Axes))
    is_type(line_color, str)
    is_type(linewidth, (int, float))
    is_type(dot_color, str)
    is_type(dot_edge_color, str)
    is_type(dot_size, (int, float))
    is_type(dot_edge_size, (int, float))
    is_type(vertical, bool)
    same_len(values, labels)
    # map None to empty dict
    kwargs_lines_dict = kwargs_lines_dict or {}
    kwargs_plot_dict = kwargs_plot_dict or {}
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # get index index to numeric
    index = range(values.shape[0])
    # ################### plot lines and dots, first updating the kwargs
    new_lines_dict = _update_kwargs(kwargs_lines_dict, color=line_color,
                                    linewidth=linewidth)
    new_plot_dict = _update_kwargs(kwargs_plot_dict,
                                   marker='o',
                                   linestyle='None',
                                   c=dot_color,
                                   markeredgecolor=dot_edge_color,
                                   markersize=dot_size,
                                   markeredgewidth=dot_edge_size,
                                   )
    if vertical == True:
        # #### vertical lines
        ax.vlines(x=index, ymin=0, ymax=values, **new_lines_dict,
                  )
        ax.plot(index, values,  **new_plot_dict,
                )
        change_ticks(ax=ax, ticks=list(index), labels=list(labels), axis='x')
        #  margins
        value_lim = ax.get_ylim()
        if not importance_margin is None:
            ax.margins(y=importance_margin)
        if importance_limit is None:
            ax.set_ylim(0, value_lim[1]*1.05)
        else:
            ax.set_ylim(importance_limit)
        #  invert feature axis
        if reverse_feature_order == True:
            ax.invert_xaxis()
    else:
        # #### horizontal lines
        ax.hlines(y=index, xmin=0, xmax=values, **new_lines_dict,
                  )
        ax.plot(values, index, **new_plot_dict,
                )
        change_ticks(ax=ax, ticks=list(index), labels=list(labels), axis='y')
        #  margins
        value_lim = ax.get_xlim()
        if not importance_margin is None:
            ax.margins(x=importance_margin)
        if importance_limit is None:
            ax.set_xlim(0, value_lim[1]*1.05)
        else:
            ax.set_xlim(importance_limit)
        #  invert feature axis
        if reverse_feature_order == True:
            ax.invert_yaxis()
    # hide spines
    try:
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    except AttributeError:
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
    # return the figure and axis
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calibration(data:pd.DataFrame | dict[str,pd.DataFrame],
                observed:str, predicted:str,
                lower_observed:str | None = None,
                upper_observed:str | None = None,
                ci_colour:str | list[str] | None = ['lightcoral'],
                ci_linewidth:str | list[float] | None = [0.5],
                dot_marker:str | list[str] = ['o'],
                dot_colour:str | list[str] = ['lightcoral'],
                line_colour:str | list[str] = ['lightcoral'],
                line_linewidth:str | list[float] = [0.7],
                line_linestyle:str | list[str] =['--'],
                figsize:tuple[float,float]=(6, 6),
                diagonal_colour:str='black',
                diagonal_linewidth:float=0.5,
                diagonal_linestyle:str='-',
                margins:tuple[float, float]=(0.01, 0.01),
                curves:dict[str,list[np.ndarray, Callable, dict, dict]] | None = None,
                ax:plt.Axes | None = None,
                kwargs_ci_dict:dict[Any,Any] | None = None,
                kwargs_dot_dict:dict[Any,Any] | None = None,
                kwargs_line_dict:dict[Any,Any] | None = None,
                kwargs_diagonal_dict:dict[Any,Any] | None = None,
                ) -> tuple[plt.Axes, plt.Figure, dict[str, np.ndarray]]:
    '''
    Provides a basic template for a calibration plot, comparing the observed
    and predicted risks. Here the observed risk will be based on some grouping
    of the predicted risk, and the average event rate within each group.
    Hence optional confidence intervals can be included for the observed risk.
    
    Can plot multiple lines (representing distinct prediction models),
    although this can quickly become crowded and one might consider a
    multi panel plot.
    
    Parameters
    ----------
    data : pd.DataFrame or dict of pd.DataFrame
        When multiple DataFrame's are provided, care should be given to ensure
        all have the same column names.
    observed : str
        A column name in `data` representing the observed risk
        (between 0 and 1).
    predicted : str
        A column name in `data` representing the predicted risk
        (between 0 and 1).
    lower_observed : str, default `NoneType`
        An optional column name in `data` representing the lower bound of
        the observed risk.
    upper_observed : str, default `NoneType`
        An optional column name in `data` representing the upper bound of
        the observed risk.
    ci_colour : string or list of strings
        The colours that the (optional) confidence intervals should have.
    ci_linewidth : string or list of strings,
        The linewidth of the (optional) confidence intervals.
    dot_colour : string or list of strings
        The marker colour.
    dot_marker : string or list of strings
        The marker for the average agreement between observed and predicted
        risk.
    line_colour : string or list of strings
        The colour of the line connecting the dots.
    line_linestyle : string or list of strings
        The linestyle of the line(s) connecting the dots.
    line_linewidth : string or list of floats
        The linewidth of the line(s) connecting the dots.
    diagonal_colour : str
        The colour of the diagonal line.
    diagonal_linestyle : str
        The linestyle of the diagonal line.
    diagonal_linewidth : float
        The width of the diagonal line.
    curves : `dict` [`str`, `list`] or `None`, default `None`
        A dictionary with list values. The list can have the following entries:
            - The first element should include a np.ndarray where the
                first column represents the y-axis value and the second column
                the x-axis values.
            - The second list entry should be a callable that returns
                predicted y-values in the same order as the observed x-axis
                values. Set this to `None` to simply plots the np.ndarray
                data.
            - The third entry can be used to pass a dictionary to
                The callable function. Set to `None` to skip.
            - The fourth entry can be used to supply a dictionary with
                keyword arguments for ax.plot, set to `None` to skip.
    ax : plt.Axes, default `NoneType`
        A `matplotlib.axes.Axes` instance to which the figure is plotted. If
        not provided, use current axes or create a new one.  Optional.
    figsize : tuple of two floats, default (6, 6),
        The figure size, when ax==None.
    kwargs_*_dict : dict, default `NoneType`
        Optional arguments supplied to the various plotting functions:
            kwargs_ci_dict       --> ax.plot
            kwargs_dot_dict      --> ax.scatter
            kwargs_line_dict     --> ax.plot
            kwargs_diagonal_dict --> ax.axline
    
    Returns
    -------
    figure: plt.Figure
    ax: plt.Axes
    curves : dict
        A dictionary with np.ndarray with observed x-values and predicted
        y-values based on the callable model supplied in `curves`.
    '''
    
    # ################### check input
    is_type(data, (dict, pd.DataFrame), 'data')
    is_type(observed, str, 'observed')
    is_type(predicted, str, 'predicted')
    is_type(ax, (plt.Axes, type(None)), 'ax')
    is_type(lower_observed, (str, type(None)), 'lower_observed')
    is_type(upper_observed, (str, type(None)), 'upper_observed')
    is_type(ci_colour, (str,list, type(None)), 'ci_colour')
    is_type(ci_linewidth, (str, list, type(None)), 'ci_linewidth')
    is_type(dot_marker,(str, list))
    is_type(dot_colour, (str, list))
    is_type(line_colour, (str, list))
    is_type(line_linewidth, (str, list))
    is_type(line_linestyle, (str, list))
    is_type(figsize, tuple)
    is_type(diagonal_linewidth, float)
    is_type(diagonal_colour, str)
    is_type(diagonal_linestyle, str)
    is_type(margins, tuple)
    # map None to empty dict
    kwargs_ci_dict = kwargs_ci_dict or {}
    kwargs_dot_dict = kwargs_dot_dict or {}
    kwargs_line_dict = kwargs_line_dict or {}
    kwargs_diagonal_dict = kwargs_diagonal_dict or {}
    # combined the columns
    columns = [predicted, observed]
    if not lower_observed is None:
        columns = columns + [lower_observed]
    if not upper_observed is None:
        columns = columns + [upper_observed]
    # creating a dictionary if needed
    if not isinstance(data, dict):
        data = {'dataset1': data}
    # testing column content
    [are_columns_in_df(d, columns) for d in data.values()]
    # compare plt params to dict len
    # NOTE if None simply repeat for the number of datasets
    if not ci_colour is None:
        same_len(data, ci_colour, [NamesML.DATA, NamesML.CI_COLOUR])
    else:
        ci_colour = [None] * len(data)
    # NOTE if None simply repeat for the number of datasets
    if not ci_linewidth is None:
        same_len(data, ci_linewidth, [NamesML.DATA,NamesML.CI_LINEWIDTH])
    else:
        ci_linewidth = [None] * len(data)
    same_len(data, dot_colour, [NamesML.DATA,NamesML.DOT_COLOUR])
    same_len(data, dot_marker, [NamesML.DATA,NamesML.DOT_MARKER])
    same_len(data, line_colour, [NamesML.DATA,NamesML.LINE_LINESTYLE])
    same_len(data, line_linewidth, [NamesML.DATA,NamesML.LINE_LINEWIDTH])
    same_len(data, line_linestyle, [NamesML.DATA,NamesML.LINE_LINESTYLE])
    # ################### making lists
    ci_linewidth = string_to_list(ci_linewidth)
    ci_colour = string_to_list(ci_colour)
    dot_marker = string_to_list(dot_marker)
    dot_colour = string_to_list(dot_colour)
    line_colour = string_to_list(line_colour)
    line_linewidth = string_to_list(line_linewidth)
    line_linestyle = string_to_list(line_linestyle)
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # Add the diagonal line, first updating the kwargs
    new_diagonal_dict =\
        _update_kwargs(kwargs_diagonal_dict, lw=diagonal_linewidth,
                       ls=diagonal_linestyle, c=diagonal_colour)
    ax.axline(xy1=(0, 0), slope=1, **new_diagonal_dict,
              )
    # ################### loop over dict
    for idx, (key, val) in enumerate(data.items()):
        # unpack data
        x_bin = val[predicted]
        y_bin = val[observed]
        # set lb and ub to the same y-values, and update based on avail data
        y_bin_lb = val[observed]
        y_bin_ub = val[observed]
        if not lower_observed is None:
            y_bin_lb = val[lower_observed]
        if not upper_observed is None:
            y_bin_ub = val[upper_observed]
        # set confidence intervals
        y_ci = [y_bin_lb, y_bin_ub]
        x_ci = [x_bin, x_bin]
        # add line connecting the dots, first updating the kwargs
        new_line_dict =\
            _update_kwargs(kwargs_line_dict, c=line_colour[idx],
                           linewidth=line_linewidth[idx],
                           linestyle=line_linestyle[idx],
                           )
        ax.plot(x_bin, y_bin, **new_line_dict,
                )
        # plot confidence interval, first updating the kwargs
        new_ci_dict =\
            _update_kwargs(kwargs_ci_dict, c=ci_colour[idx],
                           linewidth=ci_linewidth[idx],
                           )
        ax.plot(x_ci, y_ci, **new_ci_dict,
                )
        # plot dots, first updating the kwargs
        new_dot_dict =\
            _update_kwargs(kwargs_dot_dict, c=dot_colour[idx],
                           marker=dot_marker[idx],
                           )
        ax.scatter(x_bin, y_bin, **new_dot_dict,
                   )
    # ################### add a curve
    curves_res = {}
    if curves is not None:
        for idx, (nam, vals) in enumerate(curves.items()):
            # extract data, model, and kwargs
            curves_data = vals[0]
            curves_mod = vals[1]
            curves_kwargs_mod = vals[2] or {}
            curves_kwargs_plot = vals[3] or {}
            is_type(curves_data, np.ndarray)
            is_type(curves_kwargs_mod, dict)
            is_type(curves_kwargs_plot, dict)
            # sort by x-axis value
            curves_data = curves_data[curves_data[:, 1].argsort()]
            c_x = curves_data[:,1]
            c_y = curves_data[:,0]
            # do we need to fit a model
            if curves_mod is not None:
                y_pred=curves_mod(c_y, c_x, **curves_kwargs_mod)
            else:
                y_pred = c_y
            # plot the model
            curves_kwargs_plot = _update_kwargs(
                update_dict=curves_kwargs_plot,
                c=line_colour[idx],
                linewidth=line_linewidth[idx],
                linestyle=line_linestyle[idx],
            )
            ax.plot(c_x, y_pred, **curves_kwargs_plot,
                    )
            # save predictions
            curves_res[nam] = np.column_stack((y_pred, c_x))
    # ################### set the plot params
    # making sure the axis is square
    # axes_min = min(ax.get_xlim()[0], ax.get_ylim()[0])
    # NOTE this is slightly opinionated thinking that the lower limit should
    # always start at zero.
    axes_max = max(ax.get_xlim()[1], ax.get_ylim()[1])
    ax.set_xlim(0, axes_max)
    ax.set_ylim(0, axes_max)
    # hide the right and top spines
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    # margins around the both x and y
    ax.margins(margins[0], margins[1])
    # ################### return the figure and axis
    return f, ax, curves_res

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Decision Curves
class DecisionCurve(object):
    '''
    Calculates the net benefit for one or more prediction models. Can also
    produce an matplotlib figure, returning the figure and axes for further
    downstream manipulations
    
    Attributes
    ----------
    data : pd.DataFrame
        The provided input data.
    TICK_WIDTH : float, default 0.6
        The width ticks.
    TICK_LAB_SIZE : float, default 4.5
        The fontsize of the tick labels.
    TICK_LEN : float, default 3.0
        The tick length.
    LABEL_FONT_SIZE : float, default 6.0
        The fontsize of the axes labels.
    LABEL_PAD : float, default 1.2
        The padding of the axes labels.
    MODEL_NAMES : list of string
        The names of the available models, including the internally
        generated: `None model` and `All model`.
    NUMBER_OF_MODELS : integer
        The number of available models.
    NET_BENEFIT : pd.DataFrame
        The net benefit table.
    CALCULATED : bool
        Whether the net benefit table has been calculated.
    
    Parameters
    ----------
    data: pd.DataFrame
        A table including one or more columns containing predicted scores
        on the risk scale (i.e., ranging between 0 and 1), and an
        outcome/target column.
    
    Notes
    -----
    The code is based on the `dcurves` python repo [1]_ where the current
    implementation is slightly more `pythonic`. Currently there is no support
    for the survival implementation.
    
    References
    ----------
    .. [1] https://github.com/MSKCC-Epi-Bio/dcurves
    '''
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self,
                 data:pd.DataFrame,
                 ):
        '''
        Copies the data internally.
        '''
        is_df(data)
        self.data = data.copy()
        # adding plotting params
        self.TICK_WIDTH = 0.6
        self.TICK_LAB_SIZE = 4.5
        self.TICK_LEN = 3
        self.LABEL_FONT_SIZE=6
        self.LABEL_PAD=1.2
        self.CALCULATED = False
        self.MODEL_NAMES = None
        self.NUMBER_OF_MODELS = None
        self.NET_BENEFIT = None
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __str__(self):
        return f"DecisionCurve instance with data=\n{self.data.__str__()}"
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __repr__(self):
        return f"DecisionCurve(data=\n{self.data.__repr__()})"
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def calc_rates(data: pd.DataFrame, outcome:str, model:str,
                    thresholds: List[float], prevalence: Union[float,int]
    ) -> pd.DataFrame:
        '''
        Calculates the true and false positive rates per threshold value for
        the supplied models.
        
        Parameters
        ----------
        data: pd.DataFrame
            A dataframe including `outcome` and `model` as a column.
        outcome: str
            Column name in `data` of outcome/target of interest.
        model : str
            Column name from `data` that contain model risk score. Note the
            risk score should contain values between 0 and 1.
        thresholds : list of floats or inters
            The probability values the net benefit will be calculated for.
        prevalence : int or float
            Value that indicates the prevalence among the population, only to
            be specified in case-control situations.
        
        Returns
        -------
        table: pd.core.frame.DataFrame
            A dataframe with the true positives and false positives as columns.
            The index consists of the threshold values.
        
        Notes
        -----
        Code addapted from
        `here <https://github.com/MSKCC-Epi-Bio/dcurves/blob/main/dcurves/dca.py>`_.
        
        Hash: 007c64b
        '''
        
        is_type(outcome, str, 'outcome')
        is_type(model, str, 'model')
        is_type(thresholds, list, 'thresholds')
        is_type(prevalence, (float, int), 'prevalence')
        is_df(data)
        # check if the necessary columns are there
        are_columns_in_df(data, expected_columns=[model, outcome])
        # #### True positives
        selected_rows = data[data[outcome].isin([True])].copy()
        true_outcome = selected_rows[[model]].copy()
        tp_rate = []
        for threshold in thresholds:
            true_tf_above_thresh_count = sum(true_outcome[model] >= threshold)
            tp_rate.append(
                (true_tf_above_thresh_count/len(true_outcome[model])) * prevalence
            )
            # NOTE the above is equivalent to: true_tf_above_thresh_count/n
        # #### False postives
        false_outcome = data[data[outcome].isin([False])][[model]]
        fp_rate = []
        for threshold in thresholds:
            fp_counts = sum(false_outcome[model] >= threshold)
            fp_rate.append(
                fp_counts/len(false_outcome[model]) * (1-prevalence)
            )
        # ### create pandas dataframe
        rates = pd.DataFrame({NamesDC.TP_RATE: tp_rate,
                              NamesDC.FP_RATE: fp_rate},
                             index=thresholds)
        rates.index.name = NamesDC.THRESHOLD
        return rates
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def calc_net_benefit(self,
                         outcome: str, modelnames: Union[str,list],
                         thresholds: Union[List[float],None]=None,
                         harm: Union[None,Dict[str,float]] = None,
                         prevalence: Union[None,float,int] = None,
                         ):
        """
        Decision curve analysis is a method for evaluating and comparing
        prediction models that incorporates clinical consequences.
        
        Parameters
        ----------
        data: pd.DataFrame
            A dataframe including one or more columns containing predicted
            scores on the risk scale (i.e., ranging between 0 and 1), and an
            outcome/target column. Each prediction model (e.g., based on a
            regression or ML) will be univariable evaluated against the
            outcome/target variable. ``_note_`` for scores with values exactly
            0 or 1 `sys.float_info.epsilon` is added or subtracted,
            respectfully.
        outcome: str
            Column name in `data` of outcome/target of interest.
        modelnames : str or list of strings
            Column names from `data` that contain model risk scores or values
        thresholds : list of floats, default `NoneType`
            The probability values the net benefit will be calculated for. If
            `NoneType` will default to a list between 0 and 1 with 100 equally
            spaced values.
        harm : dictionary, default `NoneType`
            An optional dictionary, supplied with a `key` referring tot a
            `modelnames` entry and a float value between 0 and 1. Will be
            skipped if `NoneType`. Harm represents the burden of model might
            entail, and its value is subtracted from the crude net benefit.
        prevalence : int or float, default `NoneType`
            Value that indicates the prevalence among the population, only to
            be specified in case-control situations. Will be skipped if
            `NoneType`.
        
        Returns
        -------
        pd.DataFrame
            Data containing net benefit values for each model, as well as the
            `all` and `none` strategies
        
        Notes
        -----
        Code addapted from:
        `here <https://github.com/MSKCC-Epi-Bio/dcurves/blob/main/dcurves/dca.py>`_
        
        Hash: 007c64b
        """
        # ### check input
        is_type(outcome, str, 'outcome')
        is_type(modelnames, (str, list), 'modelnames')
        is_type(thresholds, (list, type(None), 'threshold'))
        is_type(harm, (dict, type(None)), 'harm')
        is_type(prevalence, (float, int, type(None)), 'prevalence')
        # set modelnames to list if needed
        if isinstance(modelnames, str):
            modelnames = [modelnames]
        # check if the necessary columns are there
        are_columns_in_df(self.data, expected_columns=modelnames + [outcome])
        # set threshold if not supplied
        if thresholds is None:
            thresholds = list(np.linspace(0,1,100, endpoint=False))
        # ### check if supplied values are correct
        # thresholds are within 0 and 1
        mint = min(thresholds); maxt=max(thresholds)
        thresholds_msg=\
            '`thresholds` should be between 0 and 1, the current ' + \
            'min/max: {0}/{1}.'
        if (mint < 0) or (maxt > 1):
            raise ValueError(thresholds_msg.format(mint,maxt))
        # check if score values are within 0 and 1
        non_risk_scores = []
        score_msg=\
            'The following `models` have a value outside of the expect ' +\
            '0 and 1 range: `{0}`.'
        for m in modelnames:
            maxm = np.max(self.data[m])
            minm = np.min(self.data[m])
            # check if outside 0 or 1
            if (maxm > 1) or (minm < 0):
                non_risk_scores = non_risk_scores + [m]
            # check if exactly 0 or 1
            if (maxm == 1) or (minm == 0):
                warnings.warn(
                    '`{}` contains risk(s) of exactly 1 or 0, these will '
                    'be truncated.'.format(m))
                self.data[m]=\
                    [r + sys.float_info.epsilon if r == 0 else r for r in
                     self.data[m]]
                self.data[m]=\
                    [r - sys.float_info.epsilon if r == 1 else r for r in
                     self.fdata[m]]
        if len(non_risk_scores) > 0:
            raise ValueError(score_msg.format(', '.join(non_risk_scores)))
        # ### calculating the prevalence
        if prevalence is None:
            prevalence=np.mean(self.data[outcome])
        # ### calculate true positive rate
        # NOTE 1 loop over the various models and run the calc_rates function
        # NOTE 2 for the 'all' and 'none' models use a run with a score of 1 or 0.
        # NOTE 3 column-bind the results
        self.data[NamesDC.ALL_MODEL] = 1
        self.data[NamesDC.NONE_MODEL] = 0
        modelnames_w_standard = modelnames +\
            [NamesDC.ALL_MODEL, NamesDC.NONE_MODEL]
        rates_dict = {}
        for m in modelnames_w_standard:
            rates_dict[m] = self.calc_rates(self.data, outcome, m, thresholds,
                                            prevalence)
            rates_dict[m][NamesDC.MODEL] = m
            rates_dict[m][NamesDC.THRESHOLD] = rates_dict[m].index
            # add harm
            if harm is not None:
                if m in harm.keys():
                    rates_dict[m][NamesDC.HARM] = harm[m]
                else:
                    rates_dict[m][NamesDC.HARM] = 0
            else:
                rates_dict[m][NamesDC.HARM] = 0
        # make frame
        results = pd.concat(rates_dict, ignore_index=True)
        results.set_index(NamesDC.MODEL, inplace=True)
        # For None model set rates to zero
        # NOTE fix this in the `calc_rates` function
        results.loc[NamesDC.NONE_MODEL, [NamesDC.TP_RATE, NamesDC.FP_RATE]] = 0
        # #### calculate the net benefit
        results[NamesDC.NETBENEFIT] = (
            results[NamesDC.TP_RATE] -\
            (results[NamesDC.THRESHOLD] / (1 - results[NamesDC.THRESHOLD])) *\
            results[NamesDC.FP_RATE] - results[NamesDC.HARM]
        )
        # #### finished
        self.MODEL_NAMES = modelnames + [NamesDC.NONE_MODEL, NamesDC.ALL_MODEL]
        self.NUMBER_OF_MODELS = len(self.MODEL_NAMES)
        self.NET_BENEFIT = results
        self.CALCULATED=True
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def plot(self,
             ax:Union[plt.Axes, None]=None,
             col_dict:Union[None, Dict[str, str]]=None,
             line_dict:Union[None, Dict[str, str]]=None,
             lowess_frac:Union[float, None]=None,
             linewidth:float=0.8,
             figsize:tuple=(6, 6),
             kwargs_lowess:Union[None,Dict[Any,Any]]=None,
             kwargs_plot:Union[None,Dict[Any,Any]]=None,
             ) -> Tuple[plt.Figure, plt.Axes]:
        '''
        Plots a decision curve.
        
        Parameters
        ----------
        col_dict: dict, default `NoneType`
            A dictionary with the model names as keys and the colours as values.
            Set to `Nonetype` to plot each line in black.
        line_dict: dict, default `NoneType`
            A dictionary with the model names as keys and the linetypes as values.
            Set to `Nonetype` to use a solid line for all models.
        ax : plt.axes, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis. Otherwise will internally generate a figure and axes pair.
        lowess_frac: float, default `NoneType`
            Set this to a value between 0 and 1 to use a lowess smoothed
            curve. Set to `NoneType` to use the raw values instead.
        figsize : tuple of two floats, default (6, 6),
            The figure size in inches, when ax==None.
        kwargs_*_dict : dict, default `NoneType`
            Optional arguments supplied:
                kwargs_lowess --> statsmodels.nonparametric.smoothers_lowess
                kwargs_plot   --> ax.plot
        
        Returns
        -------
        figure : plt.Figure
        axes : plt.Axes
        '''
        
        # make sure net_benefit is available
        if self.CALCULATED == False:
            raise RuntimeError('calc_net_benefit must be run before plotting.')
        # #### check input
        is_type(ax, (type(None), plt.Axes), 'ax')
        is_type(line_dict, (type(None), dict), 'line_dict')
        is_type(col_dict, (type(None), dict), 'col_dict')
        is_type(lowess_frac, (float, int, type(None)), 'lowess_frac')
        if line_dict is None:
            line_dict = {j:'-' for j in self.MODEL_NAMES }
        if self.NUMBER_OF_MODELS != len(line_dict):
            raise InputValidationError(
                'Please include a dictionary with exactly {} entries, '
                'to match the number of models. '
                'Current number supplied for `line_dict` is {}.'.format(
                    self.NUMBER_OF_MODELS, len(line_dict)
                )
            )
        if col_dict is None:
            col_dict ={k:'black' for k in self.MODEL_NAMES}
        if self.NUMBER_OF_MODELS != len(col_dict):
            raise InputValidationError(
                'Please include a dictionary with exactly {} entries, '
                'to match the number of models. '
                'Current number supplied for `col_dict` is {}.'.format(
                    self.NUMBER_OF_MODELS, len(col_dict)
                )
            )
        # map None to empty dict
        kwargs_lowess = kwargs_lowess or {}
        kwargs_plot = kwargs_plot or {}
        # #### should we create a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        # #### plot stuff
        self.NET_BENEFIT[NamesDC.COL] = pd.Series(col_dict)
        self.NET_BENEFIT[NamesDC.LTY] = pd.Series(line_dict)
        # how many models are there?
        modelnames = list(self.NET_BENEFIT.index.unique())
        # plot a line per model
        for model in modelnames:
            single_model_df = self.NET_BENEFIT.loc[model]
            X = single_model_df[NamesDC.THRESHOLD].to_numpy()
            Y = single_model_df[NamesDC.NETBENEFIT].to_numpy()
            # do we need to use a lowess
            if lowess_frac is not None:
                new_kwargs_lowess = _update_kwargs(
                    update_dict=kwargs_lowess,
                    return_sorted=False,
                    it=3,
                    frac=lowess_frac,
                )
                Y_PLOT=lowess(Y, X,
                              **new_kwargs_lowess,
                              )
            else:
                Y_PLOT = Y
            # The actual plotting
            new_kwargs_plot = _update_kwargs(
                update_dict=kwargs_plot,
                linestyle=single_model_df[NamesDC.LTY].iloc[0],
                color=single_model_df[NamesDC.COL].iloc[0],
                lw=linewidth,
            )
            ax.plot( X, Y_PLOT,
                    **new_kwargs_plot,
                    )
        # ##### some light tweaks to the axes
        # ticks
        ax.tick_params(axis="x",
                               rotation=0,
                               labelsize=self.TICK_LAB_SIZE,
                               length=self.TICK_LEN,
                               width=self.TICK_WIDTH,
                               )
        ax.tick_params(axis="y",
                               rotation=0,
                               labelsize=self.TICK_LAB_SIZE,
                               length=self.TICK_LEN,
                               width=self.TICK_WIDTH,
                               )
        # limits
        YSPAN=ax.get_ylim()
        YSPAN=np.abs(YSPAN[1] - YSPAN[0])
        ax.set_xlim(0, ax.get_xlim()[1])
        ax.set_ylim(0 - np.max((0.01,0.01*YSPAN)), ax.get_ylim()[1])
        # add lables
        ax.set_ylabel('Net benefit',
                      fontsize=self.LABEL_FONT_SIZE,
                      labelpad=self.LABEL_PAD,
                      )
        ax.set_xlabel('Threshold',
                      fontsize=self.LABEL_FONT_SIZE,
                      labelpad=self.LABEL_PAD,
                      )
        # Hide the right and top spines
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        # ##### returns
        return f, ax

