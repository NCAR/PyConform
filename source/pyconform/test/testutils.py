"""
Unit Testing Utilities

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from re import sub
from os import linesep

#===================================================================================================
# print_test_message
#===================================================================================================
def print_test_message(testname, **kwds):
    print '{}:'.format(testname)
    if len(kwds) > 0:
        nlen = max(len(k) for k in kwds)
        for k, v in kwds.iteritems():
            val_str = sub(' +', ' ', repr(v).replace(linesep, ' '))
            print ' - {0:<{1}} = {2}'.format(k, nlen, val_str)
    print

