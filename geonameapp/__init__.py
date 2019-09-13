from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from geonameapp import routes
from geonameapp import api
