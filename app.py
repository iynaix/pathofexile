import os

import flask
import flask.ext.restless
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__, static_path='/static')
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    DATABASE_URL = 'postgresql://postgres:password@localhost:5432/pathofexile'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# custom session so we can have django manager like functionality
db = SQLAlchemy(app)

# create the flask-restless API maanger
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
