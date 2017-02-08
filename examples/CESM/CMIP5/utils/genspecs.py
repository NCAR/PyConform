#!/usr/bin/env python
"""
genspecs

Command-Line Utility to generate specfiles from a set of "correct" output files

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from fnmatch import filter
from os import walk
from os.path import isdir, join
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Create a specfile from a set of output files')
__PARSER__.add_argument('-o', '--output', help='Name of the output specfile')
__PARSER__.add_argument('root', help='Root directory where output files can be found')

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
        raise ValueError('Root must be a directory')
    
    for root, dirnames, filenames in walk(args.root):
        print dirnames
        print filenames
        print
#         for filename in filter(filenames, '*.nc'):
#             print filename)
    

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
