import typing
from dataclasses import dataclass
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api, request, fields
from flask_restful_swagger import swagger
from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators

app = Flask(__name__)

app.config.from_object('config')
app.secret_key = '1E798070A145499E6F1649837221BFC3'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = swagger.docs(
    Api(app),
    apiVersion="0.1",
    basePath="http://localhost",
    resourcePath="/api/spec/",
    produces=["application/json"],
    api_spec_url="/api/spec",
    description="wanted",
)

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

    @staticmethod
    def get_company_lang(obj: object, accept_languages: str):
        return getattr(obj, f'company_name_{accept_languages}', None)

    @staticmethod
    def get_tag_lang(obj: object, accept_languages: str):
        return getattr(obj, f'company_tag_{accept_languages}', None)

    @staticmethod
    def set_tag_lang(obj: object, accept_languages: str, tag: str) -> None:
        setattr(obj, f'company_tag_{accept_languages}', tag)
    


class TagForm(Form):
    company_id = IntegerField('company_id', [validators.NumberRange(min=1)])
    tag = StringField('tag', [validators.Length(min=1)])


class CompanyAutocompleteViewSet(Resource):
    @swagger.model
    class autocomplete:
        def __init__(self, name):
            pass
    @swagger.operation(
        notes="회사명 자동완성",
        responseClass=autocomplete.__name__,
        nickname="get",
        parameters=[
            {
                "name": "Accept-Language",
                "description": "언어 코드 ex) ko",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "header",
            }
        ],
    )
    def get(self, name):
        company_lang = Company.get_company_lang(obj=Company, accept_languages=request.accept_languages)
        if company_lang:
            company = Company.query.filter(company_lang.startswith(name)).first()
        else:
            company = {}
            
        return_company_lang = Company.get_company_lang(obj=company, accept_languages=request.accept_languages)
        return {'name': return_company_lang}


api.add_resource(CompanyAutocompleteViewSet, '/autocomplete/<string:name>')


class CompanyListTagViewSet(Resource):
    @swagger.model
    class tag_list:
        resource_fields = {
            "company_name_ja": fields.String(),
            "company_name_en": fields.String(),
            "company_name_ko": fields.String(),
            "id": fields.Integer(),
        }
    @swagger.operation(
        notes="태그명으로 회사 검색",
        responseClass=tag_list.__name__,
        nickname="get",
        parameters=[
            {
                "name": "Accept-Language",
                "description": "언어 코드 ex) ko",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "header",
            }
        ],
    )
    def get(self, tag):
        tag_lang = Company.get_tag_lang(obj=Company, accept_languages=request.accept_languages)
        if tag_lang:
            company = Company.query.filter(tag_lang.like(f'%{tag}%')).all()
        else:
            company = {}

        return jsonify(company)
    
    
api.add_resource(CompanyListTagViewSet, '/tag/<string:tag>')


class CompanyTagViewSet(Resource):
    @swagger.operation(
        notes="회사 태그 정보 추가",
        nickname="post",
        parameters=[
            {
                "name": "company_id",
                "description": "company id",
                "required": True,
                "allowMultiple": False,
                "dataType": "integer",
                "paramType": "form",
            },
            {
                "name": "tag",
                "description": "태그",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "form",
            },
            {
                "name": "Accept-Language",
                "description": "언어 코드 ex) ko",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "header",
            }
        ],
    )
    def post(self):
        try:
            data: dict = self._is_valid()

            company_id = data.get('company_id')
            tag = data.get('tag')
            company = Company.query.get(company_id)
            company_tag = Company.get_tag_lang(obj=company, accept_languages=request.accept_languages)
            
            if tag in company_tag.split('|'):
                raise ValueError('이미 존재하는 태그 입니다.')
    
            Company.set_tag_lang(obj=company, accept_languages=request.accept_languages, tag=f'{company_tag}|{tag}')
            db.session.commit()
        except (ValueError, GetModelError,) as e:
            return e.__str__(), 400
        
        return '', 201
        
    @swagger.operation(
        notes="회사 태그 정보 삭제",
        nickname="delete",
        parameters=[
            {
                "name": "company_id",
                "description": "company id",
                "required": True,
                "allowMultiple": False,
                "dataType": "integer",
                "paramType": "form",
            },
            {
                "name": "tag",
                "description": "태그",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "form",
            },
            {
                "name": "Accept-Language",
                "description": "언어 코드 ex) ko",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "header",
            }
        ],
    )
    def delete(self):
        try:
            data: dict = self._is_valid()
    
            company_id = data.get('company_id')
            tag = data.get('tag')
            company = Company.query.get(company_id)
            company_tag = Company.get_tag_lang(obj=company, accept_languages=request.accept_languages)
            
            tag_list = company_tag.split('|')
    
            if tag not in tag_list:
                raise ValueError('존재하지 않는 태그 입니다.')
    
            tag_list.remove(tag)
    
            Company.set_tag_lang(obj=company, accept_languages=request.accept_languages, tag='|'.join(tag_list))
            db.session.commit()
            
        except (ValueError, GetModelError,) as e:
            return e.__str__(), 400

        return '', 204
    
    
    def _is_valid(self) -> typing.Dict[str, typing.Union[str, int]]:
        form = TagForm(request.form)

        if not form.validate():
            raise ValueError('Field not found')

        company_id = form.data.get('company_id')
        company = Company.query.get(company_id)

        if company is None:
            raise GetModelError('유효한 company가 아닙니다!')

        company_tag = Company.get_tag_lang(obj=company, accept_languages=request.accept_languages)

        if company_tag is None:
            raise ValueError('해당 언어는 지원하지 않습니다.')
        
        return form.data
        
    
api.add_resource(CompanyTagViewSet, '/tag/')


@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
