from django.test import TestCase
from django.urls import reverse
from gestor_absencies.models import (
    SomEnergiaAbsence,
    SomEnergiaAbsenceType,
    Worker
)
from gestor_absencies.tests.test_helper import (
    create_absencetype,
    create_worker
)


class AdminTest(TestCase):

    def setUp(self):
        self.test_admin = create_worker(
            username='admin',
            is_admin=True
        )

        self.test_absencetype = create_absencetype(
            name='Vacances',
            description='Holiday time!',
            spend_days=1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        self.id_absencetype = self.test_absencetype.pk
        self.base_url = reverse('absencetype')

        self.test_worker = create_worker()

    def test__absencetype_list__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'Vacances',
                      'description': 'Holiday time!',
                      'spend_days': 1,
                      'min_duration': '0.5',
                      'max_duration': '-1.0',
                      'min_spend': '0.5',
                      'max_spend': '-1.0',
                      'color': '#156420',
                      'id': self.id_absencetype,
                      'global_date': False
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_get__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )

        expected = {'name': 'Vacances',
                    'description': 'Holiday time!',
                    'spend_days': 1,
                    'min_duration': '0.5',
                    'max_duration': '-1.0',
                    'min_spend': '0.5',
                    'max_spend': '-1.0',
                    'id': self.id_absencetype,
                    'color': '#156420',
                    'global_date': False
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_post__admin(self):
        body = {
            'name': 'baiA',
            'description': 'baixa A',
            'spend_days': 0,
            'min_duration': 1,
            'max_duration': 3,
            'min_spend': 2,
            'max_spend': 4,
            'color': '#000000',
            'global_date': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'baiA')
        self.assertEqual(response.json()['description'], 'baixa A')
        self.assertEqual(response.json()['spend_days'], 0)
        self.assertEqual(response.json()['min_duration'], '1.0')
        self.assertEqual(response.json()['max_duration'], '3.0')
        self.assertEqual(response.json()['min_spend'], '2.0')
        self.assertEqual(response.json()['max_spend'], '4.0')
        self.assertEqual(response.json()['color'], '#000000')
        self.assertEqual(response.json()['global_date'], True)

    def test__absencetype_put__admin(self):
        self.client.login(username='admin', password='password')
        body = {
            'name': 'Vacances',
            'spend_days': 1,
            'min_duration': 3,
            'max_duration': 10,
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_absencetype)]),
            data=body,
            content_type='application/json'
        )

        expected = {'name': 'Vacances',
                    'description': 'Holiday time!',
                    'spend_days': 1,
                    'min_duration': '3.0',
                    'max_duration': '10.0',
                    'min_spend': '0.5',
                    'max_spend': '-1.0',
                    'color': '#156420',
                    'id': self.id_absencetype,
                    'global_date': False
                    }
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_delete__admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )
        self.assertEqual(response.status_code, 204)

    def test__absencetype_list__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            self.base_url
        )

        expected = {'count': 1,
                    'next': None,
                    'previous': None,
                    'results':
                    [{'name': 'Vacances',
                      'description': 'Holiday time!',
                      'spend_days': 1,
                      'min_duration': '0.5',
                      'max_duration': '-1.0',
                      'min_spend': '0.5',
                      'max_spend': '-1.0',
                      'color': '#156420',
                      'id': self.id_absencetype,
                      'global_date': False
                      }]
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_get__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )

        expected = {'name': 'Vacances',
                    'description': 'Holiday time!',
                    'spend_days': 1,
                    'min_duration': '0.5',
                    'max_duration': '-1.0',
                    'min_spend': '0.5',
                    'max_spend': '-1.0',
                    'color': '#156420',
                    'id': self.id_absencetype,
                    'global_date': False
                    }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test__absencetype_post__worker(self):
        body = {
            'name': 'baiA',
            'description': 'baixa A',
            'spend_days': 0,
            'min_duration': 1,
            'max_duration': 3,
            'min_spend': 2,
            'max_spend': 4,
            'color': '#000000',
            'global_date': True
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

    def test__absencetype_put__worker(self):
        self.client.login(username='username', password='password')
        body = {
            'name': 'Vacances',
            'spend_days': 1,
            'min_duration': 3,
            'max_duration': 10,
        }
        response = self.client.put(
            '/'.join([self.base_url, str(self.id_absencetype)]),
            data=body,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__absencetype_delete__worker(self):
        self.client.login(username='username', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_absencetype)])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__absencetype_post_set_create_modified_params(self):
        pass

    def test__absencetype_put_set_modified_params(self):
        pass

    def test__post__create_her_somenergiaabcences(self):
        #create_worker(username='ronald')
        body = {
            'name': 'baiR',
            'description': 'baixa A',
            'spend_days': 0,
            'min_duration': 1,
            'max_duration': 3,
            'min_spend': 2,
            'max_spend': 4,
            'color': '#000000',
            'global_date': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsenceType.objects.filter(name='baiR')),
            1
        )
        self.assertEqual(
            len(SomEnergiaAbsence.objects.filter(absence_type__name='baiR')),
            2
        )
        self.assertIsNotNone(
            SomEnergiaAbsenceType.objects.filter(
                absence__worker__username='admin'
            )
        )
        self.assertIsNotNone(
            SomEnergiaAbsenceType.objects.filter(
                absence__worker__username='username'
            )
        )

    def tearDown(self):
        self.test_absencetype.delete()


# TODO: Tests

# With unexpected body params no raise error
# Can't delete a used SomEnergiaAbsenceType (Relation with Occurrences)