"""
testing the `survival` module
"""
import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plot_misc.survival as pltm_surv
import plot_misc.example_data.examples as examples

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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class TestPlotTable:
    """Test cases for the plot_table function."""
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @pytest.fixture
    def sample_data(self):
        return examples.load_survival_table()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @pytest.fixture
    def fig_ax(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        return fig, ax
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_default(self, sample_data, fig_ax):
        """
        Test basic table plotting with a single string column.
        
        This test verifies that the function can handle:
        - Single string column input
        - Default parameter values
        - Proper text placement calls
        """
        _, ax = fig_ax
        # call function
        result_ax = pltm_surv.plot_table(
            data=sample_data,
            ax=ax,
            string_col='Not Discordant',
            x_col='time'
        )
        result_ax.set_xlim(-200, 6000)
        assert result_ax is ax
        # verify spines are hidden
        assert not ax.spines['top'].get_visible()
        assert not ax.spines['right'].get_visible()
        # verify y-axis has no tick labels (empty list)
        assert ax.get_yticklabels() == []
        # verify y-axis has no ticks
        assert len(ax.get_yticks()) == 0
        # verify x-axis has no tick labels when not specified
        assert ax.get_xticklabels() == []
        assert len(ax.get_xticks()) == 0
        # check that text objects were added to the axes
        text_objects = ax.texts
        assert len(text_objects) == len(sample_data)
        # Verify some text properties
        first_text = text_objects[0]
        assert first_text.get_text() == sample_data.iloc[0,1]
        assert first_text.get_horizontalalignment() == 'center'
        assert first_text.get_verticalalignment() == 'center'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_twogroups(self, sample_data, fig_ax):
        """
        Test table plotting with multiple string columns and custom parameters.
        
        This test verifies:
        - Multiple string columns handling
        - Custom y-tick labels
        - Custom positioning and formatting parameters
        - X-axis tick customisation
        """
        _, ax = fig_ax
        result_ax = pltm_surv.plot_table(
            data=sample_data,
            ax=ax,
            string_col=['Not Discordant', 'Discordant'],
            x_col='time',
            yloc=[0.7, 0.3],
            yticklabel=['Control Group', 'Treatment Group'],
            xticklabel=['Year 0', 'Year 5', 'Year 10', 'Year 15'],
            xtickloc=[0, 1826, 3652, 5478],
            size_text=12,
            halignment_text='left',
            pad_first=50.0,
            pad_last=25.0
        )
        assert result_ax is ax
        # check text objects were added for both columns
        text_objects = ax.texts
        expected_text_count = len(sample_data) * 2
        assert len(text_objects) == expected_text_count
        # x-axis ticks and labels
        x_ticks = ax.get_xticks()
        x_tick_labels = [lab.get_text() for lab in ax.get_xticklabels()]
        np.testing.assert_array_equal(x_ticks, [0, 1826, 3652, 5478])
        assert x_tick_labels == ['Year 0', 'Year 5', 'Year 10', 'Year 15']
        # y-axis labels
        y_tick_labels = [lab.get_text() for lab in ax.get_yticklabels()]
        assert y_tick_labels == ['Control Group', 'Treatment Group']
        # text alignment was applied
        sample_text = text_objects[0]
        assert sample_text.get_horizontalalignment() == 'left'
        assert sample_text.get_fontsize() == 12
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_errors(self, sample_data, fig_ax):
        """
        Test error handling for invalid parameter combinations.
        
        This test verifies:
        - ValueError for mismatched list lengths
        - Proper error messages
        - Input validation edge cases
        """
        fig, ax = fig_ax
        # Test mismatched yticklabel and string_col lengths
        with pytest.raises(ValueError,
                         match="`yticklabel` and `string_col` should have "
                               "the same number of elements."):
            pltm_surv.plot_table(
                data=sample_data,
                ax=ax,
                string_col=['Not Discordant', 'Discordant'],
                yticklabel=['Only One Label']  # Should be two labels
            )
        # Test mismatched yloc and string_col lengths
        with pytest.raises(ValueError,
                         match="`yloc` and `string_col` should have "
                               "the same number of elements."):
            pltm_surv.plot_table(
                data=sample_data,
                ax=ax,
                string_col=['Not Discordant', 'Discordant'],
                yloc=[0.5]  # Should be two positions
            )
        # Test xticklabel without xtickloc
        with pytest.raises(ValueError,
                         match="`xtickloc` should be supplied if "
                               "`xticklabel` is used."):
            pltm_surv.plot_table(
                data=sample_data,
                ax=ax,
                string_col='Not Discordant',
                xticklabel=['Year 0', 'Year 5']
                # Missing xtickloc
            )
        # Test mismatched xticklabel and xtickloc lengths
        with pytest.raises(ValueError):
            pltm_surv.plot_table(
                data=sample_data,
                ax=ax,
                string_col='Not Discordant',
                xticklabel=['Year 0', 'Year 5'],
                xtickloc=[0, 1826, 3652]  # Three locations, two labels
            )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @pytest.mark.parametrize("string_col_input,expected_text_count", [
        ('Not Discordant', 16),  # Single column, 16 data points
        (['Not Discordant'], 16),  # Single column as list, 16 data points
        (['Not Discordant', 'Discordant'], 32),  # Two columns, 32 total
    ])
    def test_string_col(self, sample_data, fig_ax,
                        string_col_input, expected_text_count):
        """
        Test that string_col parameter accepts both string and list inputs.
        """
        _, ax = fig_ax
        ax = pltm_surv.plot_table(
            data=sample_data,
            ax=ax,
            string_col=string_col_input,
            x_col='time'
        )
        # Verify the correct number of text objects were created
        text_objects = ax.texts
        assert len(text_objects) == expected_text_count
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_missings(self, fig_ax):
        """
        Test that the function handles NaN values in string columns gracefully.
        """
        _, ax = fig_ax
        # Create data with NaN values
        data_with_nan = pd.DataFrame({
            'time': [0, 365, 730],
            'values': ['100', np.nan, '200']
        })
        
        result_ax = pltm_surv.plot_table(
            data=data_with_nan,
            ax=ax,
            string_col='values',
            x_col='time'
        )
        # Verify function completes without error
        assert result_ax is ax
        # Check that NaN was converted to empty string
        text_objects = ax.texts
        text_values = [obj.get_text() for obj in text_objects]
        assert text_values == ['100', '', '200']
