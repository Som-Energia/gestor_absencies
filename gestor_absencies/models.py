import datetime
from decimal import Decimal

import dateutil
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

class Worker(AbstractUser):

    category = models.CharField(
        max_length=50,
        default='',
        verbose_name=_("Category"),
        help_text=_("")
    )

    holidays = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Holidays"),
        help_text=_("")
    )

    gender = models.CharField(
        max_length=50,
        default='',
        verbose_name=_("Gender"),
        help_text=_("")
    )

    vacation_policy = models.ForeignKey(
        'gestor_absencies.VacationPolicy',
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Vacation Policy"),
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
        permission = Permission.objects.get(codename='view_vacationpolicy')
        self.user_permissions.add(permission)# TODO: refactor

        # TODO: I per cada save() es tornen a crear les relacions?
        absence_type_list = SomEnergiaAbsenceType.objects.all()
        for absence_type in absence_type_list:
            absence = SomEnergiaAbsence(
                absence_type=absence_type,
                worker=self,
                created_by=self,
                modified_by=self
            )
            absence.save()

    def __str__(self):
        return self.username


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
        verbose_name=_("Name"),
        help_text=_("")
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_("Description"),
        help_text=_("")
    )

    holidays = models.IntegerField(
        default=0,
        verbose_name=_("Holidays"),
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
        verbose_name=_("Minimun Workers"),
        help_text=_("")
    )

    members = models.ManyToManyField(Worker, through='Member')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


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

class SomEnergiaAbsenceType(Base):

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Absece type name"),
        help_text=_("Absece type name")
    )

    description = models.CharField(
        max_length=250,
        verbose_name=_("Absece type description"),
        help_text=_("Absece type description")
    )

    spend_days = models.IntegerField(
        default=0,
        verbose_name=_("Computation days"),
        help_text=_("")
    )

    max_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Maximun Duration"),
        help_text=_("")
    )

    min_duration = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Minimun Duration"),
        help_text=_("")
    )

    max_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Maximun Computation"),
        help_text=_("")
    )

    min_spend = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Minimun Computation"),
        help_text=_("")
    )

    required_notify = models.BooleanField(
        default=True,
        verbose_name=_("Required Notify"),
        help_text=_("")
    )

    def save(self, *args, **kwargs):

        super(SomEnergiaAbsenceType, self).save(*args, **kwargs)

        worker_list = Worker.objects.all()
        for worker in worker_list:
            absence = SomEnergiaAbsence(
                absence_type=self,
                worker=worker,
                created_by=self.created_by,
                modified_by=self.modified_by
            )
            absence.save()

    def __str__(self):
        return self.name


class SomEnergiaAbsence(Base):

    absence_type = models.ForeignKey(
        SomEnergiaAbsenceType,
        on_delete=models.CASCADE,
        verbose_name=_("Absence Type"),
        help_text=_("")
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Worker"),
        help_text=_("")
    )

    def __str__(self):
        return (str(self.worker) + ' - ' + str(self.absence_type))


class SomEnergiaOccurrence(Base):

    start_time = models.DateTimeField(
        verbose_name=_("Start time occurrence"),
        help_text=_("Date when this occurrence end")
    )

    end_time = models.DateTimeField(
        verbose_name=_("End time occurrence"),
        help_text=_("Date when this occurrence end")
    )

    absence = models.ForeignKey(
        SomEnergiaAbsence,
        # editable=False,
        on_delete=models.CASCADE,
        verbose_name=_("Absence"),
        help_text=_("")
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

    def save(self, *args, **kwargs):

        self.full_clean()
        super(SomEnergiaOccurrence, self).save(*args, **kwargs)

        duration = self.day_counter()
        if self.absence.absence_type.spend_days != 0:
            self.absence.worker.holidays += Decimal(duration)
            self.absence.worker.save()

    def delete(self, *args, **kwargs):

        if self.start_time.replace(tzinfo=None) < datetime.datetime.now():
            raise ValidationError(_('Can not remove a started occurrence'))

        if self.absence.absence_type.spend_days != 0:
            self.absence.worker.holidays -= Decimal(self.day_counter())
            self.absence.worker.save()

        super(SomEnergiaOccurrence, self).delete(*args, **kwargs)
