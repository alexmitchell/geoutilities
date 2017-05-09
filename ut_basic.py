#!/usr/bin/env python



VERBOSE = True

def printer(msg='', n=1):
    if VERBOSE:
        for _ in range(n):
            print(msg)

def isnumeric(obj):
    # Test whether an object is numeric or not.
    # Code is from some stack exchange answer.
    try:
        float(obj)
        return True
    except ValueError:
        return False


