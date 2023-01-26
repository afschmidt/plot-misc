"""
testing the `forest` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.forest as forest
import plot_misc.example_data.examples as examples

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
CMTOINCH = 1/2.54
SHAPE_DICT = {'PGS only': 'o', 'PGS plus': 's', 'PGS extended': 'H'}
COL_DICT = {'wo T2DM/CVD': 'orangered', 'w T2DM': 'blueviolet',
              'w T2DM & CVD': 'limegreen'}

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
data1 = examples.load_forest_data()
# add y-axis position, col and shape - NOTE add strings to constants mod
data1['y_axis'] = [0.0, 2.0, 4.0, 0.0, 2.0, 4.0, 0.0, 2.0, 4.0, 10.0, 12.0,
                   14.0, 10.0, 12.0, 14.0, 10.0, 12.0, 14.0, 20.0, 22.0, 24.0,
                   20.0, 22.0, 24.0, 20.0, 22.0, 24.0, 30.0, 32.0, 34.0, 30.0,
                   32.0, 34.0, 30.0, 32.0, 34.0, 40.0, 42.0, 44.0, 40.0, 42.0,
                   44.0, 40.0, 42.0, 44.0, 50.0, 52.0, 54.0, 50.0, 52.0, 54.0,
                   50.0, 52.0, 54.0]
data1['col'] = data1.subgroup_name.map(COL_DICT)
data1['shape'] = data1.model.map(SHAPE_DICT)
# select a single 'study'
data2 = data1[data1.model=='PGS only'].copy()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# plot_forest
class TestPlotForest(object):
    """
    Testing functions for the `plot_forest` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_simple_forest(self):
        f, ax = plt.subplots(1, figsize=(15, 15))
        _, ax = forest.plot_forest(df=data2, x_col='test_cstatistic',
                                   lb_col='test_cstatistic_lb',
                                   ub_col='test_cstatistic_ub',
                                   s_col='shape',
                                   c_col='col', ci_colour='black',
                                   g_col='evaluated_outcome', shape_size= 19, ci_lwd=2,
                                   ax=ax,
                                   kwargs_scatter_dict={'edgecolors':'black',
                                                        'zorder':1},
                                   kwargs_plot_ci_dict={'zorder':2,
                                                        'solid_capstyle':'round',
                                                        'linestyle':'-'}
                                   )
        # check the points are correct
        assert list(data2['test_cstatistic']) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size
        collect=ax.collections
        assert collect[0].get_sizes() == 19
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[3].get_xdata()) == \
            list(data2.loc[:,['test_cstatistic_lb', 'test_cstatistic_ub']].iloc[3])
        assert lines[4].get_linestyle() == '-'
        assert lines[4].get_solid_capstyle() == 'round'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_complex_forest(self):
        pass
