# -*- coding: utf-8 -*-
# DB - Pymongo ORM Base Class

import os
import pymongo

DB_HOST = os.environ.get('DB_HOST', 'localhost:27017').split(",")
DB_REPLSET = os.environ.get('DB_REPLSET', None)
DB_USER = os.environ.get('DB_USER', '')
DB_PWD = os.environ.get('DB_PWD', '')
DB_NAME = os.environ.get('DB_NAME', 'mealtime')
# The time out of MongoClient, in seconds.
DB_TIMEOUT = 2


def getDatabaseFromEnv(is_log_mode=False):
    if is_log_mode:
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

    mongo_client = MongoClient(
        host=DB_HOST,
        replicaset=DB_REPLSET,
        serverSelectionTimeoutMS=DB_TIMEOUT)
    database = mongo_client[DB_NAME]

    if DB_USER != '':
        if not database.authenticate(DB_USER, DB_PWD):
            print('Database auth failed.')
            return None
    return database


class Field():
    def __init__(self, default=None):
        self._default = default

    def getDefault():
        default = self._default
        return default() if callable(default) else default


class Collection():
    _ORM_field_names = None
    _ORM_database = getDatabaseFromEnv(True)
    # Overrite by subclass
    _ORM_name = 'default'

    @classmethod
    def _ormFieldInit(cls):
        _ORM_field_names = [
            attr for attr in cls.__dict__ if isinstance(attr, Field)
        ]

    @classmethod
    def _checkInstance(cls, val, message):
        if not isinstance(orm_object, cls):
            raise ValueError(message)

    @classmethod
    def insert(cls, orm_object):
        cls._checkInstance('orm_object must be a isinstance of %s' % cls)
        # TODO

    @classmethod
    def upsert(cls, orm_object, query):
        cls._checkInstance('orm_object must be a isinstance of %s' % cls)
        # TODO

    @classmethod
    def update(cls, orm_object, query):
        cls._checkInstance('orm_object must be a isinstance of %s' % cls)
        # TODO

    @classmethod
    def query(cls, **kargs):
        pass
        # TODO

    @classmethod
    def getCollection(cls):
        return cls._ORM_database[cls._ORM_name]

    def __init__(self, *args, **kargs):
        if not self.__class__._ORM_field_names:
            self.__class__._ormFieldInit()

        self._data = {'_id': kargs.get('_id', None)}
        for attr in self.__class__._ORM_field_names:
            self._data[attr] = kargs.get(attr, )
            if attr in kargs:
                self._data[attr] = kargs[attr]
            else:
                field = getattr(self.__class__, attr)
                self._data[attr] = field.getDefault()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, val):
        self._data[key] = val

    def save(self):
        if not self._id:
            # TODO : add message
            raise RuntimeError('')
        # TODO : maybe need data filter to remove _id in $set
        self.getCollection().update_one({
            '_id': self._data['_id']
        }, {'$set': self._data})

    def delete(self):
        if not self._id:
            # TODO : add message
            raise RuntimeError('')
        # TODO
