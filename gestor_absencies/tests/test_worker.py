from django.test import TestCase
from gestor_absencies.models import Worker
from django.urls import reverse
from django.test import Client


class AdminTest(TestCase):
    def setUp(self):
        self.test_worker = Worker(
            first_name='Pablito',
            last_name='Pla',
            email='example@example.com',
            username='uplabli',
            password='uplabli'
        )
        self.test_worker.set_password('uplabli')
        self.test_worker.save()
        self.id_worker = self.test_worker.pk
        self.base_url = reverse('workers')

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
        login_response = self.login_worker('Admin', 'superpassword')

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()['token'] is not '')

    def test__worker_list__admin(self):
        self.client.login(username='Admin', password='superpassword')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 2,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'first_name': 'Pablito',
                     'last_name': 'Pla',
                     'email': 'example@example.com',
                     'username': 'uplabli',
                     'id': self.id_worker,
                     },
                    {'first_name': 'Admin',
                     'last_name': 'Pla',
                     'email': 'admin@example.com',
                     'username': 'Admin',
                     'id': self.test_admin.pk,
                     }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_get__admin(self):
        self.client.login(username='Admin', password='superpassword')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_worker)])
        )

        expected = {'first_name': 'Pablito',
                    'last_name': 'Pla',
                    'email': 'example@example.com',
                    'username': 'uplabli',
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
            'email': 'newmail@example.com'
        }
        self.client.login(username='Admin', password='superpassword')
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
        self.client.login(username='Admin', password='superpassword')
        body = {
            'username': 'Peli',
            'first_name': 'Pablito',
            'last_name': 'Pla',
            'email': 'newmail@example.com'
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_worker)]),
            data=body,
            content_type='application/json'
        )

        expected = {'first_name': 'Pablito',
                    'last_name': 'Pla',
                    'email': 'newmail@example.com',
                    'username': 'Peli',
                    'id': self.id_worker,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_delete__admin(self):
        self.client.login(username='Admin', password='superpassword')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_worker)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_worker.delete()


class WorkerTest(TestCase):
    def setUp(self):
        self.test_worker = Worker(
            first_name='Pablito',
            last_name='Pla',
            email='example@example.com',
            username='uplabli',
            password='uplabli'
        )
        self.test_worker.set_password('uplabli')
        self.test_worker.save()
        self.id_pablito = self.test_worker.pk
        self.base_url = reverse('workers')

    def login_worker(self, username, password):
        body = {
            'username': 'uplabli',
            'password': 'uplabli',
        }
        response = self.client.post(
            reverse('token_auth'), data=body
        )
        return response

    def test__worker_login(self):
        login_response = self.login_worker('uplabli', 'uplabli')

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()['token'] is not '')

    def test__worker_list__worker(self):
        self.client.login(username='uplabli', password='uplabli')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'first_name': 'Pablito',
                     'last_name': 'Pla',
                     'email': 'example@example.com',
                     'username': 'uplabli',
                     'id': self.id_pablito,
                     }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_get__worker(self):
        self.client.login(username='uplabli', password='uplabli')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_pablito)])
        )

        expected = {'first_name': 'Pablito',
                    'last_name': 'Pla',
                    'email': 'example@example.com',
                    'username': 'uplabli',
                    'id': self.id_pablito,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def tearDown(self):
        self.test_worker.delete()
