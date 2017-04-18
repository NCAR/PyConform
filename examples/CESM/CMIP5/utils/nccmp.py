#!/usr/bin/env python
"""
getinfo

Command-Line Utility to pull out attributes/definitions/etc from a specfile

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os.path import isfile
from argparse import ArgumentParser
from netCDF4 import Dataset

#===================================================================================================
# Argument Parser
#===================================================================================================
def _file_var_(arg):
    try:
        return arg.split(',')
    except:
        raise ArgumentTypeError("Filevar arguments must be in FILE,VAR format")

def _range_(arg):
    try:
        vals = []
        for i in arg.split(','):
            if i == '':
                vals.append(None)
            else:
                vals.append(int(i))
        return slice(*vals)
    except:
        raise ArgumentTypeError("Range arguments must be in LOWER,UPPER format")

__PARSER__ = ArgumentParser(description='Compare two NetCDF files')
__PARSER__.add_argument('-r', '--range', default=None, type=_range_, 
                        help='Range of values to display')
__PARSER__.add_argument('filevar1', type=_file_var_, help='Name of first NetCDF file and variable')
__PARSER__.add_argument('filevar2', type=_file_var_, help='Name of second NetCDF file and variable')


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

    FILE1, VAR1 = args.filevar1
    if not isfile(FILE1):
        raise ValueError('NetCDF file {} not found'.format(FILE1))

    FILE2, VAR2 = args.filevar2
    if not isfile(FILE2):
        raise ValueError('NetCDF file {} not found'.format(FILE2))

    ncf1 = Dataset(FILE1)
    if VAR1 in ncf1.variables:
        ncv1 = ncf1.variables[VAR1]
    else:
        raise ValueError('Variable {} not found in file {}'.format(VAR1, FILE1))

    ncf2 = Dataset(FILE2)
    if VAR2 in ncf2.variables:
        ncv2 = ncf2.variables[VAR2]
    else:
        raise ValueError('Variable {} not found in file {}'.format(VAR2, FILE2))
    
    if args.range is None:
        slc = slice(None)
    else:
        slc = args.range
    
    print '{}:{}:'.format(FILE1, VAR1)
    print ncv1[slc]
    print
    print '{}:{}:'.format(FILE2, VAR2)
    print ncv2[slc]


#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
