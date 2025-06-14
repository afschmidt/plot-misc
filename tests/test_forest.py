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
ALPHA_DICT = {'wo T2DM/CVD': .4, 'w T2DM': .65, 'w T2DM & CVD': .9}
# NOTE keep the numeric order to simplify testing
SORT_DICT = {'AF': 0,  'CVD': 1, 'CHD': 2,
             'HF': 3, 'CVD + AF + HF': 4,'Ischaemic Stroke': 5, }
COL_NAME='col'
SHAPE_NAME='shape'
ALPHA_NAME='alpha'
POINT = 'test_cstatistic'
STRING_COL = 'string'
STRING_HEAD = 'test'
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
data1[ALPHA_NAME] = data1.subgroup_name.map(ALPHA_DICT)
# select a single 'study'
data2 = data1[data1.model=='PGS only'].copy()
# y-coordinates data
DATA_SET_Y_COORD = pd.DataFrame({
    'group': ['A', 'A', 'A', 'C', 'B', 'B', 'B', 'C', 'C', 'C'],
    'subgroup': ['x', 'y', 'x', 'z', 'x', 'y', 'z', 'x', 'y', 'z'],
    'value': [10, 20, 15, 30, 40, 50, 60, 70, 75, 80]
})

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
class TestSetYCoordinates(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_set_y_coordinates_default(self):
        data = DATA_SET_Y_COORD.copy()
        data_out = forest.set_y_coordinates(data)
        assert data_out['y_axis'].to_list() ==\
            [1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_set_y_coordinates_group(self):
        data = DATA_SET_Y_COORD.copy()
        data_out = forest.set_y_coordinates(data, group='group', between_pad=3)
        # sort by group to confirm y_axis values are actually grouped
        # NOTE the values are grouped, but probably not the way the user
        # intends it, by A, B, C - see next test.
        data_out = data_out.sort_values('group')
        assert data_out['y_axis'].to_list() ==\
            [1.0, 3.0, 5.0, 17.0, 19.0, 21.0, 8.0, 10.0, 12.0, 14.0]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_set_y_coordinates_sort(self):
        data = DATA_SET_Y_COORD.copy()
        data_out = forest.set_y_coordinates(data, group='group', between_pad=3,
                                            sort_dict=None,)
        # now the dataframe is internally sorted by alphabet prior to
        # setting the y_coordinates
        assert data_out['y_axis'].to_list() ==\
            [1.0, 3.0, 5.0, 8.0, 10.0, 12.0, 15.0, 17.0, 19.0, 21.0]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_set_y_coordinates_strata(self):
        data = DATA_SET_Y_COORD.copy()
        data_out = forest.set_y_coordinates(
            data, group='group', group_by_strata='subgroup', between_pad=3,
        )
        # sort by group to confirm y_axis values are actually grouped
        data_out = data_out.sort_values('group')
        print(data_out)
        assert data_out['y_axis'].to_list() ==\
            [1.0, 1.0, 3.0, 6.0, 6.0, 6.0, 9.0, 9.0, 9.0, 11.0]

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
        res = forest.assign_distance(data_in, group=GROUP)
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
        res = forest.assign_distance(data_in, group=GROUP, strata='model',
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
        _, ax, _ = forest.plot_forest(df=data2,
                                      x_col=POINT, lb_col=LB, ub_col=UB,
                                      s_col=SHAPE_NAME, a_col=ALPHA_NAME,
                                      c_col=COL_NAME, ci_colour='black',
                                      g_col='evaluated_outcome', s_size_col= 19,
                                      ci_lwd=2,
                                      ax=ax,
                                      kwargs_scatter_dict={'edgecolors':'black',
                                                           'zorder':1},
                                      kwargs_plot_ci_dict={'zorder':2,
                                                           'solid_capstyle':'round',
                                                           'linestyle':'-.',
                                                           'alpha':'row[a_col_name]',
                                                           }
                                      )
        # check the points are correct
        assert list(data2[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size and alphas
        collect=ax.collections
        assert collect[0].get_sizes() == 19
        assert list(data2[ALPHA_NAME]) == \
            list([al.get_alpha() for al in collect])
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[3].get_xdata()) == \
            list(data2.loc[:,[LB, UB]].iloc[3])
        assert lines[4].get_linestyle() == '-.'
        assert lines[4].get_solid_capstyle() == 'round'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_noci_forest(self):
        f, ax = plt.subplots(1, figsize=(15, 15))
        _, ax, _ = forest.plot_forest(df=data2,
                                   x_col=POINT,
                                   s_col=SHAPE_NAME, a_col=ALPHA_NAME,
                                   c_col=COL_NAME, ci_colour='black',
                                   g_col='evaluated_outcome', s_size_col= 19,
                                   ci_lwd=2,
                                   ax=ax,
                                   kwargs_scatter_dict={'edgecolors':'black',
                                                        'zorder':1},
                                   )
        # check the points are correct
        assert list(data2[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size and alphas
        collect=ax.collections
        assert collect[0].get_sizes() == 19
        assert list(data2[ALPHA_NAME]) == \
            list([al.get_alpha() for al in collect])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_simple_forest_wo_ax(self):
        _, ax, _ = forest.plot_forest(df=data2,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   a_col=ALPHA_NAME,
                                   g_col='evaluated_outcome',
                                   )
        # check the points are correct
        assert list(data2[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size and alphas
        collect=ax.collections
        assert collect[0].get_sizes() == 40
        assert list(data2[ALPHA_NAME]) == \
            list([al.get_alpha() for al in collect])
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
        _, ax, _ = forest.plot_forest(df=data1,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   a_col=ALPHA_NAME, ci_colour='black',
                                   g_col='evaluated_outcome',
                                   connect_shape=True,
                                   kwargs_scatter_dict={'edgecolors':'black'},
                                   kwargs_connect_segments_dict={'zorder':1},
                                   )
        # check the points are correct
        assert list(data1[POINT]) ==\
            [list(cl.get_offsets().data[0])[0] for cl in ax.collections]
        # check the shape size and alphas
        collect=ax.collections
        assert collect[0].get_sizes() == 40
        assert list(data1[ALPHA_NAME]) == \
            list([al.get_alpha() for al in collect])
        # get conficence interval coordinates
        lines=ax.lines
        assert list(lines[9].get_xdata()) == \
            list(data1.loc[:,[LB, UB]].iloc[9])
        assert lines[5].get_linestyle() == '-'
        assert lines[6].get_solid_capstyle() == 'projecting'
        assert lines[3].get_lw() == 2.0
        assert lines[3].get_color() == 'black'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_forest_return_other(self):
        '''
        evaluating the returned 'other' tuple
        '''
        # not retruning anything
        _, ax, log = forest.plot_forest(df=data2,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   a_col=ALPHA_NAME,
                                   )
        assert len(log.__getattribute__(FNames.span)) == 0
        # retruning something
        _, ax, log = forest.plot_forest(df=data2,
                                   x_col=POINT, lb_col=LB, ub_col=UB,
                                   s_col=SHAPE_NAME, c_col=COL_NAME,
                                   a_col=ALPHA_NAME,
                                   span=True, span_return=True,
                                   )
        assert len(log.__getattribute__(FNames.span)) != 0
        assert isinstance(log.__getattribute__(FNames.span), dict)
        assert isinstance(log.__getattribute__(FNames.span), dict)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# plot_table
class TestPlotTable(object):
    """
    Testing the `plot_table` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_table(self):
        # figure
        _, ax = plt.subplots(1, figsize=(5,5))
        # string
        data2[STRING_COL] = data2[POINT].map('{:,.2f}'.format)
        ax.set_ylim(min(data2.y_axis.to_list()), max(data2.y_axis.to_list()))
        # the function to test
        _ = forest.plot_table(data2, annoteheader=STRING_HEAD,
                              string_col=STRING_COL, ax=ax,
                              halignment_text='left',
                              halignment_header='center',
                              size_text=5, size_header=6,
                              negative_padding=2,
                              )
        # assert
        assert [t.get_text() for t in ax.texts] ==\
            data2[STRING_COL].to_list() + [STRING_HEAD]
        assert ax.texts[-1].get_fontsize() == 6
        assert ax.texts[1].get_fontsize() == 5
        assert ax.texts[1].get_horizontalalignment() == 'left'


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# EmpericalSupport
class EmpericalSupport(object):
    """
    Testing the `EmpericalSupport` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_calc_empirical_support(self):
        table = forest.EmpericalSupport.calc_empirical_support(
            -2, 0.2, [0.01, 0.2, 0.8])
        assert table.mean().round(2).to_list() ==\
            [-2.0, -2.27, -1.73, 0.34, 0.66]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_empirical_support(self):
        table=pd.DataFrame(
            {'estimate': {0: -2, 1: -2, 2: -2},
             'lower_bound': {0: -2.51516586070978, 1: -2.25631031310892,
                             2: -2.05066942062716},
             'upper_bound': {0: -1.48483413929022, 1: -1.7436896868910798,
                             2: -1.9493305793728402},
             'p-value': {0: 0.01, 1: 0.2, 2: 0.8},
             'confidence_interval': {0: 0.99, 1: 0.8, 2: 0.19999999999999996}}
        )
        _, ax = forest.EmpericalSupport.plot_empirical_support(
            table, lb_col='lower_bound', ub_col='upper_bound',
            support_col='confidence_interval',
            estimate=None)
        # assert
        assert len(ax.lines) == 2
        for i, line in enumerate(ax.get_lines()):
            assert list(line.get_ydata()) ==\
                table['confidence_interval'].to_list()
            # whether to use the lower or upper bound
            if i == 0:
                assert list(line.get_xdata()) == table['lower_bound'].to_list()
            elif i == 1:
                assert list(line.get_xdata()) == table['upper_bound'].to_list()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_plot_tree(self):
        est = 0.2; m=100
        space=forest.EmpericalSupport(estimate=est, standard_error=0.001,
                                      alpha=list(np.linspace(1, 0.00001, m))
                                      )
        _, ax, results = space.plot_tree()
        # assert
        assert len(ax.lines) == 2
        assert results.estimate == est
        assert results.data_table.shape == m
