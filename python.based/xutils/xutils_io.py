import pandas as pd
import os

def read_csv(path_prefix, sdatetime, edatetime):
    filenames = os.listdir(path_prefix)

def write_csv(data_table:pd.DataFrame, path_prefix, col_datetime):
    assert col_datetime in data_table.columns.values
    all_dts = data_table[col_datetime]
    
