import numpy as np
from plot_misc.utils.formatting import(
    format_roc,
    format_estimates,
    sci_notation,
    string_interval,
    _nlog10_func,
    _superscriptinate,
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_nlog10_func(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert all(
            np.round(_nlog10_func(np.array([0.1, 0.2])), 4) ==\
            np.array([1.     , 0.699])
        )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_zeros(self):
        assert all(
            np.round(_nlog10_func(np.array([1.0, 0.1, 0.2])), 4) ==\
            np.array([0.0, 1.     , 0.699])
        )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_nlog10_func(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert format_estimates(0.2, 0.01) == '0.20 (0.18; 0.22)'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_params(self):
        assert format_estimates(0.2, 0.01, round=3) == '0.200 (0.180; 0.220)'
        assert format_estimates(0.2, 0.01, round=3) == '0.200 (0.180; 0.220)'
        assert format_estimates(0.2, 0.01, alpha=0.2) == '0.20 (0.19; 0.21)'
        assert format_estimates(0.2, 0.01, exp=True) == '1.22 (1.20; 1.25)'
        assert format_estimates(0.2, lower=0.15, upper=0.35123) ==\
            '0.20 (0.15; 0.35)'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_format_roc(object):
    '''
    Testing functions for the `format_roc` function.
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_format_roc_default_and_weighted(self):
        observed = np.array([[1, 0, 0, 0, 1, 0, 0, 0]]).T
        predicted = np.array([[0.3, 0.1, -0.2, 0.11, 0.25,0.001, 0.31, 0.02]]).T
        sample_weights = np.array([[10,1, 2, 20, 1,  2, 2, 2]]).T
        # results
        res1 = format_roc(observed, predicted)
        res2 = format_roc(observed, predicted, sample_weight=sample_weights)
        # assert
        assert res1.mean().round(2).tolist() == [0.33, 0.5, np.inf]
        assert res2.mean().round(2).tolist() == [0.39, 0.7, np.inf]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_superscriptinate(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert _superscriptinate('4') == '⁴'
        assert _superscriptinate('-5') == '⁻⁵'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_sci_notation(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert sci_notation(1256) == '1.26×10³'
        assert sci_notation(0.00125) == '1.25×10⁻³'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_params(self):
        assert sci_notation(0.0012545, sig_fig=4) == '1.2545×10⁻³'
        assert sci_notation(0.0012545, min=0.01) == '1.00×10⁻²'
        assert sci_notation(101, max=10) == '1.00×10¹'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Test_string_interval(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self):
        assert string_interval([0.2, 0.5, 1.0], lower_lim=0.0, sep=' p ') ==\
            ['0.0 < p ≤ 0.2', '< 0.5', '≤ 1.0']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=None) ==\
            ['≤ 0.2', '< 0.5', '≤ 1.0']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=0.0, middle=True) ==\
            ['0.1', '0.35', '0.75']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=None, middle=True) ==\
            ['≤ 0.2', '0.35', '0.75']
        assert string_interval([0.2, 0.5, 1.0, np.inf], lower_lim=None,
                               middle=True) ==\
            ['≤ 0.2', '0.35', '0.75', '> 1.0']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=0.0, middle=False,
                               int_notation=True) ==\
            ['(0.0, 0.2]', '(0.2, 0.5]', '(0.5, 1.0]']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=None, middle=False,
                               int_notation=True) ==\
            ['(-inf, 0.2]', '(0.2, 0.5]', '(0.5, 1.0]']
        assert string_interval([0.2, 0.5, 1.0], lower_lim=None, middle=False,
                               int_notation=True, sep=',') ==\
            ['(-inf,0.2]', '(0.2,0.5]', '(0.5,1.0]']
        assert string_interval([0.2, 0.5, 1.0, np.inf], lower_lim=0.0,
                               middle=False, int_notation=True) ==\
            ['(0.0, 0.2]', '(0.2, 0.5]', '(0.5, 1.0]', '(1.0, inf)']
        assert string_interval([0.2, 0.5, 1.0, np.inf], middle=False,
                               int_notation=True) ==\
            ['(-inf, 0.2]', '(0.2, 0.5]', '(0.5, 1.0]', '(1.0, inf)']
