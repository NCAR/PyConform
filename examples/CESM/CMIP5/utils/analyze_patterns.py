#!/usr/bin/env python
"""
cmip5_patterns

Command-Line Utility to analyze file-directory patterns in CMIP5 data

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from glob import glob
from os import listdir, linesep
from os.path import isfile, join as pjoin
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Analyze file-directory patters of CMIP5 data')
__PARSER__.add_argument('patterns', help='The text file containing all file-directory patterns')

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

    if not isfile(args.patterns):
        raise ValueError('Patterns file not found')

    # Read the patterns file
    with open('cmip5_patterns.txt') as f:
        ncvars = [line.split() for line in f]
                    
    # Analyze freq/realm/table correlations
    frtcorr = {}
    for ncvar in ncvars:
        frt = tuple(ncvar[1:4])
        table = frt[-1]
        if table in frtcorr:
            frtcorr[table].add(frt)
        else:
            frtcorr[table] = {frt}

    print 'Tables with multiple freq/realm/table patterns:'
    multfrt = [table for table in frtcorr if len(frtcorr[table]) > 1]
    if len(multfrt) > 0:
        for table in multfrt:
            print "  Table {}:  {}".format(table,', '.join('/'.join(frt) for frt in frtcorr[table]))
    else:
        print "  None"
    print
    
    # Analyze freq/table correlations
    ftcorr = {}
    for ncvar in ncvars:
        ft = tuple([ncvar[1], ncvar[3]])
        table = ft[-1]
        if table in ftcorr:
            ftcorr[table].add(ft)
        else:
            ftcorr[table] = {ft}

    print 'Tables with multiple freq/table patterns:'
    multft = [table for table in ftcorr if len(ftcorr[table]) > 1]
    if len(multft) > 0:
        for table in multft:
            print "  Table {}:  {}".format(table,', '.join('/'.join(ft) for ft in ftcorr[table]))
    else:
        print "  None"
    print

    print 'Unique freq/table patterns:'
    uniqft = [table for table in ftcorr if len(ftcorr[table]) == 1]
    if len(uniqft) > 0:
        for table in uniqft:
            print "  Table {}:  {}".format(table,', '.join('/'.join(ft) for ft in ftcorr[table]))
    else:
        print "  None"
    print
    
    # Group variables by table 
    vtcorr = {}
    vrcorr = {}
    for ncvar in ncvars:
        expt, freq, realm, table, ens = ncvar[:5]
        vars = ncvar[5:]
        for var in vars:
            if var in vtcorr:
                vtcorr[var].add(table)
            else:
                vtcorr[var] = {table}
            if var in vrcorr:
                vrcorr[var].add(realm)
            else:
                vrcorr[var] = {realm}

    print 'Variables in multiple tables:'
    multvt = [var for var in vtcorr if len(vtcorr[var]) > 1]
    if len(multvt) > 0:
        for var in multvt:
            print "  Variable {}:  {}".format(var,', '.join(vtcorr[var]))
    else:
        print "  None"
    print
    
    print 'Variables in multiple realms:'
    multvr = [var for var in vrcorr if len(vrcorr[var]) > 1]
    if len(multvr) > 0:
        for var in multvr:
            print "  Variable {}:  {}".format(var,', '.join(vrcorr[var]))
    else:
        print "  None"
    print
    
    # Analyze variable groups by freq/realm/table patterns
    vgroups = {}
    for ncvar in ncvars:
        frt = '/'.join(ncvar[1:4])
        vars = ncvar[5:]
        if frt not in vgroups:
            vgroups[frt] = [set(vars)]
        else:
            vgroups[frt].append(set(vars))
    
    print 'Freq/realm/table patterns with differing variable groups:'
    diffvgs = [frt for frt in vgroups if any(len(vg - vgroups[frt][0]) > 0 or len(vgroups[frt][0] - vg) > 0 for vg in vgroups[frt][1:])]
    if len(diffvgs) > 0:
        for frt in diffvgs:
            print "  {}".format(frt)
    else:
        print "  None"
    print
             

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
