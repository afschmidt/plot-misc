"""
testing the `incidencematrix` module
"""
import pytest
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
class TestIncidenceMatrix(object):
    """
    Testing the `incidencematrix` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # plotting
        _, ax = imat_plt.draw_incidencematrix(
            data, fsize=(6,17),
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
        _, ax = imat_plt.draw_incidencematrix(data,
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
            data=data,
            size_data=size_data,
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
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_custom_coordinates(self):
        """Testing custom x and y coordinates"""
        data = pd.DataFrame({
            "Col 1": [0, 1],
            "Col 2": [1, 0],
        }, index=["Row A", "Row B"])
        
        # Custom coordinates with non-uniform spacing
        x_coords = [0, 5]
        y_coords = [0, 3]
        
        _, ax = imat_plt.draw_incidencematrix(
            data,
            x_coords=x_coords,
            y_coords=y_coords,
            dot_colour=DOT_COLOUR,
            dot_size=DOT_SIZE,
            tick_lab_size=TICK_LAB_SIZE,
            margins=MARGINS,
        )
        
        # Get all scatter points
        scatters = [c for c in ax.collections if
                    isinstance(c, PathCollection)]
        all_offsets = np.concatenate([s.get_offsets() for s in scatters])
        
        # Extract unique x and y coordinates from plotted points
        unique_x = np.unique(all_offsets[:, 0])
        unique_y = np.unique(all_offsets[:, 1])
        
        # Verify coordinates match our custom values
        assert np.allclose(unique_x, x_coords), \
            f"Expected x coords {x_coords}, got {unique_x}"
        assert np.allclose(unique_y, y_coords), \
            f"Expected y coords {y_coords}, got {unique_y}"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_custom_coordinates_error(self):
        """Testing error when coordinate dimensions do not match data"""
        data = pd.DataFrame({
            "Col 1": [0, 1],
            "Col 2": [1, 0],
        }, index=["Row A", "Row B"])
        
        # Test x_coords mismatch (data has 2 rows, but 3 x_coords)
        x_coords_wrong = [0, 5, 10]
        y_coords_correct = [0, 3]
        
        with pytest.raises(ValueError, match=r"Length of x_coords.*must "
                                             r"match number of rows"):
            imat_plt.draw_incidencematrix(
                data,
                x_coords=x_coords_wrong,
                y_coords=y_coords_correct,
                dot_colour=DOT_COLOUR,
            )
        
        # Test y_coords mismatch (data has 2 columns, but 3 y_coords)
        x_coords_correct = [0, 5]
        y_coords_wrong = [0, 3, 10]
        
        with pytest.raises(ValueError, match=r"Length of y_coords.*must "
                                             r"match number of columns"):
            imat_plt.draw_incidencematrix(
                data,
                x_coords=x_coords_correct,
                y_coords=y_coords_wrong,
                dot_colour=DOT_COLOUR,
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestMapAttributes(object):
    """
    Testing the `_map_attributes` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        data = pd.DataFrame([[0.2, 0.6], [1.2, 2.5]])
        rules = [('grey', 0.5), ('black', 1.5), ('red', 3.0)]
        result = imat_plt._map_attributes(data, rules)
        expected = np.array([['grey', 'black'],
                             ['black', 'red']], dtype=object)
        assert np.array_equal(result, expected)
        assert list(result.flatten()) == ['grey', 'black', 'black', 'red']
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_with_nan_output(self):
        """ confirming nan's are returned for values that are not included in
            the interval (using break_limits[0] == 0.0
        """
        data = pd.DataFrame([[-0.5, 0.4], [1.6, 3.1]])
        rules = [('grey', 0.5), ('black', 1.5), ('red', 3.0)]
        result = imat_plt._map_attributes(data, rules,
                                          break_limits=(0.0, np.inf))
        expected = np.array([[np.nan, 'grey'],
                             ['red', np.nan]], dtype=object)
        assert result.shape == expected.shape
        assert all(isinstance(v, str) or np.isnan(v) for v in result.flatten())
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_float_target(self):
        data = pd.DataFrame([[0.2, 0.6], [1.2, 2.5]])
        rules = [(1.0, 0.5), (1.5, 1.5), (2.0, 3.0)]
        result = imat_plt._map_attributes(data, rules)
        assert list(result.flatten()) == [1.0, 1.5, 1.5, 2.0]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestDrawGrid(object):
    """
    Testing the `_draw_grid` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        arr = np.zeros((3, 4))
        _, ax = plt.subplots()
        imat_plt._draw_grid(arr, ax, color='red')
        # assertion
        vlines = [line for line in ax.lines if line.get_linestyle() == '-']
        assert len(vlines) == 7
        # there are 3 vertical lines who do not have an x-coordinate
        assert [line.get_xdata()[0] for line in ax.lines] == [0,1,2,3,0,0,0]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_grid_position_effect(self):
        """Test grid_position effect by comparison"""
        arr = np.zeros((2, 3))
        _, ax1 = plt.subplots()
        _, ax2 = plt.subplots()
        # centre
        imat_plt._draw_grid(arr, ax1, axis='x', grid_position='centre')
        centre_x = [line.get_xdata()[0] for line in ax1.lines]
        # outline
        imat_plt._draw_grid(arr, ax2, axis='x', grid_position='outline')
        outline_x = [line.get_xdata()[0] for line in ax2.lines]
        assert np.allclose(centre_x, [0,1,2])
        assert np.allclose(outline_x, [-0.5,0.5,1.5,2.5])
