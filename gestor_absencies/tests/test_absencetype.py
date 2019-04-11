from django.test import TestCase
from gestor_absencies.models import SomEnergiaAbsenceType, Worker
from django.urls import reverse
from gestor_absencies.tests.test_helper import (
    create_worker,
    create_absencetype
)

class AdminTest(TestCase):
    def setUp(self):
        self.test_absencetype = create_absencetype(
            abbr='vacn',
            label='Vacances',
            spend_days=1,
            min_duration=0.5,
            max_duration=-1,
        )
        self.id_absencetype = self.test_absencetype.pk
        self.base_url = reverse('absencetype')

        self.test_admin = create_worker(
            username='admin',
            is_admin=True
        )

    def test__absencetype_list__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'abbr': 'vacn',
                      'label': 'Vacances',
                      'spend_days': 1,
                      'min_duration': '0.5',
                      'max_duration': '-1.0',
                      'id': self.id_absencetype
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_get__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )

        expected = {'abbr': 'vacn',
                    'label': 'Vacances',
                    'spend_days': 1,
                    'min_duration': '0.5',
                    'max_duration': '-1.0',
                    'id': self.id_absencetype
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_post__admin(self):
        body = {
            'abbr': 'baiA',
            'label': 'baixa A',
            'spend_days': 0,
            'min_duration': 1,
            'max_duration': 3,
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['abbr'], 'baiA')
        self.assertEqual(response.json()['label'], 'baixa A')
        self.assertEqual(response.json()['spend_days'], 0)
        self.assertEqual(response.json()['min_duration'], '1.0')
        self.assertEqual(response.json()['max_duration'], '3.0')

    def test__absencetype_put__admin(self):
        self.client.login(username='admin', password='password')
        body = {
            'abbr': 'vacn',
            'spend_days': 1,
            'min_duration': 3,
            'max_duration': 10,
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_absencetype)]),
            data=body,
            content_type='application/json'
        )

        expected = {'abbr': 'vacn',
                    'label': 'Vacances',
                    'spend_days': 1,
                    'min_duration': '3.0',
                    'max_duration': '10.0',
                    'id': self.id_absencetype
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_delete__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_absencetype.delete()
