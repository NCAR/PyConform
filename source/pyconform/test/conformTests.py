"""
Unit Tests for the "conform" Command-Line Tool

Copyright 2015, University Corporation for Atmospheric Research
See LICENSE.txt for details
"""

import os
import imp
import unittest
import json
from collections import OrderedDict
from mkTestData import DataMaker

conform = imp.load_source('conform', '../../../scripts/conform')


#===============================================================================
# conformTests
#===============================================================================
class conformTests(unittest.TestCase):
    
    def setUp(self):
        self.specfile = 'testspec.json'
        specstr = """
{"name": "output",
 "attributes": {"a1": "attribute 1",
                "a2": "attribute 2"},
 "dimensions": {"space": 2,
                "time": 3},
 "unlimited": ["time"],
 "variables": {"space": {
               "attributes": {"units": "m", "standard_name": "spacial_extent"}, 
               "dimensions": ["space"], 
               "type": "double", 
               "formula": "in.space"}, 
               "time": {"attributes": {"units": "days since 01-01-0001",
                                       "standard_name": "time"},
                        "dimensions": ["time"],
                        "type": "double",
                        "formula": "in.time"},
               "DT": {"attributes": {"units": "K",
                                     "standard_name": "Temperature Difference"},
                      "dimensions": ["time", "space"],
                      "type": "double",
                      "formula": "in.T2 - in.T1"},
               "TAvg": {"attributes": {"units": "K",
                                       "standard_name": "Temperature Difference"},
                        "dimensions": ["time", "space"],
                        "type": "double",
                        "formula": "0.5*(in.T2 + in.T1)"}}
}"""
        self.specdata = json.loads(specstr, object_pairs_hook=OrderedDict)
        json.dump(self.specdata, open(self.specfile, 'w'), indent=4)
        self.dm = DataMaker()
        self.dm.write()
        
    def tearDown(self):
        self.dm.clear()
        if os.path.exists(self.specfile):
            os.remove(self.specfile)
        
    def test_CLI_empty(self):
        argv = []
        self.assertRaises(SystemExit, conform.cli, argv)

    def test_CLI_help(self):
        argv = ['-h']
        self.assertRaises(SystemExit, conform.cli, argv)

    def test_CLI_defaults(self):
        argv = [self.specfile]
        args = conform.cli(argv)
        self.assertListEqual(args.infiles, [],
                             'Default infiles list is not empty')
        self.assertEqual(args.serial, False,
                         'Default serial state is not False')
        self.assertEqual(args.verbosity, 1,
                         'Default verbosity is not 1')
        self.assertEqual(args.specfile, argv[0],
                         'Specfile is not properly set')

    def test_CLI_set_all_short(self):
        infiles = ['*.nc']
        serial = True
        verbosity = 3
        
        argv = []
        for infile in infiles:
            argv.extend(['-i', str(infile)])
        if serial:
            argv.append('-s')
        argv.extend(['-v', str(verbosity)])
        argv.append(self.specfile)

        args = conform.cli(argv)
        self.assertListEqual(args.infiles, infiles,
                             'Default infiles list is properly set')
        self.assertEqual(args.serial, serial,
                         'Default serial state is not set')
        self.assertEqual(args.verbosity, verbosity,
                         'Default verbosity is not set')
        self.assertEqual(args.specfile, self.specfile,
                         'Specfile is not properly set')
        
    def test_CLI_set_all_long(self):
        infiles = ['*.nc']
        serial = True
        verbosity = 3
        
        argv = []
        for infile in infiles:
            argv.extend(['--infile', str(infile)])
        if serial:
            argv.append('--serial')
        argv.extend(['--verbosity', str(verbosity)])
        argv.append(self.specfile)

        args = conform.cli(argv)
        self.assertListEqual(args.infiles, infiles,
                             'Default infiles list is properly set')
        self.assertEqual(args.serial, serial,
                         'Default serial state is not set')
        self.assertEqual(args.verbosity, verbosity,
                         'Default verbosity is not set')
        self.assertEqual(args.specfile, self.specfile,
                         'Specfile is not properly set')


#===============================================================================
# Command-line Operation
#===============================================================================
if __name__ == "__main__":
    unittest.main()
