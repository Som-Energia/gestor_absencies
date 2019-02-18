from django.test import TestCase
from gestor_absencies.models import Team
from django.urls import reverse


class TeamTest(TestCase):
    def setUp(self):
        self.test_team = Team(
            name='IT'
        )
        self.test_team.save()
        self.id_it = self.test_team.pk
        self.base_url = reverse('teams')

    def test__team_list(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], 'IT')

    def test__team_get(self):
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_it)])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'IT')

    def test__team_post(self):
        body = {
            'name': 'Telèfon'
        }
        response = self.client.post(
            self.base_url, body
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Telèfon')

    def test__team_put(self):
        body = {
            'name': 'IT superstar'
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_it)]),
            body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'IT superstar')

    def test__team_delete(self):
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_it)])
        )
        self.assertEqual(response.status_code, 204)

    def tearDown(self):
        self.test_team.delete()
