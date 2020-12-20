import typing
from dataclasses import dataclass
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api, request
from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators

app = Flask(__name__)

app.config.from_object('config')
app.secret_key = '1E798070A145499E6F1649837221BFC3'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)


class GetModelError(Exception):
    pass


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


class TagForm(Form):
    company_id = IntegerField('company_id', [validators.NumberRange(min=1)])
    tag = StringField('tag', [validators.Length(min=1)])


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


class CompanyListTagViewSet(Resource):
    def get(self, tag):
        company_lang = getattr(Company, f'company_tag_{request.accept_languages}', None)
        if company_lang:
            company = Company.query.filter(company_lang.like(f'%{tag}%')).all()
        else:
            company = {}

        return jsonify(company)
    
    
api.add_resource(CompanyListTagViewSet, '/tag/<string:tag>')


class CompanyTagViewSet(Resource):
    def post(self):
        form = TagForm(request.form)
        
        if not form.validate():
            return "Field not found", 400

        company_id = form.data.get('company_id')
        tag = form.data.get('tag')
        company = Company.query.get(company_id)
        
        try:
            if company is None:
                raise GetModelError('유효한 company가 아닙니다!')
        except GetModelError as e:
            return e.__str__(), 400

        company_tag = getattr(company, f'company_tag_{request.accept_languages}', None)
        
        try:
            if company_tag is None:
                raise ValueError
        except ValueError:
            return '해당 언어는 지원하지 않습니다.', 400
        
        if tag in company_tag.split('|'):
            return '이미 존재하는 태그 입니다.', 400

        setattr(company, f'company_tag_{request.accept_languages}', f'{company_tag}|{tag}')
        db.session.commit()
        
        return '', 201
        
    def delete(self):
        form = TagForm(request.form)
    
        if not form.validate():
            return "Field not found", 400
    
        company_id = form.data.get('company_id')
        tag = form.data.get('tag')
        company = Company.query.get(company_id)
    
        try:
            if company is None:
                raise GetModelError('유효한 company가 아닙니다!')
        except GetModelError as e:
            return e.__str__(), 400
    
        company_tag = getattr(company, f'company_tag_{request.accept_languages}', None)
    
        try:
            if company_tag is None:
                raise ValueError
        except ValueError:
            return '해당 언어는 지원하지 않습니다.', 400

        tag_list = company_tag.split('|')

        if tag not in tag_list:
            return '존재하지 않는 태그 입니다.', 400

        tag_list.remove(tag)

        setattr(company, f'company_tag_{request.accept_languages}', '|'.join(tag_list))
        db.session.commit()

        return '', 204
    
    
    
api.add_resource(CompanyTagViewSet, '/tag/')


@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
