#!/usr/bin/env python



VERBOSE = True

def printer(msg='', n=1, logger=None):
    msgs = msg*n
    if logger is None:
        if VERBOSE:
            for msg in msgs:
                print(msg)
    else:
        logger.write(msgs)

def isnumeric(obj):
    # Test whether an object is numeric or not.
    # Code is from some stack exchange answer.
    try:
        float(obj)
        return True
    except ValueError:
        return False


