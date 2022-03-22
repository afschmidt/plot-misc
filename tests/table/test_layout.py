"""
testing extract_compressed
"""
import pytest
import pandas as pd
import numpy as np
import warnings
from plot_misc.example_data import examples
from plot_misc.table import layout
from plot_misc.constants import TableNames


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class Test_formatting(object):
    """
    Description
    ----------
    Formats a table
    
    Depends on
    ----------
    
    Note
    ----
    
    """
    ###########################################################################
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_noformatting(self):
        '''
        Returns the same table if no formatting is applied
        '''
        table = examples.load_table_data()
        res = layout.formatting(table)
        assert res.shape == table.shape
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_strip_string(self, tmp_path):
        table = examples.load_table_data()
        check1 = table[TableNames.analysis].iloc[0]
        table[TableNames.analysis] = table[TableNames.analysis] + '     '
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # correct
        res = layout.formatting(table.copy(),
                                [TableNames.index, TableNames.analysis])
        assert res[TableNames.analysis].iloc[0] == check1
        # wrong input
        with pytest.raises(AttributeError):
            res = layout.formatting(table, [TableNames.index,
                                            TableNames.pvalue])
        # single column
        res = layout.formatting(table, [TableNames.analysis])
        assert res[TableNames.analysis].iloc[0] == check1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_replace_string(self, tmp_path):
        table = examples.load_table_data()
        # dictionary
        dict1 = {TableNames.exposure: ['_.*', ''],
                 TableNames.analysis: [r'\.tar', 'HELLO']
                 }
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        res = layout.formatting(table,
                                replace_string_columns=dict1
                                )
        assert (res[TableNames.analysis] == 'yang_sapHELLO.gz').all()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_rename(self, tmp_path):
        table = examples.load_table_data()
        # dictionary
        dict1 = {TableNames.pvalue: 'p-value',
                 TableNames.analysis: 'anal'
                 }
        # with drop true
        res = layout.formatting(table, rename_columns=dict1)
        assert 'anal' in list(res.columns)
        assert 'p-value' in list(res.columns)
        assert not 'pvalue' in list(res.columns)
        # with drop false
        res = layout.formatting(table, rename_columns=dict1,
                                drop_original=False)
        assert 'anal' in list(res.columns)
        assert 'p-value' in list(res.columns)
        assert TableNames.pvalue in list(res.columns)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_log10(self):
        warnings.filterwarnings('ignore')
        table = examples.load_table_data()
        # overwriting the same column
        res = layout.formatting(table, log10_columns=[TableNames.pvalue])
        assert res[TableNames.pvalue].max() > 1
        # renaming original and log10
        res = layout.formatting(table, log10_columns=[TableNames.pvalue],
                                rename_columns={
                                    TableNames.pvalue: 'pval_original'},
                                drop_original=False,
                                )
        assert 'pval_original' in list(res.columns)
        assert res[TableNames.pvalue].max() > 1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_order(self):
        table = examples.load_table_data()
        test1 = ['ld', 'qpvalue', 'se']
        res = layout.formatting(table, order_columns=test1)
        assert (res.columns[0:3] == test1).all()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def test_rename_column_values(self):
        table = examples.load_table_data()
        map = {'outcome': {'ldl_glgc': 'LDL-C', 'hdl_glgc': 'HDL-C'}}
        res = layout.formatting(table, rename_column_values=map)
        assert list(res['outcome'].unique()) == ['LDL-C', 'HDL-C', np.nan]

