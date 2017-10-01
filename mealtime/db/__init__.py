#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" DB - init
"""

from __future__ import absolute_import, print_function, unicode_literals

from pymongo import MongoClient

import os

from .base import getDatabaseFromEnv
from .user import User
