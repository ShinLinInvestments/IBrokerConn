import pandas as pd

def read_csv(path_prefix:str, datetimes:list):
    filenames = [path_prefix + x + '.csv' for x in datetimes]
    res = pd.DataFrame()
    for x in map(pd.read_csv, filenames):
        res = pd.concat([res, x])
    res.index = list(range(len(res)))
    return res

def write_csv(data_table:pd.DataFrame, path_prefix, col_datetime):
    if len(data_table) == 0: return
    assert col_datetime in data_table.columns.values
    all_dts = data_table[col_datetime]
    print(type(all_dts))

