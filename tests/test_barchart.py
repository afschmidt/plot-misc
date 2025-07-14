"""
testing the `barchart` module
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.barchart as barchart
from plot_misc.example_data import examples

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
COLOURS = ['red', 'green', 'orange']
EDGECOLOUR = 'black'
LABELS = 'labels'
TABLE = examples.load_barchart_data()
TABLE_T = TABLE.T.copy()
TABLE_T[LABELS] = TABLE.T.index
GROUP = examples.load_groupbar_data()
GR_COL = ['white'] + COLOURS
GR_LAB = 'Age'
GENES = ['Control', 'AP4S1', 'LRRC39', 'ZFAND4']
COLS = [x + '_mean' for x in GENES]
ERRS = [x + '_std' for x in GENES]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# stack_bar
class TestStackBar(object):
    """
    Testing functions for the `stack_bar` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        _, ax = barchart.stack_bar(TABLE_T, label=LABELS,
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
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_wo_ax(self):
        # running the function
        _, ax = barchart.stack_bar(TABLE_T, label=LABELS,
                                   columns=TABLE_T.columns[:-1].to_list(),
                                   wd=0.6, edgecolor=EDGECOLOUR, colours=COLOURS,
                                   horizontal=True, **{'linewidth':2},
                                   )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert all(p.get_height() == 0.6 for p in patch)
        assert all(p.get_linewidth() == 2.0 for p in patch)
        assert len([p.get_x() for p in patch]) ==\
            TABLE_T.iloc[:,:-1].shape[0] * TABLE_T.iloc[:,:-1].shape[1]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_error(self):
        TABLE_N = TABLE_T.copy()
        TABLE_N.iloc[1,1] = np.nan
        # input data with nan
        with pytest.raises(ValueError):
            _, _ = barchart.stack_bar(TABLE_N, label=LABELS,
                                       columns=TABLE_T.columns[:-1].to_list(),
                                       )
        # insufficient colours
        with pytest.raises(AttributeError):
            _, _ = barchart.stack_bar(TABLE_T, label=LABELS,
                                       columns=TABLE_T.columns[:-1].to_list(),
                                       )

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
        _, ax = barchart.stack_bar(TABLE_T, label=LABELS,
                                   columns=TABLE_T.columns[:-1].to_list(),
                                   wd=0.6, edgecolor=EDGECOLOUR, colours=COLOURS,
                                   horizontal=True,
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
# total_bar
class TestTotalBar(object):
    """
    Testing functions for the `total_bar` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        _, ax = barchart.subtotal_bar(TABLE_T, label=LABELS,
                                subtotal_col=TABLE_T.columns.to_list()[1],
                                total_col=TABLE_T.columns.to_list()[2],
                                wd=(0.6, 0.4),
                                ax=ax, subtotal_kwargs_dict={'linewidth':2},
                                )
        _, ax2 = barchart.subtotal_bar(TABLE_T, label=LABELS,
                                total_col=TABLE_T.columns.to_list()[2],
                                wd=(0.1,),
                                total_kwargs_dict={'linewidth':0.8},
                                )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        patch2=ax2.patches
        assert patch[0].get_width() == 0.6
        assert patch[5].get_width() == 0.4
        assert patch[5].get_linewidth() == 2.0
        assert patch2[0].get_width() == 0.1
        assert patch2[0].get_linewidth() == 0.8
        assert len([p.get_y() for p in patch2]) ==\
            TABLE_T.iloc[:,:-1].shape[0]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# bar
class TestBar(object):
    """
    Testing functions for the `bar` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        _, ax = barchart.bar(TABLE_T, label=LABELS,
                             column=TABLE_T.columns.to_list()[0],
                             error_max=TABLE_T.columns.to_list()[1],
                             error_min=TABLE_T.columns.to_list()[2],
                             wd=0.2, edgecolour=EDGECOLOUR, colours=COLOURS,
                             ax=ax, kwargs_bar={'linewidth':1.2},
                             )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_width() == 0.2
        assert patch[1].get_linewidth() == 1.2
        assert len([p.get_y() for p in patch]) == TABLE_T.shape[0]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_horizontal(self):
        # running the function
        _, ax = barchart.bar(TABLE_T, label=LABELS,
                             column=TABLE_T.columns.to_list()[0],
                             error_max=TABLE_T.columns.to_list()[1],
                             error_min=TABLE_T.columns.to_list()[2],
                             wd=0.2, edgecolour=EDGECOLOUR, colours=COLOURS,
                             horizontal=True,
                             kwargs_bar={'linewidth':1.2},
                             )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_height() == 0.2
        assert patch[1].get_linewidth() == 1.2
        assert len([p.get_x() for p in patch]) == TABLE_T.shape[0]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_error(self):
        TABLE_N = TABLE_T.copy()
        TABLE_N.iloc[1,1] = np.nan
        with pytest.raises(ValueError):
            _, _ = barchart.bar(TABLE_N, label=LABELS,
                                column=TABLE_T.columns.to_list()[0],
                                )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# bar
class TestGroupBar(object):
    """
    Testing functions for the `group_bar` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # supplying external axes
        fig, ax = plt.subplots(1, figsize=(1, 1))
        # running the function
        _, ax = barchart.group_bar(GROUP, label=GR_LAB,
                                columns=COLS,
                                wd=0.6, edgecolour=EDGECOLOUR, colours=GR_COL,
                                ax=ax, kwargs_bar={'linewidth':1},
                                )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_width() == 0.6
        assert patch[1].get_linewidth() == 1
        assert len([p.get_y() for p in patch]) == GROUP.shape[0] * len(GENES)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_horizontal(self):
        # running the function
        _, ax = barchart.group_bar(GROUP, label=GR_LAB,
                                   columns=COLS,
                                   wd=0.6, edgecolour=EDGECOLOUR, colours=GR_COL,
                                   horizontal=True,
                                   kwargs_bar={'linewidth':1},
                                   )
        # asserting - getting the raw data is more difficult here will confirm
        # the length instead
        patch=ax.patches
        assert patch[0].get_height() == 0.6
        assert patch[1].get_linewidth() == 1
        assert len([p.get_x() for p in patch]) == GROUP.shape[0] * len(GENES)
