#!/usr/bin/env python

import sys

class TaskManager:

    # A minimal task manager that handles command line arguments and 
    # automatically calls provided function callbacks. This class should be 
    # inherited and then expanded for the specific project by including 
    # additional options (see __init__ for more info) and defining callback 
    # functions for those options. Help and All options are provided by 
    # default, look at those for examples.

    def __init__(self, additional_options, help_format='{option:<30}{info}'):
        # Automatically load data, parse command line options, and execute 
        # tasks in the specified order. If no argument is given, it is assumed 
        # to execute all options.
        #
        ## args is a list of command line arguments (use sys.argv)
        #
        # additional_options should be an ordered list of tuples (argument 
        # name, function callback, and help info). The order will be the 
        # execution order. Help and all options will be added in front.
        #
        # help_format should be a formatting string with only option and info 
        # as format variables. Default has options left aligned and 30 chars 
        # wide.

        # Load data. User does not have to define a new load_data function, but 
        # it will be automatically called if they do
        self.load_data()

        # Set up option lists and dictionaries
        options = additional_options
        options.insert(0, ('--all' , self.do_all    , 'Execute all tasks.'))
        options.insert(0, ('--help', self.print_help, 'Print usage and option info'))
        self.help = '--help'
        self.all = '--all'
        self.help_format = help_format

        self.option_dict = {}
        self.option_order = []
        self.messages = []
        for name, callback, info in options:
            self.option_dict[name] = callback
            self.option_order.append(name)
            self.messages.append(name, info)

        # Get command line arguments and parse/execute them
        args = sys.argv
        self.handle_args(args)

    def load_data(self):
        pass

    def handle_args(self, args):
        dict = self.option_dict
        
        if self.help in args:
            dict[self.help]()
        elif self.all in args or not args[1:]:
            self.do_all()
        else:
            for option in self.option_order:
                dict[option]() if option in args

    def print_help(self, messages=[]):
        for option, info in self.messages:
            print(self.help_format.format(option, info))

    def do_all(self):
        print('Executing all tasks...')
        print()

        options = list(self.option_dict.keys())
        options.remove(self.help)
        options.remove(self.all)
        self.handle_args(options)


