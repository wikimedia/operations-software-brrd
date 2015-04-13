#!/usr/bin/env python

PROJECT = 'brrd'
VERSION = '0.1'

from setuptools import setup, find_packages

with open('README.rst', 'rt') as f:
    long_description = f.read()

with open('requirements.txt', 'rt') as f:
    required = f.read().splitlines()

setup(
    name=PROJECT,
    version=VERSION,

    description='Navigation Timing RRD logger',
    long_description=long_description,

    author='Ori Livneh',
    author_email='ori@wikimedia.org',

    url='https://github.com/wikimedia/brrd',
    download_url='https://github.com/wikimedia/brrd/tarball/master',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=required,

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'brrd = brrd.main:main',
        ],
        'brrd': [
            'logger = brrd.logger:MetricLogger',
        ],
    },

    zip_safe=False,
)
