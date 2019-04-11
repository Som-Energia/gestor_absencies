import datetime
from decimal import Decimal

import dateutil
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from swingtime.models import Event, EventType, Occurrence


class Worker(AbstractUser):

    category = models.CharField(
        max_length=50,
        default='',
        verbose_name=_(""),
        help_text=_("")
    )

    holidays = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_(""),
        help_text=_("")
    )

    gender = models.CharField(
        max_length=50,
        default='',
        verbose_name=_(""),
        help_text=_("")
    )

    vacation_policy = models.ForeignKey(
        'gestor_absencies.VacationPolicy',
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_(""),
        help_text=_("")
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.vacation_policy:
                self.holidays = round(
                    self.vacation_policy.calculate_proportional_holidays(),
                    0
                )

        super(Worker, self).save(*args, **kwargs)

        permission = Permission.objects.get(codename='view_worker')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='change_worker')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='view_team')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='change_team')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='view_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='add_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='change_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='delete_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='view_somenergiaabsencetype')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='add_somenergiaabsencetype')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='delete_somenergiaabsencetype')
        self.user_permissions.add(permission)# TODO: refactor

        # TODO: I per cada save() es tornen a crear les relacions?
        absence_type_list = SomEnergiaAbsenceType.objects.all()
        for absence_type in absence_type_list:
            absence = SomEnergiaAbsence(
                absence_type=absence_type,
                worker=self
            )
            absence.save()


class Base(models.Model):

    created_by = models.ForeignKey(
        get_user_model(),
        related_name='+',
        verbose_name=_('Created By'),
        on_delete=models.CASCADE,
        help_text=_('User who created the object')
    )

    modified_by = models.ForeignKey(
        get_user_model(),
        related_name='+',
        on_delete=models.CASCADE,
        verbose_name=_('Modified By'),
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


class VacationPolicy(Base):

    name = models.CharField(
        max_length=50,
        verbose_name=_(""),
        help_text=_("")
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_(""),
        help_text=_("")
    )

    holidays = models.IntegerField(
        default=0,
        verbose_name=_(""),
        help_text=_("")
    )

    def calculate_proportional_holidays(self):
        now = datetime.date.today()
        end_year = datetime.date(year=now.year, month=12, day=31)
        difference = end_year - now
        year_proportion = (difference.days) / 365
        return year_proportion * self.holidays


class Team(Base):

    name = models.CharField(
        max_length=50,
        verbose_name=_("Team name"),
        help_text=_("Team name")
    )

    min_worker = models.IntegerField(
        default=0,
        verbose_name=_(""),
        help_text=_("")
    )

    members = models.ManyToManyField(Worker, through='Member')

    # def __repr__(self):
    #     return self.name

    class Meta:
        ordering = ('name',)


class Member(models.Model):

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    is_referent = models.BooleanField(
        default=False,
        verbose_name=_("Referent in Team"),
        help_text=_("")
    )

    is_representant = models.BooleanField(
        default=False,
        verbose_name=_("IT Representant in Team"),
        help_text=_("")
    )

    class Meta:
        ordering = ('is_representant', 'is_referent')


class SomEnergiaAbsenceType(EventType):

    # TEET si fos +1 el div no sumari i diss si
    spend_days = models.IntegerField(   # Possible (-1 spend / 0 not / +1 add)
        default=0,
        verbose_name=_(""),
        help_text=_("")
    )

    max_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_(""),
        help_text=_("")
    )

    min_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_(""),
        help_text=_("")
    )

    max_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_(""),
        help_text=_("")
    )

    min_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_(""),
        help_text=_("")
    )

    required_notify = models.BooleanField(
        default=True,
        verbose_name=_(""),
        help_text=_("")
    )

    def save(self, *args, **kwargs):

        super(SomEnergiaAbsenceType, self).save(*args, **kwargs)

        worker_list = Worker.objects.all()
        for worker in worker_list:
            absence = SomEnergiaAbsence(
                absence_type=self,
                worker=worker
            )
            absence.save()


class SomEnergiaAbsence(Event):

    absence_type = models.ForeignKey(
        SomEnergiaAbsenceType,
        on_delete=models.CASCADE,
        verbose_name=_(""),
        help_text=_("")
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_(""),
        help_text=_("")
    )

    def save(self, *args, **kwargs):

        self.event_type = self.absence_type
        super(SomEnergiaAbsence, self).save(*args, **kwargs)


class SomEnergiaOccurrence(Occurrence):

    absence = models.ForeignKey(
        SomEnergiaAbsence,
        editable=False,
        on_delete=models.CASCADE
    )

    def day_counter(self):

        if self.absence.absence_type.spend_days > 0:
            byweekday = [5, 6]
        else:
            byweekday = [0, 1, 2, 3, 4]

        days = len(list(dateutil.rrule.rrule(
            dtstart=self.start_time,
            until=self.end_time,
            freq=dateutil.rrule.DAILY,
            byweekday=byweekday
        )))

        if self.start_time.hour == 13:
            days -= 0.5
        if self.end_time.hour == 13:
            days -= 0.5

        if self.absence.absence_type.spend_days < 0:
            days *= -1

        return days

    def clean_fields(self, exclude=None, *args, **kwargs):
        super().clean_fields(exclude=exclude)

        duration = abs(self.day_counter())
        if ((self.absence.absence_type.max_duration != -1 and
             duration > self.absence.absence_type.max_duration) or
                duration < self.absence.absence_type.min_duration):
                    raise ValidationError(_('Incorrect duration'))
        elif self.start_time.replace(tzinfo=None) < datetime.datetime.now():
                raise ValidationError(_('Passed occurrence'))

    def save(self, *args, **kwargs):

        self.full_clean()

        duration = self.day_counter()
        if duration < 0 and self.absence.worker.holidays < abs(duration):
            raise ValidationError(_('Worker do not have enough holidays'))

        self.event = self.absence
        super(SomEnergiaOccurrence, self).save(*args, **kwargs)

        if self.absence.absence_type.spend_days != 0:
            # self.absence.worker.holidays = F('holidays') + duration # TODO: more performance
            self.absence.worker.holidays += Decimal(duration)
            self.absence.worker.save()

    def delete(self, *args, **kwargs):

        if self.start_time.replace(tzinfo=None) < datetime.datetime.now():
            raise ValidationError(_('Can not remove a started occurrence'))

        if self.absence.absence_type.spend_days != 0:
            # self.absence.worker.holidays = F('holidays') - self.day_counter() # TODO: more performance
            self.absence.worker.holidays -= Decimal(self.day_counter())
            self.absence.worker.save()

        super(SomEnergiaOccurrence, self).save(*args, **kwargs)
