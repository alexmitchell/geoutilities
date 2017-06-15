#!/usr/bin/env python

from .ut_basic import printer

import pandas as pd
import os

class DataLoader:

    def __init__(self, data_path, pickle_path):
        self.data_path = data_path
        self.pickle_path = pickle_path
        self.pickle_path_str = pickle_path + '{}.pkl'

    def is_pickled(self, *names):
        # Check to see if there is a pickled-data file

        names = [names] if isinstance(names, str) else names # force names to be a list
        plural = ["s", ""] if len(names) > 1 else ["","s"]
        printer("Checking if pickle{0} {names} exist{1}...".format(*plural, names=list(names)))
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

    def load_csv(self, filename, flip=False, **kwargs):
        kwargs['delimiter'] = ','
        return self.load_txt(filename, flip=flip, **kwargs)

    def load_txt(self, filename, flip=False, **kwargs):
    #def load_txt(self, filename, skiprows, skipfooter, flip=False, delimiter='\s*'):
        filepath = self.data_path + filename

        # Some default parameters
        keys = kwargs.keys()
        if 'engine' not in keys:
            kwargs['engine'] = 'python'
        if 'dtype' not in keys:
            kwargs['dtype'] = None
        if 'index_col' not in keys:
            kwargs['index_col'] = 0
        if 'delimiter' not in keys:
            kwargs['delimiter'] = '\s*'

        data = pd.read_csv(filepath, **kwargs)

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


