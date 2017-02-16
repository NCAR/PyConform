#!/usr/bin/env python
"""
analyze_variables

Command-Line Utility to analyze variable metadata in CMIP5 data

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

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

    # Variables by attributes
    vatts = {}
    for ncvar in ncvars:
        xfrte = pjoin(ncvar[:5])
        vars = ncvar[5:]
        for var in vars:
            print args.root, xfrte, var, '*.nc'
            vfile = glob(pjoin(args.root, xfrte, var, '*.nc'))[0]
            with Dataset(vfile) as vds:
                vobj = vds.variables[var]
                vatt = {att:vds.getncattr(att) for att in vds.ncattrs}
                if var in vatts:
                    vatts[var][xfrte] = vatt
                else:
                    vatts[var] = {xfrte: vatt}

    print "Done."

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
