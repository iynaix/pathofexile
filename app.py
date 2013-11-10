from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = \
                'postgresql://postgres:password@localhost:5432/pathofexile'

#custom session so we can have django manager like functionality
db = SQLAlchemy(app)
