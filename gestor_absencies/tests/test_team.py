from django.test import TestCase
from gestor_absencies.models import Team, Worker
from django.urls import reverse


class AdminTest(TestCase):
    def setUp(self):
        self.test_team = Team(
            name='IT',
        )
        self.test_team.save()
        self.id_team = self.test_team.pk
        self.base_url = reverse('teams')

        self.test_admin = Worker(
            first_name='Admin',
            last_name='Pla',
            email='admin@example.com',
            username='Admin',
            password='superpassword'
        )
        self.test_admin.set_password('superpassword')
        self.test_admin.is_superuser = True
        self.test_admin.save()

    def test__team_list__admin(self):
        self.client.login(username='Admin', password='superpassword')
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
        self.client.login(username='Admin', password='superpassword')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_team)])
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
        self.client.login(username='Admin', password='superpassword')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'ET')

    def test__team_put__admin(self):
        self.client.login(username='Admin', password='superpassword')
        body = {
            'name': 'OV Team',
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_team)]),
            data=body,
            content_type='application/json'
        )

        expected = {'name': 'OV Team',
                    'id': self.id_team,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__team_delete__admin(self):
        self.client.login(username='Admin', password='superpassword')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_team)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_team.delete()


class WorkerTest(TestCase):
    def setUp(self):
        self.test_team = Team(
            name='IT',
        )
        self.test_team.save()
        self.id_team = self.test_team.pk
        self.base_url = reverse('teams')

        self.test_worker = Worker(
            first_name='Pablito',
            last_name='Pla',
            email='example@example.com',
            username='uplabli',
            password='uplabli'
        )
        self.test_worker.set_password('uplabli')
        self.test_worker.save()

    def test__team_list__worker(self):
        self.client.login(username='uplabli', password='uplabli')
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
        self.client.login(username='uplabli', password='uplabli')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_team)])
        )

        expected = {'name': 'IT',
                    'id': self.id_team,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def tearDown(self):
        self.test_worker.delete()
        self.test_team.delete()
