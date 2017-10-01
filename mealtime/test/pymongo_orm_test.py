# -*- coding: utf-8 -*-

# Test the ORM module of pymongo

from datetime import datetime

import pymongo
import unittest

from mealtime.db.base import Collection, Field, getDatabaseFromEnv


def getDateTime():
    return datetime(2017, 8, 12)


class TestUser(Collection):
    _ORM_collection = 'TestUser'

    name = Field()
    age = Field(default=18)
    birthday = Field(default=datetime(1997, 1, 12))
    created = Field(default=getDateTime)


class MongoOrmTest(unittest.TestCase):
    def setUp(self):
        self._db = getDatabaseFromEnv()
        self._db.drop_collection(TestUser._ORM_collection)
        self._collection = self._db[TestUser._ORM_collection]
        self._fields = ['name', 'age', 'birthday', 'created']
        self._test_user = TestUser(
            name='Bob', age=20, birthday=datetime(1997, 11, 2))

    def getDefaultData(self, **kargs):
        data = {
            'age': 18,
            'birthday': datetime(1997, 1, 12),
            'created': getDateTime(),
        }
        data.update(kargs)
        return data

    def assertMongoDataEqual(self, orm_object, data):
        self.assertEqual(orm_object['_id'], data['_id'])
        for field in self._fields:
            self.assertEqual(orm_object[field], data[field])

    def testClassField(self):
        self.assertCountEqual(TestUser._getFieldNames(), self._fields)

    def testSave(self):
        test_user = self._test_user
        test_user.save()
        test_user.save()  # call twice do nothing
        self.assertMongoDataEqual(test_user,
                                  self._collection.find_one({
                                      'name': 'Bob'
                                  }))

        test_user['age'] = 17
        test_user.save()
        self.assertMongoDataEqual(test_user,
                                  self._collection.find_one({
                                      'name': 'Bob'
                                  }))

    def testDelete(self):
        test_user = self._test_user
        with self.assertRaises(RuntimeError):
            test_user.delete()
        test_user.save()
        test_user.delete()
        self.assertIsNone(self._collection.find_one({'name': 'Bob'}))

    def testFind(self):
        self._test_user.save()
        bob = TestUser.findOne(name='Bob')
        self.assertMongoDataEqual(bob,
                                  self._collection.find_one({
                                      'name': 'Bob'
                                  }))

        alice = TestUser(name='Alice', age=bob['age'])
        alice.save()
        query = {'age': bob['age']}
        self.assertEqual(TestUser.count(query), 2)
        self.assertEqual(
            len([x for x in TestUser.findMany(query, limit=1)]), 1)
        self.assertEqual(len([x for x in TestUser.findMany(query, skip=2)]), 0)
        self.assertEqual(
            next(TestUser.findMany(query, sort=[('name', 1)]))['name'],
            'Alice')
        self.assertEqual(
            next(TestUser.findMany(query, sort=[('name', -1)]))['name'], 'Bob')
        for found_user in TestUser.findMany(query):
            self.assertEqual(found_user['age'], bob['age'])

    def testGetById(self):
        bob = self._test_user
        bob.save()
        self.assertMongoDataEqual(TestUser.getById(bob['_id']), bob)
        self.assertMongoDataEqual(TestUser.getById(str(bob['_id'])), bob)

    def testUpsert(self):
        alice = TestUser(name='Alice')
        TestUser.upsert(alice, {'name': 'Bob'})
        test_query = TestUser.findOne(name='Alice')
        self.assertIsNotNone(test_query)
        self.assertMongoDataEqual(test_query,
                                  self.getDefaultData(
                                      _id=test_query['_id'], name='Alice'))
        TestUser.findOne(name='Alice').delete()

        bob = self._test_user
        bob.save()
        alice = TestUser(name='Alice')
        alice['age'] = 18
        alice['created'] = datetime(2017, 1, 7)
        TestUser.upsert(alice, {'name': 'Bob'})
        test_query = TestUser.findOne(name='Alice')
        self.assertIsNotNone(test_query)
        self.assertMongoDataEqual(test_query, {
            '_id': test_query['_id'],
            'name': 'Alice',
            'age': 18,
            'birthday': bob['birthday'],
            'created': datetime(2017, 1, 7),
        })

    def testUpdate(self):
        alice = TestUser(name='Alice')
        TestUser.update(alice, {'name': 'Bob'})
        self.assertIsNone(TestUser.findOne(name='Alice'))

        bob = self._test_user
        bob.save()
        TestUser.update(alice, {'name': 'Bob'})
        test_query = TestUser.findOne(name='Alice')
        self.assertIsNotNone(test_query)
        self.assertMongoDataEqual(test_query, {
            '_id': test_query['_id'],
            'name': 'Alice',
            'age': bob['age'],
            'birthday': bob['birthday'],
            'created': bob['created'],
        })
