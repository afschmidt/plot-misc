#!/usr/bin/env python3
import pandas as pd
from plot_misc.errors import (
    is_series_type,
    is_type,
)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestIs_Series_Type(object):
    '''
    Testing the `is_series_type` function
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_series_type(self):
        ser = pd.Series([1.0, 2.0], dtype = float)
        pad = pd.DataFrame({'col1':[1.0, 2.0], 'col2': [2, 4.3], })
        assert is_series_type(ser, float)
        assert is_series_type(pad, float)

