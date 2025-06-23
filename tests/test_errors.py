import pytest
import pandas as pd
from types import SimpleNamespace
from plot_misc.errors import (
    is_type, is_df, are_columns_in_df,
    is_series_type, same_len, string_to_list,
    InputValidationError,
    _get_param_name,
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestIsType(object):
    # -------------------------------------------------------------------------
    def test_is_type_passes_on_correct_type(self):
        assert is_type(5, int) is True
        assert is_type("test", (str, list)) is True
    # -------------------------------------------------------------------------
    def test_is_type_raises_on_wrong_type(self):
        with pytest.raises(InputValidationError) as excinfo:
            is_type(5, str)
        assert "Expected any of" in str(excinfo.value)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestIsDF(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_is_df_valid(self):
        df = pd.DataFrame({'a': [1, 2]})
        assert is_df(df) is True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_is_df_invalid(self):
        with pytest.raises(InputValidationError):
            is_df([1, 2, 3])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestAreColumnsInDF(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_are_columns_in_df_valid(self):
        df = pd.DataFrame({'a': [1], 'b': [2]})
        assert are_columns_in_df(df, ['a']) is True
        assert are_columns_in_df(df, 'a') is True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_are_columns_in_df_missing_with_error(self):
        df = pd.DataFrame({'a': [1]})
        with pytest.raises(InputValidationError):
            are_columns_in_df(df, ['b'])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_are_columns_in_df_missing_with_warning(self):
        df = pd.DataFrame({'a': [1]})
        with pytest.warns(UserWarning):
            result = are_columns_in_df(df, ['b'], warning=True)
        assert result is False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestIsSeriesType(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_is_series_type_valid_series(self):
        s = pd.Series(['x', 'y'])
        assert is_series_type(s, str)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_is_series_type_valid_df(self):
        df = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        assert is_series_type(df, int)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_is_series_type_invalid_element_type(self):
        s = pd.Series(['x', 1])
        with pytest.raises(InputValidationError):
            is_series_type(s, str)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestSameLen(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_same_len_valid(self):
        assert same_len([1, 2], (3, 4)) is True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_same_len_invalid_lengths(self):
        with pytest.raises(ValueError):
            same_len([1, 2], [1])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestStringToList(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_string_to_list_wraps_string(self):
        assert string_to_list("abc") == ['a', 'b', 'c']
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_string_to_list_returns_object(self):
        assert string_to_list([1, 2]) == [1, 2]
        assert string_to_list(3.14) == 3.14

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestGetParamName(object):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_get_param_name_recovers_name(self):
        test_value = 42
        assert _get_param_name(test_value) is None
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_get_param_name_correct_frame(self):
        """
        We need to have an outer function that class a subsequent function
        which can be used to infer the passed object name.
        """
        test_value = 42
        def outer(x):
            return _get_param_name(x)
        assert outer(test_value) == 'test_value'
