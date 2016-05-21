"""
The flask application package.
"""

import flask
from flask import Flask
import gevent
import grequests
patched = False
if not patched:
    gevent.monkey.patch_all()
    patched = True

app = Flask(__name__)


@app.after_request
def per_request_callbacks(response: flask.Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

import api