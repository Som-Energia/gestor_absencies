from django.test import TestCase
from gestor_absencies.models import (
	Worker,
	SomEnergiaAbsenceType,
	SomEnergiaAbsence,
	SomEnergiaOccurrence,
	VacationPolicy
)
from django.urls import reverse


class SomEnergiaOccurrenceTest(TestCase):
	def setUp(self):
		self.base_url = reverse('absences')

		self.test_vacationpolicy = VacationPolicy(
            name='normal',
            description='normal vacation policy',
            holidays=25
        )
		self.test_vacationpolicy.save()

		self.test_admin = Worker(
			first_name='admin',
            last_name='admin',
            email='admin@admin.com',
            username='admin',
            password='admin'
        )
		self.test_admin.set_password('admin')
		self.test_admin.is_superuser = True
		self.test_admin.vacation_policy = self.test_vacationpolicy
		self.test_admin.save()

		self.test_absencetype = SomEnergiaAbsenceType(
		    abbr='bdef',
		    label='Baixa defuncio',
		    spend_days=0,
		    min_duration=3,
		    max_duration=3,
		)
		self.test_absencetype.save()
		self.id_absencetype = self.test_absencetype.pk

		self.test_absence = self.test_admin.somenergiaabsence_set.all()[0]
		self.id_absence = self.test_absence.pk

		self.test_occurrence = SomEnergiaOccurrence(
			absence=self.test_absence,
			start_time='2019-03-18T09:00:00Z',
			end_time='2019-03-20T17:00:00Z'
		)
		self.test_occurrence.save()

	def test__list(self):
		self.client.login(username='admin', password='admin')
		response = self.client.get(
			self.base_url
		)
		expected = {
			'count': 1,
			'next': None,
			'previous': None,
			'results':
			[{
				'id': 1,
				'absence': self.id_absence,
				'start_time': '2019-03-18T09:00:00Z',
				'end_time': '2019-03-20T17:00:00Z'
			}]
		}
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), expected)

	def test__simple_post_occurrence(self): # Todo: more cases
		body = {
			'absence': self.id_absence,
			'start_time': '2019-03-18 12:34:56+00:00',
			'start_morning': True,
			'start_afternoon': True,
			'end_time': '2019-03-20 12:34:56+00:00',
			'end_morning': True,
			'end_afternoon': True
		}
		self.client.login(username='admin', password='admin')
		response = self.client.post(
			self.base_url, data=body
		)

		expected = {
			'id': 2,
			'absence': self.id_absence,
			'start_time': '2019-03-18T09:00:00Z',
			'end_time': '2019-03-20T17:00:00Z'
		}
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.json()['absence'], self.id_absence)
		self.assertEqual(response.json()['start_time'], '2019-03-18T09:00:00Z')
		self.assertEqual(response.json()['end_time'], '2019-03-20T17:00:00Z')
