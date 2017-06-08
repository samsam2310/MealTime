#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" DB - init
"""

from __future__ import absolute_import, print_function, unicode_literals


from pymongo import MongoClient

import os


__all__ = ['get_db',]


DB_HOST		= os.environ.get('DB_HOST', 'localhost:27017').split(",")
DB_REPLSET	= os.environ.get('DB_REPLSET', None)
DB_USER		= os.environ.get('DB_USER', '')
DB_PWD		= os.environ.get('DB_PWD', '')
DB_NAME		= os.environ.get('DB_NAME', 'mealtime')


def get_db(show_detail=False):
    if show_detail:
        print("Connect to DB: %s/%s" % (','.join(DB_HOST), DB_NAME))
        if DB_REPLSET:
            print("Replica Set: %s" % DB_REPLSET)
        if DB_USER:
            print("Login with user: %s" % DB_USER)
        else:
            print("Login without user.")
    if not DB_REPLSET and len(DB_HOST) > 1:
        print('Missing Replica set.')
        return None

    db = MongoClient(host=DB_HOST, replicaset=DB_REPLSET)[DB_NAME]

    if DB_USER != '':
        if not db.authenticate(DB_USER, DB_PWD):
            print('Database auth failed.')
            return None
    return db
