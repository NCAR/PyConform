#!/usr/bin/env python
"""
genspecs

Command-Line Utility to generate specfiles from a set of "correct" output files

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from glob import glob
from os import listdir, linesep
from os.path import isdir, join as pjoin
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

    ROOT = args.root.rstrip('/')
    if not isdir(ROOT):
        raise ValueError('Root must be a directory')

    # Assume that ROOT directory is of the form:
    # ROOT = <root>/<institution>/<model>/<experiment>/<frequency>/<realm>/<table>
    root, inst, model, expmnt, freq, realm, table = ROOT.rsplit('/', 6)
    
    # Check for consistency
    if inst != 'NCAR' and model != 'CCSM4':
        raise ValueError('Root appears to be malformed')
    
    print 'Experiment: {}'.format(expmnt)
    print 'Table: {}'.format(table)
    
    # Pick an ensemble member (doesn't matter which)
    ens = listdir(pjoin(ROOT))[0]
    
    # Find all files for the 'latest' version
    ncfiles = glob(pjoin(ROOT, ens, 'latest', '*', '*.nc'))
    print linesep.join(ncfiles)
    
    

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
