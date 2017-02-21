#!/usr/bin/env python
"""
getinfo

Command-Line Utility to pull out attributes/definitions/etc from a specfile

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import json
from os.path import isfile
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Pull out information from a JSON specfile')
__PARSER__.add_argument('-v', '--variable', default=None, help='Name of variable to pull from')
__PARSER__.add_argument('-a', '--attribute', default=None, help='Name of attribute to pull')
__PARSER__.add_argument('-d', '--definition', default=False, action='store_true',
                        help='Pull the definitions (instead of attributes).  '
                             'Attribute argument ignored, if specified.')
__PARSER__.add_argument('specfile', help='Name of specfile to pull from')

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

    SPECFILE = args.specfile
    if not isfile(SPECFILE):
        raise ValueError('Specfile {} not found'.format(SPECFILE))
    
    with open(SPECFILE) as f:
        spec = json.load(f)
    
    if args.variable is not None:
        if args.variable in spec:
            vars = [args.variable]
        else:
            raise ValueError('Variable {} not found in specfile'.format(args.variable))
    else:
        vars = [v for v in spec]
    
    for v in sorted(vars):
        if args.definition:
            if 'definition' in spec[v]:
                vdef = spec[v]['definition']
            else:
                vdef = ''
            print '{} = {}'.format(v, vdef)
        else:
            if args.attribute is not None:
                if args.attribute in spec[v]['attributes']:
                    vatts = {args.attribute:  spec[v]['attributes'][args.attribute]}
            else:
                vatts = spec[v]['attributes']
            print '{}:'.format(v)
            for a in vatts:
                print '   {}: {}'.format(a, vatts[a])
    

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
