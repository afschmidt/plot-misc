#!/usr/bin/env python3
"""
testing the `barchart` module
"""
import pandas as pd
import matplotlib.pyplot as plt
import plot_misc.barchart as barchart
from plot_misc.constants import UtilsNames as UNames
from plot_misc.example_data import examples

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
COLOURS = ['red', 'green', 'orange']
EDGECOLOUR = 'black'
LABELS = 'labels'
TABLE = examples.load_barchart_data()
TABLE_T = TABLE.T.copy()
TABLE_T[LABELS] = TABLE.T.index

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# stack_bar
class TestStackBar(object):
    """
    Testing functions for the `stack_bar` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_stack_bar(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        ax = barchart.stack_bar(TABLE_T, label=LABELS,
                                columns=TABLE_T.columns[:-1].to_list(),
                                wd=0.6, edgecolor=EDGECOLOUR, colours=COLOURS,
                                ax=ax, **{'linewidth':2},
                                )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_width() == 0.6
        assert patch[1].get_linewidth() == 2.0
        assert len([p.get_y() for p in patch]) ==\
            TABLE_T.iloc[:,:-1].shape[0] * TABLE_T.iloc[:,:-1].shape[1]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# stack_bar horizontal
class TestStackBarH(object):
    """
    Testing functions for the `stack_barh` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_stack_barh(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        ax = barchart.stack_barh(TABLE_T, label=LABELS,
                                columns=TABLE_T.columns[:-1].to_list(),
                                wd=0.6, edgecolor=EDGECOLOUR, colours=COLOURS,
                                ax=ax, **{'linewidth':2},
                                )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_height() == 0.6
        assert patch[1].get_linewidth() == 2.0
        assert len([p.get_y() for p in patch]) ==\
            TABLE_T.iloc[:,:-1].shape[0] * TABLE_T.iloc[:,:-1].shape[1]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# bar
class TestBar(object):
    """
    Testing functions for the `stack_barh` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_bar(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        ax = barchart.bar(TABLE_T, label=LABELS,
                                column=TABLE_T.columns.to_list()[0],
                                wd=0.2, edgecolor=EDGECOLOUR, colours=COLOURS,
                                ax=ax, **{'linewidth':1.2},
                                )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_width() == 0.2
        assert patch[1].get_linewidth() == 1.2
        assert len([p.get_y() for p in patch]) == TABLE_T.shape[0]

