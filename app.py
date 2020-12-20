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


@dataclass
class Company(db.Model):
    id: int
    company_name_ko: str
    company_name_en: str
    company_name_ja: str
    
    id = db.Column(db.Integer, primary_key=True)
    company_name_ko = db.Column(db.String(255))
    company_name_en = db.Column(db.String(255))
    company_name_ja = db.Column(db.String(255))
    company_tag_ko = db.Column(db.Text)
    company_tag_en = db.Column(db.Text)
    company_tag_ja = db.Column(db.Text)


class CompanyAutocompleteViewSet(Resource):
    def get(self, name):
        company_lang = getattr(Company, f'company_name_{request.accept_languages}', None)
        if company_lang:
            company = Company.query.filter(company_lang.startswith(name)).first()
        else:
            company = {}
            
        return_company_lang = getattr(company, f'company_name_{request.accept_languages}', None)
        return {'name': return_company_lang}


api.add_resource(CompanyAutocompleteViewSet, '/autocomplete/<string:name>')


class CompanyTagViewSet(Resource):
    def get(self, tag):
        company_lang = getattr(Company, f'company_tag_{request.accept_languages}', None)
        if company_lang:
            company = Company.query.filter(company_lang.like(f'%{tag}%')).all()
        else:
            company = {}

        return jsonify(company)
    
    
api.add_resource(CompanyTagViewSet, '/tag/<string:tag>')

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
