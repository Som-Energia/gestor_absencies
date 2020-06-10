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


class MemberInline(admin.TabularInline):
    model = Team.members.through
    extra = 0


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = [
        '__str__', 'username', 'holidays', 'vacation_policy'
    ]

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ("Personal info", {
            'fields': ('first_name', 'last_name', 'gender')
        }),
        ("Worker info", {
            'fields': ('category', 'holidays', 'vacation_policy')
        }),
        ("Permissions", {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Important dates", {
            'fields': ('last_login', 'date_joined')
        })
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'name'
    ]

    inlines = (MemberInline, )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'worker', 'team', 'is_referent', 'is_representant'
    ]


@admin.register(VacationPolicy)
class VacationPolicyAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'name', 'description', 'holidays'
    ]


@admin.register(SomEnergiaAbsenceType)
class SomEnergiaAbseneTypeAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'spend_days', 'max_duration', 'min_duration', 'required_notify'
    ]


@admin.register(SomEnergiaAbsence)
class SomEnergiaAbsenceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'absence_type', 'worker'
    ]


@admin.register(SomEnergiaOccurrence)
class SomEnergiaOccurrenceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'start_time', 'end_time', 'absence'
    ]
