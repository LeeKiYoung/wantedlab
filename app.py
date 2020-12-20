import typing
from dataclasses import dataclass
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

app = Flask(__name__)

app.config.from_object('config')
app.secret_key = '1E798070A145499E6F1649837221BFC3'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name_ko = db.Column(db.String(255))
    company_name_en = db.Column(db.String(255))
    company_name_ja = db.Column(db.String(255))
    company_tag_ko = db.Column(db.Text)
    company_tag_en = db.Column(db.Text)
    company_tag_ja = db.Column(db.Text)


@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
