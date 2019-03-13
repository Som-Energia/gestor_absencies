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
        permission = Permission.objects.get(codename='view_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='add_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='change_member')
        self.user_permissions.add(permission)# TODO: refactor
        permission = Permission.objects.get(codename='delete_member')
        self.user_permissions.add(permission)# TODO: refactor


class Team(Base):

    name = models.CharField(
        max_length=50,
        verbose_name=_("Team name"),
        help_text=_("Team name")
    )
    members = models.ManyToManyField(Worker, through='Member')

    # def __repr__(self):
    #     return self.name

    class Meta:
        ordering = ('name',)


class Member(models.Model): # TODO: BaseModel?

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