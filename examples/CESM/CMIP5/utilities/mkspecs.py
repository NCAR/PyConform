#!/usr/bin/env python
"""
genspecs

Command-Line Utility to generate specfiles from a set of "correct" output files

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import json
import numpy
from netCDF4 import Dataset
from glob import glob
from os import listdir, linesep
from os.path import isdir, join as pjoin
from argparse import ArgumentParser

__PARSER__ = ArgumentParser(description='Create a specfile from a set of output files')
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
# MyEncoder
#===================================================================================================
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


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
    # ROOT = <root>/<institution>/<model>/<experiment>/<frequency>/<realm>/<table>/<ensemble>
    root, inst, model, expt, freq, realm, table, rip = ROOT.rsplit('/', 7)
    
    # Check for consistency
    if inst != 'NCAR' and model != 'CCSM4':
        raise ValueError('Root appears to be malformed')
    
    print 'Institution:     {}'.format(inst)
    print 'Model:           {}'.format(model)
    print 'Experiment:      {}'.format(expt)
    print 'Frequency:       {}'.format(freq)
    print 'Realm:           {}'.format(realm)
    print 'Table:           {}'.format(table)
    print 'Ensemble Member: {}'.format(rip)
    print
    
    base = pjoin(root, inst, model, expt, freq, realm, table, rip, 'latest')
    vars = listdir(base)
    
    specinfo = {}
    for var in vars:
        vdir = pjoin(base, var)
        vfile = sorted(glob(pjoin(vdir,'*.nc')))[0]
        vds = Dataset(vfile)
        fattrs = {str(a):vds.getncattr(a) for a in vds.ncattrs()}
        for v in vds.variables:
            vobj = vds.variables[v]
            if v not in specinfo:
                specinfo[v] = {"attributes": {str(a):vobj.getncattr(a) for a in vobj.ncattrs()},
                               "datatype": str(vobj.dtype),
                               "dimensions": [str(d) for d in vobj.dimensions]}
                if 'comment' in vobj.ncattrs():
                    specinfo[v]["definition"] = vobj.getncattr('comment')
                else:
                    specinfo[v]["definition"] = ''
                if v == var:
                    fname = '{}_{}_{}_{}_{}_YYYYMM.nc'.format(v,table,model,expt,rip)
                    specinfo[v]["file"] = {"filename": fname,
                                           "attributes": fattrs}
    
    specname = '{}_{}_{}_{}.json'.format(model, expt, realm, table)
    with open(specname, 'w') as f:
        json.dump(specinfo, f, indent=4, cls=MyEncoder)

    print "Done."
    

#===================================================================================================
# Command-line Operation
#===================================================================================================
if __name__ == '__main__':
    main()
