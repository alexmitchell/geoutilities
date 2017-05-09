#!/usr/bin/env python

from ut_basic import printer

import pandas as pd
import os

class DataLoader:

    def __init__(self, data_path):
        self.data_path = data_path
        self.pickle_path_str = data_path + '{}.pkl'

    def is_pickled(self, names):
        # Check to see if there is a pickled-data file

        printer("Checking if pickles exist...")
        path = self.pickle_path_str
        isfile = os.path.isfile
        return all([isfile(path.format(name)) for name in names])

    def load_pickle(self, name):
        # Load pickle data
        pickle_path = self.pickle_path_str.format(name)
        return pd.read_pickle(pickle_path)

    def load_xlsx(self, filename, pd_kwargs):
        filepath = self.data_path + filename

        data = pd.read_excel(filepath, **pd_kwargs)
        return data

    def load_csv(self, filename, skiprows, skipfooter, flip=False):
        filepath = self.data_path + filename

        data = pd.read_csv(filepath, engine='python', dtype=None,
                delimiter=',', index_col=0,
                skiprows=skiprows, skipfooter=skipfooter)

        if flip:
            return data.iloc[::-1]
        else:
            return data

    def produce_pickles(self, prepickles):
        # Pickle things so I don't have to keep rereading excel files
        # prepickles is a dictionary of {'name':data}
        printer(" Performing pickling process...")
        for name in prepickles:
            pickle_path = self.pickle_path_str.format(name)
            prepickles[name].to_pickle(pickle_path)

        printer(" Pickles produced!")


