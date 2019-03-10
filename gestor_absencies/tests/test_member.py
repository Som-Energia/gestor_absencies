from django.test import TestCase
from gestor_absencies.models import Team, Worker
from django.urls import reverse


class MemberTest(TestCase):
    def setUp(self):
        self.test_team = Team(
            name='IT',
        )
        self.test_team.save()
        self.id_team = self.test_team.pk
        self.base_url = reverse('members')

        self.test_worker = Worker(
            first_name='Worker',
            last_name='Pla',
            email='Worker@example.com',
            username='Pablito',
            password='superpassword'
        )
        self.test_worker.set_password('superpassword')
        self.test_worker.save()
        self.id_worker = self.test_worker.pk

        self.member_relation = Member(
            worker=self.test_worker,
            team=self.test_team
        )
        self.member_relation.save()
        self.id_member = self.member_relation.pk

    def test_list_members(self):
        self.client.login(username='Pablito', password='superpassword')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'id_worker': self.id_worker,
                    'id_team': self.id_team,
                    'is_referent': True,
                    'id_representant': False,
                    'id': self.id_member,
                    }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__add_member(self):
        body = {
            'id_worker': self.id_worker,
            'id_team': self.id_team
        }
        self.client.login(username='Pablito', password='superpassword')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['id_worker'], self.id_worker)
        self.assertEqual(response.json()['id_team'], self.id_team)
        self.assertEqual(response.json()['is_referent'], False)
        self.assertEqual(response.json()['id_representant'], False)

    def test__remove_member(self):
        self.client.login(username='Pablito', password='superpassword')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_member)])
        )

        self.assertEqual(response.status_code, 204)

    def test__update_member(self):
        body = {
            'is_referent': True
        }
        self.client.login(username='Pablito', password='superpassword')
        response = self.client.put(    #TODO: Partial patch or put
            '/'.join([self.base_url, str(self.id_member)]),
            data=body,
            content_type='application/json'
        )

        expected = {'id_worker': self.id_worker,
                    'id_team': self.id_team,
                    'is_referent': True,
                    'id_representant': False,
                    'id': self.id_member,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
