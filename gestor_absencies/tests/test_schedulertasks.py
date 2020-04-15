import logging
from django.test import TestCase
from testfixtures import LogCapture
from .test_helper import (create_worker, create_vacationpolicy)
from gestor_absencies.models import (SomEnergiaOccurrence, Worker)
from gestor_absencies.scheduler_tasks import change_year

class SchedulerTasksTest(TestCase):

    def setUp(self):
        self.worker = create_worker(username='Worker', email='worker@mail.coop')
        vacation_policy = create_vacationpolicy(
            description='normal vacation policy',
            created_by=self.worker
        )
        self.worker.vacation_policy = vacation_policy
        self.worker.holidays = 10
        self.worker.save()

    def tearDown(self):
        self.worker.delete()
        LogCapture.uninstall_all()

    def test__change_year__update_worker_holidays(self):
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
