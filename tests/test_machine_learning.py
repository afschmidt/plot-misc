"""
testing the `machine_learning` module
"""
import pandas as pd
import matplotlib.pyplot as plt
import plot_misc.machine_learning as ml
from plot_misc.constants import UtilsNames as UNames
from plot_misc.example_data import examples


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
VALUES='importance'
LABELS='name'
PRED = 'average_predict_risk'
OBS = 'average_observed_risk'
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
            kwargs_lines_dict={'linestyles': '--'},
        )
        _, ax2 = ml.lollipop(
            values=data[VALUES].to_numpy(), labels=data[LABELS].to_numpy(),
            kwargs_lines_dict={'alpha': 0.2},
        )
        # asserting
        line=ax.lines[0]
        line2=ax2.lines[0]
        assert all(line.get_xdata() == data[VALUES].to_numpy())
        assert all(line2.get_xdata() == data[VALUES].to_numpy())

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing the calibration function
class TestClibration(object):
    """
    Testing functions for the `lollipop` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_supplied_axes(self):
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
    def test_lollipop_without_axes(self):
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
    def test_lollipop_multiple_datasets(self):
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
        DOT_MARK = ['o', 'o']
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
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_lollipop_multiple_datasets(self):
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
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        lines=ax2.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        lines=ax3.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())
        lines=ax4.lines
        assert all(lines[1].get_xdata() == data[PRED].to_numpy())



