from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, ContentType, Permission
from django.db import models


class Base(models.Model):

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


class Worker(AbstractUser): # TODO: add BaseModel

    def save(self, *args, **kwargs):
        if not self.pk:
            pass

        super(Worker, self).save(*args, **kwargs)

        permission = Permission.objects.get(codename='view_worker')
        self.user_permissions.add(permission)
        permission = Permission.objects.get(codename='view_team')
        self.user_permissions.add(permission)# TODO: refactor


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(Employee)

    def __repr__(self):
        return self.name

    class Meta:
        ordering = ('name',)
