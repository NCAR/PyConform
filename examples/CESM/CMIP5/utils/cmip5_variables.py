#!/usr/bin/env python
"""
cmip5_variables

Command-Line Utility to extract variable attributes in CMIP5 data

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
__PARSER__.add_argument('root', help='The root directory from where the directory patterns were found')

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
                allkeys.remove(k)
    unequal = {}
    for k in allkeys:
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

    if not isdir(args.root):
        raise ValueError('Patterns file not found')

    # Read the patterns file
    with open('cmip5_patterns.txt') as f:
        ncvars = [line.split() for line in f]

    # Attributes with expected differences (to be skipped)
    xkeys = ['table_id', 'history', 'processed_by', 'tracking_id', 'creation_date']
    
    # Variables by attributes
    vatts = {}
    for ncvar in ncvars:
        xfrte = pjoin(*ncvar[:5])
        print '{}:'.format(xfrte)
        vars = ncvar[5:]
        for var in vars:
            print '   {}...'.format(var),
            vdir = pjoin(args.root, xfrte, 'latest', var)
            vfile = glob(pjoin(vdir, '*.nc'))[0]
            with Dataset(vfile) as vds:
                vobj = vds.variables[var]
                vatt = {att:vds.getncattr(att) for att in vds.ncattrs() if att not in xkeys}
                if var in vatts:
                    vatts[var][xfrte] = vatt
                else:
                    vatts[var] = {xfrte: vatt}
            print 'done.'
    print

    # Save variable attributes to file
    with open('variable_attribs.json', 'w') as f:
        json.dump(vatts, f)

    print "Done."


#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
