import pandas as pd


def read_optical_fitted_table(filename):
    data = pd.read_csv(filename, header=None, delim_whitespace=True, comment='#')

    return data
