"""
testing the `heatmap` module
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import plot_misc.example_data.examples as examples
import plot_misc.heatmap as heatmap
from plot_misc.errors import InputValidationError

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
DATA = examples.load_heatmap_data()
# a binary indicator the same shape as DATA, derived independently of the
# function under test (1 where the absolute value exceeds the global median)
THRESH = np.median(DATA.abs().to_numpy())
IND = (DATA.abs() > THRESH).astype(int)
# CONSTANTS
CMTOINCH = 1/2.54

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# heatmap
class TestHeatmap(object):
    """
    Testing the `heatmap` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_heatmap_w_colobar(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        # plotting heatmap
        im, cbar = heatmap.heatmap(data=DATA, row_labels=DATA.index.to_list(),
                                   col_labels=DATA.columns.to_list(), ax=ax,
                                   cbar_bool=True,
                                   cbar_kw={'location':'top',
                                            'orientation': 'horizontal',
                                            }
                                   )
        # asserting
        assert isinstance(cbar, mpl.colorbar.Colorbar)
        assert (np.array(im.axes.images[0].get_array()) == DATA.to_numpy()).all()
        assert cbar.orientation == 'horizontal'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_heatmap_wo_colobar(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        # plotting heatmap
        im, cbar = heatmap.heatmap(data=DATA, row_labels=DATA.index.to_list(),
                                   col_labels=DATA.columns.to_list(), ax=ax,
                                   cbar_bool=False,
                                   grid_kw={'color':'red',},
                                   aspect='auto',
                                   )
        # asserting
        assert cbar is None
        assert (np.array(im.axes.images[0].get_array()) == DATA.to_numpy()).all()
        assert im.axes.get_aspect() == 'auto'

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# annotate_heatmap
class TestAnnotateHeatmap(object):
    """
    Testing the `annotate_heatmap` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_annotate_heatmap(self):
        # getting an imshow object
        im, _ = heatmap.heatmap(data=DATA,
                                row_labels=DATA.index.to_list(),
                                col_labels=DATA.columns.to_list()
                                )
        # testing annotate_heatmap
        texts = heatmap.annotate_heatmap(im, threshold=2, valfmt="{x:.1%}",
                                         fontsize=12,
                                         horizontalalignment='left',
                                         )
        # assert
        assert len(texts) == DATA.shape[0] * DATA.shape[1]
        assert texts[1].get_text() == '{:.1%}'.format(DATA.iloc[0,1])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_annotate_masked_heatmap(self):
        # annotate a masked heatmap: only indicator==1 cells get text, with no
        # MaskError raised on the masked (background) cells
        im, _ = heatmap.masked_heatmap(data=DATA, indicator=IND,
                                       row_labels=DATA.index.to_list(),
                                       col_labels=DATA.columns.to_list(),
                                       )
        texts = heatmap.annotate_heatmap(im, valfmt="{x:.1f}")
        # only the flagged cells are annotated
        assert len(texts) == int(IND.to_numpy().sum())

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# masked_heatmap
class TestMaskedHeatmap(object):
    """
    Testing the `masked_heatmap` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_two_layers_and_masking(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        im, _ = heatmap.masked_heatmap(data=DATA, indicator=IND,
                                       row_labels=DATA.index.to_list(),
                                       col_labels=DATA.columns.to_list(),
                                       ax=ax,
                                       )
        # two images: a constant background drawn first, masked heatmap on top
        assert len(ax.images) == 2
        background = np.asarray(ax.images[0].get_array())
        assert (background == background.flat[0]).all()
        assert ax.images[1] is im
        # the foreground is masked exactly where indicator == 0
        assert np.ma.is_masked(im.get_array())
        assert (np.ma.getmaskarray(im.get_array()) == (IND.to_numpy() == 0)).all()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_outline_only_on_indicator_cells(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        heatmap.masked_heatmap(data=DATA, indicator=IND,
                               row_labels=DATA.index.to_list(),
                               col_labels=DATA.columns.to_list(),
                               ax=ax,
                               )
        # one outline rectangle per indicator == 1 cell, none on the zeros
        rects = [p for p in ax.patches if isinstance(p, mpl.patches.Rectangle)]
        assert len(rects) == int((IND.to_numpy() == 1).sum())
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_zorder_params(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        heatmap.masked_heatmap(data=DATA, indicator=IND,
                               row_labels=DATA.index.to_list(),
                               col_labels=DATA.columns.to_list(),
                               ax=ax, outline_zorder=5, background_zorder=0,
                               )
        # outline rectangles carry the requested zorder
        rects = [p for p in ax.patches if isinstance(p, mpl.patches.Rectangle)]
        assert rects
        assert all(r.get_zorder() == 5 for r in rects)
        # the background lattice carries the requested zorder
        grid = [t.gridline for t in ax.xaxis.get_minor_ticks()]
        assert grid
        assert all(g.get_zorder() == 0 for g in grid)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_invalid_indicator_raises(self):
        # a shape mismatch is rejected
        with pytest.raises(InputValidationError):
            heatmap.masked_heatmap(data=DATA, indicator=IND.iloc[:, :-1],
                                   row_labels=DATA.index.to_list(),
                                   col_labels=DATA.columns.to_list(),
                                   )
        # a non-binary indicator is rejected
        bad_ind = IND.copy()
        bad_ind.iloc[0, 0] = 5
        with pytest.raises(InputValidationError):
            heatmap.masked_heatmap(data=DATA, indicator=bad_ind,
                                   row_labels=DATA.index.to_list(),
                                   col_labels=DATA.columns.to_list(),
                                   )

