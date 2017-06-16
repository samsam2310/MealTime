#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Handler - Fb webhook
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import hashlib
import hmac

from .base import BaseApiHandler


FB_WEBHOOK_TOKEN = os.environ.get('FB_WEBHOOK_TOKEN', '')
FB_APP_ID = os.environ.get('FB_APP_ID', '')
FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_TOKEN = os.environ.get('FB_TOKEN', '')


class MealCmd():
	def __init__(self, user_id):
		pass

	def parse(cmd_str):
		pass


class FBWebHookHandler(BaseApiHandler):
	# def prepare(self):
	# 	super(self.__class__, self).prepare()

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
		messaging_events = data['entry'][0]['messaging']
		text = ''
		for event in messaging_events:
			sender = event["sender"]["id"];
			if ("message" in event and "text" in event["message"]):
				text = event["message"]["text"]
				print('Got:',text)
