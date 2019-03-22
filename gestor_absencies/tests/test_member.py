from django.test import TestCase
from gestor_absencies.models import Team, Worker, Member
from django.urls import reverse


class MemberTest(TestCase):

    def setUp(self):
        self.test_team = create_team()

        self.id_team = self.test_team.pk
        self.base_url = reverse('members')

        self.test_worker = create_worker()
        self.id_worker = self.test_worker.pk

        self.member_relation = create_member(
            worker=self.test_worker,
            team=self.test_team,
        )
        self.id_member = self.member_relation.pk

    def test_list_members(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'worker': self.id_worker,
                    'team': self.id_team,
                    'is_referent': False,
                    'is_representant': False,
                    'id': self.id_member,
                    }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__list_filter_members(self):
        self.test_otherteam = create_team(name='ET')
        self.id_otherteam = self.test_otherteam.pk
        self.member_otherrelation = create_member(
            worker=self.test_worker,
            team=self.test_otherteam
        )

        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url, {'team': self.id_otherteam}
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'worker': self.id_worker,
                    'team': self.id_otherteam,
                    'is_referent': False,
                    'is_representant': False,
                    'id': self.member_otherrelation.pk,
                    }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

        self.member_otherrelation.delete()

    def test__add_member(self):
        body = {
            'worker': self.id_worker,
            'team': self.id_team
        }
        self.client.login(username='username', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['worker'], self.id_worker)
        self.assertEqual(response.json()['team'], self.id_team)
        self.assertEqual(response.json()['is_referent'], False)
        self.assertEqual(response.json()['is_representant'], False)

    def test__remove_member(self):
        self.client.login(username='username', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_member)]) #TODO: Refactor URLjoin
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

        expected = {'worker': self.id_worker,
                    'team': self.id_team,
                    'is_referent': True,
                    'is_representant': False,
                    'id': self.id_member,
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
