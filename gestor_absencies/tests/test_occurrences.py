import calendar
import datetime
from datetime import timedelta as td

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from gestor_absencies.models import (SomEnergiaAbsence, SomEnergiaOccurrence,
                                     Worker)
from gestor_absencies.tests.test_helper import (calculate_occurrence_dates,
                                                create_absencetype,
                                                create_member,
                                                create_occurrence, create_team,
                                                create_vacationpolicy,
                                                create_worker, next_monday,
                                                create_global_occurrence,
                                                days_between_dates)


class SomEnergiaOccurrenceSetupMixin(object):

    def make_datetime(self, year, month, day, hour):
        class MockDatetime(datetime.datetime):
            @classmethod
            def now(cls):
                return datetime.datetime(year, month, day, hour)
        return MockDatetime

    def setUp(self):

        self.base_url = reverse('absences')

        self.test_admin = create_worker(
            username='admin', email='oriol@somenergia.coop', is_admin=True
        )
        self.id_admin = self.test_admin.pk
        self.test_worker = create_worker()

        self.test_vacationpolicy = create_vacationpolicy(
            description='normal vacation policy',
            created_by=self.test_admin
        )
        self.test_admin.vacation_policy = self.test_vacationpolicy
        self.test_admin.holidays = 25
        self.test_admin.save()

        self.test_absencetype = create_absencetype(
            name='Baixa defuncio',
            description='Baixa defuncio',
            spend_days=0,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        self.id_absencetype = self.test_absencetype.pk

        self.test_absence = SomEnergiaAbsence.objects.get(
            worker=self.test_admin,
            absence_type=self.test_absencetype
        )
        self.id_absence = self.test_absence.pk

        self.testoccurrence_start_time = (next_monday() + td(days=2)).replace(hour=9, microsecond=0, minute=0, second=0)
        self.testoccurrence_end_time = calculate_occurrence_dates(
            self.testoccurrence_start_time, 3, 0
        ).replace(hour=17)

        self.test_occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_admin,
            start_time=self.testoccurrence_start_time,
            end_time=self.testoccurrence_end_time
        )
        self.id_occurrence = self.test_occurrence.pk

        self.id_global_occurrence = create_global_occurrence(
            'Global date',
            start_time=(datetime.datetime(datetime.datetime.now().year + 1, 1, 1)).replace(
                hour=9, microsecond=0, minute=0, second=0
            ),
            end_time=(datetime.datetime(datetime.datetime.now().year + 1, 1, 1)).replace(
                hour=17, microsecond=0, minute=0, second=0
            )
        )

    def tearDown(self):
        for occurrence in SomEnergiaOccurrence.objects.all():
            occurrence.delete()
        self.test_vacationpolicy.delete()
        self.test_admin.delete()
        self.test_absencetype.delete()
        self.test_worker.delete()


