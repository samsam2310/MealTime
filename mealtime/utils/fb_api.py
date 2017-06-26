#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" FB API
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import base64
import requests


# FB_APP_ID = os.environ.get('FB_APP_ID', '')
# FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_TOKEN = os.environ.get('FB_TOKEN', '')
FB_PAGE_NAME = os.environ.get('FB_PAGE_NAME', '')


def fbRequestPost(url, data):
	json_data = json.dumps(data)
	req = requests.post(
			url,
			headers={"Content-Type": "application/json"},
			data=json_data)


FB_SEND_API_URL = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % FB_TOKEN
def fbSendMessage(uid, message):
	data = {
		'recipient': {
			'id': uid
		},
		'message': {
			'text': message
		}
	}
	fbRequestPost(FB_SEND_API_URL, data)

def fbSendHaveRead(uid):
	data = {
		'recipient': {
			'id': uid
		},
		'sender_action': 'mark_seen'
	}
	fbRequestPost(FB_SEND_API_URL, data)

def fbSendShippingUpdate(uid, message):
	data = {
		'recipient': {
			'id': uid
		},
		'message': {
			'text': message
		},
		'tag': 'SHIPPING_UPDATE'
	}
	fbRequestPost(FB_SEND_API_URL, data)

FB_MME_URL = 'http://m.me/%s' % FB_PAGE_NAME
def fbGetMMeLink(ref = ''):
	url = FB_MME_URL
	if ref:
		enc_data = base64.urlsafe_b64encode(ref.encode()).decode()
		url += '?ref=%s' % enc_data
	return url
