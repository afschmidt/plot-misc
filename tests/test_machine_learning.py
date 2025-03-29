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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
plt.rcParams.update({'figure.max_open_warning': 0})
VALUES='importance'
LABELS='name'
PRED = 'average_predict_risk'
OBS = 'average_observed_risk'
DC_OUTCOME='Composite outcome'
DC_MODELNAMES=['DCM-PROGRESS', 'maggic (3-years risk of death)']
DC_MODELNAMES2 = DC_MODELNAMES + [NamesDC.NONE_MODEL, NamesDC.ALL_MODEL]
COL_DICT = {k:j for j, k in zip(['orangered', 'blue', 'pink', 'black'],
                                DC_MODELNAMES2)}
LINE_DICT = {k:j for j, k in zip(['--', '--', '-', '-'], DC_MODELNAMES2)}

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
    def test_lollipop_reverse_y(self):
        # data
        data = examples.load_lollipop_data()
        data = data[data[VALUES] > 0]
        # running the function
        _, ax = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            reverse_y=True)
        _, ax2 = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            reverse_y=False)
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
        _, ax = ml.calibration(data, predicted=PRED,
                               observed=OBS,
                               lower_observed='lower_observed_risk',
                               upper_observed='upper_observed_risk',
                               ax=ax)
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
        _, ax = ml.calibration(data, predicted=PRED,
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
        _, ax = ml.calibration(data_dict, predicted=PRED, observed=OBS,
                               ci_colour=None, ci_linewidth=None,
                               dot_marker=DOT_MARK, dot_colour=DOT_COL,
                               line_colour=LINE_COL, line_linestyle=LINE_LS,
                               line_linewidth=LINE_LW,
                               )
        # asserting
        lines=ax.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        assert all(lines[1].get_ydata() == data[OBS].to_numpy())
        assert lines[9].get_c() == 'lightgreen'
        assert lines[9].get_markerfacecolor() == 'lightgreen'
        assert lines[1].get_markerfacecolor() == 'lightcoral'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calibration_kwargs(self):
        # data
        data = examples.load_calibration_bins()
        # make plot
        _, ax = ml.calibration(data, predicted=PRED, observed=OBS,
                               ci_colour=None, ci_linewidth=None,
                               kwargs_dot_dict={'s':100},
                               )
        _, ax2 = ml.calibration(data, predicted=PRED, observed=OBS,
                               ci_colour=None, ci_linewidth=None,
                               kwargs_line_dict={'alpha':0.2},
                               )
        _, ax3 = ml.calibration(data, predicted=PRED, observed=OBS,
                               lower_observed='lower_observed_risk',
                               upper_observed='upper_observed_risk',
                               kwargs_ci_dict={'alpha':0.2},
                               )
        _, ax4 = ml.calibration(data, predicted=PRED, observed=OBS,
                               ci_colour=None, ci_linewidth=None,
                               kwargs_diagonal_dict={'c':'red'},
                               )
        # asserting
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
