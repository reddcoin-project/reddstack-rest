#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .version import __version__

VERSION = __version__
port = 8082

def get_working_dir():
    from os.path import expanduser
    home = expanduser('~')

    working_dir = os.path.join(home, '.reddstackrest')

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    return working_dir

def get_pid_filename():
    return 'reddstackrest'