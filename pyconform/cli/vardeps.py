#! /usr/bin/env python
"""
vardeps - Find variable dependencies

Find output variable dependencies in a definitions file or a standardization JSON file

COPYRIGHT: 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from argparse import ArgumentParser
from collections import OrderedDict
from json import load
from os.path import exists

from pyconform import parsing


def cli(argv=None):
    desc = """This tool will analyze a definitions text file or a JSON standardization
              file and print out the variables needed for each defined output variable."""

    parser = ArgumentParser(description=desc)
    parser.add_argument(
        '-d',
        '--deffile',
        default=False,
        action='store_true',
        help=(
            'Flag to use if the file to read is a definitions file, '
            'instead of a JSON-formatted standardization file'
        ),
    )
    parser.add_argument(
        '-f',
        '--frequency',
        default=False,
        action='store_true',
        help='Output variable frequency with their dependencies',
    )
    parser.add_argument(
        '-n',
        '--filename',
        default=None,
        metavar='FILENAME',
        type=str,
        help='Name of the file from which variable definitions will be read',
    )
    parser.add_argument(
        'variables',
        metavar='VARIABLE',
        nargs='*',
        type=str,
        help=(
            'Output variables to search for.  If not specified, then '
            'search for all output variables.'
        ),
    )

    return parser.parse_args(argv)


def variable_search(obj, vars=None):
    if vars is None:
        vars = set()
    if isinstance(obj, parsing.VarType):
        vars.add(obj.key)
    elif isinstance(obj, parsing.OpType):
        for arg in obj.args:
            vars = variable_search(arg, vars=vars)
    elif isinstance(obj, parsing.FuncType):
        for arg in obj.args:
            vars = variable_search(arg, vars=vars)
        for kwd in obj.kwds:
            vars = variable_search(obj.kwds[kwd], vars=vars)
    return vars


def print_columnar(x, textwidth=10000000, indent=0, header=''):
    hrstrp = '{}  '.format(str(header).rstrip())
    if len(hrstrp) > indent:
        indent = len(hrstrp)
    else:
        hrstrp = '{: <{indent}}'.format(header, indent=indent)
    Lmax = max(len(str(i)) for i in x)
    Nc = (textwidth - indent + 3) // (Lmax + 3)
    Nr = len(x) // Nc + int(len(x) % Nc > 0)
    A = [x[i::Nr] for i in range(Nr)]
    print(
        '{}{}'.format(
            hrstrp, '   '.join('{: <{Lmax}}'.format(r, Lmax=Lmax) for r in A[0])
        )
    )
    for row in A[1:]:
        print(
            '{}{}'.format(
                ' ' * indent,
                '   '.join('{: <{Lmax}}'.format(r, Lmax=Lmax) for r in row),
            )
        )


def main(argv=None):
    args = cli(argv)

    # Check that the file exists
    if not exists(args.filename):
        raise OSError('File {!r} not found'.format(args.filename))

    # Read the definitions from the file
    vardefs = {}
    varfreqs = {}
    varrealm = {}
    if args.deffile:
        with open(args.filename) as f:
            for line in f:
                line = line.strip()
                if '#' in line:
                    line = line.split('#')[0].strip()
                split = line.split('=')
                if len(split) == 2:
                    vardefs[split[0].strip()] = split[1].strip()
                elif len(line) > 0:
                    print('Could not parse this line: {!r}'.format(line))
    else:
        stddict = load(open(args.filename), object_pairs_hook=OrderedDict)
        for var in stddict:
            if 'definition' in stddict[var] and isinstance(
                stddict[var]['definition'], str
            ):
                vardefs[var] = stddict[var]['definition']
            if (
                'attributes' in stddict[var]
                and 'frequency' in stddict[var]['attributes']
            ):
                varfreqs[var] = stddict[var]['attributes']['frequency']
            if 'attributes' in stddict[var] and 'realm' in stddict[var]['attributes']:
                varrealm[var] = stddict[var]['attributes']['realm']

    # Determine list of output variables to search for
    if len(args.variables) == 0:
        outvars = sorted(vardefs.keys())
    else:
        outvars = sorted(args.variables)

    # Use the parser to determine what variables are needed
    print('Output Variable Dependencies:')
    alldeps = set()
    for var in outvars:
        if var in vardefs:
            try:
                vdeps = variable_search(parsing.parse_definition(vardefs[var]))
                alldeps.update(vdeps)
                fheader = (
                    ' [{},{}]'.format(varfreqs[var], varrealm[var])
                    if var in varfreqs
                    else ''
                )
                vheader = '   {}{}:'.format(var, fheader)
                print_columnar(sorted(vdeps), header=vheader)
            except:
                print('   {}: No dependencies.'.format(var))
        else:
            print('   {}: Not defined.'.format(var))

    print()
    print('Complete Specification Requires the Following Input Variables:')
    print_columnar(sorted(alldeps), indent=3)


if __name__ == '__main__':
    main()
