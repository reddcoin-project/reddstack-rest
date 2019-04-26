#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Reddstack Rest Server
"""

import sys
import os

# Hack around absolute paths
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(current_dir + "/../")

sys.path.insert(0, parent_dir)

from reddstackrest.reddstackrestd import run_reddstackrestd

if __name__ == '__main__':
    run_reddstackrestd()
