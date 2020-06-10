import django_rq

from django.apps import AppConfig


class GestorAbsenciesConfig(AppConfig):
    name = 'gestor_absencies'

    def ready(self):
        scheduler = django_rq.get_scheduler('default')
        for job in scheduler.get_jobs():
            scheduler.cancel(job)

        from gestor_absencies import scheduler_tasks

        scheduler.cron(
            "0 23 31 12 *",
            func=scheduler_tasks.change_year,
            repeat=1,
            queue_name='default',
        )
