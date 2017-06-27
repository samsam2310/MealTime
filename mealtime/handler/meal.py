#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Handler - Meal detail show
"""

from __future__ import absolute_import, print_function, unicode_literals

from bson.objectid import ObjectId

import os
import json
import hashlib
import hmac
import logging
import base64
import binascii

from .base import BaseApiHandler
from ..db import get_db


class MealHandler(BaseApiHandler):
	def get(self, key):
		meal_id_obj = ObjectId(key) if ObjectId.is_valid(key) else None
		meal = self._db['Meal'].find_one({'_id': meal_id_obj, 'is_Done': False}) if meal_id_obj else None
		if not meal:
			raise self.HTTPError(404)

		orders = [x for x in self._db['Order'].find({'meal_id': meal['_id']})]

		# TODO : add summary

		self.render('meal.html', meal=meal, orders=orders)