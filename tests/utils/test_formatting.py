#!/usr/bin/env python3

import numpy as np
from plot_misc.utils.formatting import(
    format_roc,
)
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

