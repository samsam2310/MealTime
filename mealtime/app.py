# -*- coding: utf-8 -*-

""" MealTime app
"""

from __future__ import absolute_import, print_function, unicode_literals


from .handler import route

import os

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer


def make_app():
    return Application(
        handlers = route,
        template_path = os.path.join(os.path.dirname(__file__), 'template'),
        static_path = os.path.join(os.path.dirname(__file__), 'static'),
        debug = os.environ.get('DEBUG_MODE', '') == 'True',
        autoreload = False
    )


PORT = int(os.environ.get('LISTEN_PORT', 8000))
UNIX_SOCKET = os.environ.get('UNIX_SOCKET', '')

if __name__ == '__main__':
    make_app().listen(PORT, xheaders=True)
    application = make_app()
    if UNIX_SOCKET:
        server = HTTPServer(application)
        socket = bind_unix_socket(UNIX_SOCKET)
        server.add_socket(socket)
    else:
        application.listen(PORT, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()
