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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
DATA = examples.load_heatmap_data()
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
        fig, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
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
    @pytest.mark.dependency(name='depends1')
    def test_heatmap_wo_colobar(self):
        # plotting
        fig, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
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
    @pytest.mark.dependency(depends=["depends1"])
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
        assert texts[0].get_text() == '{:.1%}'.format(DATA.iloc[0,0])
