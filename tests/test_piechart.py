"""
testing the `pychart` module
"""
import matplotlib.pyplot as plt
import plot_misc.example_data.examples as examples
import plot_misc.piechart as pychart
from matplotlib.text import Annotation
from matplotlib.colors import to_rgba

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# DATA
DATA = examples.load_percentage_data()
# CONSTANTS
CMTOINCH = 1/2.54


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# pychart
class TestPychart(object):
    """
    Testing the `pychart` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_pychart(self):
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        # plotting pychart
        _, ax = pychart.piechart(
            DATA, col_values='percentages', col_labels='labels',
            ax=ax, colours=['red', 'blue', 'green', 'yellow', 'purple', 'lightblue',
                    'orange'],
        )
        # asserting wedges have been plotted
        wedges = ax.patches
        for wedge in wedges:
            assert wedge.get_alpha() == 0.5
            assert wedge.get_edgecolor() == (0.0, 0.0, 0.0, 0.5)
            assert wedge.get_linewidth() == 0.5
            fcolor = wedge.get_facecolor()
            assert fcolor != to_rgba('black'), f"Found black wedge: {fcolor}"
        # assert the labels
        annot = [t for t in ax.texts if isinstance(t, Annotation)]
        assert len(annot) == DATA.shape[0]
        for ann in annot:
            assert ann.get_text(), "Annotation text is empty"

