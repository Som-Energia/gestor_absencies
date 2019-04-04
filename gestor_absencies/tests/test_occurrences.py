from django.test import TestCase
from gestor_absencies.models import (
    Worker,
    SomEnergiaAbsenceType,
    SomEnergiaAbsence,
    SomEnergiaOccurrence,
    VacationPolicy
)
from django.urls import reverse
from datetime import (
    datetime as dt,
    timedelta as td
)
from gestor_absencies.tests.test_helper import (
    calculate_occurrence_dates,
    create_worker,
    create_vacationpolicy,
    create_absencetype,
    create_occurrence
)
# from unittest.mock import MagicMock, PropertyMock, patch
import mock
from django.core.exceptions import ValidationError


class SomEnergiaOccurrenceTest(TestCase):
    def setUp(self):
        self.base_url = reverse('absences')

        self.test_vacationpolicy = create_vacationpolicy(
            description='normal vacation policy'
        )

        self.test_admin = create_worker(username='admin', is_admin=True)
        self.id_admin = self.test_admin.pk
        self.test_admin.vacation_policy = self.test_vacationpolicy
        self.test_admin.holidays = 25 #Todo: mock dt.now()
        self.test_admin.save()

        self.test_absencetype = create_absencetype(
            abbr='bdef',
            label='Baixa defuncio',
            spend_days=0,
            min_duration=3,
            max_duration=3,
        )
        self.id_absencetype = self.test_absencetype.pk

        self.test_absence = self.test_admin.somenergiaabsence_set.all()[0]
        self.id_absence = self.test_absence.pk

        self.testoccurrence_start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        self.test_occurrence = create_occurrence(
            #absence=self.test_absence,
            absence_type=self.test_absencetype,
            worker=self.test_admin,
            start_time=self.testoccurrence_start_time,
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            ),
        )
        self.id_occurrence = self.test_occurrence.pk

    def test__list_occurrences(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['next'], None)
        self.assertEqual(response.json()['previous'], None)
        self.assertEqual(
            response.json()['results'][0]['absence_type'], self.id_absencetype
        )
        self.assertEqual(
            response.json()['results'][0]['worker'], self.id_admin
        )
        self.assertEqual(
            response.json()['results'][0]['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(self.testoccurrence_start_time)
        )
        self.assertEqual(
            response.json()['results'][0]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                calculate_occurrence_dates(self.testoccurrence_start_time, 3, 0)
            )
        )

    def test__simple_post_occurrence(self): # Todo: more cases
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_morning': True,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], self.id_absencetype)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 3, 0)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )

    def test__post_passade_occurrence(self):
        start_time = (dt.now() - td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_morning': True,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ['Incorrect occurrence'])

    def test__post_occurrence__generate_holidays(self):
        absence_type = create_absencetype(
            abbr='esco',
            label='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 3, 1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 28)

    def test__post_occurrence__substraction_holidays(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, -1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 3, -1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 22)

    def test__post_occurrence__not_enough_holidays(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=30,
            max_duration=30
        )
        start_time = (dt.now() + td(days=30)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 30, -1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        expected = ['Incorrect occurrence']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
        self.assertEqual(self.test_admin.holidays, 25)

    def test__post_occurrence__generate_holidays_without_worker_holidays(self):
        absence_type = create_absencetype(
            abbr='esco',
            label='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.test_admin.holidays = 0
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 3, 1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 3)

    def test__post_occurrence__substraction_holidays_without_worker_holidays(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 3, -1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.test_admin.holidays = 0
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        expected = ['Incorrect occurrence']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
        self.assertEqual(self.test_admin.holidays, 0)

    def test__post_ilimitate_days(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1
        )
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 20, -1),
            'end_morning': True,
            'end_afternoon': True
        }
        self.test_admin.holidays = 25
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 20, -1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 5)

    def test__post_half_day(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1
        )
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': False,
            'end_time': calculate_occurrence_dates(start_time, 1, -1),
            'end_morning': True,
            'end_afternoon': False
        }
        self.test_admin.holidays = 25
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 1, -1)).replace(
                    hour=13,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 24.5)

    def test__post_split_day(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1
        )
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': False,
            'start_afternoon': True,
            'end_time': calculate_occurrence_dates(start_time, 2, 0),
            'end_morning': True,
            'end_afternoon': False
        }
        self.test_admin.holidays = 25
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], self.id_admin)
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (start_time).replace(hour=13, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%SZ}'.format(
                (calculate_occurrence_dates(start_time, 2, -1)).replace(
                    hour=13,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 24)

    def test__post_cant_fractionate_occurrence(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1
        )
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': False,
            'end_time': calculate_occurrence_dates(start_time, 2, 0),
            'end_morning': True,
            'end_afternoon': False
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        expected = {'non_field_errors': ['Incorrect occurrence']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)


    def test__post_cant_empty_day(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1
        )
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': self.id_admin,
            'start_time': start_time,
            'start_morning': False,
            'start_afternoon': False,
            'end_time': calculate_occurrence_dates(start_time, 2, 0),
            'end_morning': True,
            'end_afternoon': False
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        expected = {'non_field_errors': ['Incorrect occurrence']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)

    def test__delete_occurrence(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )
        self.assertEqual(response.status_code, 204)

    def test__delete_occurrence__generate_holidays(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        self.new_occurrence = create_occurrence(
            absence_type=absence_type,
            worker=self.test_admin,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 3, -1)
        )
        self.test_admin.holidays = 25
        self.test_admin.save()

        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.new_occurrence.pk)])
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.test_admin.holidays, 28)

    def test__delete_occurrence__substraction_holidays(self):
        absence_type = create_absencetype(
            abbr='esce',
            label='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3
        )
        start_time = (dt.now() + td(days=3)).replace(microsecond=0)
        self.new_occurrence = create_occurrence(
            absence_type=absence_type,
            worker=self.test_admin,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 3, 1)
        )
        self.test_admin.holidays = 25
        self.test_admin.save()

        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.new_occurrence.pk)])
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.test_admin.holidays, 22)

    def test__cant_delete_started_occurrence(self):
        start_time = (dt.now() + td(days=1)).replace(microsecond=0)
        self.new_occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_admin,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 3, 0)
        )
        self.new_occurrence.save()
        self.new_occurrence.start_time = (dt.now() + td(days=-1)).replace(microsecond=0)

        with self.assertRaises(ValidationError) as ctx:
            self.new_occurrence.delete()
        self.assertEqual(ctx.exception.message, 'Can not remove a started occurrence')


# TODO:

# test create other worker occurrence
# test create with other occurrence at same time

# test delete generate (spend_days=1) without enough holidays
# test delete own occurrence - worker
# test delete other worker occurrence's (worker)
# test delete other worker occurrence's (admin)


# duration != compute days