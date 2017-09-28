# -*- coding: utf-8 -*-

""" MealTime app
"""

from __future__ import absolute_import, print_function, unicode_literals


from .handler import route

import os
import logging

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_unix_socket
from datetime import datetime


DEBUG_MODE = bool(os.environ.get('DEBUG_MODE', ''))
LISTEN_PORT	= int(os.environ.get('LISTEN_PORT', 8000))
UNIX_SOCKET	= os.environ.get('UNIX_SOCKET', '')

if DEBUG_MODE:
	logging.basicConfig(level=logging.DEBUG)

def make_app():
	return Application(
		handlers = route,
		template_path = os.path.join(os.path.dirname(__file__), 'template'),
		static_path = os.path.join(os.path.dirname(__file__), '../public'),
		debug = DEBUG_MODE,
		autoreload = False
	)

if __name__ == '__main__':
	application = make_app()
	server_info = ''
	if UNIX_SOCKET:
		server = HTTPServer(application)
		socket = bind_unix_socket(UNIX_SOCKET, mode=0o666)
		server.add_socket(socket)
		server_info = 'Server(%s)' % UNIX_SOCKET
	else:
		application.listen(LISTEN_PORT, xheaders=True)
		server_info = 'Server(Port: %d)' % LISTEN_PORT
	logging.info('%s start at %s' % (server_info, str(datetime.now()) ) )
	IOLoop.instance().start()
	logging.info('%s top at %s' % (server_info, str(datetime.now()) ) )
