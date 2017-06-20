#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Meal Cmd Obj
"""

from __future__ import absolute_import, print_function, unicode_literals


class MealCmd():	
	def __init__(self, uid):
		pass

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
		pass

	def group_del(self, arg):
		pass

	def group_join(self, arg):
		pass

	def group_quit(self, arg):
		pass

	CMD_MEAL = ['new', 'show', 'del', 'edit']
	def meal(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MEAL:
			getattr(self, 'meal_%s' % subcmd)(self, cmd[1:])
		else:
			# TODO send error message

	def meal_new(self, arg):
		pass

	def meal_show(self, arg):
		pass

	def meal_del(self, arg):
		pass

	def meal_edit(self, arg):
		pass

	CMD_MENU = ['new', 'show', 'done']
	def menu(self, arg):
		subcmd = arg[0] if arg else ''
		if subcmd in self.CMD_MENU:
			getattr(self, 'menu_%s' % subcmd)(self, cmd[1:])
		else:
			# TODO send error message

	def menu_new(self, arg):
		pass

	def menu_show(self, arg):
		pass

	def menu_done(self, arg):
		pass

	# Order has no subcmd
	def order(self, arg):
		pass
