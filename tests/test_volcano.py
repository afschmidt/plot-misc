"""
testing the `volcano` module
"""
import pytest
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import plot_misc.example_data.examples as examples
from plot_misc.volcano import plot_volcano as plt_volcano

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
CMTOINCH = 1/2.54
# The y, x axes labels,title, point size, text size, ytick size, x ticks size
ANNOT_SIZE = [6.0, 6.0, 10.0, 15.0, 3.4, 14.0, 14.0]
# load data
DATA = examples.load_volcano_data()
# limits
SIGNIFICANCE = DATA['multiple_testing_threshold'].unique()[0]
YLIM = [0, 22] # adding some space to the top
XLIM = [-800,800]
LABEL = 'WFDC1'
POINT = 'point'

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# plot_forest
class TestPlotVolcano(object):
    """
    Testing the `plot_volcano` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_volcano(self):
        # plotting
        fig, ax = plt.subplots(1, 1, figsize=(12 * CMTOINCH, 12 * CMTOINCH))
        _, ax = plt_volcano(DATA,
                            y_column='pvalue_log10', x_column='point',
                            ylim = YLIM, msize=ANNOT_SIZE[3],
                            alpha=SIGNIFICANCE, ax=ax,
                            )
        # check the points are correct
        assert list(DATA['pvalue_log10'])[1] in\
            ax.collections[1].get_offsets().data[:,1]
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[0].get_xdata()) == [0, 0]
        assert lines[0].get_color() == 'lightcoral'
        assert lines[0].get_zorder() == 1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_volcano_wlabels(self):
        # adding label data
        data2 = DATA.copy()
        # data2['label'] = np.nan
        data2.loc['9316_67_3_WFDC1',  'label'] = LABEL
        index = ['9316_67_3_WFDC1']
        # plotting
        fig, ax = plt.subplots(1, 1, figsize=(12 * CMTOINCH, 12 * CMTOINCH))
        _, ax = plt_volcano(data2,
                            y_column='pvalue_log10', x_column='point',
                            ylim = YLIM, msize=ANNOT_SIZE[3],
                            alpha=SIGNIFICANCE, ax=ax,
                            point_label='label',
                            index_label=index,
                            lsize=20,
                            adjust=True,
                            label_kwargs_dict={
                                'arrowprops':dict(arrowstyle='->', color='red')
                            },
                            )
        # check if label is there
        text = ax.axes.texts[-1]
        assert text.get_text() == LABEL
        # check the points are correct
        assert list(data2['pvalue_log10'])[0] in\
            ax.collections[1].get_offsets().data[:,1]
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[0].get_xdata()) == [0, 0]
        assert lines[0].get_color() == 'lightcoral'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_volcano_warning(self):
        with pytest.warns(UserWarning):
            _ = plt_volcano(DATA,
                            y_column='pvalue_log10', x_column='point',
                            ylim = YLIM, msize=ANNOT_SIZE[3],
                            alpha=SIGNIFICANCE,
                            adjust=True,
                            )
        with pytest.raises(IndexError):
            _ = plt_volcano(DATA,
                            y_column='pvalue_log10', x_column='point',
                            ylim = YLIM, msize=ANNOT_SIZE[3],
                            alpha=SIGNIFICANCE,
                            adjust=True,
                            point_label='wrong',
                            )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_c_col(self):
        # data with a literal-colour column so facecolors are assertable
        data3 = DATA.copy()
        data3['point_col'] = 'blue'
        expected_rgba = to_rgba('blue')
        # plotting works: c_col drives per-point colour, and using it
        # alongside the default col_sgnd/col_nsgnd raises a warning
        fig, ax = plt.subplots(1, 1, figsize=(12 * CMTOINCH, 12 * CMTOINCH))
        with pytest.warns(UserWarning):
            _, ax = plt_volcano(data3,
                                y_column='pvalue_log10', x_column='point',
                                ylim = YLIM, msize=ANNOT_SIZE[3],
                                alpha=SIGNIFICANCE, ax=ax,
                                c_col='point_col',
                                )
        # check the points are correct
        assert list(data3['pvalue_log10'])[1] in\
            ax.collections[1].get_offsets().data[:,1]
        # check the colour values were taken from `point_col`
        # (non-significant points get `transparency_ns` applied to alpha)
        assert tuple(ax.collections[0].get_facecolors()[0]) == expected_rgba
        assert tuple(ax.collections[1].get_facecolors()[0]) ==\
            to_rgba('blue', alpha=0.6)
        # warning is suppressed when col_sgnd/col_nsgnd are set to None
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            _ = plt_volcano(data3,
                            y_column='pvalue_log10', x_column='point',
                            ylim = YLIM, msize=ANNOT_SIZE[3],
                            alpha=SIGNIFICANCE,
                            c_col='point_col', col_sgnd=None, col_nsgnd=None,
                            )

