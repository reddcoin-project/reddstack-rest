#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    reddstack-rest
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2019 by Reddcoin

    This file is part of Reddcoin

    Reddcoin is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Reddcoin is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Blockstore. If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup, find_packages
import sys
import os

setup(
    name='reddstack-rest',
    version='',
    license='GPLv3',
    author='John Nash',
    author_email='gnasher@reddcoin.com',
    description='RESTful api to the Reddcoin name registrations',
    keywords='blockchain reddcoin rdd cryptocurrency name key value store data',
    packages=find_packages(),
    scripts=['bin/reddstack-rest'],
    download_url='https://github.com/reddcoin-project/reddstack-rest/archive/master.zip',
    zip_safe=False,
    include_package_data=True,
    install_requires=[

    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
