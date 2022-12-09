"""
testing commandline_scripts.make_heatmap
"""
import pandas as pd
from plot_misc.constants import UtilsNames as UNames
from plot_misc.example_data import examples
from plot_misc.utils import (
    extract,
    format_matrices,
)
from merit_helper.commandline_scripts.make_heatmap import (
     _mapper_format,
    calc_matrices,
)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing extraction and formating
class TestExtractionFormatting(object):
    """
    Testing functions to extract and format the `data`
    
    Depends on
    ----------
    - mapper
    - data
    
    Evaluates
    ---------
    - extract
    - format_matrices
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # testing extraction
    def test_extract(self):
        data = examples.get_data('heatmap_data')
        # running extract
        point_mat, pvalue_mat = extract(
            data,
            exposure_col=UNames.mat_exposure,
            outcome_col=UNames.mat_outcome,
            point_col=UNames.mat_point,
            pvalue_col=UNames.mat_pvalue,
        )
        # assertions
        assert point_mat.dropna(axis=1).sum(axis=1).round(2).to_list() ==\
            [-0.16, -0.18]
        assert point_mat.dropna(axis=1).sum(axis=0).round(2).to_list() ==\
            [-0.21, 0.01, -0.13]
        assert pvalue_mat.dropna(axis=1).mean(axis=1).round(2).to_list() ==\
            [0.47, 0.00]
        assert pvalue_mat.dropna(axis=1).mean(axis=0).round(2).to_list() ==\
            [0.13, 0.48, 0.10]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # with missings
    def test_extract_w_nan(self):
        data = examples.get_data('heatmap_data')
        # running extract
        point_mat, pvalue_mat = extract(
            data,
            exposure_col=UNames.mat_exposure,
            outcome_col=UNames.mat_outcome,
            point_col=UNames.mat_point,
            pvalue_col=UNames.mat_pvalue,
            dropna=False,
        )
        # assertions
        assert point_mat.sum(axis=1).round(2).to_list() ==\
            [-0.16, -0.18]
        assert point_mat.sum(axis=0).round(2).to_list() ==\
            [-0.21, 0.01, 0.0, -0.13]
        assert pvalue_mat.mean(axis=1).round(2).to_list() ==\
            [0.47, 0.00]
        assert pvalue_mat.fillna(0).mean(axis=0).round(2).to_list() ==\
            [0.13, 0.48, 0.0, 0.10]
    #######################################################################
    # test format_matrices function
    def test_format_matrices(self):
        point_mat = examples.get_data('heatmap_point_matrix')
        pvalue_mat = examples.get_data('heatmap_pvalue_matrix')
        # formatting
        values, annot_effect, _, _, _ =\
            format_matrices(point_mat, pvalue_mat,
                            sig=1.3, ptrun=16, digits='6', log=True)
        values2, _, annot_star, _, _ =\
            format_matrices(point_mat, pvalue_mat,
                            sig=0.05, ptrun=16, digits='2', log=False)
        values3, _, _, annot_pval, _ =\
            format_matrices(point_mat, pvalue_mat,
                            sig=0.3, ptrun=16, digits='2', log=True)
        assert values.iloc[:,3].tolist() == [-0.689009, 3.272177]
        assert values2.iloc[:,1].tolist() == [0.0, -0.95]
        assert values3.iloc[:,1].tolist() == [-0.02, 4.0]
        assert annot_effect.iloc[:,3].tolist() == ['.' '0.027800']
        assert annot_effect.iloc[:,2].tolist() == ['nan', 'nan']
        assert annot_star.iloc[:,1].tolist() == ['.', '★']
        assert annot_pval.iloc[:,1].tolist() == ['.', '4.0']

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Testing _calc_matrices
class TestCalcMatrices(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_correct_usage(self):
        data = examples.get_data('heatmap_data')
        r = 2
        # res 1
        res1 = calc_matrices(data, exposure_col=UNames.mat_exposure,
                             outcome_col=UNames.mat_outcome,
                             )
        assert res1.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [0.0, 2.58, 3.98, -1.68]
        assert res1.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '★', '★', '★']
        # res 2
        res2 = calc_matrices(data,
                             exposures_col=MHnames.name,
                             phenotypes_col=MHnames.index,
                             ptrun=2)
        assert res2.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [0.0, 1.31, 1.98, -1.4]
        assert res2.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '★', '★', '★']
        # res 3
        res3 = calc_matrices(data, alpha=0.5,
                             exposures_col=MHnames.name,
                             phenotypes_col=MHnames.index,
                             )
        assert res3.curated_matrix_annotation.iloc[1].to_list() == \
            ['.', '★', '.', '★']
        # res 4
        res4 = calc_matrices(data, alpha=0.001, without_log=True,
                             exposures_col=MHnames.name,
                             phenotypes_col=MHnames.index,
                             )
        assert res4.curated_matrix_value.sum(axis=0).round(r).to_list() == \
            [2.0, -0.2, -0.95, 0.24]
        assert res4.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '★', '★', '.']
        # res 5
        res5 = calc_matrices(data, sig_numbers=3, annotate='pvalues',
                             exposures_col=MHnames.name,
                             phenotypes_col=MHnames.index,
                             )
        assert res5.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '3.272', '4.0', '-2.281']
        # res6
        res6 = calc_matrices(data, sig_numbers=3, annotate='pvalues',
                             exposures_col=MHnames.name,
                             phenotypes_col='phenotype'
                             )
        assert res6.curated_matrix_annotation.iloc[0].to_list() == \
            ['.', '3.272', '4.0', '-2.281']



