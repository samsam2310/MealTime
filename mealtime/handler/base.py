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

	def prepare(self):
		"""This method is executed at the beginning of each request.
		"""
		self._db = get_db()

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
