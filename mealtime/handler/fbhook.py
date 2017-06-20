#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Handler - Fb webhook
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import hashlib
import hmac
import logging

from .base import BaseApiHandler
from ..db import get_db
from ..util.mealcmd import MealCmd


FB_WEBHOOK_TOKEN = os.environ.get('FB_WEBHOOK_TOKEN', '')
# FB_APP_ID = os.environ.get('FB_APP_ID', '')
FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
# FB_TOKEN = os.environ.get('FB_TOKEN', '')


class FBWebHookHandler(BaseApiHandler):
	def prepare(self):
		super(self.__class__, self).prepare()
		self._db = get_db()

	def get(self):
		token = self.get_argument('hub.verify_token', default='')
		if token and token == FB_WEBHOOK_TOKEN:
			self.current_user = 'fb'
		else:
			raise self.HTTPError(403, reason='Invalid token.')

		challenge = self.get_argument('hub.challenge', default='')
		self.write(challenge)

	def verifyPost(self):
		sign = 'sha1=%s' % hmac.new(
								FB_APP_SECRET.encode('utf-8'),
								msg=self.request.body,
								digestmod=hashlib.sha1 ).hexdigest()
		hub_sign = self.request.headers.get('X-Hub-Signature', '')
		return sign == hub_sign

	def post(self):
		if not self.verifyPost():
			raise self.HTTPError(403)

		data = json.loads(self.request.body.decode('utf-8'))
		if len(data['entry']) >= 1:
			# Only one page belone to this webhook, so only one entry obj.
			entry = data['entry'][0]
			logging.info('Got entry(PageId: %s)' % entry['id'])
			for m in entry.get('messaging', []):
				if m.get('message', None)
					self.handleMessage(m)
				# else: Not message webhook.

	# Assert 'message' is a message webhook obj.
	def handleMessage(self, message):
		# TODO: A message(same mid) only be handle once.
		uid = message['sender']['id']
		cmd_obj = MealCmd(uid)
		text = message['message'].get('text', None)
		if text:
			cmd_obj.parse(text)
		# else: Not a text message(maybe like img or something else).
