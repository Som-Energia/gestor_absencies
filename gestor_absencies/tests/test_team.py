from os.path import join

from django.test import TestCase
from django.urls import reverse
from gestor_absencies.tests.test_helper import (
    create_team,
    create_worker
)


class TeamTest(TestCase):
    def setUp(self):
        self.base_url = reverse('teams')

        self.test_admin = create_worker(username='admin', is_admin=True)
        self.test_worker = create_worker()

        self.test_team = create_team(created_by=self.test_admin)
        self.id_team = self.test_team.pk

    def test__team_list__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'IT',
                     'id': self.id_team
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__team_get__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            join(self.base_url, str(self.id_team))
        )

        expected = {'name': 'IT',
                    'id': self.id_team,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__team_post__admin(self):
        body = {
            'name': 'ET',
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'ET')

    def test__team_put__admin(self):
        self.client.login(username='admin', password='password')
        body = {
            'name': 'OV Team',
        }
        response = self.client.put(
            join(self.base_url, str(self.id_team)),
            data=body,
            content_type='application/json'
        )

        expected = {'name': 'OV Team',
                    'id': self.id_team,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__team_delete__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            join(self.base_url, str(self.id_team))
        )
        self.assertEqual(response.status_code, 204)

    def test__team_list__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'IT',
                     'id': self.id_team,
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__team_get__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            join(self.base_url, str(self.id_team))
        )

        expected = {'name': 'IT',
                    'id': self.id_team,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def tearDown(self):
        self.test_worker.delete()
        self.test_team.delete()
        self.test_admin.delete()
