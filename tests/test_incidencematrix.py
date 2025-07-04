"""
testing the `incidencematrix` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.example_data.examples as examples
from plot_misc import incidencematrix as imat_plt

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
DOT_COLOUR = [('#C4C4C4', 0), ('#B12137', np.inf)]
DOT_SIZE = [10, 40]
TICK_LAB_SIZE = [10, 10]
MARGINS = [0.060, 0.025]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# data
data = examples.load_incidence_matrix_data()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# plot_forest
class TestIncidenceMatrix(object):
    """
    Testing the `incidencematrix` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_incidencematrix(self):
        # plotting
        _, ax = imat_plt.draw_incidencematrix(
            data.iloc[::-1].T, fsize=(6,17),
            dot_colour=DOT_COLOUR,
            dot_size=DOT_SIZE,
            tick_lab_size=TICK_LAB_SIZE,
            margins=MARGINS,
            kwargs_scatter_dict={'edgecolor': ['black'],
                                 'linewidths':0.8,
                                 }
        )
        # evaluate points
        point0 = ax.collections[0]
        point1 = ax.collections[1]
        assert list(np.round(point0.get_facecolors()[0], 1)) == [0.8, 0.8, 0.8, 0.9]
        assert list(np.round(point1.get_facecolors()[0], 1)) == [0.7, 0.1, 0.2, 1.0]
        # evaluate lines
        lines=ax.lines
        assert list(lines[2].get_xdata()) == [0, 1]
        assert lines[0].get_color() == 'lightgrey'
