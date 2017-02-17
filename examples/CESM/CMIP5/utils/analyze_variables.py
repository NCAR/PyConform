#!/usr/bin/env python
"""
analyze_variables

Command-Line Utility to analyze variable metadata in CMIP5 data

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import json
from netCDF4 import Dataset
from glob import glob
from os import listdir, linesep
from os.path import isdir, join as pjoin
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Analyze variable metadata of CMIP5 data')

#===================================================================================================
# cli - Command-Line Interface
#===================================================================================================
def cli(argv=None):
    """
    Command-Line Interface
    """
    return __PARSER__.parse_args(argv)


#===================================================================================================
# ddiff
#===================================================================================================
def ddiff(ds):
    """
    Difference of multiple dictionaries
    """
    rem = {}
    allkeys = set(k for d in ds for k in d)
    nonunif = set()
    for d in ds:
        for k in allkeys:
            if k not in d:
                nonunif.add(k)
    uniform = set(k for k in allkeys if k not in nonunif)
    unequal = {}
    for k in uniform:
        kvals = set(d[k] for d in ds)
        if len(kvals) > 1:
            unequal[k] = kvals
    return nonunif, unequal


#===================================================================================================
# main - Main Program
#===================================================================================================
def main(argv=None):
    """
    Main program
    """
    args = cli(argv)

    # Read the variable attributes file
    with open('variable_attribs.json') as f:
        vatts = json.load(f)
    
    # Find variable attribute differences
    print 'Finding differences in attributes...'
    print
    for var in vatts:
        nonunif, unequal = ddiff([vatts[var][xfrte] for xfrte in vatts[var]])
        if len(nonunif) > 0 or len(unequal) > 0:
            print 'Diffs in Variable: {}'.format(var)
        if len(nonunif) > 0:
            print '    Non-uniform keys: {}'.format(', '.join(sorted(nonunif)))
        if len(unequal) > 0:
            for k in unequal:
                print '   {}: {}'.format(k, ', '.join(unequal[k]))
    print

    print "Done."

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
