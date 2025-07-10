"""
testing the `machine_learning` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.machine_learning as ml
from plot_misc.constants import (
    UtilsNames as UNames,
    NamesDecisionCurves as NamesDC,
)
from plot_misc.example_data import examples
from statsmodels.nonparametric.smoothers_lowess import lowess

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
plt.rcParams.update({'figure.max_open_warning': 0})
VALUES='importance'
LABELS='name'
PRED = 'average_predict_risk'
OBS = 'average_observed_risk'
DC_OUTCOME='Composite outcome'
DC_MODELNAMES=['DCM-PROGRESS', 'maggic (3-years risk of death)']
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing the lollipop function
class TestLollipop(object):
    """
    Testing functions for the `lollipop` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_supplied_axes(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            ax=ax)
        # asserting
        line=ax.lines[0]
        assert all(line.get_xdata() == data[VALUES].to_numpy())
        assert all(
            [i.get_text() in  data[LABELS].to_numpy() for i in
             ax.get_yticklabels()[0::]]
        )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_without_axes(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy())
        # asserting
        line=ax.lines[0]
        assert all(line.get_xdata() == data[VALUES].to_numpy())
        assert all(
            [i.get_text() in  data[LABELS].to_numpy() for i in
             ax.get_yticklabels()[0::]]
        )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_vertical(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            vertical=True,)
        # asserting
        line=ax.lines[0]
        assert all(line.get_ydata() == data[VALUES].to_numpy())
        assert all(
            [i.get_text() in  data[LABELS].to_numpy() for i in
             ax.get_xticklabels()[0::]]
        )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_reverse_y(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            reverse_feature_order=True)
        _, ax2 = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            reverse_feature_order=False)
        # asserting
        line=ax.lines[0]
        assert all(line.get_xdata() == data[VALUES].to_numpy())
        assert all(
            [i.get_text() in  data[LABELS].to_numpy() for i in
             ax.get_yticklabels()[0::]]
        )
        # note the ylims get inverted by `reverse_y`, not the positions
        assert ax.get_ylim()[0] == ax2.get_ylim()[1]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_kwargs(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            kwargs_lines_dict={'linewidth': 22},
        )
        _, ax2 = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            kwargs_plot_dict={'marker': 's'},
        )
        # asserting
        line=ax.lines[0]
        collect = ax.collections[0]
        line2=ax2.lines[0]
        assert all(line.get_xdata() == data[VALUES].to_numpy())
        assert collect.get_linewidth() == 22
        assert all(line2.get_xdata() == data[VALUES].to_numpy())
        assert line2.get_marker() == 's'

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing the calibration function
class TestClibration(object):
    """
    Testing functions for the `calibration` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calibration_supplied_axes(self):
        # data
        data = examples.load_calibration_bins()
        fig, ax = plt.subplots(1, figsize=(1,1))
        # make plot
        ml.Calibration(data, ax).plot(predicted=PRED,
                                      observed=OBS,
                                      lower_observed='lower_observed_risk',
                                      upper_observed='upper_observed_risk',
                                      )
        # asserting
        lines=ax.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert all(lines[1].get_ydata() == data[OBS].to_numpy())
        # evaluate confidence interval (plot per y and x pairs)
        assert all(lines[2].get_ydata() == data.iloc[0, 2:4].to_numpy())
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calibration_without_axes(self):
        # data
        data = examples.load_calibration_bins()
        # make plot
        cal_obj = ml.Calibration(data).plot(
            predicted=PRED,
            observed=OBS,
            lower_observed='lower_observed_risk',
            upper_observed='upper_observed_risk',
        )
        # asserting
        ax = cal_obj.ax
        lines=ax.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert all(lines[1].get_ydata() == data[OBS].to_numpy())
        # evaluate confidence interval (plot per y and x pairs)
        assert all(lines[2].get_ydata() == data.iloc[0, 2:4].to_numpy())
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calibration_multiple_lines(self):
        # data
        data = examples.load_calibration_bins()
        data2 = data.copy()
        data2[['average_predict_risk', 'average_observed_risk']] = \
             data2[['average_predict_risk', 'average_observed_risk']] + 0.04
        data_dict = {'one': data, 'two': data2}
        # need to expand the mark-up
        LINE_COL = ['lightcoral', 'lightgreen']
        LINE_LW = [1.5, 1.5]
        LINE_LS = ['--', '--']
        DOT_COL = ['lightcoral', 'lightgreen']
        DOT_MARK = ['s', 'o']
        # make plot
        cal_obj = ml.Calibration(data_dict).plot(
            predicted=PRED, observed=OBS,
            ci_colour=None, ci_linewidth=None,
            dot_marker=DOT_MARK, dot_colour=DOT_COL,
            line_colour=LINE_COL, line_linestyle=LINE_LS,
            line_linewidth=LINE_LW,
        )
        # asserting
        ax = cal_obj.ax
        lines=ax.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert all(lines[1].get_ydata() == data[OBS].to_numpy())
        assert any(line.get_c() == 'lightgreen' for line in ax.lines)
        marker_colours = [line.get_markerfacecolor() for line in ax.lines]
        assert any(c == 'lightgreen' for c in marker_colours)
        assert any(c == 'lightcoral' for c in marker_colours)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calibration_kwargs(self):
        # data
        data = examples.load_calibration_bins()
        # make plot
        cal_obj1 = ml.Calibration(data).plot(
            predicted=PRED, observed=OBS,
            ci_colour=None, ci_linewidth=None,
            kwargs_dot_dict={'s':100},
        )
        cal_obj2 = ml.Calibration(data).plot(
            predicted=PRED, observed=OBS,
            ci_colour=None, ci_linewidth=None,
            kwargs_line_dict={'alpha':0.2},
        )
        cal_obj3 = ml.Calibration(data).plot(
            predicted=PRED, observed=OBS,
            lower_observed='lower_observed_risk',
            upper_observed='upper_observed_risk',
            kwargs_ci_dict={'alpha':0.2},
        )
        cal_obj4 = ml.Calibration(data).plot(
            predicted=PRED, observed=OBS,
            ci_colour=None, ci_linewidth=None,
            kwargs_diagonal_dict={'c':'red'},
        )
        # asserting
        ax = cal_obj1.ax
        ax2 = cal_obj2.ax
        ax3 = cal_obj3.ax
        ax4 = cal_obj4.ax
        lines=ax.lines
        collect=ax.collections
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert collect[0].get_sizes() == 100
        lines=ax2.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert lines[1].get_alpha() == 0.2
        lines=ax3.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert lines[1].get_alpha() is None # the non-ci lines are not affected.
        assert lines[2].get_alpha() == 0.2
        lines=ax4.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert lines[0].get_c() == 'red'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_curve(self):
        data = examples.load_calibration_bins()
        data_curve = examples.load_calibration_data()
        # create plot without lines
        cal_obj = cal_plot = ml.Calibration(data).plot(
            predicted='average_predict_risk',
            observed='average_observed_risk',
            line_linestyle=' ')
        # call add_curves - testing both the line_colour param and the kwargs
        cal_plot.add_curves(
            data=data_curve,
            smoother=lowess,
            line_colour='slategrey',
            kwargs_smoother={
                "return_sorted": False, "it": 2, "frac": 1/5
            },
            kwargs_curve={
                'linewidth': 1.5,
                'zorder': 0
            }
        )
        # collect lines
        ax = cal_obj.ax
        lines = ax.lines
        # find the newly added 'slategrey' curve
        smoothed_line_col = [
            line for line in lines
            if line.get_color() == 'slategrey'
        ]
        smoothed_line_wd = [
            line for line in lines
            if np.isclose(line.get_linewidth(), 1.5)
        ]
        # check that at least one such line exists
        assert len(smoothed_line_col) >= 1
        assert len(smoothed_line_wd) >= 1

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing the Decision Curve class
class TestDecisionCurve(object):
    """
    Testing functions for the `DecisionCurve` class.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_decisioncurve_calc_net_benefit(self):
        data = examples.load_net_benefit_data()
        nb_obj = ml.DecisionCurve(data)
        # basic application
        nb_obj.calc_net_benefit(
            outcome=DC_OUTCOME, modelnames=DC_MODELNAMES,
            thresholds=list(np.linspace(0.0, 0.3, 100))
        )
        assert nb_obj.data.shape[1] == 5
        assert NamesDC.ALL_MODEL in nb_obj.data.columns
        assert nb_obj.NET_BENEFIT.mean(axis=0).round(2).to_list()  ==\
            [0.08, 0.46, 0.15, 0.0, 0.01]
        # with harms and prevalence
        nb_obj.calc_net_benefit(
            outcome=DC_OUTCOME, modelnames=DC_MODELNAMES,
            thresholds=list(np.linspace(0.0, 0.3, 100)),
            prevalence=0.2,
            harm={DC_MODELNAMES[0]: 0.05},
        )
        assert nb_obj.NET_BENEFIT.shape == (400, 5)
        assert NamesDC.NONE_MODEL in nb_obj.data.columns
        assert nb_obj.NET_BENEFIT.mean(axis=0).round(2).to_list()  ==\
            [0.14, 0.42, 0.15, 0.01, 0.06]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_decisioncurve_plot_without_axes(self):
        # input data
        DC_MODELNAMES2 = DC_MODELNAMES + [NamesDC.NONE_MODEL, NamesDC.ALL_MODEL]
        LINE_DICT = {k:j for j, k in zip(['--', '--', '-', '-'], DC_MODELNAMES2)}
        COL_DICT = {k:j for j, k in zip(['orangered', 'blue', 'pink', 'black'],
                                        DC_MODELNAMES2)}
        data = examples.load_net_benefit_data()
        nb_obj = ml.DecisionCurve(data)
        # basic plot
        nb_obj.calc_net_benefit(
            outcome=DC_OUTCOME, modelnames=DC_MODELNAMES,
            thresholds=list(np.linspace(0.0, 0.3, 100))
        )
        f, ax = nb_obj.plot(figsize=(3,3),
                            col_dict=COL_DICT,
                            line_dict=LINE_DICT,
                            linewidth=1, lowess_frac=1/3,
                            kwargs_lowess={'it':3},
                            )
        assert len(ax.lines) == 4
        assert np.round(np.max(ax.lines[1].get_ydata()), 2) == 0.12
        assert np.round(np.min(ax.lines[1].get_ydata()), 2) == 0.00
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_decisioncurve_plot_with_axes(self):
        data = examples.load_net_benefit_data()
        nb_obj = ml.DecisionCurve(data)
        # basic plot
        fig, ax = plt.subplots(1, figsize=(1, 1))
        nb_obj.calc_net_benefit(
            outcome=DC_OUTCOME, modelnames=DC_MODELNAMES,
            thresholds=list(np.linspace(0.0, 0.3, 100))
        )
        _, _ = nb_obj.plot(ax=ax)
        assert len(ax.lines) == 4
        assert np.round(np.max(ax.lines[1].get_ydata()), 2) == 0.12
        assert np.round(np.min(ax.lines[1].get_ydata()), 2) == -0.01
        assert ax.lines[1].get_linewidth() == 0.80
