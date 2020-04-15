import logging
from datetime import timedelta as td, datetime as dt
from django.test import TestCase
from testfixtures import LogCapture
from .test_helper import (create_worker, create_vacationpolicy,
                          create_absencetype, create_occurrence,
                          calculate_occurrence_dates)
from gestor_absencies.models import (SomEnergiaOccurrence, Worker)
from gestor_absencies.scheduler_tasks import change_year


class SchedulerTasksTest(TestCase):

    def setUp(self):
        self.worker = create_worker(
            username='Worker', email='worker@mail.coop'
        )
        self.vacation_policy = create_vacationpolicy(
            description='normal vacation policy',
            created_by=self.worker
        )
        self.worker.vacation_policy = self.vacation_policy
        self.worker.holidays = 10
        self.worker.save()

    def tearDown(self):
        self.worker.delete()
        LogCapture.uninstall_all()

    def setup_absencetypes(self):
        self.holiday_absence_type = create_absencetype(
            name='Vacances', description='vacances',
            spend_days=-1, min_duration=0.5, max_duration=-1,
            created_by=self.worker, color='#fcba03'
        )
        self.school_absence_type = create_absencetype(
            name='Escola', description='escola',
            spend_days=1, min_duration=0.5, max_duration=-1,
            created_by=self.worker, color='#fcba03'
        )

    def test__change_year__update_worker_holidays_without_occurrences(self):
        past_holidays = self.worker.holidays

        with LogCapture(level=logging.INFO) as log_captured:
            change_year()
        log_messages = [log_record.msg for log_record in log_captured.records]
        self.worker.refresh_from_db()

        self.assertEqual(
            self.worker.holidays,
            past_holidays + self.worker.vacation_policy.holidays
        )
        self.assertListEqual(
            log_messages,
            ["Start change_year", "change_year finished"]
        )

    def test__change_year__update_worker_holidays_with_occurrences(self):
        past_holidays = self.worker.holidays
        self.setup_absencetypes()
        start_time = dt(dt.now().year + 1, 2, 5)
        create_occurrence(
            absence_type=self.holiday_absence_type, worker=self.worker,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 10, -1)
        )
        start_time = dt(dt.now().year + 1, 3, 5)
        create_occurrence(
            absence_type=self.school_absence_type, worker=self.worker,
            start_time=start_time,
            end_time=calculate_occurrence_dates(start_time, 2, 1)
        )

        change_year()
        self.worker.refresh_from_db()

        self.assertEqual(
            self.worker.holidays,
            past_holidays + self.worker.vacation_policy.holidays - 10 + 2
        )
