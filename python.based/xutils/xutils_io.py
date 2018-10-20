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

##
def check_path_prefix(path_prefix:str):
    path_last_dir = os.path.dirname(path_prefix)
    if not os.path.exists(path_last_dir):
        os.mkdir(path_last_dir)
    return

def read_csv(path_prefix:str, datetimes:list):
    filenames = [path_prefix + x + '.csv' for x in datetimes]
    res = pd.DataFrame()
    for x in map(pd.read_csv, filenames):
        res = pd.concat([res, x])
    res.index = list(range(len(res)))
    return res

def _write_single_csv(data_table:pd.DataFrame, rows_to_print:int, path_output:str, index = False):
    data_table.loc[rows_to_print].to_csv(path_output, index=index, quoting=1)
    xlog.info("Wrote " + str(sum(rows_to_print)) + " rows to " + path_output)

def write_csv(df:pd.DataFrame, path_prefix, col_datetime, file_freq:int = 8, index = False,
              num_cores = xutils_num_cores):
    if len(df) == 0: return
    check_path_prefix(path_prefix)
    if col_datetime in df.index.names:
        df = df.reset_index()
    assert col_datetime in df.columns.values, col_datetime + " not in column of df"
    all_dtss = np.vectorize(lambda x : x[:file_freq])(df[col_datetime])
    all_dts = np.unique(all_dtss)
    xlog.info("Planning to write " + str(len(all_dts)) + " files for: " + ','.join(all_dts))
    for x in all_dts:
        _write_single_csv(df, (all_dtss == x), path_prefix + x + '.csv', index=index)

