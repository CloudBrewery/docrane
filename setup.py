#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from docrane import __version__ as version

packages = [
    'docrane'
]

setup(
    name='docrane',
    version=version,
    description='Manage docker container runtime configuration with etcd',
    long_description='',
    author='Jacob Godin',
    author_email='jacobgodin@gmail.com',
    url='https://github.com/CloudBrewery/docrane',
    packages=packages,
    scripts=['bin/docrane'],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
