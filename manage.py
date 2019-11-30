# -*- code utf-8 -*-
from flask import Flask
from flask_talisman import Talisman

from app.config import config
from app.helpers.assets import Assets
from app.models import database
from app.services import ServicesLoader
from app.www.mobile.module import MobileMod

app = Flask(__name__)
app.config.from_object(config)

assets = Assets.register(app)
mobile_mod = MobileMod(app)
services_loader = ServicesLoader(app)

talisman = Talisman(app,
                    content_security_policy=config.get('CONTENT_SECURITY_POLICY'),
                    content_security_policy_nonce_in=['script-src'])


# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    database.connect()


# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()

