"""
testing the `incidencematrix` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.example_data.examples as examples
from matplotlib.colors import to_rgba
from matplotlib.collections import PathCollection
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
    def test_default(self):
        # plotting
        _, ax = imat_plt.draw_incidencematrix(
            data.iloc[::-1].T, fsize=(6,17),
            dot_colour=DOT_COLOUR,
            dot_size=DOT_SIZE,
            tick_lab_size=TICK_LAB_SIZE,
            margins=MARGINS,
            kwargs_scatter_dict={'edgecolor': 'black',
                                 'linewidths':0.8,
                                 }
        )
        # evaluate points
        point0 = ax.collections[0]
        point1 = ax.collections[1]
        assert list(np.round(point1.get_facecolors()[0], 1)) ==\
            [0.8, 0.8, 0.8, 0.9]
        assert list(np.round(point0.get_facecolors()[0], 1)) ==\
            [0.7, 0.1, 0.2, 1.0]
        # evaluate lines
        lines=ax.lines
        assert list(lines[2].get_xdata()) == [0, 1]
        assert lines[0].get_color() == 'lightgrey'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_grid_pos(self):
        """ Testing grid pos `outline` """
        DOT_SIZE = [0,40]
        LW = 0.8
        _, ax = imat_plt.draw_incidencematrix(data.iloc[::-1].T,
                                dot_colour=DOT_COLOUR,
                                dot_size=DOT_SIZE,
                                tick_lab_size=TICK_LAB_SIZE,
                                lw = [1,1],
                                line_colour=['black', 'black'],
                                margins = [0, 0],
                                grid_position='outline',
                                kwargs_scatter_dict={'edgecolor': 'black',
                                                     'linewidths':LW,
                                                     },
                                kwargs_vline_dict={'linestyle': '-',},
                                kwargs_hline_dict={'linestyle': '-',},
                                )
        # ### confirm the dots and lines do not cross
        x_dots = [p.get_offsets()[:, 0] for p in ax.collections if
                  isinstance(p, PathCollection)]
        x_dots = np.concatenate(x_dots)
        vlines = [line for line in ax.lines if
                  line.get_xdata()[0] == line.get_xdata()[1]]
        vline_x = [line.get_xdata()[0] for line in vlines]
        for x in x_dots:
            for v in vline_x:
                assert not np.isclose(x, v), f"Grid line crosses dot at x={x}"
        # ### confirm dot size
        scatter = [c for c in ax.collections if isinstance(c, PathCollection)]
        all_sizes = np.concatenate([s.get_sizes() for s in scatter])
        assert set(all_sizes).issubset(DOT_SIZE), \
            f"Unexpected dot sizes: {all_sizes}"
        # ### Dot edge linewidths
        all_lw = np.concatenate([s.get_linewidths() for s in scatter])
        assert np.allclose(all_lw, LW), f"Unexpected edge linewidths: {edge_lw}"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_size_table(self):
        # Data setup
        data = pd.DataFrame({
            "Col 1": [-1.2, 0.1, 1.5],
            "Col 2": [-0.15, -0.8, 2.0],
        }, index=["Gene A", "Gene B", "Gene C"])
        size_data = pd.DataFrame({
            "Col 1": [0.05, 0.3, 0.04],
            "Col 2": [0.01, 0.15, 0.5],
        }, index=data.index)
        DOT_COLOUR = [
            ("#d62728", -0.2),
            ("#bbbbbb", 0.2),
            ("#1f77b4", np.inf),
        ]
        DOT_SIZE = [
            (150, 0.05),
            (40, 1.0),
        ]
        # Plot
        _, ax = imat_plt.draw_incidencematrix(
            data=data.iloc[::-1].T,
            size_data=size_data.iloc[::-1].T,
            dot_colour=DOT_COLOUR,
            dot_size=DOT_SIZE,
            dot_transparency=[1.0],
            tick_lab_size=(10, 10),
            margins=[0, 0],
            grid_position='outline',
            kwargs_scatter_dict={'edgecolor': 'black', 'linewidths': 1.2},
        )
        # assert size
        scatters = [c for c in ax.collections if isinstance(c, PathCollection)]
        sizes = np.concatenate([s.get_sizes() for s in scatters])
        assert set(sizes) == {s[0] for s in DOT_SIZE},\
            f"Unexpected sizes: {set(sizes)}"
        # assert colours
        face_rgba = np.concatenate([s.get_facecolor() for s in scatters])
        expected_rgba = {tuple(to_rgba(c[0])) for c in DOT_COLOUR}
        observed_rgba = {tuple(c) for c in face_rgba}
        assert observed_rgba.issubset(expected_rgba), \
            f"Unexpected colours: {observed_rgba} not in {expected_rgba}"


