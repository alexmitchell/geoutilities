#!/usr/bin/env python

from ut_misc import printer

import pandas as pd
import os

import logger as logger_module
from helpyr_misc import ensure_dir_exists

class DataLoader:

    def __init__(self, data_dir, pickle_dir, logger=None):
        self.data_dir = data_dir
        self.pickle_dir = pickle_dir
        self.pickle_path = os.path.join(pickle_dir, '{}.pkl')
        self.logger = logger

        ensure_dir_exists(self.pickle_dir, self.logger)

    def is_pickled(self, *names):
        # Check to see if there is a pickled-data file

        names = [names] if isinstance(names, str) else names # force names to be a list
        plural = ["s", ""] if len(names) > 1 else ["","s"]
        msg = f"Checking if pickle{plural[0]} {names} exist{plural[1]}..."
        printer(msg, logger=self.logger)
        path = self.pickle_path
        isfile = os.path.isfile
        return all([isfile(path.format(name)) for name in names])

    def load_pickle(self, name, add_path=True):
        # Load pickle data
        pickle_path = self.pickle_path.format(name) if add_path else name
        return pd.read_pickle(pickle_path)

    def load_pickles(self, names, add_path=True):
        # Load pickle data store in dict
        output = {}
        for name in names:
            output[name] = self.load_pickle(name, add_path)
        return output

    def load_xlsx(self, filename, pd_kwargs, is_path=False):
        filepath = filename if is_path else os.path.join(self.data_dir, filename)

        data = pd.read_excel(filepath, **pd_kwargs)
        return data

    def load_csv(self, filename, flip=False, **kwargs):
        kwargs['delimiter'] = ','
        return self.load_txt(filename, flip=flip, **kwargs)

    def load_txt(self, filename, flip=False, **kwargs):
    #def load_txt(self, filename, skiprows, skipfooter, flip=False, delimiter='\s*'):
        filepath = os.path.join(self.data_dir, filename)

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
        # prepickles is a dictionary of {'filename':data}
        msg = "Performing pickling process..."
        printer(msg, logger=self.logger)
        for name in prepickles:
            pickle_path = self.pickle_path.format(name)
            printer(f"Making pickle {name} at {pickle_path}",
                    logger=self.logger)
            prepickles[name].to_pickle(pickle_path)

        printer("Pickles produced!", logger=self.logger)

