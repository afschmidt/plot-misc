"""
testing the `forest` module
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.forest as forest
import plot_misc.example_data.examples as examples
from plot_misc.constants import ForestNames as FNames

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CONSTANT
CMTOINCH = 1/2.54
SHAPE_DICT = {'PGS only': 'o', 'PGS plus': 's', 'PGS extended': 'H'}
COL_DICT = {'wo T2DM/CVD': 'orangered', 'w T2DM': 'blueviolet',
              'w T2DM & CVD': 'limegreen'}
# NOTE keep the numeric order to simplify testing
SORT_DICT = {'AF': 0,  'CVD': 1, 'CHD': 2,
             'HF': 3, 'CVD + AF + HF': 4,'Ischaemic Stroke': 5, }
COL_NAME='col'
SHAPE_NAME='shape'
POINT = 'test_cstatistic'
UB = POINT + '_ub'
LB = POINT + '_lb'
GROUP='evaluated_outcome'
MODEL='model'
ORDER_OUTER ={GROUP: ['CVD', 'AF', 'HF', 'Ischaemic Stroke', 'CVD + AF + HF']}
ORDER_INNER ={MODEL: ['PGS only', 'PGS extended', 'PGS plus']}

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
data1 = examples.load_forest_data()
#  col and shape
data1[COL_NAME] = data1.subgroup_name.map(COL_DICT)
data1[SHAPE_NAME] = data1.model.map(SHAPE_DICT)
# select a single 'study'
data2 = data1[data1.model=='PGS only'].copy()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# assign_distance
class TestOrderRow(object):
    '''
    Test the `order_row` function
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_order_row(self):
        # copy data
        data_in = data1.copy()
        # run
        res1 = forest.order_row(data_in, order_outer=ORDER_OUTER,
                               order_inner=ORDER_INNER,
                               )
        res2 = forest.order_row(data_in, order_outer=ORDER_OUTER,
                               )
        # test
        assert list(res1[GROUP].unique()) == list(ORDER_OUTER.values())[0]
        assert list(res1[MODEL].unique()) == list(ORDER_INNER.values())[0]
        assert list(res1[res1[GROUP]=='AF'][MODEL].unique()) ==\
            list(ORDER_INNER.values())[0]
        assert list(res2[GROUP].unique()) == list(ORDER_OUTER.values())[0]
        assert list(res2[MODEL].unique()) != list(ORDER_INNER.values())[0]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# assign_distance
class TestAssignDistance(object):
    '''
    Test the `_assign_distance` function
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_assign_distance_default(self):
        # removing y_axis
        data_in = data1.copy()
        del data_in[FNames.y_col]
        # getting y_axis
        res = forest._assign_distance(data_in, group=GROUP)
        # test
        assert FNames.y_col in res.columns
        assert res[FNames.y_col].mean() == 59.0
        assert sum(res[FNames.y_col].isnull()) == 0
        # testing if the y-axis values are the distinct per model
        assert list(res[res['model'] == 'PGS only'][FNames.y_col]) != \
            list(res[res['model'] == 'PGS plus'][FNames.y_col])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_assign_distance_custom(self):
        # removing y_axis
        data_in = data1.copy()
        del data_in[FNames.y_col]
        # getting y_axis
        res = forest._assign_distance(data_in, group=GROUP, strata='model',
                                      start=2,
                                      sort_dict=SORT_DICT,
                                      )
        # test
        assert list(res[GROUP].unique()) == list(SORT_DICT.keys())
        # testing if the y-axis values are the same per model
        assert list(res[res['model'] == 'PGS only'][FNames.y_col]) == \
            list(res[res['model'] == 'PGS plus'][FNames.y_col])
        assert res[FNames.y_col].mean() == 24.0
        assert res[FNames.y_col].min() == 2
        assert sum(res[FNames.y_col].isnull()) == 0

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# plot_forest
class TestPlotForest(object):
    """
    Testing the `plot_forest` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_simple_forest(self):
        f, ax = plt.subplots(1, figsize=(15, 15))
        _, ax = forest.plot_forest(df=data2,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME,
                                   c_col=COL_NAME, ci_colour='black',
                                   g_col='evaluated_outcome', shape_size= 19,
                                   ci_lwd=2,
                                   ax=ax,
                                   kwargs_scatter_dict={'edgecolors':'black',
                                                        'zorder':1},
                                   kwargs_plot_ci_dict={'zorder':2,
                                                        'solid_capstyle':'round',
                                                        'linestyle':'-.'}
                                   )
        # check the points are correct
        assert list(data2[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size
        collect=ax.collections
        assert collect[0].get_sizes() == 19
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[3].get_xdata()) == \
            list(data2.loc[:,[LB, UB]].iloc[3])
        assert lines[4].get_linestyle() == '-.'
        assert lines[4].get_solid_capstyle() == 'round'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_simple_forest_wo_ax(self):
        _, ax = forest.plot_forest(df=data2,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   g_col='evaluated_outcome',
                                   )
        # check the points are correct
        assert list(data2[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size
        collect=ax.collections
        assert collect[0].get_sizes() == 40
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[9].get_xdata()) == \
            list(data2.loc[:,[LB, UB]].iloc[9])
        assert lines[5].get_linestyle() == '-'
        assert lines[6].get_solid_capstyle() == 'projecting'
        assert lines[3].get_lw() == 2.0
        assert lines[3].get_color() == 'indianred'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_complex_forest(self):
        _, ax = forest.plot_forest(df=data1,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   ci_colour='black',
                                   g_col='evaluated_outcome',
                                   connect_shape=True,
                                   kwargs_scatter_dict={'edgecolors':'black'},
                                   kwargs_connect_segments_dict={'zorder':1},
                                  )
        # check the points are correct
        assert list(data1[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size
        collect=ax.collections
        assert collect[0].get_sizes() == 40
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[9].get_xdata()) == \
            list(data2.loc[:,[LB, UB]].iloc[9])
        assert lines[5].get_linestyle() == '-'
        assert lines[6].get_solid_capstyle() == 'projecting'
        assert lines[3].get_lw() == 2.0
        assert lines[3].get_color() == 'black'
