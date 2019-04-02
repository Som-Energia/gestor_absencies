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


class SomEnergiaOccurrenceTest(TestCase):
    def setUp(self):
        self.base_url = reverse('absences')

        self.test_vacationpolicy = create_vacationpolicy(
            description='normal vacation policy'
        )

        self.test_admin = create_worker(username='admin', is_admin=True)

        self.test_admin.vacation_policy = self.test_vacationpolicy
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
            absence=self.test_absence,
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
            response.json()['results'][0]['absence'], self.id_absence
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
            'absence': self.id_absence,
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
        self.assertEqual(response.json()['absence'], self.id_absence)
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

    def test__delete_occurrence(self):
        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.id_occurrence)])
        )
        self.assertEqual(response.status_code, 204)

    def test__cant_delete_started_occurrence(self):
        start_time = (dt.now() + td(days=-1)).replace(microsecond=0)
        self.new_occurrence = create_occurrence(
            absence=self.test_absence,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 3, 0)
        )

        self.client.login(username='admin', password='password')
        response = self.client.delete(
            '/'.join([self.base_url, str(self.new_occurrence.pk)])
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()[0], 'Can not delete')


# TODO:

# helper function to calculate correct occurrence duration
# test create a passade occurrence
# test create with spend_days +1 generate holidays
# test create with spend_days -1 substraction holidays
# test create without enough holidays
# test create with min duration 0.5
# test create with max duration -1
# test create with other occurrence at same time

# mock start_time attribute or datetime.now() in test__cant_delete_started_occurrence
# test delete own occurrence - worker
# test delete other worker occurrence's (worker)
# test delete other worker occurrence's (admin)
# test delete with spend_days +1 substraction holidays
# test delete with spend_days -1 generate holidays


# duration != compute days