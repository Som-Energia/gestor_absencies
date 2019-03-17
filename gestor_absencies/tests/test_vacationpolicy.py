from django.test import TestCase
from gestor_absencies.models import VacationPolicy, Worker
from django.urls import reverse


class AdminTest(TestCase):
    def setUp(self):
        self.test_vacationpolicy = VacationPolicy(
            name='normal',
            description='normal vacation policy',
            holidays=25
        )
        self.test_vacationpolicy.save()
        self.id_vacationpolicy = self.test_vacationpolicy.pk
        self.base_url = reverse('vacationpolicy')

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

    def test__vacationpolicy_list__admin(self):
        self.client.login(username='Admin', password='superpassword')
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
        self.client.login(username='Admin', password='superpassword')
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
        self.client.login(username='Admin', password='superpassword')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'special')
        self.assertEqual(response.json()['description'], 'special vacation policy')
        self.assertEqual(response.json()['holidays'], 30)

    def test__vacationpolicy_put__admin(self):
        self.client.login(username='Admin', password='superpassword')
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
        self.client.login(username='Admin', password='superpassword')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_vacationpolicy)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_vacationpolicy.delete()
