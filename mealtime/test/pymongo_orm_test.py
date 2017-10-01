# -*- coding: utf-8 -*-

# Run the unit test by "python -m mealtime.test"

import unittest


class PyMongoORMTestCase(unittest.TestCase):
    @unittest.skip("demonstrating skipping")
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
