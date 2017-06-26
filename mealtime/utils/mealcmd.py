#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Meal Cmd Obj
"""

from __future__ import absolute_import, print_function, unicode_literals

from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime

from .fb_api import fbSendMessage, fbSendHaveRead, fbSendShippingUpdate, fbGetMMeLink


class MealCmd():	
	def __init__(self, uid, db):
		self._db = db
		self._uid = uid
		# user may be none!!
		user = self._db['User'].find_one({'uid': uid})
		self._user = user if user else {'_id': uid, 'cmd': [], 'error_cnt': 0}
		self._save_cmd = []
		self._error_cnt = self._user['error_cnt']
		self._clear_tag = False

	@staticmethod
	def getObjectId(key):
		return ObjectId(key) if ObjectId.is_valid(key) else None

	def sendMessage(self, message):
		fbSendMessage(self._uid, message)

	def sendSuccess(self, message):
		self.clearCmd()
		self.sendMessage(message)	

	# When error_count up to 3 clear the saved cmd.
	def sendError(self, message):
		self.clearCmd()
		fbSendMessage(self._uid, 'Failed: ' + message)

	def sendWrongFormat(self, message):
		error_message = 'Wrong format: %s\n' % message
		self._error_cnt += 1
		if self._error_cnt >= 3:
			error_message += 'Faild: Enter wrong format too many times.'
			self.clearCmd()
		else:
			error_message += 'Please enter it again:'
		fbSendMessage(self._uid, error_message)

	def sendHaveRead(self):
		fbSendHaveRead(self._uid)

	def pushCmd(self, cmd):
		self._save_cmd.append(cmd)

	def clearCmd(self):
		self._clear_tag = True

	CMD = ['meal', 'menu', 'order']
	def parse(self, cmd_str, is_start_new=False):
		new_cmd = cmd_str.split()
		arg = self._user['cmd'] + new_cmd if not is_start_new else new_cmd
		subcmd = arg[0] if arg else ''
		if self._user['cmd'] and not new_cmd:
			self.sendWrongFormat('Blank input.')
		elif subcmd in self.CMD:
			self.pushCmd(subcmd)
			getattr(self, subcmd)(arg[1:])
		else:
			self.clearCmd()
			self.sendHaveRead()

		if self._clear_tag:
			self._save_cmd.clear()
			self._error_cnt = 0
		self._db['User'].update_one({'uid': self._uid}, {'$set': {
				'uid': self._uid,
				'cmd': self._save_cmd,
				'error_cnt': self._error_cnt
			}}, upsert=True)


	# ------------------------------------------------------
	# Menu
	# ------------------------------------------------------
	CMD_MENU = ['new', 'show', 'del', 'edit']
	def menu(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MENU:
			self.pushCmd(subcmd)
			getattr(self, 'menu_%s' % subcmd)(arg[1:])
		else:
			self.clearCmd()
			self.sendHaveRead()

	def getMenu(self, arg, idx):
		cursor = self._db['Menu'].find({ 'owner': self._uid }, sort=[('name', 1)])
		if cursor.clone().count() == 0:
			self.sendError('There is no menu.')
			return None
		if len(arg) < idx+1:
			menu_list_str = 'Enter the index of menu:\n'
			for i, menu in enumerate(cursor):
				menu_list_str += 'ID:%d %s\n' % (i, menu['name'])
			self.sendMessage(menu_list_str)
			return None
		elif not arg[idx].isdigit():
			self.sendWrongFormat('Index not integer.')
			return None

		midx = int(arg[idx])
		self.pushCmd(arg[idx])
		menu = self._db['Menu'].find_one(
					{ 'owner': self._uid },
					skip = midx,
					sort = [('name', 1)] )
		if not menu:
			self.sendWrongFormat('Index is out of range.')
		return menu

	def menu_new(self, arg):
		if len(arg) < 1:
			self.sendMessage('Please enter a name:')
			return
		name = arg[0]
		if self._db['Menu'].find_one({
				'name': name,
				'owner': self._uid }):
			self.sendError('The name has been used.')
			return
		self._db['Menu'].insert_one({
				'name': name,
				'owner': self._uid,
				'items': [],
				'ops': [],
				'addis': []
			})
		self.sendSuccess('Menu "%s" successfully created.' % name)

	def menu_show(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return

		menu_str = 'Menu item:\n'
		for i,item in enumerate(menu['items']):
			op_str = ''
			for opidx in item['opidxs']:
				op = menu['ops'][opidx]
				op_str += ' %s $%d' % (op['name'], op['price'])
			menu_str += '%d. %s $%d (%s )\n' % (i, item['name'], item['price'], op_str)
		menu_str += 'Additional options:\n'
		for addi in menu['addis']:
			menu_str += '%s $%d ;' % (addi['name'], addi['price'])
		self.sendMessage(menu_str)

		menu_raw_str = 'Menu raw data:\n'
		for item in menu['items']:
			op_raw_str = ';'.join(map(lambda x:str(x), item['opidxs']) )
			menu_raw_str += '%s|%d|%s ' % (item['name'], item['price'], op_raw_str)
		menu_raw_str += '$ '
		for op in menu['ops']:
			menu_raw_str += '%s|%d ' % (op['name'], op['price'])
		menu_raw_str += '$ '
		for addi in menu['addis']:
			menu_raw_str += '%s|%d ' % (addi['name'], op['price'])
		self.sendSuccess(menu_raw_str)

	def menu_del(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return
		if self._db['Meal'].find({'isDone': False, 'menu_id': menu['_id']}).count() != 0:
			self.sendError('There are some meal still using this menu, complete them before delete this menu.')
			return
		self._db['Menu'].delete_one({'_id': menu['_id']})
		self.sendSuccess('Menu "%s" deleted.' % menu['name'])

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
		if not arr:
			self.sendMessage('Enter the menu data:')
			return
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
				item['opidxs'] = [int(x) for x in item_arr[2].split(';')] if item_arr[2] else []
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
			self.sendWrongFormat('Menu data is not correct.')
			return

		self._db['Menu'].update_one(
			{'_id': menu['_id']},
			{'$set': {
				'items': items,
				'ops': ops,
				'addis': addis}
			} )
		self.sendSuccess('Menu "%s" successfully updated.' % menu['name'])

	# ------------------------------------------------------
	# Meal
	# ------------------------------------------------------
	CMD_MEAL = ['new', 'show', 'done', 'del']
	def meal(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MEAL:
			self.pushCmd(subcmd)
			getattr(self, 'meal_%s' % subcmd)(arg[1:])
		else:
			self.clearCmd()
			self.sendHaveRead()

	def getTime(self, arg, idx, title):
		time_format = '%Y-%m-%d-%H:%M'
		if len(arg) < idx+1:
			self.sendMessage('Enter the %s (ex: 2017-08-12-12:00):' % title)
			return None
		try:
			time_obj = datetime.strptime(arg[idx], time_format)
		except ValueError:
			self.sendWrongFormat('Input does not match the format.')
			return
		self.pushCmd(arg[idx])
		return time_obj

	def getMeal(self, arg, idx):
		cursor = self._db['Meal'].find({ 'owner': self._uid, 'isDone': False }, sort=[('_id', 1)])
		if cursor.clone().count() == 0:
			self.sendError('There is no meal.')
			return None
		if len(arg) < idx+1:
			meal_list_str = 'Enter the index of the meal:\n'
			for i, meal in enumerate(cursor):
				meal_list_str += 'IDX:%d MEAL_ID:%s\n' % (i, meal['_id'])
			self.sendMessage(meal_list_str)
			return None
		elif not arg[idx].isdigit():
			self.sendWrongFormat('Index not integer.')
			return None

		midx = int(arg[idx])
		self.pushCmd(arg[idx])
		meal = self._db['Meal'].find_one(
					{ 'owner': self._uid, 'isDone': False },
					skip = midx,
					sort = [('_id', 1)] )
		if not meal:
			self.sendWrongFormat('Index is out of range.')
		return meal

	def meal_new(self, arg):
		menu = self.getMenu(arg, 0)
		if not menu:
			return

		start_time = self.getTime(arg, 1, 'start time')
		if not start_time:
			return

		stop_time = self.getTime(arg, 2, 'stop time')
		if not stop_time:
			return

		meal_time = self.getTime(arg, 3, 'meal time')
		if not meal_time:
			return

		arr = arg[4:]
		if not arr:
			self.sendMessage('Enter informations\' title, split by blank. If there is no informations\' title, enter single "$".')
			return
		info_titles, arr = self.getSplitList(arr)

		res = self._db['Meal'].insert_one({
				'menu_id': menu['_id'],
				'owner': self._uid,
				'infos': info_titles,
				'start_time': start_time,
				'stop_time': stop_time,
				'meal_time': meal_time,
				'isDone': False
			})
		self.sendMessage('Meal created. id: %s\nStart at: %s\nStop at: %s\nMeal time: %s\nInformations list: %s\nPeople can order the meal by this link:' % (
			res.inserted_id, arg[1], arg[2], arg[3], ' '.join(info_titles) ))
		self.sendSuccess(fbGetMMeLink('order %s' % res.inserted_id))


	def meal_show(self, arg):
		meal = self.getMeal(arg, 0)
		if not meal:
			return

		menu = self._db.find_one({'_id': meal['menu_id']})

		meal_str = 'Meal(ID: %s):\n' % meal['_id']
		meal_str += 'Menu Name: %s\n' % menu['name']
		meal_str += 'Start at: %s\n' % meal['start_time'].strftime('%Y-%m-%d-%H:%M')
		meal_str += 'Stop at: %s\n' % meal['stop_time'].strftime('%Y-%m-%d-%H:%M')
		meal_str += 'Meal time: %s\n' % meal['meal_time'].strftime('%Y-%m-%d-%H:%M')
		meal_str += 'Informations list: %s' % ' '.join(meal['infos'])
		self.sendSuccess(meal_str)

	def meal_done(self, arg, is_del=False):
		meal = self.getMeal(arg, 0)
		if not meal:
			return

		arr = arg[1:]
		if not arr:
			self.sendMessage('Enter any other comments(Enter single "$" if no comments.):')
			return
		message_list, arr = self.getSplitList(arr)
		ann = ' '.join(message_list) if message_list else 'None.'

		self._db['Meal'].update_one({'_id': meal['_id']}, {'$set': {'isDone': True}})
		if is_del:
			info_str = 'Meal(id: %s) is delete.\nNotify all subscribers.' % meal['_id']
		else:
			info_str = 'Meal(id: %s) is done.\nNotify all subscribers.' % meal['_id']
		self.sendSuccess(info_str)

		cursor = self._db['Order'].find({'meal_id': meal['_id']})
		for order in cursor:
			if is_del:
				noti_str = 'Your order is cancel by the publisher.(Meal ID: %d)' % meal['_id']
			else:
				noti_str = 'The meal(ID: %s) has arrived.\nYour order is:\n%s\nMessage: %s' % (
					meal['_id'], order['order_string'], ann)
			fbSendShippingUpdate(order['uid'], noti_str)

	def meal_del(self, arg):
		self.meal_done(arg, is_del=True)


	# ------------------------------------------------------
	# Order
	# ------------------------------------------------------
	def getMealByOid(self, arg, idx):
		if len(arg) < idx + 1:
			self.sendMessage('Enter the meal id:')
			return None
		meal_oid = self.getObjectId(arg[idx])
		if not meal_oid:
			self.sendWrongFormat('Meal id incorrect.')
			return None
		meal = self._db['Meal'].find_one({'_id': meal_oid})
		if not meal or meal['isDone']:
			self.sendError('Meal do not exist.')
			return None
		now_time = datetime.now()
		if now_time < meal['start_time']:
			self.sendError('You can order meal after %s' % meal['start_time'].strftime('%Y-%m-%d-%H:%M'))
			return None
		if now_time > meal['stop_time']:
			self.sendError('The meal has expired at %s.' % meal['stop_time'].strftime('%Y-%m-%d-%H:%M'))
			return None
		self.pushCmd(arg[idx])
		return meal

	def getItem(self, menu, arg, idx):
		if len(arg) < idx + 1:
			item_str = 'Enter the index of the selected item:\n'
			for i, item in enumerate(menu['items']):
				item_str += 'ID:%d %s $%d\n' % (i, item['name'], item['price'])
			self.sendMessage(item_str)
			return None
		elif not arg[idx].isdigit():
			self.sendWrongFormat('Index not integer.')
			return None

		item_idx = int(arg[idx])
		if item_idx in range(len(menu['items'])):
			self.pushCmd(arg[idx])
			return menu['items'][item_idx]
		self.sendWrongFormat('Index out of range.')
		return None

	# Order has no subcmd
	def order(self, arg):
		meal = self.getMealByOid(arg, 0)
		if not meal:
			return
		menu = self._db['Menu'].find_one({'_id': meal['menu_id']})

		arr = arg[1:]
		# Show Order Infomation
		if not arr:
			self.sendMessage('Order\nMenu: %s\nMeal Time: %s' % (menu['name'], meal['meal_time'].strftime('%Y-%m-%d-%H:%M')))
		info_list, arr = self.getSplitList(arr)
		for info in info_list:
			self.pushCmd(info)
		if len(info_list) != len(meal['infos']):
			if len(info_list) > len(meal['infos']):
				self.sendError('Command format error.')
			else:
				self.sendMessage('Please enter your "%s":' % meal['infos'][len(info_list)])
			return
		self.pushCmd('$')

		item = self.getItem(menu, arr, 0)
		if not item:
			return
		order_string = item['name'] + ' ('
		order_price = item['price']

		arr = arr[1:]
		# No op_list
		if not arr:
			info_str = 'Enter the indexs of the options(Split them by blank character(s). Enter single "$" if no options.):\n'
			for i,opidx in enumerate(item['opidxs']):
				op = menu['ops'][opidx]
				info_str += 'ID:%d %s $%d\n' % (i, op['name'], op['price'])
			self.sendMessage(info_str)
			return
		op_list, arr = self.getSplitList(arr)
		try:
			for x in op_list:
				op = menu['ops'][item['opidxs'][int(x)]]
				order_string += op['name'] + ' '
				order_price += op['price']
			order_string += ') '
		except (IndexError, ValueError):
			self.sendWrongFormat('Indexs of options have wrong format.')
			return
		for op in op_list:
			self.pushCmd(op)
		self.pushCmd('$')

		# No addi_list
		if not arr:
			info_str = 'Enter the indexs of the additional options(Split them by blank character(s). Enter single "$" if no options.):\n'
			for i,addi in enumerate(menu['addis']):
				info_str += 'ID:%d %s $%d\n' % (i, addi['name'], addi['price'])
			self.sendMessage(info_str)
			return
		addi_list, arr = self.getSplitList(arr)
		try:
			for x in addi_list:
				addi = menu['addis'][int(x)]
				order_string += addi['name'] + ' '
				order_price += addi['price']
		except (IndexError, ValueError):
			self.sendWrongFormat('Indexs of additional options have wrong format.')
			return
		for addi in addi_list:
			self.pushCmd(addi)
		self.pushCmd('$')

		# No message_list
		if not arr:
			info_str = 'Enter any other comments(Enter single "$" if no comments.):'
			self.sendMessage(info_str)
			return
		message_list, arr = self.getSplitList(arr)

		order_string += 'price: ' + str(order_price)
		message = ' '.join(message_list)

		self._db['Order'].update_one({
				'uid': self._uid,
				'meal_id': meal['_id']
			}, { '$set': {
				'uid': self._uid,
				'meal_id': meal['_id'],
				'infos': info_list,
				'order_string': order_string,
				'message': message
			}}, upsert=True)
		info_str = 'Information:\n'
		for i in range(len(meal['infos'])):
			info_str += '  %s: %s\n' % (meal['infos'][i], info_list[i])
		self.sendSuccess('Orders received!\n%s\nMeal ID:%s\nOrder:\n  %s\nMessage:\n  %s' % (
				info_str, meal['_id'], order_string, message))
