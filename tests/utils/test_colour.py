import re
import pytest
from plot_misc.utils.colour import Colours


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
HEX_PATTERN = re.compile(r'^#(?:[0-9a-fA-F]{6})$')

@pytest.mark.parametrize("palette_name", [
    'diverse20',
    'sweetie',
    'pico8',
    'vanilamilkshake',
    'chembl_red',
    'chembl_green',
    'gwas_catalog',
    'bnf',
    'distinct8'
])
def test_colour_palette(palette_name):
    """
    Ensures that:
    - That each palette is a list of hex colour codes.
    - That all items in each palette are valid hex strings.
    - That the palette has at least one colour (i.e. non-empty).
    """
    palettes = Colours()
    palette = getattr(palettes, palette_name)
    assert isinstance(palette, list), f"{palette_name} should return a list"
    assert len(palette) > 0, f"{palette_name} should not be empty"
    for colour in palette:
        assert isinstance(colour, str), f"{palette_name} contains non-string entry"
        assert HEX_PATTERN.match(colour), f"{palette_name} has invalid hex code: {colour}"