class SomEnergiaOccurrenceGETTest(SomEnergiaOccurrenceSetupMixin, TestCase):

    def test__list_occurrences(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
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
            '{0:%Y-%m-%dT%H:%M:%S}'.format(self.testoccurrence_start_time)
        )
        self.assertEqual(
            response.json()['results'][0]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(self.testoccurrence_start_time, 3, 0).replace(hour=17)
            )
        )

    def test__list_occurrences_with_worker_filter(self):
        create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_worker,
            start_time=self.testoccurrence_start_time,
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            )
        )

        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url, {'worker': [self.test_worker.pk]}
        )


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['next'], None)
        self.assertEqual(response.json()['previous'], None)
        self.assertEqual(
            response.json()['results'][0]['absence_type'], self.id_absencetype
        )
        self.assertEqual(
            response.json()['results'][0]['worker'], self.test_worker.pk
        )
        self.assertEqual(
            response.json()['results'][0]['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(self.testoccurrence_start_time)
        )
        self.assertEqual(
            response.json()['results'][0]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(self.testoccurrence_start_time, 3, 0)
            )
        )

    def test__list_occurrences_with_team_filter(self):
        team = create_team(created_by=self.test_admin)
        create_member(worker=self.test_worker, team=team)
        self.test_occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_worker,
            start_time=self.testoccurrence_start_time,
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            )
        )

        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url, {'team': [team.pk]}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['next'], None)
        self.assertEqual(response.json()['previous'], None)
        self.assertEqual(
            response.json()['results'][0]['absence_type'], self.id_absencetype
        )
        self.assertEqual(
            response.json()['results'][0]['worker'], self.test_worker.pk
        )
        self.assertEqual(
            response.json()['results'][0]['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(self.testoccurrence_start_time)
        )
        self.assertEqual(
            response.json()['results'][0]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(self.testoccurrence_start_time, 3, 0)
            )
        )

    def test__list_occurrences_with_interval_dates_filter(self):
        start_time = (datetime.datetime.now() + td(days=10)).replace(microsecond=0)
        team = create_team(created_by=self.test_admin)
        create_member(worker=self.test_worker, team=team)
        self.test_occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_worker,
            start_time=start_time,
            end_time=calculate_occurrence_dates(
                start_time, 3, 0
            )
        )
        second_start_time = calculate_occurrence_dates(start_time, 5, 0)
        self.second_test_occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_worker,
            start_time=second_start_time,
            end_time=calculate_occurrence_dates(
                second_start_time, 3, 0
            )
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(
            self.base_url,
                {
                    'start_period': calculate_occurrence_dates(
                        start_time, 3, 0
                    ),
                    'end_period': calculate_occurrence_dates(
                        second_start_time, 1, 0
                    )
                }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['next'], None)
        self.assertEqual(response.json()['previous'], None)
        self.assertEqual(
            response.json()['results'][0]['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(start_time)
        )
        self.assertEqual(
            response.json()['results'][0]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(start_time, 3, 0)
            )
        )
        self.assertEqual(
            response.json()['results'][1]['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(second_start_time)
        )
        self.assertEqual(
            response.json()['results'][1]['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(second_start_time, 3, 0)
            )
        )


class SomEnergiaOccurrencePOSTTest(SomEnergiaOccurrenceSetupMixin, TestCase):

    def test__simple_post_occurrence(self):
        start_time = (datetime.datetime.now() + td(days=6)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], self.id_absencetype)
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (calculate_occurrence_dates(start_time, 3, 0)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )

    def test__post_multiple_occurrence(self):
        start_time = (self.testoccurrence_start_time + td(weeks=1)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin, self.test_worker.pk],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], self.id_absencetype)
        self.assertEqual(
            response.json()['worker'], [self.id_admin, self.test_worker.pk]
        )
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (calculate_occurrence_dates(start_time, 3, 0)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__absence_type=self.id_absencetype,
                absence__worker=self.id_admin
            ).count(),
            2
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__absence_type=self.id_absencetype,
                absence__worker=self.test_worker.pk
            ).count(),
            1
        )

    def test__transaction_multiple_occurrence(self):
        self.test_worker.holidays = 0
        self.test_worker.save()
        absence_type = create_absencetype(
            name='Vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin, self.test_worker.pk],
            'start_time': self.testoccurrence_start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            ),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__absence_type=absence_type.pk
            ).count(),
            0
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__absence_type=self.id_absencetype
            ).count(),
            1
        )
        self.assertEqual(response.json(), ['Not enough holidays'])

    def test__post_occurrence_with_global_dates_count_global_dates(self):
        global_date = create_absencetype(
            name='Festa nacional',
            description='Festa nacional',
            spend_days=0,
            min_duration=1,
            max_duration=1,
            created_by=self.test_admin,
            color='#000000',
            global_date=True
        )
        occurrence = create_occurrence(
            absence_type=global_date.pk,
            worker=self.test_admin,
            start_time=self.testoccurrence_start_time,
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time,
                1,
                0
            ),
        )
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin],
            'start_time': self.testoccurrence_start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(
                self.testoccurrence_start_time,
                4,
                0
            ),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)

    def test__post_occurrence_with_global_dates_not_override_global_dates(self):
        global_date = create_absencetype(
            name='Festa nacional',
            description='Festa nacional',
            spend_days=0,
            min_duration=1,
            max_duration=1,
            created_by=self.test_admin,
            color='#000000',
            global_date=True
        )
        global_occurrence = create_occurrence(
            absence_type=global_date.pk,
            worker=self.test_admin,
            start_time=self.testoccurrence_start_time - td(days=1),
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time - td(days=1),
                1,
                0
            ).replace(hour=17),
        )
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin],
            'start_time': self.testoccurrence_start_time - td(days=1),
            'start_morning': True,
            'end_time': calculate_occurrence_dates(
                self.testoccurrence_start_time - td(days=1),
                4,
                0
            ),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SomEnergiaOccurrence.objects.filter(
            absence__absence_type=global_date
            ).count(),
            1
        )
        self.assertEqual(SomEnergiaOccurrence.objects.filter(
            absence__absence_type=self.id_absencetype
            ).count(),
            1
        )

    def test__post_global_date_generate_occurrences(self):

        global_date = create_absencetype(
            name='Festa nacional',
            description='Festa nacional',
            spend_days=0,
            min_duration=1,
            max_duration=1,
            created_by=self.test_admin,
            color='#000000',
            global_date=True
        )

        all_workers = Worker.objects.all()
        all_workers_ids = [worker.pk for worker in all_workers]
        body = {
            'absence_type': global_date.pk,
            'worker': all_workers_ids,
            'start_time': self.testoccurrence_start_time - td(days=1),
            'start_morning': True,
            'end_time': calculate_occurrence_dates(
                self.testoccurrence_start_time - td(days=1),
                1,
                0
            ).replace(hour=17),
            'end_afternoon': True
        }

        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.assertEqual(response.status_code, 201)

        global_occurrence_list = SomEnergiaOccurrence.objects.filter(
            absence__absence_type__global_date=True
        ).distinct('start_time', 'end_time')

        self.assertEqual(
            len(global_occurrence_list), 2
        )

    def test__post_passade_occurrence(self):
        start_time = (datetime.datetime.now() - td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ['Can\'t create a passade occurrence'])

    def test__post_occurrence_today(self):
        old_datetime = datetime.datetime
        datetime.datetime = self.make_datetime(
            self.testoccurrence_start_time.year,
            self.testoccurrence_start_time.month,
            self.testoccurrence_start_time.day,
            11
        )
        start_time = (datetime.datetime.now() - td(hours=2)).replace(microsecond=0)
        body = {
            'absence_type': self.id_absencetype,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_afternoon': True
        }
        self.test_occurrence.delete()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        datetime.datetime = old_datetime
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], self.id_absencetype)
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (calculate_occurrence_dates(start_time, 3, 0)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )

    def test__post_occurrence__next_year(self):
        absence_type = create_absencetype(
            name='vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime(
            datetime.datetime.now().year + 1, 1, datetime.datetime.now().day
        )).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 10, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        del(response.json()['id'])
        expected = {
            'absence_type': absence_type.pk,
            'start_time': '{0:%Y-%m-%dT%H:%M:%S}'.format(start_time.replace(hour=9)),
            'end_time': '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(start_time, 10, 0).replace(hour=17)),
            'worker': [self.id_admin]
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected, response.json())

        self.test_admin.refresh_from_db()
        self.assertEqual(
            self.test_admin.holidays, self.test_admin.vacation_policy.holidays
        )

    def test__post_occurrence__year_transition(self):
        absence_type = create_absencetype(
            name='vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime(
            datetime.datetime.now().year, 12, 30
        )).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 10, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        del(response.json()['id'])
        occurrence_current_year = SomEnergiaOccurrence.objects.filter(
            absence__worker=self.test_admin,
            absence__absence_type=absence_type,
            start_time__year=datetime.datetime.now().year
        ).first()
        occurrence_next_year = SomEnergiaOccurrence.objects.filter(
            absence__worker=self.test_admin,
            absence__absence_type=absence_type,
            start_time__year=datetime.datetime.now().year + 1
        ).first()
        expected = {
            'absence_type': absence_type.pk,
            'start_time': '{0:%Y-%m-%dT%H:%M:%S}'.format(start_time.replace(hour=9)),
            'end_time': '{0:%Y-%m-%dT%H:%M:%S}'.format(
                calculate_occurrence_dates(start_time, 10, 0).replace(hour=17)),
            'worker': [self.id_admin]
        }

        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected, response.json())
        self.test_admin.refresh_from_db()
        self.assertEqual(
            self.test_admin.holidays,
            self.test_admin.vacation_policy.holidays - abs(occurrence_current_year.day_counter())
        )
        self.assertEqual(
            self.test_admin.next_year_holidays(),
            self.test_admin.vacation_policy.holidays - abs(occurrence_next_year.day_counter())
        )

    def test__post_occurrence__generate_holidays(self):
        absence_type = create_absencetype(
            name='Escola',
            description='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 1),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
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
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=6)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, -1),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (calculate_occurrence_dates(start_time, 3, -1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(self.test_admin.holidays, 22)

    def test__post_occurrence__not_enough_holidays_current_year(self):
        old_datetime = datetime.datetime
        datetime.datetime = self.make_datetime(
            year=old_datetime.now().year,
            month=1,
            day=1,
            hour=11
        )
        absence_type = create_absencetype(
            name='Vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=30)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 30, -1),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        datetime.datetime = old_datetime
        self.test_admin.refresh_from_db()
        expected = ['Not enough holidays']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
        self.assertEqual(self.test_admin.holidays, 25)

    def test__post_occurrence__not_enough_holidays_next_year(self):
        absence_type = create_absencetype(
            name='vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=20,
            max_duration=20,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime(
            datetime.datetime.now().year + 1, 1, datetime.datetime.now().day
        )).replace(microsecond=0)
        create_occurrence(
            absence_type=absence_type,
            worker=self.test_admin,
            start_time=start_time + td(days=30),
            end_time=calculate_occurrence_dates(start_time + td(days=30), 20, -1)
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 20, -1),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        expected = ['Not enough holidays']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                start_time__year=datetime.datetime.now().year + 1,
                end_time__year=datetime.datetime.now().year + 1,
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            ).count(),
            1
        )

    def test__post_occurrence__generate_holidays_without_worker_holidays(self):
        absence_type = create_absencetype(
            name='esco',
            description='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 1),
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
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
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
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=3)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, -1),
            'end_afternoon': True
        }
        self.test_admin.holidays = 0
        self.test_admin.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        expected = ['Not enough holidays']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)
        self.assertEqual(self.test_admin.holidays, 0)

    def test__post_ilimitate_days(self):
        absence_type = create_absencetype(
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=6)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 20, -1),
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
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
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
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = self.testoccurrence_start_time
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
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
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
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
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=6)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': False,
            'end_time': calculate_occurrence_dates(start_time, 2, 0),
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
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=13, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
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
            name='esce',
            description='Escola',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
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

        expected = {'non_field_errors': ['Incorrect format occurrence']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)

    def test__post_cant_empty_day(self):
        absence_type = create_absencetype(
            name='esce',
            description='Escola',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=1)).replace(microsecond=0)
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
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

        expected = {'non_field_errors': ['Incorrect format occurrence']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)

    def test__post__occurrence_between_other_occurrences_split(self):
        
        #   |----|
        #   ||||||
        start_time = (self.testoccurrence_start_time + td(days=1)).replace(hour=10, microsecond=0)
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 1, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            2
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            (self.testoccurrence_start_time).replace(hour=17, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[1].start_time,
            (calculate_occurrence_dates(start_time, 1, 0) + td(days=1)).replace(hour=9, minute=0, second=0)
        )

    def test__post__occurrence_beginning_coincide_with_other_occurrences_override_other_occurrence(self):
        
        #   |----|
        #   |||--|
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': self.testoccurrence_start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(self.testoccurrence_start_time, 1, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            1
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            self.testoccurrence_start_time.replace(hour=9, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].start_time,
            (calculate_occurrence_dates(self.testoccurrence_start_time, 1, 0) + td(days=1))
        )

    def test__post__occurrence_end_coincide_with_other_occurrences_override_other_occurrence(self):
        
        #   |----|
        #   |--|||
        start_time = (self.testoccurrence_start_time + td(days=2))
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 1, 0),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            1
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            start_time
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            (start_time - td(days=1)).replace(hour=17, minute=0, second=0)
        )

    def test__post__occurrence_first_half_day_beginning_coincide_with_other_occurrences_override_other_occurrence(self):
        
        #   |----|
        #   ||---|
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': self.testoccurrence_start_time,
            'start_morning': True,
            'start_afternoon': False,
            'end_time': calculate_occurrence_dates(self.testoccurrence_start_time, 1, 0),
            'end_morning': True,
            'end_afternoon': False
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            1
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].end_time,
            self.testoccurrence_start_time.replace(hour=13, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].start_time,
            self.testoccurrence_start_time.replace(hour=13)
        )

    def test__post__occurrence_second_half_day_beginning_coincide_with_other_occurrences_override_other_occurrence(self):
        
        #   |----|
        #   |||--|
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': self.testoccurrence_start_time,
            'start_morning': False,
            'end_time': calculate_occurrence_dates(self.testoccurrence_start_time, 1, 0),
            'end_morning': False,
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            2
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            self.testoccurrence_start_time.replace(hour=13, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            self.testoccurrence_start_time.replace(hour=13)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[1].start_time,
            (self.testoccurrence_start_time + td(days=1)).replace(hour=9)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            (self.testoccurrence_start_time).replace(hour=13)
        )

    def test__post__occurrence_first_half_day_end_coincide_with_other_occurrences_override_other_occurrence(self):
        
        #   |----|   
        #   |--|||
        start_time = (self.testoccurrence_start_time + td(days=2)).replace(hour=9, microsecond=0, second=0)
        absence_type = create_absencetype(
            name='Baixa M',
            description='Baixa',
            spend_days=0,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'start_afternoon': False,
            'end_time': calculate_occurrence_dates(start_time, 1, 0),
            'end_morning': True,
            'end_afternoon': False
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaAbsence.objects.all().filter(
                worker=self.test_admin,
                absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            2
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            start_time
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[1].start_time,
            start_time.replace(hour=13, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[1].end_time,
            start_time.replace(hour=17, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            (start_time - td(days=1)).replace(hour=17, minute=0, second=0)
        )

    def test__worker_can_create_your_occurrence(self):
        start_time = (datetime.datetime.now() + td(days=2)).replace(hour=10, microsecond=0)
        body = {
            'absence_type': self.test_absencetype.pk,
            'worker': [self.test_worker.pk],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, 0),
            'end_afternoon': True
        }
        self.client.login(username='username', password='password')
        response = self.client.post(
            self.base_url, data=body
        )

        self.assertEqual(response.status_code, 201)

    def test__worker_cant_create_another_occurrence_worker(self):
        start_time = (datetime.datetime.now() + td(days=2)).replace(hour=10, microsecond=0)
        body = {
            'absence_type': self.test_absencetype.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 1, 0),
            'end_afternoon': True
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

    def test__greater_coincidence_occurrence(self):

        #   |----|
        # |--------|
        start_time = (self.testoccurrence_start_time - td(days=1)).replace(hour=9, microsecond=0, second=0)
        absence_type = create_absencetype(
            name='Vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 5, -1),
            'end_afternoon': True
        }

        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['absence_type'], absence_type.pk)
        self.assertEqual(response.json()['worker'], [self.id_admin])
        self.assertEqual(
            response.json()['start_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (start_time).replace(hour=9, minute=0, second=0))
        )
        self.assertEqual(
            response.json()['end_time'],
            '{0:%Y-%m-%dT%H:%M:%S}'.format(
                (calculate_occurrence_dates(start_time, 5, -1)).replace(
                    hour=17,
                    minute=0,
                    second=0
                )
            )
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            0
        )
        self.assertEqual(self.test_admin.holidays, 20)

    def test__end_coincidence_occurrence(self):

        #   |----|
        #   |---|----|
        start_time = (self.testoccurrence_start_time + td(days=2)).replace(hour=9, microsecond=0, second=0)
        absence_type = create_absencetype(
            name='Vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 3, -1),
            'end_afternoon': True
        }

        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            1
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            (start_time - td(days=1)).replace(hour=17, minute=0, second=0)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].start_time,
            self.testoccurrence_start_time
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            start_time
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].end_time,
            calculate_occurrence_dates(start_time, 3, -1).replace(hour=17)
        )
        self.assertEqual(self.test_admin.holidays, 22)

    def test__start_coincidence_occurrence(self):

        #   |----|
        # |--||--|
        start_time = (self.testoccurrence_start_time - td(days=1)).replace(hour=9, microsecond=0, second=0)
        absence_type = create_absencetype(
            name='Vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        body = {
            'absence_type': absence_type.pk,
            'worker': [self.id_admin],
            'start_time': start_time,
            'start_morning': True,
            'end_time': calculate_occurrence_dates(start_time, 2, -1),
            'end_afternoon': True
        }
        self.client.login(username='admin', password='password')
        response = self.client.post(
            self.base_url, data=body
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )),
            1
        )
        self.assertEqual(
            len(SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )),
            1
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].end_time,
            calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            ).replace(hour=17)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=self.test_absencetype
            )[0].start_time,
            (self.testoccurrence_start_time + td(days=1)).replace(hour=9)
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].start_time,
            start_time
        )
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                absence__worker=self.test_admin,
                absence__absence_type=absence_type
            )[0].end_time,
            calculate_occurrence_dates(start_time, 2, -1).replace(hour=17)
        )
        self.assertEqual(self.test_admin.holidays, 23)


