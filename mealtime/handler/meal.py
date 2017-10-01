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

from .base import BasePageHandler


class MealHandler(BasePageHandler):
    def get(self, key):
        meal_id_obj = ObjectId(key) if ObjectId.is_valid(key) else None
        meal = self._db['Meal'].find_one({
            '_id': meal_id_obj,
            'is_done': False
        }) if meal_id_obj else None
        if not meal:
            raise self.HTTPError(404)

        menu = self._db['Menu'].find_one({'_id': meal['menu_id']})
        orders = [x for x in self._db['Order'].find({'meal_id': meal['_id']})]

        item_d = {}
        for order in orders:
            item_p = (order['item_string'], order['item_price'])
            item_d[item_p] = item_d.get(item_p, 0) + 1
            for addi_idx in order['addi_idxs']:
                addi = menu['addis'][addi_idx]
                addi_p = (addi['name'], addi['price'])
                item_d[addi_p] = item_d.get(addi_p, 0) + 1
        item_strs = []
        total_price = 0
        for item_p in item_d:
            num = item_d[item_p]
            item_strs.append('%s (Price: $%d) x%d' % (item_p[0], item_p[1],
                                                      num))
            total_price += item_p[1] * num

        self.render(
            'meal.html',
            menu=menu,
            orders=orders,
            item_strs=item_strs,
            total_price=total_price)
