"""
The flask application package.
"""

from flask import Flask
from gevent import monkey; monkey.patch_all()

app = Flask(__name__)
import api