import logging

from .models import SomEnergiaOccurrence, Worker
from django.db import transaction

logger = logging.getLogger('scheduler_tasks')


@transaction.atomic
def change_year():
    logger.info("Start change_year")
    workers = Worker.objects.all()
    for worker in workers:
        logger.debug("Update {} holidays", worker.email)
        worker.holidays += worker.vacation_policy.holidays
        worker.save()
    logger.info("change_year finished")
