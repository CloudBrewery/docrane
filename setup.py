#!/usr/bin/env python

from setuptools import setup

try:
    import multiprocessing
except ImportError:
    pass

execfile('docrane/version.py')

setup(
    setup_requires=['pbr>=0.10.0'],
    pbr=True,
)
