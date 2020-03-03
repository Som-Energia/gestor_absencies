import datetime
from decimal import Decimal

import dateutil.rrule as rrule
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils.timezone import now as django_now


class Worker(AbstractUser):

    CATEGORY_CHOICES = (
        ('Technical', _('Tècnic')),
        ('Specialist', _('Especialista')),
        ('Manager', _('Gerència'))
    )

    GENDER_CHOICES = (
        ('Male', _('Home')),
        ('Female', _('Dona')),
        ('Intersex', _('Intersex')),
        ('Trans', _('Trans')),
        ('Queer', _('Queer')),
        ('Other', _('Altre')),
    )

    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
        editable=True,
        max_length=50,
        blank=False,
        null=False
    )

    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=50,
        verbose_name=_("Category"),
        help_text=_(""),
        editable=True
    )

    holidays = models.DecimalField(
        default=0,
        decimal_places=1,
        max_digits=10, # ??
        verbose_name=_("Holidays"),
        help_text=_(""),
        editable=True
    )

    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=50,
        verbose_name=_("Gender"),
        help_text=_(""),
        editable=True
    )

    vacation_policy = models.ForeignKey(
        'gestor_absencies.VacationPolicy',
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Vacation Policy"),
        help_text=_(""),
        editable=True
    )

    working_week = models.IntegerField(
        default=0,
        verbose_name=_("Work hours per week"),
        help_text=_(""),
        editable=True
    )

    contract_date = models.DateTimeField(
        default=django_now,
        verbose_name=_("Start contract date"),
        help_text=_(""),
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
        permission = Permission.objects.get(codename='view_somenergiaoccurrence')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='add_somenergiaoccurrence')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='delete_somenergiaoccurrence')
        self.user_permissions.add(permission)# TODO: refactor


    class Meta:
        ordering = ('email',)

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

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted At'),
        help_text=_('Date when object was deleted')
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

    color = models.CharField(
        max_length=7,
        verbose_name=_('Representation color'),
        help_text=_("")
    )

    global_date = models.BooleanField(
        default=False,
        verbose_name=_("Global holidays"),
        help_text=_("")
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

    def __str__(self):
        return self.name


class SomEnergiaAbsence(Base):

    absence_type = models.ForeignKey(
        SomEnergiaAbsenceType,
        related_name='absence',
        on_delete=models.CASCADE,
        verbose_name=_("Absence Type"),
        help_text=_("")
    )

    worker = models.ForeignKey(
        Worker,
        null=True,
        related_name='absence',
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
        related_name='occurrence',
        on_delete=models.CASCADE,
        verbose_name=_("Absence"),
        help_text=_("")
    )

    def day_counter(self):

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
