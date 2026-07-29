"""
plot-misc: matplotlib-based plotting archetypes for scientific figures.

A curated collection of user-oriented plotting functions and
classes built on top of `matplotlib`. Each function returns standard
matplotlib `Figure`/`Axes` objects, so results can be further customised
with familiar matplotlib methods. Per the package design callables are limited
to creating illustrations, and should data be internally calculated this is
done with options for user overwrites, while making the derived data available
for inspection and reuse.
"""
from ._version import __version__

__citation__ = (
    "Schmidt AF, Hukerikar N, Finan C, van Vugt M. Effective visualization "
    "of biomedical data using plot-misc. Bioinformatics Advances. "
    "2026;6(1):vbag184. https://doi.org/10.1093/bioadv/vbag184"
)
