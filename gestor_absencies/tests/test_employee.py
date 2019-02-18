from django.test import TestCase
from gestor_absencies.models import Employee
from django.urls import reverse


class EmployeeTest(TestCase):
    def setUp(self):
        self.test_employee = Employee(
            firstname='Pablito',
            secondname='Pla',
            email='example@example.com'
        )
        self.test_employee.save()
        self.id_pablito = self.test_employee.pk
        self.base_url = reverse('employees')

    def test__employees_list(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['firstname'], 'Pablito')
        self.assertEqual(response.json()['results'][0]['secondname'], 'Pla')
        self.assertEqual(response.json()['results'][0]['email'], 'example@example.com')

    def test__employee_get(self):
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_pablito)])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['firstname'], 'Pablito')
        self.assertEqual(response.json()['secondname'], 'Pla')
        self.assertEqual(response.json()['email'], 'example@example.com')

    def test__employee_post(self):
        body = {
            'firstname': 'Pelayo',
            'secondname': 'Manzano',
            'email': 'newmail@example.com'
        }
        response = self.client.post(
            self.base_url, body
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['firstname'], 'Pelayo')
        self.assertEqual(response.json()['secondname'], 'Manzano')
        self.assertEqual(response.json()['email'], 'newmail@example.com')

    def test__employee_put(self):
        body = {
            'firstname': 'Pablito',
            'secondname': 'Pla',
            'email': 'renewmail@example.com'
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_pablito)]),
            body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['firstname'], 'Pablito')
        self.assertEqual(response.json()['secondname'], 'Pla')
        self.assertEqual(response.json()['email'], 'renewmail@example.com')

    def test__employee_delete(self):
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_pablito)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_employee.delete()
