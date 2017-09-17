#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" FB API
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import base64
import requests
import logging

from io import StringIO

# FB_APP_ID = os.environ.get('FB_APP_ID', '')
# FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_TOKEN = os.environ.get('FB_TOKEN', '')
FB_PAGE_NAME = os.environ.get('FB_PAGE_NAME', '')

FB_API_BASE = 'https://graph.facebook.com/v2.9'

def fbRequestPost(url, data):
	json_data = json.dumps(data)
	req = requests.post(
			url,
			headers={"Content-Type": "application/json"},
			data=json_data)
	err = req.json().get('error', None)
	if err:
		logging.error('FB Send API Error: %s' % err['message'])
		return err
	return None

FB_SEND_API_URL = FB_API_BASE + '/me/messages?access_token=%s' % FB_TOKEN
def fbSendMessage(uid, message):
	data = {
		'recipient': {
			'id': uid,
		},
		'message': {
			'text': message
		}
	}
	err = fbRequestPost(FB_SEND_API_URL, data)
	if err and err['code'] == 100 and err['error_subcode'] == '2018109':
		fbSendMessage(uid, 'Error: Message too long.')

def _fbSendFile(uid, payload, file):
	data = {
		'recipient': json.dumps({
			'id': uid,
		}),
		'message': json.dumps({
			'attachment': {
				'type': 'file',
				'payload': payload,
			},
		}),
	}
	req = requests.post(FB_SEND_API_URL, data=data, files=file)
	err = req.json().get('error', None)
	if err:
		logging.error('FB Send API Error: %s' % err['message'])
	return req

def fbSendFileById(uid, file_id):
	_fbSendFile(uid, {'attachment_id': file_id}, None)

def fbSendFileFromString(uid, file_name, string):
	req = _fbSendFile(
		uid, {'is_reusable': True}, {'filedata': 
			(file_name, StringIO(string), 'text/csv')})
	attachment_id = req.json().get('attachment_id', None)
	return attachment_id

MAX_LEN = 640 - 10
def fbSplitMessageLine(message, sp_char = '\n'):
	sp_message = ''
	for line in message.split(sp_char):
		if len(sp_message) + len(line) + 1 >= MAX_LEN:
			# len of single line may >= MAX_LEN
			yield sp_message
			sp_message = ''
		sp_message += line + sp_char
	if sp_message:
		yield sp_message

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


FB_API_USER_DATA_URL = FB_API_BASE + '/%s?access_token=%s'
def fbGetUserData(uid):
	url = FB_API_USER_DATA_URL % (uid, FB_TOKEN)
	req = requests.get(url)
	data = req.json()
	if not data.get('locale', None) or not data.get('timezone', None):
		logging.error('User data do not contain locale or timezone(ID: %s)' % uid)
	return data
