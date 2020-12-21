import unittest
import json
from app import app, Company


class UnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = app.test_client()
        self.ko_headers = {
            'Accept-Language': 'ko'
        }
        self.ja_headers = {
            'Accept-Language': 'ja'
        }
        self.data = {
            'company_id': 1,
            'tag': '이기영'
        }
        
    def test_get_autocomplete(self) -> None:
        response = self.app.get('autocomplete/원티', headers=self.ko_headers)
        self.assertEqual(200, response.status_code)

        data: dict = json.loads(response.get_data())
        company_name = data.get('name', None)
        self.assertEqual('원티드랩', company_name)
        
    def test_get_tag(self) -> None:
        response = self.app.get('tag/タグ_4', headers=self.ja_headers)
        self.assertEqual(200, response.status_code)

        data: list = json.loads(response.get_data())
        wanted_company = False
        company: dict
        for company in data:
            if company.get('company_name_ko', '') == '원티드랩':
                wanted_company = True
        self.assertTrue(wanted_company)
        
    def test_post_delete_tag(self) -> None:
        response = self.app.post('/tag/', data=self.data, headers=self.ko_headers)
        self.assertEqual(201, response.status_code)
        
        company = Company.query.get(self.data.get('company_id'))
        company_tag = company.company_tag_ko.split('|')
        tag = self.data.get('tag')
        
        exist_tag = False
        if tag in company_tag:
            exist_tag = True
        self.assertTrue(exist_tag)
        
        response = self.app.delete('/tag/', data=self.data, headers=self.ko_headers)
        self.assertEqual(204, response.status_code)
        
        company = Company.query.get(self.data.get('company_id'))
        company_tag = company.company_tag_ko.split('|')
        
        if tag not in company_tag:
            exist_tag = False
        self.assertFalse(exist_tag)
        
        
if __name__ == '__main__':
    unittest.main()