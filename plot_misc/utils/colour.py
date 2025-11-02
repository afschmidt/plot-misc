"""
Curated colour palettes for data visualisation.

This module provides a collection of predefined colour palettes for use in
matplotlib plots and other visualisations. The palettes are designed to cover
a variety of use cases, including high-contrast schemes, pastel tones, and
domain-specific colours inspired by resources such as the GWAS catalog or the
British National Formulary (BNF).

Classes
-------
Colours
    A container for commonly used colour palettes, exposed as read-only
    properties.
"""

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Colours(object):
    """
    Container for curated colour palettes used in visualisation.
    
    Provides access to a variety of named colour palettes, each returned as a
    list of hexadecimal colour codes. These palettes can be used in matplotlib
    or other plotting libraries to ensure consistent, visually distinct styles.
    
    All palettes are exposed as read-only properties
    """
    # /////////////////////////////////////////////////////////////////////////
    @property
    def diverse20(self):
        """
        A palette of 20 diverse colors.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4',
            '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080', '#e6beff',
            '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
            '#000080', '#808080', '#ffffff', '#000000'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def sweetie(self):
        """
        Sweetie color palette with contrasting tones.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#1a1c2c', '#5d275d', '#b13e53', '#ef7d57', '#ffcd75', '#a7f070',
            '#38b764', '#257179', '#29366f', '#3b5dc9', '#41a6f6', '#73eff7',
            '#f4f4f4', '#94b0c2', '#566c86', '#333c57'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def pico8(self):
        """
        Pico-8 color palette for retro-inspired visuals.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#000000', '#1D2B53', '#7E2553', '#008751', '#AB5236', '#5F574F',
            '#C2C3C7', '#FFF1E8', '#FF004D', '#FFA300', '#FFEC27', '#00E436',
            '#29ADFF', '#83769C', '#FF77A8', '#FFCCAA'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def vanilamilkshake(self):
        """
        Vanilla milkshake color palette with soft pastels.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#28282e', '#6c5671', '#d9c8bf', '#f98284', '#b0a9e4', '#accce4',
            '#b3e3da', '#feaae4', '#87a889', '#b0eb93', '#e9f59d', '#ffe6c6',
            '#dea38b', '#ffc384', '#fff7a0', '#fff7e4'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def chembl_red(self):
        """
        ChEMBL-inspired red color palette.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return ['#E485A0', '#B83C5F', '#82203B']
    # /////////////////////////////////////////////////////////////////////////
    @property
    def chembl_green(self):
        """
        ChEMBL-inspired green color palette.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return ['#9BD8D5', '#64A0A4', '#395F65', '#224044']
    # /////////////////////////////////////////////////////////////////////////
    @property
    def gwas_catalog(self):
        """
        GWAS catalog color palette with earthy tones.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return ['#C4C4C4', '#8AA19C', '#A8B486', '#D0C290', '#D1AD8F',
                '#B36387',
                ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def bnf(self):
        """
        British National Formulary (BNF) color palette with strong hues.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#CB422A', '#DF931E', '#569BBB', '#EADA30', '#A2B229', '#B12137',
            '#5394B6', '#665987', '#D09F21'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def distinct8(self):
        """
        Eight distinct colours.
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#E6194B', '#F58231', '#FFE119', '#BFEF45', '#3CB44B',
            '#42D4F4', '#4363D8', '#911EB4',
        ]
        # /////////////////////////////////////////////////////////////////////////
    @property
    def green9(self):
        """
        Green9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476',
            '#41ab5d', '#238b45', '#006d2c', '#00441b'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def purple9(self):
        """
        Purple9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8',
            '#807dba', '#6a51a3', '#54278f', '#3f007d'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def blue9(self):
        """
        Blue9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6',
            '#4292c6', '#2171b5', '#08519c', '#08306b'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def red9(self):
        """
        Red9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
            '#ef3b2c', '#cb181d', '#a50f15', '#67000d'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def orange9(self):
        """
        Orange9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c',
            '#f16913', '#d94801', '#a63603', '#7f2704'
        ]
    # /////////////////////////////////////////////////////////////////////////
    @property
    def black9(self):
        """
        Black9 palette (ColorBrewer sequential scheme).
        
        Returns
        -------
        list of str
            Hex color codes.
        """
        return [
            '#ffffff', '#f0f0f0', '#d9d9d9', '#bdbdbd', '#969696',
            '#737373', '#525252', '#252525', '#000000'
        ]
        

