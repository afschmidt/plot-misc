"""
testing the `utils` module
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pytest
from plot_misc.constants import (
    UtilsNames as UNames,
)
from plot_misc.errors import (
    InputValidationError,
)
from matplotlib.text import Text
from plot_misc.example_data import examples
from plot_misc.utils.utils import (
    Results,
    calc_matrices,
    _dict_string_argument,
    adjust_labels,
    calc_mid_point,
    calc_angle_points,
    segment_labelled,
    annotate_axis_midpoints,
    _extract,
    _format_matrices,
    _update_kwargs,
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
# Testing extraction and formatting
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
        # `_format_matrices` returns three numeric p-value tables (signed
        # -log10, unsigned -log10, raw) plus the effect / star / p-value
        # annotation matrices and the raw effect matrix. `sig` is supplied in
        # -log10 units (the private interface).
        (signed, unsigned, raw, annot_effect, annot_star, annot_pval,
         effect_float) = _format_matrices(point_mat, pvalue_mat,
                                          sig=1.3, ptrun=16, digits='6')
        # the three numeric p-value tables
        assert signed.iloc[:,3].tolist() == [-0.689009, 3.272459]
        assert unsigned.iloc[:,3].tolist() == [0.689009, 3.272459]
        assert raw.iloc[:,3].tolist() == [0.20464, 0.000534]
        # effect annotation: '.' where non-significant, 'nan' where missing
        assert annot_effect.iloc[:,3].tolist() == ['.', '0.027800']
        assert annot_effect.iloc[:,2].tolist() == ['nan', 'nan']
        # star annotation honours the significance mask
        assert annot_star.iloc[:,1].tolist() == ['.', '★']
        # custom significance symbol is honoured
        (_, _, _, _, annot_star_sym, _, _) =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=1.3, ptrun=16, digits='2', symbol='●')
        assert annot_star_sym.iloc[:,1].tolist() == ['.', '●']
        # p-value annotation modes: signed / unsigned -log10 and raw
        (_, _, _, _, _, annot_signed, _) =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=0.3, ptrun=16, digits='2',
                            pval_mode='signed_log')
        (_, _, _, _, _, annot_unsigned, _) =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=0.3, ptrun=16, digits='2',
                            pval_mode='unsigned_log')
        (_, _, _, _, _, annot_raw, _) =\
            _format_matrices(point_mat, pvalue_mat,
                            sig=0.3, ptrun=16, digits='3',
                            pval_mode='raw')
        # 'signed_log' carries the effect-direction sign ...
        assert annot_signed.iloc[:,1].tolist() == ['.', '4.0']
        assert annot_signed.iloc[:,3].tolist() == ['-0.69', '3.27']
        # ... while 'unsigned_log' drops it and 'raw' shows the p-value itself
        assert annot_unsigned.iloc[:,3].tolist() == ['0.69', '3.27']
        assert annot_raw.iloc[:,3].tolist() == ['0.205', '0.001']
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
        # the two additional numeric p-value tables (unsigned -log10, raw)
        assert res1.curated_matrix_value_unsigned_log.iloc[1].round(r)\
            .to_list() == [2.28, 4.0, 0.0, 0.0]
        assert res1.curated_matrix_value_raw.iloc[1].round(r)\
            .to_list() == [0.01, 0.0, 1.0, 1.0]
        # res 2 - `ptrun` is now a raw p-value (0.01 == old exponent 2)
        res2 = calc_matrices(data,
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             ptrun=0.01)
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
        # res 4 - `without_log` is deprecated: it now warns and no longer
        # changes the (always signed -log10) value matrix.
        with pytest.warns(DeprecationWarning):
            res4 = calc_matrices(data, alpha=0.001, without_log=True,
                                 exposure_col=UNames.mat_exposure,
                                 outcome_col=UNames.mat_outcome,
                                 )
        assert res4.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [-1.68, 3.98, 3.27, -0.69]
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
        # res 7 - explicit `annotate='symbol'`
        res7b = calc_matrices(data, annotate='symbol', symbol='◆',
                              exposure_col=UNames.mat_exposure,
                              outcome_col=UNames.mat_outcome,
                              )
        assert res7b.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '.', '◆', '.']
        # res 8 - 'pvalues_signed' reproduces the legacy 'pvalues' output
        res8 = calc_matrices(data, sig_numbers=3, annotate='pvalues_signed',
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res8.curated_matrix_annotation.iloc[1].to_list() == \
            ['-2.281', '4.0', '.', '.']
        # res 9 - unsigned -log10 annotation; value matrix stays signed -log10
        res9 = calc_matrices(data, sig_numbers=3, annotate='pvalues_unsigned',
                             exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res9.curated_matrix_annotation.iloc[1].to_list() == \
            ['2.281', '4.0', '.', '.']
        assert res9.curated_matrix_value.iloc[1].round(3).to_list() == \
            [-2.281, 4.0, 0.0, 0.0]
        # res 10 - raw p-value annotation; value matrix stays signed -log10
        res10 = calc_matrices(data, sig_numbers=3, annotate='pvalues_raw',
                              exposure_col=UNames.mat_exposure,
                              outcome_col=UNames.mat_outcome,
                              )
        assert res10.curated_matrix_annotation.iloc[1].to_list() == \
            ['0.005', '0.0', '.', '.']
        assert res10.curated_matrix_value.iloc[1].round(3).to_list() == \
            [-2.281, 4.0, 0.0, 0.0]
        # res 11 - an unknown annotation still raises
        with pytest.raises(ValueError):
            calc_matrices(data, annotate='not_a_mode',  # type: ignore[arg-type]
                          exposure_col=UNames.mat_exposure,
                          outcome_col=UNames.mat_outcome,
                          )
        # res 12 - `alpha` is now a raw p-value in (0, 1]; values > 1 raise
        with pytest.raises(InputValidationError):
            calc_matrices(data, alpha=1.3,
                          exposure_col=UNames.mat_exposure,
                          outcome_col=UNames.mat_outcome,
                          )
        # res 13 - `ptrun` is now a raw p-value in (0, 1]; the old exponent
        # convention (e.g. 2) and 0 are out of range and raise.
        with pytest.raises(InputValidationError):
            calc_matrices(data, ptrun=2,
                          exposure_col=UNames.mat_exposure,
                          outcome_col=UNames.mat_outcome,
                          )
        with pytest.raises(InputValidationError):
            calc_matrices(data, ptrun=0,
                          exposure_col=UNames.mat_exposure,
                          outcome_col=UNames.mat_outcome,
                          )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Testing `ptrun=None` (the default): no truncation of -log10(p-values)
    def test_ptrun_none(self):
        # inline long-format data with a p-value of exactly 0 and a tiny one
        data = pd.DataFrame({
            'exposure': ['e1', 'e1', 'e2', 'e2'],
            'outcome': ['o1', 'o2', 'o1', 'o2'],
            'point': [0.5, -0.5, 0.25, -0.25],
            'pvalue': [0.0, 1e-300, 0.04, 0.5],
        })
        # `ptrun=None` is the default: -log10(p) is uncapped, p == 0 -> +inf
        res = calc_matrices(data, exposure_col='exposure',
                            outcome_col='outcome',
                            )
        unsigned = res.curated_matrix_value_unsigned_log
        signed = res.curated_matrix_value
        assert np.isinf(unsigned.loc['o1', 'e1'])
        assert unsigned.loc['o2', 'e1'] == 300.0
        assert unsigned.loc['o1', 'e2'] == 1.40
        # the signed table carries the effect direction (point < 0 for o2/e1)
        assert np.isposinf(signed.loc['o1', 'e1'])
        assert signed.loc['o2', 'e1'] == -300.0
        # an explicit `ptrun` still truncates: both extreme cells cap at 16
        res_trun = calc_matrices(data, exposure_col='exposure',
                                 outcome_col='outcome', ptrun=1e-16,
                                 )
        unsigned_trun = res_trun.curated_matrix_value_unsigned_log
        assert unsigned_trun.loc['o1', 'e1'] == 16.0
        assert unsigned_trun.loc['o2', 'e1'] == 16.0
        assert unsigned_trun.loc['o1', 'e2'] == 1.40
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Testing `alpha=None`: the significance filter is disabled
    def test_alpha_none(self):
        # inline long-format data without missing values
        data = pd.DataFrame({
            'exposure': ['e1', 'e1', 'e2', 'e2'],
            'outcome': ['o1', 'o2', 'o1', 'o2'],
            'point': [0.5, -0.5, 0.25, -0.25],
            'pvalue': [0.5, 0.04, 0.9, 0.001],
        })
        # with the default `alpha=0.05` the non-significant cells are masked
        res_default = calc_matrices(data, exposure_col='exposure',
                                    outcome_col='outcome',
                                    )
        annot_default = res_default.curated_matrix_annotation
        assert annot_default.loc['o1'].to_list() == ['.', '.']
        assert annot_default.loc['o2'].to_list() == ['★', '★']
        # with `alpha=None` every cell is annotated
        res_none = calc_matrices(data, alpha=None, exposure_col='exposure',
                                 outcome_col='outcome',
                                 )
        annot_none = res_none.curated_matrix_annotation
        assert annot_none.loc['o1'].to_list() == ['★', '★']
        assert annot_none.loc['o2'].to_list() == ['★', '★']
        # `alpha=None` combined with a p-value annotation shows every p-value
        res_raw = calc_matrices(data, alpha=None, annotate='pvalues_raw',
                                sig_numbers=3, exposure_col='exposure',
                                outcome_col='outcome',
                                )
        annot_raw = res_raw.curated_matrix_annotation
        assert annot_raw.loc['o1'].to_list() == ['0.5', '0.9']
        assert annot_raw.loc['o2'].to_list() == ['0.04', '0.001']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~----
class TestAjustLabels(object):
    '''
    Testing function `adjust_labels`.
    '''
    def test_adjust_labels(self):
        # Create a mock axis
        fig, ax = plt.subplots()
        # Create mock annotations with overlapping positions
        ann1 = ax.annotate("Annotation 1", xy=(0.5, 0.5), xytext=(0.5, 0.5))
        ann2 = ax.annotate("Annotation 2", xy=(0.5, 0.55), xytext=(0.5, 0.55))
        # Call the utility function to fix labels
        adjust_labels([ann1, ann2], ax, min_distance=0.1)
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
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_label_rotation_follows_segment(self):
        # regression: the second endpoint must use ``x[1]`` (not ``y[0]``)
        # when transforming to display space, otherwise the label rotation
        # does not align with the drawn segment.
        x = [1, 8]
        y = [2, 7]
        _, ax = plt.subplots()
        segment_labelled(x=x, y=y, ax=ax, label='link')
        # expected rotation computed from the correctly transformed endpoints
        p1 = list(ax.transData.transform_point((x[0], y[0])))
        p2 = list(ax.transData.transform_point((x[1], y[1])))
        expected = calc_angle_points(x=[p1[0], p2[0]], y=[p1[1], p2[1]])
        assert np.round(ax.texts[0].get_rotation(), 5) == np.round(expected, 5)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_overrule_angle(self):
        # the override path bypasses the internal angle calculation
        _, ax = plt.subplots()
        segment_labelled(x=[1, 8], y=[2, 7], ax=ax, label='link',
                         overrule_angle=0)
        assert ax.texts[0].get_rotation() == 0

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_Annotate_axis_midpoints(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_annotate_axis_midpoints_y_axis(self):
        _, ax = plt.subplots()
        ax.set_yticks([0, 1, 2, 4, 5])
        labels = "Label 1"
        result_ax = annotate_axis_midpoints(ax=ax, labels=[labels],
                                            axis='y', gap=2)
        texts = [t.get_text() for t in result_ax.texts]
        assert labels in texts
        assert len(texts) == 1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_annotate_axis_midpoints_x_axis_with_start_and_end(self):
        _, ax = plt.subplots()
        ax.set_xticks([0, 2, 4, 6, 9])
        labels = ["One", "Two", "Three"]
        start_label = {"Start": -1.0}
        end_label = {"End": 10.0}
        result_ax = annotate_axis_midpoints(ax=ax, labels=labels,
                                            axis='x', gap=2,
                                            start_label=start_label,
                                            end_label=end_label)
        texts = [t.get_text() for t in result_ax.texts]
        assert set(texts) == {"Start", "One", "Two", "Three", "End"}
        assert len(texts) == 5
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_annotate_axis_midpoints_invalid_label_count(self):
        _, ax = plt.subplots()
        ax.set_xticks([0, 2, 4, 6])  # 3 gaps of size 2
        with pytest.raises(IndexError, match="Expected 3 labels.*"):
            annotate_axis_midpoints(ax=ax, labels=["Too few"],
                                    axis='x', gap=2)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestResults(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_results_default(self):
        # Set up expected arguments
        set_args = ['estimate', 'ci', 'array_data', 'dict', 'tupl', 'sers',
                    'tab']
        estimate = 0.712
        ci = (0.60, 0.84)
        array_data = np.array([1, 2, 3, 4, 5, 6, 7])
        dict_in = {'hi' : 2}
        tupl = (2, 4, 0, 0, 0)
        sers = pd.Series(tupl)
        tab = pd.DataFrame(sers)
        # Create the results object
        result = Results(set_args=set_args, estimate=estimate, ci=ci,
                         array_data=array_data, dict=dict_in, tupl=tupl,
                         sers=sers, tab=tab,)
        # Check attribute assignment
        assert result.estimate == estimate
        assert result.ci == ci
        assert isinstance(result.array_data, np.ndarray)
        # Check string representation
        s = str(result)
        assert isinstance(s, str)
        assert "results class" in s.lower()
        # Check repr formatting
        r = repr(result)
        assert 'estimate=0.712' in r
        assert '[0.600, 0.840]' in r or '(0.600, 0.840)' in r
        assert 'array' in r
        # Check warning for missing key
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            r2 = Results(set_args=['missing'])
            assert hasattr(r2, 'missing')
            assert w, "Expected warning for missing key"
            assert "argument 'missing' is set to 'None'" in str(w[0].message)
        # Check AttributeError for unknown kwargs
        with pytest.raises(AttributeError):
            Results(set_args=['x'], foo=42)