class SomEnergiaOccurrenceDELETETest(SomEnergiaOccurrenceSetupMixin, TestCase):

    def test__delete_occurrence(self):
        self.client.login(username='admin', password='password')
        delete_response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )

        get_response = self.client.get(
            self.base_url, {'worker': [self.test_worker.pk]}
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                pk=self.test_occurrence.pk,
                deleted_at=None
            ).count(),
            0
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json().get('count'), 1) # Global date

    def test__delete_occurrence__generate_holidays(self):
        absence_type = create_absencetype(
            name='esce',
            description='Escola',
            spend_days=-1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=3)).replace(hour=10, microsecond=0)
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
            name='esce',
            description='Escola',
            spend_days=1,
            min_duration=3,
            max_duration=3,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime.now() + td(days=3)).replace(hour=10, microsecond=0)
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

    def test__worker_can_delete_her_occurrences(self):
        start_time = (datetime.datetime.now() + td(days=1)).replace(hour=10, microsecond=0, minute=0)
        occurrence = create_occurrence(
            absence_type=self.test_absencetype,
            worker=self.test_worker,
            start_time=start_time,
            end_time=calculate_occurrence_dates(
                self.testoccurrence_start_time, 3, 0
            )
        )
        self.client.login(username='username', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(occurrence.pk)])
        )

        self.assertEqual(response.status_code, 204)

    def test__worker_cant_delete_another_worker_occurrences(self):
        self.client.login(username='username', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {'detail': 'You do not have permission to perform this action.'}
        )

    def test__cant_delete_passade_occurrence(self):
        old_datetime = datetime.datetime
        datetime.datetime = self.make_datetime(
            (self.testoccurrence_start_time + td(weeks=8)).year,
            (self.testoccurrence_start_time + td(weeks=8)).month,
            (self.testoccurrence_start_time - td(days=1)).day,
            11
        )
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )

        datetime.datetime = old_datetime
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ['Can not remove a started occurrence'])

    def test__can_delete_next_month_occurrence(self):
        old_datetime = datetime.datetime
        datetime.datetime = self.make_datetime(
            (self.testoccurrence_start_time + td(days=1)).year,
            (self.testoccurrence_start_time - td(weeks=4)).month,
            calendar.monthrange(
                (self.testoccurrence_start_time + td(days=1)).year,
                (self.testoccurrence_start_time - td(weeks=4)).month
            )[1],
            11
        )
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )

        datetime.datetime = old_datetime
        self.assertEqual(response.status_code, 204)

    def test__can_delete_next_year_occurrence(self):
        absence_type = create_absencetype(
            name='vacances',
            description='Vacances',
            spend_days=-1,
            min_duration=0.5,
            max_duration=-1,
            created_by=self.test_admin,
            color='#156420',
        )
        start_time = (datetime.datetime(
            datetime.datetime.now().year + 1, 1, datetime.datetime.now().day
        )).replace(microsecond=0)
        occurrence_to_remove = create_occurrence(
            absence_type=absence_type, worker=self.test_admin,
            start_time=start_time, end_time=calculate_occurrence_dates(start_time, 10, 0)
        )

        self.client.login(username='admin', password='password')
        delete_response = self.client.delete(
            '/'.join([self.base_url, str(occurrence_to_remove.pk)])
        )
        get_response = self.client.get(
            self.base_url, {'worker': [self.test_worker.pk]}
        )
        self.test_admin.refresh_from_db()

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(
            SomEnergiaOccurrence.objects.filter(
                pk=occurrence_to_remove.pk,
                deleted_at=None
            ).count(),
            0
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json().get('count'), 1) # Global date
        self.assertEqual(
            self.test_admin.holidays, self.test_admin.vacation_policy.holidays
        )



# TODO:

# test create with other occurrence at same time

# test delete generate (spend_days=1) without enough holidays


# duration != compute days
