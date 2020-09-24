.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3895009.svg
   :target: https://doi.org/10.5281/zenodo.3895009

.. image:: https://codecov.io/gh/NCAR/PyConform/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/NCAR/PyConform

.. image:: https://github.com/NCAR/PyConform/workflows/Tests/badge.svg
  :target: https://github.com/NCAR/PyConform/actions?query=workflow%3ATests

.. image:: https://github.com/NCAR/PyConform/workflows/Linting/badge.svg
  :target: https://github.com/NCAR/PyConform/actions?query=workflow%3ALinting

PyConform
=========

A package for transforming a NetCDF dataset into a defined format
suitable for publication according to a defined publication standard.

:AUTHORS: Sheri Mickelson, Kevin Paul
:COPYRIGHT: 2020, University Corporation for Atmospheric Research
:LICENSE: See the LICENSE.rst file for details

Send questions and comments to Kevin Paul (kpaul@ucar.edu) or
Sheri Mickelson (mickelso@ucar.edu).


Overview
--------

The PyConform package is a Python-based package for converting model time-series
data into MIP-conforming (i.e., *standardized*) time-series data.  It was designed
for CMIP6 *specifically for NCAR's CESM CMIP6 workflow*, but we attempted to
design the code in a way that is general purpose.  PyConform attempts to divide
the standardization problem specification step into two separate pieces:

1. a specification of the *standard*, and
2. a specification of the *conversion process*.

This separate was created to allow the *standard* to be defined by (for example)
the MIP designers and the *conversion process* to be defined by the model
developers (i.e., scientists).  For CMIP6, we used the ``dreqpy`` utility to
define the *standard*, and the scientists then just needed to provide one-line
*definitions* for how to convert the raw CESM data into the requested
standardized output.

Currently, the main considerations that need to be made when creating
*definitions* are the following:

1. physical units will be converted *automatically*, if possible according to
   the ``cf_units`` package,
2. the *dimensions* of the resulting data variable produced by the *definition*
   operation must be *mappable* to requested dimensions specified in the
   standard, and
3. special operations/computations that are not supplied with PyConform in
   the ``functions`` module may need to be written by hand and called explicitly
   in the output variable *definition*.

.. warning::
    PyConform should only be used with caution!  As mentioned, it was created
    specifically for NCAR's contributions to CMIP6.  PyConform is not designed
    to fix *problems* with your input data, and as such is completely incapable
    of detecting many problems with your data!  (That is, "garbage in, garbage
    out!")

    The *core* part of PyConform was designed and implemented
    before a full understanding of the requirements could be obtained.  Full
    testing of PyConform could not be done without knowing what all of the
    input (i.e., model output) data would look like!  And, to make matters
    more difficult, the *specification* utility that PyConform depends upon
    (``dreqpy``) took quite a while to stabilize.  As a result, much of
    PyConform's testing had to be done *on-the-fly*.

.. warning::
    **Deprecation:**
    With the completion of CMIP6, this project is essentially deprecated.  Much
    of the operations and core functionality of this tool can be reproduced in
    a much more robust way with Xarray_.  The parallelism provided via MPI
    in PyConform can be handled in a much better way with Dask_, which already
    works with Xarray_.  It is our belief that this utility should be replaced
    in the future by a framework built on Xarray_ and Dask_, but due to
    resource limitations, we cannot build that tool.  We would certainly
    welcome any others to take on that challenge!

.. _Xarray: http://xarray.pydata.org/
.. _Dask: http://dask.org

Dependencies
------------

The PyConform package directly depends upon 4 main external packages:

* ASAPTools (>=0.6)
* cf-units
* dreqpy
* netCDF4-python
* ply
* python-dateutil

These dependencies imply the dependencies:

* numpy (>=1.5)
* netCDF4
* MPI
* UDUNITS2

Additionally, the entire package is designed to work with Python v2.7 and up
to (but not including) Python v3.0.

The version requirements have not been rigidly tested, so earlier versions
may actually work.  No version requirement is made during installation, though,
so problems might occur if an earlier versions of these packages have been
installed.


Obtaining the Source Code
-------------------------

Currently, the most up-to-date development source code is available
via git from the site::

    https://github.com/NCAR/PyConform

Check out the most recent stable tag.  The source is available in
read-only mode to everyone.  Developers are welcome to update the source
and submit Pull Requests via GitHub.


Building & Installing from Source
---------------------------------

Installation of the PyConform package is very simple.  After checking out the source
from the above svn link, via::

    $ git clone https://github.com/NCAR/PyConform

Enter the newly cloned directory::

    $ cd PyConform

Then, run the Python setuptools setup script.  On unix, this involves::

    $  python setup.py install [--prefix=/path/to/install/location]

The prefix is optional, as the default prefix is typically /usr/local on
linux machines.  However, you must have permissions to write to the prefix
location, so you may want to choose a prefix location where you have write
permissions.  Like most distutils installations, you can alternatively
install the PyReshaper with the '--user' option, which will automatically
select (and create if it does not exist) the $HOME/.local directory in which
to install.  To do this, type (on unix machines)::

    $  python setup.py install --user

This can be handy since the site-packages directory will be common for all
user installs, and therefore only needs to be added to the PYTHONPATH once.

The documentation_ for PyConform is hosted on GitHub Pages.

.. _documentation:  https://ncar.github.io/pyconform
