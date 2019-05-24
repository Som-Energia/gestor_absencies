from django.test import TestCase
from django.urls import reverse
from gestor_absencies.tests.test_helper import (
    create_vacationpolicy,
    create_worker
)


class AdminTest(TestCase):
    def setUp(self):
        self.base_url = reverse('vacationpolicy')

        self.test_admin = create_worker(
            username='admin',
            is_admin=True
        )
        self.test_worker = create_worker()

        self.test_vacationpolicy = create_vacationpolicy(
            description='normal vacation policy',
            created_by=self.test_admin
        )
        self.id_vacationpolicy = self.test_vacationpolicy.pk

    def test__vacationpolicy_list__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'normal',
                     'description': 'normal vacation policy',
                     'holidays': 25,
                     'id': self.id_vacationpolicy
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__vacationpolicy_get__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_vacationpolicy)])
        )

        expected = {'name': 'normal',
                    'description': 'normal vacation policy',
                    'holidays': 25,
                    'id': self.id_vacationpolicy
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__vacationpolicy_post__admin(self):
        body = {
            'name': 'special',
            'description': 'special vacation policy',
            'holidays': 30
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'special')
        self.assertEqual(response.json()['description'], 'special vacation policy')
        self.assertEqual(response.json()['holidays'], 30)

    def test__vacationpolicy_put__admin(self):
        self.client.login(username='admin', password='password')
        body = {
            'name': 'normal',
            'holidays': 30
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_vacationpolicy)]),
            data=body,
            content_type='application/json'
        )

        expected = {'name': 'normal',
                    'description': 'normal vacation policy',
                    'holidays': 30,
                    'id': self.id_vacationpolicy
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__vacationpolicy_delete__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_vacationpolicy)])
        )
        self.assertEqual(response.status_code, 204)

    def test__vacationpolicy_list__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'normal',
                     'description': 'normal vacation policy',
                     'holidays': 25,
                     'id': self.id_vacationpolicy
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__vacationpolicy_get__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_vacationpolicy)])
        )

        expected = {'name': 'normal',
                    'description': 'normal vacation policy',
                    'holidays': 25,
                    'id': self.id_vacationpolicy
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__vacationpolicy_post__worker(self):
        body = {
            'name': 'special',
            'description': 'special vacation policy',
            'holidays': 30
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

    def test__vacationpolicy_put__worker(self):
        self.client.login(username='username', password='password')
        body = {
            'name': 'normal',
            'holidays': 30
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_vacationpolicy)]),
            data=body,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__vacationpolicy_delete__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_vacationpolicy)])
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__cant_repeat_same_name(self):
        pass

    def test__vacationpolicy_post_set_create_modified_params(self):
        pass

    def test__vacationpolicy_put_set_modified_params(self):
        pass

    def tearDown(self):
        self.test_vacationpolicy.delete()


# TODO: Tests

# With unexpected body params no raise error
# Can't delete a used VP (Relation with Worker)