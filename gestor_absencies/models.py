import datetime
from datetime import timedelta as td
from decimal import Decimal

import dateutil.rrule as rrule
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.timezone import now as django_now
from django.utils.translation import gettext as _

from gestor_absencies.common.utils import find_concurrence_dates

class GenderChoices:

    MALE = 'male'
    FEMALE = 'female'
    INTER = 'intersex'
    TRANS = 'trans'
    QUEER = 'queer'
    OTHER = 'other'

    choices = (
        (MALE, _('Home')),
        (FEMALE, _('Dona')),
        (INTER, _('Intersex')),
        (TRANS, _('Trans')),
        (QUEER, _('Queer')),
        (OTHER, _('Altre')),
    )

class CategoryChoices:

    TECHNICAL = 'technical'
    SPECIALIST = 'specialist'
    MANAGER = 'manager'

    choices = (
        (TECHNICAL, _('Tècnic')),
        (SPECIALIST, _('Especialista')),
        (MANAGER, _('Gerència'))
    )


class Worker(AbstractUser):

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name=_('email address'),
        help_text=_('Email of the worker'),
        editable=True
    )

    category = models.CharField(
        choices=CategoryChoices.choices,
        max_length=50,
        verbose_name=_("Category"),
        help_text=_("Category of the worker"),
        editable=True
    )

    holidays = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=4, # ??
        verbose_name=_("Holidays"),
        help_text=_("Holidays that still has this worker"),
        editable=True
    )

    gender = models.CharField(
        choices=GenderChoices.choices,
        max_length=50,
        verbose_name=_("Gender"),
        help_text=_("Gender of the worker"),
        editable=True
    )

    vacation_policy = models.ForeignKey(
        'gestor_absencies.VacationPolicy',
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Vacation Policy"),
        help_text=_("What kind of vacacion policy will have this worker"),
        editable=True
    )

    working_week = models.IntegerField(
        default=0,
        verbose_name=_("Workday"),
        help_text=_("Work hours per week"),
        editable=True
    )

    contract_date = models.DateTimeField(
        null=True,
        verbose_name=_("Contract date"),
        help_text=_("When this worker signed its contract"),
        editable=True
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.vacation_policy:
                self.holidays = round(
                    self.vacation_policy.calculate_proportional_holidays(),
                    0
                )
            super(Worker, self).save(*args, **kwargs)
            absence_type_list = SomEnergiaAbsenceType.objects.all()
            for absence_type in absence_type_list:
                absence = SomEnergiaAbsence(
                    absence_type=absence_type,
                    worker=self,
                    created_by=self,
                    modified_by=self
                )
                absence.save()
        else:
            super(Worker, self).save(*args, **kwargs)

        views = [
            'view_worker',
            'change_worker',
            'view_team',
            'view_member',
            'add_member',
            'change_member',
            'delete_member',
            'view_somenergiaabsencetype',
            'view_vacationpolicy',
            'view_somenergiaoccurrence',
            'add_somenergiaoccurrence',
            'delete_somenergiaoccurrence',
        ]
        for view in views:
            permission = Permission.objects.get(codename=view)
            self.user_permissions.add(permission)

    class Meta:
        ordering = ('email',)

    def __repr__(self):
        return f'<Worker({self.username})>'

    def __str__(self):
        return self.__repr__()


class Base(models.Model):

    created_by = models.ForeignKey(
        get_user_model(),
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_('Created By'),
        help_text=_('User who created the object')
    )

    modified_by = models.ForeignKey(
        get_user_model(),
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_('Modified by'),
        help_text=_('User who modified the object')
    )

    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Create date"),
        help_text=_("Date when this object was saved")
    )

    modified_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modified date"),
        help_text=_("Date when this object was modified")
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted at'),
        help_text=_('Date when object was deleted')
    )

    class Meta:
        abstract = True


class VacationPolicy(Base):

    name = models.CharField(
        max_length=50,
        verbose_name=_("Name"),
        help_text=_("Name of this vacation policy")
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_("Description"),
        help_text=_("Verbose description of this vacations policy")
    )

    holidays = models.IntegerField(
        default=0,
        verbose_name=_("Holidays days"),
        help_text=_("Number of days that will have this vacacion policy")
    )

    def calculate_proportional_holidays(self):
        now = datetime.date.today()
        end_year = datetime.date(year=now.year, month=12, day=31)
        difference = end_year - now
        year_proportion = (difference.days) / 365
        return year_proportion * self.holidays

    class Meta:
        verbose_name_plural = 'Vacation policies'

    def __repr__(self):
        return f'<VacationPolicy({self.name})>'

    def __str__(self):
        return self.__repr__()


