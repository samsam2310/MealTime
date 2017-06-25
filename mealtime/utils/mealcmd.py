#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Meal Cmd Obj
"""

from __future__ import absolute_import, print_function, unicode_literals

from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime

from .fb_api import fbSendMessage


class MealCmd():	
	def __init__(self, uid, db):
		self._db = db
		self._uid = uid
		self._user = self._db['User'].find_one({'uid': uid})

	@staticmethod
	def getObjectId(key):
		return ObjectId(key) if ObjectId.is_valid(key) else None

	def sendMessage(self, message):
		fbSendMessage(self._uid, message)

	CMD = ['meal', 'menu', 'order']
	def parse(self, cmd_str):
		arg = cmd_str.split()
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD:
			getattr(self, subcmd)(arg[1:])
		else:
			pass
			# TODO: send error message

	# ------------------------------------------------------
	# Menu
	# ------------------------------------------------------
	CMD_MENU = ['new', 'show', 'del', 'edit']
	def menu(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MENU:
			getattr(self, 'menu_%s' % subcmd)(arg[1:])
		else:
			pass
			# TODO send error message

	def getMenu(self, arg, idx):
		if len(arg) < idx+1 or not arg[idx].isdigit():
			return None
		midx = int(arg[idx])
		return self._db['Menu'].find_one(
					{ 'owner': self._uid },
					skip = midx,
					sort = [('name', 1)] )

	def menu_new(self, arg):
		if len(arg) < 1:
			# TODO
			return
		name = arg[0]
		if self._db['Menu'].find_one({
				'name': name,
				'owner': self._uid }):
			# TODO: menu exist
			return
		self._db['Menu'].insert_one({
				'name': name,
				'owner': self._uid,
				'items': [],
				'ops': [],
				'addi': []
			})
		self.sendMessage('Menu successfully created.')

	def menu_show(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return
		# self.sendMessage('')

	def menu_del(self, arg):
		pass

	@staticmethod
	def getListIndex(l, item):
		if not item in l:
			return len(l)
		return l.index(item)

	@classmethod
	def getSplitList(cls, arr):
		pos = cls.getListIndex(arr, '$')
		return arr[:pos], arr[pos+1:]

	def menu_edit(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return

		arr = arg[1:]
		item_list, arr = self.getSplitList(arr)
		op_list, arr = self.getSplitList(arr)
		addi_list, arr = self.getSplitList(arr)
		try:
			items = []
			for item_s in item_list:
				item = {}
				item_arr = item_s.split('|')
				item['name'] = item_arr[0]
				item['price'] = int(item_arr[1])
				item['opidxs'] = [int(x) for x in item_arr[2].split(';')]
				items.append(item)

			ops = []
			for op_s in op_list:
				op = {}
				op_arr = op_s.split('|')
				op['name'] = op_arr[0]
				op['price'] = int(op_arr[1])
				ops.append(op)

			addis = []
			for addi_s in addi_list:
				addi = {}
				addi_arr = addi_s.split('|')
				addi['name'] = addi_arr[0]
				addi['price'] = int(addi_arr[1])
				addis.append(addi)

			if not all(
					all(idx in range(len(ops)) for idx in item['opidxs'])
					for item in items):
				raise IndexError
		except (IndexError, ValueError):
			# TODO: error
			return

		self._db['Menu'].update_one(
			{'_id': menu['_id']},
			{'$set': {
				'items': items,
				'ops': ops,
				'addis': addis}
			} )
		self.sendMessage('Menu successfully updated.')

	# ------------------------------------------------------
	# Meal
	# ------------------------------------------------------
	CMD_MEAL = ['new', 'show', 'done']
	def meal(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MEAL:
			getattr(self, 'meal_%s' % subcmd)(arg[1:])
		else:
			pass
			# TODO send error message

	def getTime(self, arg, idx):
		time_format = '%Y-%m-%d-%H:%M'
		if len(arg) < idx+1:
			return None
		return datetime.strptime(arg[idx], time_format)

	def meal_new(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return

		start_time = self.getTime(arg, 1)
		if not start_time:
			# TODO
			return

		stop_time = self.getTime(arg, 2)
		if not stop_time:
			# TODO
			return

		meal_time = self.getTime(arg, 3)
		if not meal_time:
			# TODO
			return

		info_titles = arg[4:]

		res = self._db['Meal'].insert_one({
				'menu_id': menu['_id'],
				'owner': self._uid,
				'infos': info_titles,
				'start_time': start_time,
				'stop_time': stop_time,
				'meal_time': meal_time
			})
		# TODO: alert all members in the group
		self.sendMessage('Meal created. id: %s' % res.inserted_id)

	def meal_show(self, arg):
		pass

	def meal_done(self, arg):
		pass

	# ------------------------------------------------------
	# Order
	# ------------------------------------------------------
	def getMeal(self, arg, idx):
		if len(arg) < idx + 1:
			return None
		meal_oid = self.getObjectId(arg[idx])
		return self._db['Meal'].find_one({'_id': meal_oid}) if meal_oid else None

	def getItem(self, menu, arg, idx):
		if len(arg) < idx + 1 or not arg[idx].isdigit():
			return None
		item_idx = int(arg[idx])
		if item_idx in range(len(menu['items'])):
			return menu['items'][item_idx]
		return None

	# Order has no subcmd
	def order(self, arg):
		meal = self.getMeal(arg, 0)
		if not meal:
			# TODO
			return
		menu = self._db['Menu'].find_one({'_id': meal['menu_id']})

		arr = arg[1:]
		info_list, arr = self.getSplitList(arr)
		if len(info_list) != len(meal['infos']):
			# TODO
			return

		item = self.getItem(menu, arr, 0)
		arr = arr[1:]
		if not item:
			# TODO
			return

		op_list, arr = self.getSplitList(arr)
		addi_list, arr = self.getSplitList(arr)
		message_list, arr = self.getSplitList(arr)

		try:
			order_s = item['name'] + ' '
			price = item['price']
			for x in op_list:
				op = menu['ops'][item['opidxs'][int(x)]]
				order_s += op['name'] + ' '
				price += op['price']
			for x in addi_list:
				addi = menu['addis'][int(x)]
				order_s += addi['name'] + ' '
				price += addi['price']
			order_s += 'price: ' + str(price)
			message = ' '.join(message_list)
		except (IndexError, ValueError):
			# TODO
			return

		self._db['Order'].update_one({
				'uid': self._uid,
				'meal_id': meal['_id']
			}, { '$set': {
				'uid': self._uid,
				'meal_id': meal['_id'],
				'infos': info_list,
				'order_string': order_s,
				'message': message
			}}, upsert=True)
		self.sendMessage('Orders received!\n%s' % order_s)
