import logging
from datetime import datetime as dt

from .models import SomEnergiaOccurrence, Worker
from django.db import transaction

logger = logging.getLogger('scheduler_tasks')


@transaction.atomic
def change_year():
    now = dt.now()
    logger.info("Start change_year")
    workers = Worker.objects.all()
    for worker in workers:
        logger.debug("Update {} holidays", worker.email)
        worker.holidays += worker.vacation_policy.holidays
        next_year_occurrences = SomEnergiaOccurrence.objects.filter(
            start_time__year=now.year + 1,
            end_time__year=now.year + 1,
            absence__worker=worker
        )
        for next_year_occurrence in next_year_occurrences:
            worker.holidays += next_year_occurrence.day_counter()
        worker.save()
    logger.info("change_year finished")
