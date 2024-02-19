"""
testing the `utils` module
"""
import numpy as np
import matplotlib.pyplot as plt
import pytest
from plot_misc.constants import (
    UtilsNames as UNames,
    InputValidationError,
)
from plot_misc.example_data import examples
from plot_misc.utils.utils import (
    _extract,
    _format_matrices,
    calc_matrices,
    _update_kwargs,
    _dict_string_argument,
    fix_labels,
    calc_mid_point,
    calc_angle_points,
    segment_labelled,
)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestUpdate_Kwargs(object):
    '''
    Testing the `_update_kwargs` function
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_update_kwargs(self):
        res = _update_kwargs(update_dict={'c': 'black'}, c='red', alpha = 0.5,)
        assert res == {'c': 'black', 'alpha': 0.5}

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing _dict_string_argument
class TestDict_String_Argument(object):
    '''
    Testing the `_dict_string_argument` function
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_dict_string_argument(self):
        # test data
        pmatch='row'
        row=[1, 2]
        dict_string={'obj1': 'row[0]',
                     'obj2' : 2}
        dict_expected = dict_string.copy()
        dict_expected['obj1'] = row[0]
        #actual test
        new_dict = _dict_string_argument(pmatch, dict_string,
                                         context={'row':row})
        assert dict_expected == new_dict

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing extraction and formating
class TestCalcMatrices(object):
    """
    Testing functions for the `calc_matrices` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # testing extraction
    def test_extract(self):
        data = examples.get_data('heatmap_data')
        # running extract
        point_mat, pvalue_mat = _extract(
            data,
            exposure_col=UNames.mat_exposure,
            outcome_col=UNames.mat_outcome,
            point_col=UNames.mat_point,
            pvalue_col=UNames.mat_pvalue,
            dropna=True,
        )
        # assertions
        assert point_mat.dropna(axis=1).sum(axis=1).round(2).to_list() ==\
            [0.0, -0.2]
        assert point_mat.dropna(axis=1).sum(axis=0).round(2).to_list() ==\
            [-0.21, 0.01,]
        assert pvalue_mat.dropna(axis=1).mean(axis=1).round(2).to_list() ==\
            [0.60, 0.00]
        assert pvalue_mat.dropna(axis=1).mean(axis=0).round(2).to_list() ==\
            [0.13, 0.48]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # with missings
    def test_extract_wo_nan(self):
        data = examples.get_data('heatmap_data')
        # running extract
        point_mat, pvalue_mat = _extract(
            data,
            exposure_col=UNames.mat_exposure,
            outcome_col=UNames.mat_outcome,
            point_col=UNames.mat_point,
            pvalue_col=UNames.mat_pvalue,
        )
        # assertions
        assert point_mat.sum(axis=1).round(2).to_list() ==\
            [-0.13, -0.20]
        assert point_mat.sum(axis=0).round(2).to_list() ==\
            [-0.21, 0.01, 0.03, -0.16]
        assert pvalue_mat.mean(axis=1).round(2).to_list() ==\
            [0.35, 0.0]
        assert pvalue_mat.fillna(0).mean(axis=0).round(2).to_list() ==\
            [0.13, 0.48, 0.0, 0.10]
    #######################################################################
    # test format_matrices function
    def test_format_matrices(self):
        point_mat = examples.get_data('heatmap_point_matrix')
        pvalue_mat = examples.get_data('heatmap_pvalue_matrix')
        # formatting
        values, annot_effect, _, _, _ =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=1.3, ptrun=16, digits='6', log=True)
        values2, _, annot_star, _, _ =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=0.05, ptrun=16, digits='2', log=False)
        values3, _, _, annot_pval, _ =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=0.3, ptrun=16, digits='2', log=True)
        assert values.iloc[:,3].tolist() == [-0.689009, 3.272459]
        assert values2.iloc[:,1].tolist() == [-0.95, 0.0]
        assert values3.iloc[:,1].tolist() == [-0.02, 4.0]
        assert annot_effect.iloc[:,3].tolist() == ['.', '0.027800']
        assert annot_effect.iloc[:,2].tolist() == ['nan', 'nan']
        assert annot_star.iloc[:,1].tolist() == ['.', '★']
        assert annot_pval.iloc[:,1].tolist() == ['.', '4.0']
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Testing _calc_matrices
    def test_correct_usage(self):
        data = examples.get_data('heatmap_data')
        r = 2
        # res 1
        res1 = calc_matrices(data, exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res1.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [ -1.68, 3.98, 3.27, -0.69]
        assert res1.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '.','★','.']
        # res 2
        res2 = calc_matrices(data,
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             ptrun=2)
        assert res2.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [-1.4, 1.98, 2.0, -0.69]
        assert res2.curated_matrix_annotation.iloc[1].to_list() == \
            ['★', '★', '.', '.']
        # res 3
        res3 = calc_matrices(data, alpha=0.5,
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res3.curated_matrix_annotation.iloc[1].to_list() == \
            [ '★','★','.', '.']
        # res 4
        res4 = calc_matrices(data, alpha=0.001, without_log=True,
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res4.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [0.24, -0.95, 1.0, 0.8]
        assert res4.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '.','★','.']
        # res 5
        res5 = calc_matrices(data, sig_numbers=3, annotate='pvalues',
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res5.curated_matrix_annotation.iloc[1].to_list() == \
            ['-2.281', '4.0', '.', '.']
        # res 6
        res6 = calc_matrices(data, sig_numbers=3, mask_na=False,
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res6.curated_matrix_value.iloc[0].to_list() == \
            [0.596, -0.02]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~----
class TestFixLabels(object):
    '''
    Testing function `fix_labels`.
    '''
    def test_fix_labels(self):
        # Create a mock axis
        fig, ax = plt.subplots()
        # Create mock annotations with overlapping positions
        ann1 = ax.annotate("Annotation 1", xy=(0.5, 0.5), xytext=(0.5, 0.5))
        ann2 = ax.annotate("Annotation 2", xy=(0.5, 0.55), xytext=(0.5, 0.55))
        # Call the utility function to fix labels
        fix_labels([ann1, ann2], ax, min_distance=0.1)
        # Assert that annotations are adjusted to prevent overlap
        pos1 = ax.transData.inverted().transform(ax.transData.transform(ann1.get_position()))
        pos2 = ax.transData.inverted().transform(ax.transData.transform(ann2.get_position()))
        vertical_distance = abs(pos1[1] - pos2[1])
        # Floating point precision issue....
        assert vertical_distance >= 0.1 - 1e-10

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_Calc_Mid_Point(object):
    '''
    Testing functions for the `calc_mid_point` function.
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert calc_mid_point(x=[0, 2], y=[2, 2]) == (1, 2)
        assert calc_mid_point(x=[0, 2], y=[2, 6]) == (1, 4)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_errors(self):
        # wrong input type
        with pytest.raises(InputValidationError):
            calc_mid_point(x=np.array([2,2]), y=[2,2])
        # wrong length
        with pytest.raises(InputValidationError):
            calc_mid_point(x=[1], y=[2,2])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_Calc_Angle_Points(object):
    '''
    Testing functions for the `calc_angle_points` function.
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert calc_angle_points(x=[0, 2], y=[2, 2]) == 0.0
        assert calc_angle_points(x=[0, 2], y=[2, 4]) == 45.0
        assert calc_angle_points(x=[2, 0], y=[2, 4]) == 315.0
        assert calc_angle_points(x=[0, 2], y=[2, 4], radians=True) == np.pi/4
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_errors(self):
        # wrong input type
        with pytest.raises(InputValidationError):
            calc_angle_points(x=np.array([2,2]), y=[2,2])
        # wrong length
        with pytest.raises(InputValidationError):
            calc_angle_points(x=[1], y=[2,2])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_Segment_Labelled(object):
    '''
    Testing functions for the `segment_labelled` function.
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        # test 1
        _, ax = plt.subplots()
        segment_labelled(x=[0, 2], y=[2, 2], ax=ax)
        assert list(ax.get_lines()[0].get_ydata()) == [2,2]
        # test 2
        lab='hi'
        _, ax = plt.subplots()
        segment_labelled(x=[0, 2], y=[2, 2], ax=ax, label=lab)
        assert ax.texts[0].get_text() == lab
        # test 3
        lab='hi'
        _, ax = plt.subplots()
        segment_labelled(x=[0, 2], y=[2, 4], ax=ax, label=lab)
        assert ax.texts[0].get_position() == (1.0, 3.0)
        assert np.round(ax.texts[0].get_rotation(), 2) == 36.69
