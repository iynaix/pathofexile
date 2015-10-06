import os

from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    'postgresql://postgres:password@localhost:5432/pathofexile',
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# custom session so we can have django manager like functionality
db = SQLAlchemy(app)

# create the flask-restless API maanger
api = Api(app)
