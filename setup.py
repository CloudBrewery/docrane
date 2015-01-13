#!/usr/bin/env python

from setuptools import setup

from docrane import __version__ as version

setup(
    setup_requires=['pbr'],
    pbr=True,
    version=version,
)
