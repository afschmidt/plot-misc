"""
testing the `pychart` module
"""
import matplotlib.pyplot as plt
import plot_misc.example_data.examples as examples
import plot_misc.piechart as pychart
from matplotlib.text import Annotation
from matplotlib.patches import Wedge
from matplotlib.colors import to_rgba
from numpy import cos, sin, deg2rad, sign

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# constants
CMTOINCH = 1/2.54


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# pychart
class TestPychart(object):
    """
    Testing the `pychart` function.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_pychart(self):
        DATA = examples.load_percentage_data()
        # plotting
        _, ax = plt.subplots(1, figsize=(15*CMTOINCH, 15*CMTOINCH))
        # plotting pychart
        _, ax = pychart.piechart(
            DATA, col_values='percentages', col_labels='labels',
            ax=ax, colours=['red', 'blue', 'green', 'yellow', 'purple',
                            'lightblue', 'orange'],
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
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_pychart_position(self):
        scl = (1.8, 1.4)
        df = examples.load_percentage_data()
        lt='TTN (10.0%)'
        explode = [0.2 if l == lt else 0.0 for l in df['labels']]
        # adjust the xy text position for the exploded wedge
        xyp_s = [scl if l == lt else (1.15, 1.15) for l in df['labels']]
        # plotting
        _, ax = pychart.piechart(
            df, col_values='percentages', col_labels='labels',
            text_pos_scaling = xyp_s, pie_kwargs={'explode': explode})
        # confirming the scaling was applied
        idx = list(df.index[df['labels'] == lt])[0]
        wedges = [p for p in ax.patches if isinstance(p, Wedge)]
        target_wedge = wedges[idx]
        assert target_wedge.center != (0, 0), \
            f"Wedge '{label_text}' is not exploded (center = {target_wedge.center})"
        # confirm the explsion was applied
        annotations = [t for t in ax.texts if isinstance(t, Annotation)]
        target_ann = [a for a in annotations if a.get_text() == lt][0]
        angle_rad = deg2rad((target_wedge.theta1 + target_wedge.theta2) / 2)
        x, y = cos(angle_rad), sin(angle_rad)
        assert target_ann.get_position() == (scl[0] * sign(x),scl[1] * y)
