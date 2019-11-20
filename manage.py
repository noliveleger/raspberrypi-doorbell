# -*- code utf-8 -*-
from flask import Flask

from app.services import ServicesLoader
from app.config import config

app = Flask(__name__)
app.config.from_object(config)

services_loader = ServicesLoader(app)


@app.route('/')
def index():
    return 'Hello, World!'

