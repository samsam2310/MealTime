#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" FB API
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import requests


FB_APP_ID = os.environ.get('FB_APP_ID', '')
FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_TOKEN = os.environ.get('FB_TOKEN', '')
