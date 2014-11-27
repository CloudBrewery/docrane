#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'etcdocker'
]

setup(
    name='etcdocker',
    version='beta',
    description='Manage docker container runtime configuration with etcd',
    long_description='',
    author='Jacob Godin',
    author_email='jacobgodin@gmail.com',
    url='https://bitbucket.org/clouda/etcdocker',
    packages=packages,
    scripts=['bin/etcdocker'],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)