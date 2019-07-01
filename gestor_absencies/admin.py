from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Worker,
    Team,
    Member,
    VacationPolicy,
    SomEnergiaAbsenceType,
    SomEnergiaAbsence,
    SomEnergiaOccurrence
)


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = ['email', 'username']
    fieldsets = ()


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['worker', 'team', 'is_referent', 'is_representant']


@admin.register(VacationPolicy)
class VacationPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'holidays']


@admin.register(SomEnergiaAbsenceType)
class SomEnergiaAbsenceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'spend_days', 'max_duration', 'min_duration']


@admin.register(SomEnergiaAbsence)
class SomEnergiaAbsence(admin.ModelAdmin):
    list_display = ['absence_type', 'worker']


@admin.register(SomEnergiaOccurrence)
class SomEnergiaOccurrenceAdmin(admin.ModelAdmin):
    list_display = ['absence', 'start_time', 'end_time']
