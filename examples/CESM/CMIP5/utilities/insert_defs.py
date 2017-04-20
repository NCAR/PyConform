#!/usr/bin/env python
"""
insert_defs

Command-Line Utility to push definitions into a standardization file

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import json
from os.path import isfile
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Push definitions into a JSON standardization file')
__PARSER__.add_argument('-a', '--all', default=False, action='store_true',
                        help=('Overwrite all definitions according to the definitions file. '
                              'If a definition is not specified, it is considered blank.'))
__PARSER__.add_argument('stdfile', help='Name of the standardization file')
__PARSER__.add_argument('deffile', help='Name of the definitions file')

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

    STDFILE = args.stdfile
    if not isfile(STDFILE):
        raise ValueError('Standardization file {} not found'.format(STDFILE))
    
    with open(SPECFILE) as f:
        stdinfo = json.load(f)
    
    DEFFILE = args.deffile
    if not isfile(DEFFILE):
        raise ValueError('Definitions file {} not found'.format(DEFFILE))
    
    if args.variable is not None:
        if args.variable in spec:
            vars = [args.variable]
        else:
            raise ValueError('Variable {} not found in specfile'.format(args.variable))
    else:
        vars = [v for v in spec]
    
    for v in vars:
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
