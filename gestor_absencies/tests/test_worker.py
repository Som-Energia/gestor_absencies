from django.test import TestCase
from os.path import join
from django.urls import reverse
from gestor_absencies.tests.test_helper import (
    create_worker,
    create_vacationpolicy
)


class AdminTest(TestCase):
    def setUp(self):
        self.test_worker = create_worker()
        self.test_admin = create_worker(username='admin', is_admin=True)
        self.id_worker = self.test_worker.pk
        self.base_url = reverse('workers')

        self.test_vacation_policy = create_vacationpolicy(
            description='tomorrow',
            created_by=self.test_admin
        )

    def login_worker(self, username, password):
        body = {
            'username': username,
            'password': password,
        }
        response = self.client.post(
            reverse('token_auth'), data=body
        )
        return response

    def test__worker_login(self):
        login_response = self.login_worker('admin', 'password')

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()['token'] is not '')

    def test__worker_list__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 2,
                    'next': None,
                    'previous': None,
                    'results':
                    [
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.test_admin.pk,
                         'last_name': 'last_name',
                         'username': 'admin',
                         },
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.id_worker,
                         'last_name': 'last_name',
                         'username': 'username',
                         },
                    ]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_get__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            join(self.base_url, str(self.id_worker))
        )

        expected = {'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email@example.com',
                    'username': 'username',
                    'id': self.id_worker,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_post__admin(self):
        body = {
            'username': 'Peli',
            'password': 'yalo',
            'first_name': 'Pelayo',
            'last_name': 'Manzano',
            'email': 'newmail@example.com',
            'vacation_policy': self.test_vacation_policy.pk
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        login_response = self.login_worker('Peli', 'yalo')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['first_name'], 'Pelayo')
        self.assertEqual(response.json()['last_name'], 'Manzano')
        self.assertEqual(response.json()['email'], 'newmail@example.com')
        self.assertEqual(response.json()['username'], 'Peli')
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()['token'] is not '')

    def test__worker_put_email__admin(self):
        self.client.login(username='admin', password='password')
        body = {
            'username': 'worker',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'newmail@example.com'
        }
        response = self.client.put(
            join(self.base_url, str(self.id_worker)),
            data=body,
            content_type='application/json'
        )

        expected = {'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'newmail@example.com',
                    'username': 'worker',
                    'id': self.id_worker,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_delete__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            join(self.base_url, str(self.id_worker))
        )
        self.assertEqual(response.status_code, 204)

    def test__worker_list__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 2,
                    'next': None,
                    'previous': None,
                    'results':
                    [
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.test_admin.pk,
                         'last_name': 'last_name',
                         'username': 'admin',
                         },
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.id_worker,
                         'last_name': 'last_name',
                         'username': 'username',
                         },
                    ]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_get__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            join(self.base_url, str(self.id_worker))
        )

        expected = {'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email@example.com',
                    'username': 'username',
                    'id': self.id_worker,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def tearDown(self):
        self.test_worker.delete()
        self.test_admin.delete()
