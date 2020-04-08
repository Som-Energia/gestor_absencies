from datetime import datetime, timedelta

from dateutil import rrule
from gestor_absencies.models import (Member, SomEnergiaAbsence,
                                     SomEnergiaAbsenceType,
                                     SomEnergiaOccurrence, Team,
                                     VacationPolicy, Worker)

worker_attributes = {
    'first_name': 'first_name',
    'last_name': 'last_name',
    'password': 'password',
    'contract_date': datetime(2018, 9, 1),
    'working_week': 40
}


def create_worker(
    username='username', email='email@example.com', is_admin=False
):

    worker = Worker(
        first_name=worker_attributes['first_name'],
        last_name=worker_attributes['last_name'],
        email=email,
        username=username,
        password=worker_attributes['password'],
        contract_date=worker_attributes['contract_date'],
        working_week=worker_attributes['working_week'],        
    )
    worker.set_password(worker_attributes['password'])
    worker.is_superuser = is_admin
    worker.save()
    return worker


def create_team(created_by, name='IT'):
    team = Team(
        name=name,
        created_by=created_by,
        modified_by=created_by
    )
    team.save()
    return team


def create_member(worker, team):
    member = Member(
        worker=worker,
        team=team,
        created_by=worker,
        modified_by=worker
    )
    member.save()
    return member


def create_vacationpolicy(description, created_by, name='normal', holidays=25):
    vacationpolicy = VacationPolicy(
        name=name,
        description=description,
        holidays=holidays,
        created_by=created_by,
        modified_by=created_by
    )
    vacationpolicy.save()
    return vacationpolicy


def create_absencetype(name, description, spend_days, min_duration, max_duration, created_by, color, global_date=False):
    absencetype = SomEnergiaAbsenceType(
        name=name,
        description=description,
        spend_days=spend_days,
        min_duration=min_duration,
        max_duration=max_duration,
        min_spend=min_duration,
        max_spend=max_duration,
        created_by=created_by,
        modified_by=created_by,
        color=color,
        global_date=global_date,
    )
    absencetype.save()
    return absencetype


def create_occurrence(absence_type, worker, start_time, end_time, created_by=None):
    absence = SomEnergiaAbsence.objects.all().filter(
        worker=worker,
        absence_type=absence_type
    )[0]
    if not created_by:
        created_by = worker
    occurrence = SomEnergiaOccurrence(
        absence=absence,
        start_time=start_time,
        end_time=end_time,
        created_by=created_by,
        modified_by=created_by
    )
    occurrence.save()
    return occurrence


def days_between_dates(start_time, end_time, dates_types):
    return len(list(rrule.rrule(
        dtstart=start_time,
        until=end_time,
        freq=rrule.DAILY,
        byweekday=dates_types
    )))


def calculate_occurrence_dates(start_time, duration, spend_days):
    workday = [0, 1, 2, 3, 4]
    weekend = [5, 6]
    end_time = start_time

    if spend_days < 0 or spend_days == 0:
        while days_between_dates(start_time, end_time, workday) < duration:
            end_time = end_time + timedelta(days=1)
    elif spend_days > 0:
        while days_between_dates(start_time, end_time, weekend) < duration:
            end_time = end_time + timedelta(days=1)

    return end_time


def next_monday():
    date = datetime.now()
    while date.isoweekday() != 1:
        date = date + timedelta(days=1)
    return date
