#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Handler - BaseHandler
"""

from __future__ import absolute_import, print_function, unicode_literals


from datetime import datetime

import functools
import os
import tornado.web

from ..db import get_db


class BaseApiHandler(tornado.web.RequestHandler):
	def initialize(self):
		""" This method run at handler object initialize.
		"""
		self._db = get_db()
		self._db_token = self._db['AccessToken']

	def prepare(self):
		"""This method is executed at the beginning of each request.
		"""
		token = self.get_argument('access_token', default='')
		if token and self._db_token.find({'token': token}).count():
			self.current_user = token
		else:
			raise self.HTTPError(403, reason='Invalid token.')

	def on_finish(self):
		"""Finish this response, ending the HTTP request 
		and properly close the database.
		"""
		pass

	def write_error(self, error, **kwargs):
		if kwargs.get('exc_info'):
			if issubclass(kwargs['exc_info'][0], self.HTTPError):
				error_str = str(kwargs['exc_info'][1])
			else:
				error_str = str(self.HTTPError(500))
		else:
			error_str = 'HTTP %d: %s' % (error, kwargs.get('reason', ''))
		self.write({'error': error_str})

	def write_success(self, data={}):
		data['success'] = 1
		self.write(data)

	@property
	def HTTPError(self):
		return tornado.web.HTTPError

	_ARG_DEFAULT = object()
	def get_argument(self, arg_name, default=_ARG_DEFAULT, *a, **args):
		arg = super(BaseApiHandler, self).get_argument(arg_name, default=default, *a, **args)
		if default is self._ARG_DEFAULT and not arg:
			raise self.HTTPError(403, 'Missing argument "%s".' % arg_name)
		return arg
