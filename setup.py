#!/usr/bin/env python

from setuptools import setup

try:
    import multiprocessing
except ImportError:
    pass

from docrane import __version__ as version

setup(
    setup_requires=['pbr'],
    pbr=True,
    version=version,
)
