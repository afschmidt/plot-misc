"""
testing the `volcano` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
LABEL = ['WFDC1']
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
        list(DATA['pvalue_log10'])[1] in ax.collections[1].get_offsets().data[:,1]
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[0].get_xdata()) == [0, 0]
        assert lines[0].get_color() == 'lightcoral'
        assert lines[0].get_zorder() == 1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_volcano_wlabels(self):
        # adding label data
        data2 = DATA.copy()
        data2['label'] = np.nan
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
                            )
        # check if label is there
        text = ax.axes.texts.pop()
        assert text.get_text() == LABEL[0]
        # check the points are correct
        list(data2['pvalue_log10'])[0] in ax.collections[1].get_offsets().data[:,1]
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[0].get_xdata()) == [0, 0]
        assert lines[0].get_color() == 'lightcoral'
