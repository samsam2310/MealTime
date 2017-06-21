#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Meal Cmd Obj
"""

from __future__ import absolute_import, print_function, unicode_literals

from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime


class MealCmd():	
	def __init__(self, uid, db):
		self._db = db
		self._uid = uid
		self._user = self._db['User'].find_one({'uid': uid})

	@staticmethod
	def getObjectId(key):
		try:
			return ObjectId(key)
		except (InvalidId, TypeError):
			return None	

	CMD = ['group', 'meal', 'menu', 'order']
	def parse(self, cmd_str):
		cmd = cmd_str.split()
		subcmd = cmd[0] if cmd else ''
		if subcmd in self.CMD:
			getattr(self, subcmd)(self, cmd[1:])
		else:
			# TODO: send error message

	CMD_GROUP = ['new', 'del', 'join', 'quit']
	def group(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_GROUP:
			getattr(self, 'group_%s' % subcmd)(self, cmd[1:])
		else:
			# TODO send error message

	def group_new(self, arg):
		if len(arg) < 1:
			#TODO send error message
			return
		name = arg[0]
		info = arg[1:]
		if self._db['Group'].find_one({'name': name}):
			#TODO send error message
			return
		self._db['Group'].insert_one({
			'name': name,
			'owner': self._uid,
			'info_names': info })
		# TODO send success message

	def group_del(self, arg):
		pass

	def group_join(self, arg):
		if len(arg) < 1:
			# TODO
			return

		gid = arg[0]
		info = arg[1:]
		gid_oid = self.getObjectId(gid)
		group = self._db['Group'].find_one({'_id': gid_oid}) if gid_oid else None
		if not group:
			# TODO
			return

		if len(group['info_names']) != len(info):
			# TODO
			return

		self._db['GroupRelation'].update_one({
				'uid': self._uid,
				'gid': group['_id'],
			}, { '$set': {
					'uid': self._uid,
					'gid': group['_id'],
					'info': info
				}
			}, upsert=True)
		# TODO send success message

	def group_quit(self, arg):
		pass

	CMD_MENU = ['new', 'show', 'del', 'edit']
	def menu(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MENU:
			getattr(self, 'menu_%s' % subcmd)(self, cmd[1:])
		else:
			# TODO send error message

	def getGroup(self, arg, idx):
		if len(arg) < idx+1 or not arg[idx].isdigit():
			return None
		gidx = int(arg[idx])
		return self._db['Group'].find_one(
					{ 'owner': self._uid },
					skip = gidx,
					sort = [('name', 1)] )

	def getMenu(self, gid, arg, idx):
		if len(arg) < idx+1 or not arg[idx].isdigit():
			return None
		midx = int(arg[idx])
		return self._db['Menu'].find_one(
					{ 'gid': gid },
					skip = midx,
					sort = [('name', 1)] )

	def menu_new(self, arg):
		group = self.getGroup(arg, 0)
		if not group:
			# TODO
			return

		if len(arg) < 2:
			# TODO
			return
		name = arg[1]
		if self._db['Menu'].find_one({
				'name': name,
				'gid': group['_id'] }):
			# TODO: menu exist
			return
		self._db['Menu'].insert_one({
				'name': name,
				'gid': group['_id'],
				'items': [],
				'ops': [],
				'addi': []
			})
		# TODO send success message

	def menu_show(self, arg):
		pass

	def menu_del(self, arg):
		pass

	@staticmethod
	def getListIndex(l, item):
		if not item in l:
			return len(l)
		return l.index(item)

	def meal_edit(self, arg):
		group = self.getGroup(arg, 0)
		if not group:
			return

		menu = self.getMenu(group['_id'], arg, 1)
		if not menu:
			return

		arg, pos = arg[2:], self.getListIndex(arg,'$')
		item_list, arg = arg[:pos], arg[pos:]
		pos = self.getListIndex(arg,'$')
		op_list, arg = arg[:pos], arg[pos:]
		pos = self.getListIndex(arg,'$')
		addi_list, arg = arg[:pos], arg[pos:]
		try:
			items = []
			for item_s in item_list:
				item = {}
				arr = item_s.split('|')
				item['name'] = arr[0]
				item['price'] = int(arr[1])
				item['opidxs'] = [int(x) for x in arr[2].split(';')]
				items.append(item)

			ops = []
			for op_s in op_list:
				op = {}
				arr = item_s.split('|')
				op['name'] = arr[0]
				op['price'] = int(arr[1])
				ops.append(op)

			addis = []
			for addi_s in addi_list:
				addi = {}
				arr = item_s.split('|')
				addi['name'] = arr[0]
				addi['price'] = int(arr[1])
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
		# TODO: success

	CMD_MEAL = ['new', 'show', 'done']
	def meal(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MEAL:
			getattr(self, 'meal_%s' % subcmd)(self, cmd[1:])
		else:
			# TODO send error message

	def meal_new(self, arg):
		group = self.getGroup(arg, 0)
		if not group:
			return

		menu = self.getMenu(group['_id'], arg, 1)
		if not menu:
			return

		time_format = '%Y-%m-%d-%H:%M'
		if len(arg) < 3:
			# TODO
			return
		start_time = datetime.strptime(arg[2], time_format)

		if len(arg) < 4:
			# TODO
			return
		stop_time = datetime.strptime(arg[3], time_format)

		if len(arg) < 5:
			# TODO
			return
		meal_time = datetime.strptime(arg[4], time_format)

		self._db['Meal'].insert_one({
				'gid': group['_id'],
				'menu_id': menu['_id'],
				'owner': self._uid,
				'start_time': start_time,
				'stop_time': stop_time,
				'meal_time': meal_time
			})
		# TODO: alert all members in the group
		# TODO: success

	def meal_show(self, arg):
		pass

	def meal_done(self, arg):
		pass

	def getMeal(self, arg, idx):
		if len(arg) < idx + 1 or not arg[idx].isdigit():
			return None
		gids = [ x['_id'] for x in self._db['GroupRelation'].find({'uid': self._uid}) ]
		meal_idx = int(arg[idx])
		return self._db['Meal'].find_one({
				'gid': {'$in': gids }
			}, skip=meal_idx, sort=('meal_time', 1))

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
		group = self._db['Group'].find_one({'_id': meal['gid']})
		menu = self._db['Menu'].find_one({'_id': meal['menu_id']})

		item = self.getItem(menu, arg, 1)
		if not item:
			# TODO
			return

		arr = arg[2:]
		pos = self.getListIndex(pos, '$')
		op_list, arr = arr[:pos], arr[pos:]
		pos = self.getListIndex(pos, '$')
		addi_list, arr = arr[:pos], arr[pos:]
		pos = self.getListIndex(pos, '$')
		message_list, arr = arr[:pos], arr[pos:]

		try:
			order_s = item['name'] + ' '
			price = item['price']
			for x in op_list:
				op = menu['ops'][item['opidxs'][x]]
				order_s += op['name'] + ' '
				price += op['price']
			for x in addi_list:
				addi = menu['addis'][x]
				order_s += addi['name'] + ' '
				price += addi['price']
			order_s += 'price: ' + str(price)
			message = ' '.join(message_list)
		except (IndexError):
			# TODO
			return

		self._db['Order'].update_one({
				'uid': self._uid,
				'meal_id': meal['_id']
			}, { '$set': {
				'uid': self._uid,
				'meal_id': meal['_id'],
				'order_string': order_s,
				'message': message
			}}, upsert=True)
		# TODO: seccess