class Team(Base):

    name = models.CharField(
        max_length=50,
        verbose_name=_("Name"),
        help_text=_("Name of the team")
    )

    min_worker = models.IntegerField(
        default=0,
        verbose_name=_("Min workers"),
        help_text=_("Number of workers of this team")
    )

    members = models.ManyToManyField(
        Worker,
        through='Member',
        through_fields=('team', 'worker'),
        related_name='teams',
        verbose_name=_("Members"),
        help_text=_("Actual Members of this team")
    )

    class Meta:
        ordering = ('name',)

    def __repr__(self):
        return f'<Team({self.name})>'

    def __str__(self):
        return self.__repr__()


class Member(Base):

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    is_referent = models.BooleanField(
        default=False,
        verbose_name=_("Referring person in the team"),
        help_text=_("Flag that indicates if this member is referring")
    )

    is_representant = models.BooleanField(
        default=False,
        verbose_name=_("IT representative person in the team"),
        help_text=_("Flag that indicates if this member is representative")
    )

    class Meta:
        ordering = ('is_representant', 'is_referent')

    def __repr__(self):
        return f'<Member({self.worker.username}, {self.team.name})>'

    def __str__(self):
        return self.__repr__()


class SomEnergiaAbsenceType(Base):

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("Absece type name")
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_("Description"),
        help_text=_("Absece type description")
    )

    spend_days = models.IntegerField(
        default=0,
        verbose_name=_("Compute days"),
        help_text=_("Indicates how many days will discount or add this absence type")
    )

    max_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=4,
        verbose_name=_("Max duration"),
        help_text=_("Total amount of days that this absence can last")
    )

    min_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=4,
        verbose_name=_("Min duration"),
        help_text=_("Minimal amount of days that this absence can last")
    )

    max_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=4, # ??
        verbose_name=_("Maximun computation"),
        help_text=_("Maximun of days that will compute this absence type")
    )

    min_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=4,
        verbose_name=_("Minimun computation"),
        help_text=_("Minimun of days that will compute this absence type")
    )

    required_notify = models.BooleanField(
        default=True,
        verbose_name=_("Notify required"),
        help_text=_("Flag to tell if this absence requiers some kind of notification")
    )

    color = models.CharField(
        max_length=7,
        verbose_name=_("Color"),
        help_text=_("Color of this type of absence")
    )

    global_date = models.BooleanField(
        default=False,
        verbose_name=_("Global date"),
        help_text=_("Check that indentify if this absence type is a global holidays")
    )

    def save(self, *args, **kwargs):

        if not self.id:
            super(SomEnergiaAbsenceType, self).save(*args, **kwargs)
            for worker in Worker.objects.all():
                absence = SomEnergiaAbsence(
                    absence_type=self,
                    worker=worker,
                    created_by=self.created_by,
                    modified_by=self.modified_by
                )
                absence.save()
        else:
            super(SomEnergiaAbsenceType, self).save(*args, **kwargs)

    def __repr__(self):
        return f"<AbsenceType({self.name})>"

    def __str__(self):
        return self.__repr__()


class SomEnergiaAbsence(Base):

    absence_type = models.ForeignKey(
        SomEnergiaAbsenceType,
        related_name='absence',
        on_delete=models.CASCADE,
        verbose_name=_("Absence type"),
        help_text=_("Type of this absence")
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        related_name='absence',
        on_delete=models.CASCADE,
        verbose_name=_("Worker"),
        help_text=_("Worker that takes this absence")
    )

    def __repr__(self):
        return f"<Absence({self.absence_type.name}, {self.worker.username})>"

    def __str__(self):
        return self.__repr__()


