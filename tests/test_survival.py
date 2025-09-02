"""
testing the `survival` module
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.survival as pltm_surv
import plot_misc.example_data.examples as examples

sample_data = examples.create_survival_data(nrows=20, random_seed=42)
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestPlotStepWise:
    """Test suite for the plot_step_wise function."""
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @pytest.fixture
    def sample_data(self):
        """Create sample survival data for testing."""
        return examples.create_survival_data(nrows=20, random_seed=42)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self, sample_data):
        fig, ax = pltm_surv.plot_step_wise(sample_data, 'survival_estimate')
        # check return types
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        # check that the plot has data
        lines = ax.get_lines()
        assert len(lines) >= 1
        # check that the line has step-wise appearance (more than 2 points)
        line_data = lines[0].get_xydata()
        assert line_data.shape[0] > 2
        # Verify x-axis uses index values (time)
        expected_x_values = sample_data.index.values
        plotted_x_values = line_data[:len(expected_x_values), 0]
        np.testing.assert_array_almost_equal(
            plotted_x_values, expected_x_values,
        )
        plt.close(fig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_confidence_intervals_and_fill(self, sample_data):
        # Call function with confidence intervals and fill
        fig, ax = pltm_surv.plot_step_wise(
            sample_data, 'survival_estimate',
            lower_ci_col='lower_ci_95',
            upper_ci_col='upper_ci_95',
            fill=True,
            fill_alpha=0.3
        )
        # check that we have multiple lines (main + 2 CI lines)
        lines = ax.get_lines()
        assert len(lines) == 3
        # check that fill area exists
        collections = ax.collections
        assert len(collections) == 1
        # verify fill properties
        fill_collection = collections[0]
        assert fill_collection.get_alpha() == 0.3
        # Clean up
        plt.close(fig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_custom_styling_and_parameters(self, sample_data):
        custom_kwargs = {
            'line_colour': 'red',
            'line_width': 3,
            'line_style': '--',
            'line_colour_ci': 'blue',
            'line_width_ci': 1.5,
            'fill_colour': 'green',
            'figsize': (8, 6),
            'xlim': (0, 50)
        }
        fig, ax = pltm_surv.plot_step_wise(
            sample_data, 'survival_estimate',
            lower_ci_col='lower_ci_95',
            upper_ci_col='upper_ci_95',
            fill=True,
            **custom_kwargs
        )
        # check figure size
        fig_size = fig.get_size_inches()
        np.testing.assert_array_equal(
            fig_size, [8, 6],
        )
        # check x-axis limits
        xlim = ax.get_xlim()
        assert xlim[0] == 0 and xlim[1] == 50
        # check main line properties
        main_line = ax.get_lines()[0]
        assert main_line.get_color() == 'red'
        assert main_line.get_linewidth() == 3
        assert main_line.get_linestyle() == '--'
        # check CI line properties (should be blue)
        ci_lines = ax.get_lines()[1:]  # Skip main line
        for ci_line in ci_lines:
            assert ci_line.get_color() == 'blue'
            assert ci_line.get_linewidth() == 1.5
        # Clean up
        plt.close(fig)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_add_to_existing_axes(self, sample_data):
        # create initial plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.set_title("Existing Plot")
        # add step-wise plot to existing axes
        returned_fig, returned_ax = pltm_surv.plot_step_wise(
            sample_data, 'survival_estimate',
            ax=ax,
            add=True,
            line_colour='purple'
        )
        # check that the same figure and axes are returned
        assert returned_fig is fig
        assert returned_ax is ax
        # check that title is preserved (axes properties not modified)
        assert ax.get_title() == "Existing Plot"
        # check that the plot was added
        lines = ax.get_lines()
        assert len(lines) >= 1
        assert lines[0].get_color() == 'purple'
        # test error case: add=True without providing ax
        with pytest.raises(ValueError, match="please supply an `ax`"):
            pltm_surv.plot_step_wise(
                sample_data, 'survival_estimate',
                add=True
            )
        # Clean up
        plt.close(fig)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestExtractFollowUp:
    """Test suite for the extract_follow_up function."""
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @pytest.fixture
    def sample_data(self):
        """Create sample survival data for testing using examples module."""
        return examples.create_survival_data(nrows=24)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self, sample_data):
        result = pltm_surv.extract_follow_up(sample_data, 'at_risk', points=5)
        # data structure
        expected_columns = ['time', 'group_1_at_risk',
                           'group_1_at_risk_format', 'group_1_raw_time']
        assert list(result.columns) == expected_columns
        assert len(result) == 5
        # check that time points are integers and in ascending order
        time_values = result['time'].values
        assert all(isinstance(t, (int, np.integer)) for t in time_values)
        assert np.all(time_values[:-1] <= time_values[1:])
        # check that raw_time values correspond to actual data times
        raw_times = result['group_1_raw_time'].values
        data_times = sample_data.index.values
        for raw_time in raw_times:
            assert raw_time in data_times
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_specific_time_points(self, sample_data):
        # Define specific time points including edge cases
        min_time = sample_data.index.min()
        max_time = sample_data.index.max()
        specific_points = [
            float(min_time),        # Exact start time
            min_time + 10,          # Early time
            (min_time + max_time) / 2,  # Middle time
            max_time - 5,           # Late time within range
            float(max_time),        # Exact end time
            max_time + 20           # Beyond study range
        ]
        # Test with custom output column name
        result = pltm_surv.extract_follow_up(
            sample_data, 'at_risk',
            points=specific_points,
            output_col='treatment_group'
        )
        # correct rows
        assert len(result) == len(specific_points)
        # column names
        expected_columns = ['time', 'treatment_group_at_risk',
                           'treatment_group_at_risk_format',
                           'treatment_group_raw_time']
        assert list(result.columns) == expected_columns
        # check times within range
        within_range_mask =\
            (result['time'] >= min_time) & (result['time'] <= max_time)
        within_range_results = result[within_range_mask]
        within_range_at_risk =\
            within_range_results['treatment_group_at_risk'].values
        assert np.all(within_range_at_risk > 0)
        # time points beyond data range
        beyond_range_mask = result['time'] > max_time
        if beyond_range_mask.any():
            beyond_range_at_risk = result.loc[beyond_range_mask,
                                              'treatment_group_at_risk']
            assert np.all(beyond_range_at_risk == 0)
        # First time point should match exactly
        first_result_idx = result['time'].idxmin()
        first_raw_time = result.loc[
            first_result_idx, 'treatment_group_raw_time']
        assert abs(first_raw_time - min_time) < 1e-10
        # Test error case: time point before data range
        early_point = min_time - 10
        with pytest.raises(ValueError, match="before the first observation"):
            pltm_surv.extract_follow_up(
                sample_data, 'at_risk', points=[early_point])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_custom_formatting_and_parameters(self, sample_data):
        # ### Test 1: with custom thousands separator (European style)
        specific_points = [0, 25, 50, 75, 100]
        result = pltm_surv.extract_follow_up(
            sample_data, 'at_risk',
            points=specific_points,
            output_col='european_group',
            thousands_sep=' '  # Space separator
        )
        # Check that space separator is used for large numbers
        formatted_values = result['european_group_at_risk_format'].values
        raw_values = result['european_group_at_risk'].values
        for raw, formatted in zip(raw_values, formatted_values):
            if raw >= 1000:
                assert ' ' in formatted
                # Check that comma is not present
                assert ',' not in formatted
        # ### Test 2: using explicit time column instead of index
        data_with_time_col = sample_data.reset_index()
        data_with_time_col.rename(columns={'time': 'follow_up_time'}, inplace=True)
        result_time_col = pltm_surv.extract_follow_up(
            data_with_time_col, 'at_risk',
            time_col='follow_up_time',
            points=3,
            output_col='time_col_test'
        )
        # Should produce same structure as index-based approach
        assert len(result_time_col) == 3
        assert 'time_col_test_at_risk' in result_time_col.columns
        time_values = result_time_col['time'].values
        original_time_range = data_with_time_col['follow_up_time']
        assert time_values[0] >= original_time_range.min()
        assert time_values[-1] <= original_time_range.max()
        # ### Test 3: edge case: single time point
        single_point_result = pltm_surv.extract_follow_up(
            sample_data, 'at_risk', points=[50.0]
        )
        assert len(single_point_result) == 1
        assert single_point_result['group_1_at_risk'].iloc[0] >= 0
