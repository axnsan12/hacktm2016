"""
This script runs the hacktm2016 application using a development server.
"""

from os import environ
from init import app
from gevent.wsgi import WSGIServer

if __name__ == '__main__':
	HOST = environ.get('SERVER_HOST', 'localhost')
	HOST = '0.0.0.0'
	try:
		PORT = int(environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	app.debug = True
	server = WSGIServer((HOST, PORT), app)
	server.serve_forever()