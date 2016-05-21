"""
The flask application package.
"""

import flask
from flask import Flask
from gevent import monkey; monkey.patch_all()

app = Flask(__name__)


@app.after_request
def per_request_callbacks(response: flask.Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

import api