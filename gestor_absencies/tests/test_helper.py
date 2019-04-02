from gestor_absencies.models import (
    Worker,
    Team,
    Member,
    VacationPolicy,
    SomEnergiaAbsenceType,
    SomEnergiaOccurrence
)
import dateutil
from datetime import timedelta


worker_attributes = {
    'first_name': 'first_name',
    'last_name': 'last_name',
    'email': 'email@example.com',
    'password': 'password'
}


def create_worker(username='username', is_admin=False):

    worker = Worker(
        first_name=worker_attributes['first_name'],
        last_name=worker_attributes['last_name'],
        email=worker_attributes['email'],
        username=username,
        password=worker_attributes['password'],
    )
    worker.set_password(worker_attributes['password'])
    worker.is_superuser = is_admin
    worker.save()
    return worker


def create_team(name='IT'):
    team = Team(
        name=name
    )
    team.save()
    return team


def create_member(worker, team):
    member = Member(
        worker=worker,
        team=team
    )
    member.save()
    return member


def create_vacationpolicy(description, name='normal', holidays=25):
    vacationpolicy = VacationPolicy(
        name=name,
        description=description,
        holidays=holidays
    )
    vacationpolicy.save()
    return vacationpolicy


def create_absencetype(abbr, label, spend_days, min_duration, max_duration):
    absencetype = SomEnergiaAbsenceType(
        abbr=abbr,
        label=label,
        spend_days=spend_days,
        min_duration=min_duration,
        max_duration=max_duration,
    )
    absencetype.save()
    return absencetype


def create_occurrence(absence, start_time, end_time):
    occurrence = SomEnergiaOccurrence(
        absence=absence,
        start_time=start_time,
        end_time=end_time
    )
    occurrence.save()
    return occurrence


def days_between_dates(start_time, end_time, dates_types):
    return len(list(dateutil.rrule.rrule(
        dtstart=start_time,
        until=end_time,
        freq=dateutil.rrule.DAILY,
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
