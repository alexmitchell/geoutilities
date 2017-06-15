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

        # Set up option lists and dictionaries
        options = additional_options
        options.insert(0, ('--all' , self.do_all    , 'Execute all tasks.'))
        options.insert(0, ('--reload', self.force_reload, 'Forces the data to be reloaded.'))
        options.insert(0, ('--help', self.print_help, 'Print usage and option info'))
        options.insert(0, ('--pass', lambda: None, 'Pass without doing anything. Mostly for testing initialization stuff.'))
        self.help = '--help'
        self.all = '--all'
        self.reload = '--reload'
        self.pass_opt = '--pass'
        self.help_format = help_format

        self.option_dict = {}
        self.option_order = []
        self.messages = []
        for name, callback, info in options:
            self.option_dict[name] = callback
            self.option_order.append(name)
            self.messages.append([name, info])

        # Get command line arguments and parse/execute them
        args = sys.argv[1:] # first arg is file name; ignore it
        self.handle_args(args)

    def handle_args(self, args, skip_load=False):
        dict = self.option_dict

        if self.reload in args:
            dict[self.reload]()
            args.remove(self.reload)
        elif not skip_load:
            self.load_data()

        if self.help in args:
            dict[self.help]()
        elif self.all in args or not args:
            dict[self.all]()
        else:
            # Call list is only used so that invalid options are printed first.
            call_list = []
            for option in self.option_order:
                if option in args:
                    args.remove(option)
                    call_list.append(dict[option])

            for option in args:
                print('{} is not an option'.format(option))
            if args: dict[self.help]()

            for callback in call_list:
                callback()

    def load_data(self, reload=False):
        raise NotImplementedError

    def print_help(self):
        print()
        print('Available options are:')
        for option, info in self.messages:
            print(self.help_format.format(option=option, info=info))

    def do_all(self):
        print('Executing all tasks...')
        print()

        options = list(self.option_dict.keys())
        options.remove(self.help)
        options.remove(self.all)
        options.remove(self.reload)
        options.remove(self.pass_opt)
        if options:
            # Execute all options.
            self.handle_args(options, skip_load=True)
        else:
            # If no other options are defined, then print help and quit
            self.print_help()

    def force_reload(self):
        print("Reloading data")
        self.load_data(reload=True)

