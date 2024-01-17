"""
testing the `pychart` module
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import plot_misc.example_data.examples as examples
import plot_misc.pychart as pychart

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
DATA = examples.load_pychart_data()
# CONSTANTS
CMTOINCH = 1/2.54
genes = ['PKP2', 'MYL2', 'JUP', 'DSC2', 'DSG2', 'TTN', 'DES', 'DSP', 'PLN',
       'RBM20', 'BAG3']


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# pychart
class TestPychart(object):
    """
    Testing the `pychart` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_pychart(self):
        # plotting
        fig, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        # plotting pychart
        fig, ax = pychart.pychart(DATA, "HCM", genes, colors=['red', 'blue', 'green', 'yellow', 'purple', 'lightblue', 'orange'], smaller=0.5,  title_kwargs={'fontsize': 12, 'y':1.05,'fontweight': 'bold'})
        # asserting
        assert isinstance(fig, plt.Figure)
        assert ax.get_title() == "HCM"

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# pychart grid
class TestPyChartGrid(object):
    """
    Testing the `pychart_grid` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_pychart_grid(self):
        # Load example data
        df = examples.load_pychart_data()
        genes = ['PKP2', 'MYL2', 'JUP', 'DSC2', 'DSG2', 'TTN', 'DES', 'DSP', 'PLN',
                'RBM20', 'BAG3']

        # Plotting
        fig, axes = pychart.pychart_grid(df, ["HCM", "DCM"], genes, num_columns=1,
                                         title_kwargs={'fontsize': 12, 'y': 1.1, 'fontweight': 'bold'},
                                         subplots_adjust_kwargs={'hspace': 0.2})
        # Asserting
        assert isinstance(fig, plt.Figure)
        assert len(axes) == 2
        assert axes[0].get_title() == "Distribution for HCM"
        assert axes[1].get_title() == "Distribution for DCM"




