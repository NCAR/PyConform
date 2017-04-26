#!/usr/bin/env python
"""
ncdiff

Command-Line Utility to show the differences between two NetCDF files

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os.path import isfile
from argparse import ArgumentParser
from netCDF4 import Dataset, Dimension, Variable
from numpy import ravel
from itertools import izip_longest

#===================================================================================================
# Argument Parser
#===================================================================================================
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
__PARSER__.add_argument('-r', '--range', default=slice(0,10), type=_range_, 
                        help='Range of values to display')
__PARSER__.add_argument('-a', '--attributes', default=False, action='store_true',
                        help='Diff attributes instead of values')
__PARSER__.add_argument('file1', type=str, help='Name of first NetCDF file')
__PARSER__.add_argument('file2', type=str, help='Name of second NetCDF file')


#===================================================================================================
# cli - Command-Line Interface
#===================================================================================================
def cli(argv=None):
    """
    Command-Line Interface
    """
    return __PARSER__.parse_args(argv)


#===================================================================================================
# _cmp - Comparison function
#===================================================================================================
def _cmp(a1,a2):
    if a1 is None or a2 is None:
        return True
    elif isinstance(a1, Dimension):
        if a1.name != a2.name:
            return True
        elif a1.size != a2.size:
            return True
        else:
            return a1.isunlimited() != a2.isunlimited()
    elif isinstance(a1, Variable):
        if a1.name != a2.name:
            return True
        elif a1.dtype != a2.dtype:
            return True
        else:
            return a1.dimensions != a2.dimensions
    else:
        return a1 != a2

#===================================================================================================
# _str - String producing function
#===================================================================================================
def _str(a, len=25):
    if a is None:
        return '-'*len
    elif isinstance(a, Dimension):
        return '{}[{}{}]'.format(a.name, a.size, '+' if a.isunlimited() else '')[:len]
    elif isinstance(a, Variable):
        dstr = '({})'.format(','.join(a.dimensions))
        return '{} {}{}'.format(a.dtype, a.name, dstr)
    else:
        return str(a)[:len]

        
#===================================================================================================
# diff_dicts
#===================================================================================================
def diff_dicts(d1, d2, name='object'):
    d12union = set.union(set(d1), set(d2))
    if len(d12union) > 0:
        print
        print 'Differences found in {}:'.format(name)
    diffs = False
    for k in sorted(d12union):
        d1k = d1.get(k, None)
        d2k = d2.get(k, None)
        if _cmp(d1k, d2k):
            diffs = True
            print '   {:10s}:  [1]   {:>25s}  <--->  {:25s}   [2]'.format(k, _str(d1k), _str(d2k))
    if not diffs:
        print '   None'

    
#===================================================================================================
# main - Main Program
#===================================================================================================
def main(argv=None):
    """
    Main program
    """
    args = cli(argv)

    FILE1 = args.file1
    if not isfile(FILE1):
        raise ValueError('NetCDF file {} not found'.format(FILE1))
    shortf1 = FILE1.split('/')[-1]

    FILE2 = args.file2
    if not isfile(FILE2):
        raise ValueError('NetCDF file {} not found'.format(FILE2))
    shortf2 = FILE2.split('/')[-1]

    ncf1 = Dataset(FILE1)
    ncf2 = Dataset(FILE2)
    
    if args.range is None:
        slc = slice(None)
    else:
        slc = args.range
        
    print
    print '[1]:  {}'.format(shortf1)
    print '[2]:  {}'.format(shortf2)
    
    # Global file attributes
    f1atts = {a:ncf1.getncattr(a) for a in ncf1.ncattrs()}
    f2atts = {a:ncf2.getncattr(a) for a in ncf2.ncattrs()}
    diff_dicts(f1atts, f2atts, name='Global File Attributes')
    
    # Dimensions
    f1dims = {d:ncf1.dimensions[d] for d in ncf1.dimensions}
    f2dims = {d:ncf2.dimensions[d] for d in ncf2.dimensions}
    diff_dicts(f1dims, f2dims, name='File Dimensions')
    
    # Variables
    f1vars = {v:ncf1.variables[v] for v in ncf1.variables}
    f2vars = {v:ncf2.variables[v] for v in ncf2.variables}
    diff_dicts(f1vars, f2vars, name='Variables')


#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
