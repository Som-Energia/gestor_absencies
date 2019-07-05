from datetime import datetime as dt
from os.path import join

from django.test import TestCase
from django.urls import reverse
from gestor_absencies.models import Worker
from gestor_absencies.tests.test_helper import (
    create_absencetype,
    create_vacationpolicy,
    create_worker
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
            reverse('login'), data=body
        )
        return response

    def test__worker_login(self):
        login_response = self.login_worker('admin', 'password')

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()['token'] is not '')
        self.assertEqual(login_response.json()['user_id'], self.test_admin.id)
        self.assertEqual(login_response.json()['is_admin'], True)

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
                         'holidays': '0.0',
                         'gender': '',
                         'category': '',
                         'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                         'vacation_policy': None,
                         'working_week': 40
                         },
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.id_worker,
                         'last_name': 'last_name',
                         'username': 'username',
                         'holidays': '0.0',
                         'gender': '',
                         'category': '',
                         'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                         'vacation_policy': None,
                         'working_week': 40
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
                    'holidays': '0.0',
                    'gender': '',
                    'category': '',
                    'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                    'vacation_policy': None,
                    'working_week': 40
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
            'category': 'dasgdasfg',
            'email': 'newmail@example.com',
            'contract_date': dt(2019, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            'working_week': 32
        }
        response = self.client.put(
            join(self.base_url, str(self.id_worker)),
            data=body,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

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
                         'holidays': '0.0',
                         'gender': '',
                         'category': '',
                         'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                         'vacation_policy': None,
                         'working_week': 40
                         },
                        {'email': 'email@example.com',
                         'first_name': 'first_name',
                         'id': self.id_worker,
                         'last_name': 'last_name',
                         'username': 'username',
                         'holidays': '0.0',
                         'gender': '',
                         'category': '',
                         'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                         'vacation_policy': None,
                         'working_week': 40
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
                    'holidays': '0.0',
                    'gender': '',
                    'category': '',
                    'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                    'vacation_policy': None,
                    'working_week': 40
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_cant_post__worker(self):
        body = {
            'username': 'Peli',
            'password': 'yalo',
            'first_name': 'Pelayo',
            'last_name': 'Manzano',
            'email': 'newmail@example.com',
            'vacation_policy': self.test_vacation_policy.pk
        }
        self.client.login(username='username', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__worker_cant_put_another_email__worker(self):
        second_worker = create_worker(username='new_worker')
        self.client.login(username='username', password='password')
        body = {
            'username': 'new_worker',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'newmail@example.com'
        }
        response = self.client.put(
            join(self.base_url, str(second_worker.pk)),
            data=body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__worker_can_update_her_profile__worker(self):
        self.client.login(username='username', password='password')
        body = {
            'username': 'worker',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'newmail@example.com',
            'contract_date': dt(2019, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            'working_week': 32
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
                    'holidays': '0.0',
                    'gender': '',
                    'category': '',
                    'contract_date': dt(2019, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
                    'vacation_policy': None,
                    'working_week': 32
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__worker_can_change_password__worker(self):
        self.client.login(username='username', password='password')
        body = {
            'username': 'username',
            'password': 'newpassword'
        }
        response = self.client.put(
            join(self.base_url, str(self.id_worker)),
            data=body,
            content_type='application/json'
        )
        login_response = self.login_worker('username', 'newpassword')

        expected = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email@example.com',
            'username': 'username',
            'id': self.id_worker,
            'holidays': '0.0',
            'gender': '',
            'category': '',
            'contract_date': dt(2018, 9, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            'vacation_policy': None,
            'working_week': 40
        }
        self.test_worker.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
        self.assertEqual(login_response.status_code, 200)

    def test__worker_cant_delete__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.delete(
            join(self.base_url, str(self.id_worker))
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__worker_need_vacationpolicy(self):
        body = {
            'username': 'Peli',
            'password': 'yalo',
            'first_name': 'Pelayo',
            'last_name': 'Manzano',
            'email': 'newmail@example.com'
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'vacation_policy': ['This field is required.']}
        )

    def test__post_with_gender_choice(self):
        body = {
            'username': 'Peli',
            'password': 'yalo',
            'first_name': 'Pelayo',
            'last_name': 'Manzano',
            'gender': 'random',
            'email': 'newmail@example.com'
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'gender': ['"random" is not a valid choice.']}
        )

    def test__post_with_category_choice(self):
        body = {
            'username': 'Peli',
            'password': 'yalo',
            'first_name': 'Pelayo',
            'last_name': 'Manzano',
            'category': 'random',
            'email': 'newmail@example.com'
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'category': ['"random" is not a valid choice.']}
        )

    def test__create_worker_create_her_somenergiaabsences(self):
        absence_type = create_absencetype(
            name='Baixa defuncio',
            description='Baixa defuncio',
            spend_days=0,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#000000',
        )
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

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(Worker.objects.all().filter(username='Peli')[0].
                absence.all()),
            1
        )

    def test__bad_login__response_error(self):
        login_response = self.login_worker('admin', 'bad_password')

        self.assertEqual(login_response.status_code, 400) #401?
        self.assertEqual(login_response.json(),
            {'non_field_errors': ['Unable to log in with provided credentials.']}
        )

    def test__worker_post_set_create_modified_params(self):
        pass

    def test__worker_put_set_modified_params(self):
        pass

    def tearDown(self):
        self.test_worker.delete()
        self.test_admin.delete()


# TODO: Tests

# Post Worker no need category and gender attributes
# With unexpected body params no raise error
