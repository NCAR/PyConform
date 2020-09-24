#!/usr/bin/env python
"""
PyConform -- Setup Script

Copyright 2017-2020, University Corporation for Atmospheric Research
See the LICENSE.rst file for details
"""

from setuptools import find_packages, setup

__version__ = '0.3.0'

with open('README.rst', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='PyConform',
    version=__version__,
    author='Kevin Paul',
    author_email='kpaul@ucar.edu',
    description='Parallel Python NetCDF Dataset Standardization Tool',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/NCAR/PyConform',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Utilities',
    ],
    python_requires='>=2.7',
    entry_points="""
        [console_scripts]
        iconform=pyconform.cli.iconform:main
        vardeps=pyreshaper.cli.vardeps:main
        xconform=pyreshaper.cli.xconform:main
        """,
    install_requires=install_requires,
)
