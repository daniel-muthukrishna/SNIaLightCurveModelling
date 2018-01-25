import pandas as pd


def read_optical_fitted_table(filename):
    """ Read in optical parameters as a pandas DataFrame. """
    data = pd.read_csv(filename, header=None, delim_whitespace=True, comment='#')

    return data