class SomEnergiaOccurrence(Base):

    start_time = models.DateTimeField(
        verbose_name=_("Start time"),
        help_text=_("Date when this occurrence end")
    )

    end_time = models.DateTimeField(
        verbose_name=_("End time"),
        help_text=_("Date when this occurrence end")
    )

    absence = models.ForeignKey(
        SomEnergiaAbsence,
        on_delete=models.CASCADE,
        related_name='occurrence',
        verbose_name=_("Absence"),
        help_text=_("Absence for this occurrence"),
        editable=True
    )

    def day_counter(self):
        """
        Given an occurrency tells the number of days to be
        added to the pending holidays because of it.
        """
        if self.absence.absence_type.spend_days > 0:
            byweekday = [rrule.SA, rrule.SU]
        else:
            byweekday = [
                rrule.MO,
                rrule.TU,
                rrule.WE,
                rrule.TH,
                rrule.FR
            ]

        days = len(list(rrule.rrule(
            dtstart=self.start_time,
            until=self.end_time,
            freq=rrule.DAILY,
            byweekday=byweekday
        )))

        if self.start_time.hour == 13:
            days -= 0.5
        if self.end_time.hour == 13:
            days -= 0.5

        if self.absence.absence_type.spend_days < 0:
            days *= -1

        return days

    def get_coincident_global_dates_occurrences(self, worker, start_period, end_period):
        return SomEnergiaOccurrence.objects.filter(
            absence__worker=worker,
            absence__absence_type__global_date=True,
            start_time__gte=start_period,
            end_time__lte=end_period
        )

    def create_frontier_occurrences(self, occurrence_to_override, occurrence_to_overrided):
    
        first_occurrence = None
        second_occurrence = None
        if occurrence_to_override.start_time < occurrence_to_overrided.start_time:
            if occurrence_to_overrided.start_time.hour == 13:
                first_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_override.start_time,
                    end_time=occurrence_to_overrided.start_time.replace(hour=13),
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
            else:
                first_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_override.start_time,
                    end_time=(occurrence_to_overrided.start_time - td(days=1)).replace(hour=17),
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
        if occurrence_to_override.end_time > occurrence_to_overrided.end_time:
            if occurrence_to_overrided.end_time.hour == 13:
                second_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_overrided.end_time.replace(hour=13),
                    end_time=occurrence_to_override.end_time,
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
            else:
                second_occurrence = SomEnergiaOccurrence(
                    start_time=(occurrence_to_overrided.end_time + td(days=1)).replace(hour=9),
                    end_time=occurrence_to_override.end_time,
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
        return first_occurrence, second_occurrence

    def occurrence_splitter_with_global_dates(self, occurrence):
        first_occurrence = None
        second_occurrence = None
        global_occurrences = self.get_coincident_global_dates_occurrences(
            worker=occurrence.absence.worker,
            start_period=occurrence.start_time,
            end_period=occurrence.end_time
        )
        if len(global_occurrences) > 0:
            global_occurrence = global_occurrences[0]

            first_occurrence, second_occurrence = self.create_frontier_occurrences(
                occurrence_to_override=occurrence,
                occurrence_to_overrided=global_occurrence
            )

            if first_occurrence and second_occurrence:
                first_call = self.occurrence_splitter_with_global_dates(first_occurrence)
                second_call = self.occurrence_splitter_with_global_dates(second_occurrence)
                first_call.extend(second_call)
                return first_call
            if first_occurrence:
                return self.occurrence_splitter_with_global_dates(first_occurrence)
            if second_occurrence:
                return self.occurrence_splitter_with_global_dates(second_occurrence)
        else:
            return [occurrence]

    def override_occurrence(self, worker, user, absence, occurrence):
    
        occurrences = SomEnergiaOccurrence.objects.filter(
            start_time__lte=occurrence.start_time,
            end_time__gte=occurrence.end_time,
            absence__worker__id=worker
        ).all()
        if occurrences:
            for o in occurrences:
                first_occurrence, second_occurrence = self.create_frontier_occurrences(
                    occurrence_to_override=o,
                    occurrence_to_overrided=occurrence
                )
                o.delete()
                if first_occurrence:
                    first_occurrence.save()
                if second_occurrence:
                    second_occurrence.save()

        occurrences = SomEnergiaOccurrence.objects.filter(
            (
                (
                    Q(start_time__gt=occurrence.start_time) &
                    Q(start_time__lt=occurrence.end_time)
                ) | (
                    Q(end_time__gt=occurrence.start_time) &
                    Q(end_time__lt=occurrence.end_time)
                ) | (
                    Q(start_time__gt=occurrence.start_time) &
                    Q(end_time__lt=occurrence.end_time)
                )
            ) & Q(absence__worker__id=worker)
        ).all()
        if occurrences:
            for o in occurrences:
                start_concurrence, end_concurrence = find_concurrence_dates(
                    occurrence,
                    o
                )

                first_occurrence, second_occurrence = self.create_frontier_occurrences(
                    occurrence_to_override=o,
                    occurrence_to_overrided=occurrence
                )
                o.delete()
                if first_occurrence:
                    first_occurrence.save()
                if second_occurrence:
                    second_occurrence.save()

    def save(self, *args, **kwargs):

        if not self.id:
            self.full_clean()
            super(SomEnergiaOccurrence, self).save(*args, **kwargs)
            duration = self.day_counter()
            if self.absence.absence_type.spend_days != 0:
                self.absence.worker.holidays += Decimal(duration)
                self.absence.worker.save()
        else:
            super(SomEnergiaOccurrence, self).save(*args, **kwargs)

    def __repr__(self):
        return f"<Ocurrence({self.absence.absence_type.name})>"

    def __str__(self):
        return self.__repr__()
