import logging
from decimal import Decimal

from .models import (
    Worker,
    Member,
    Team,
    SomEnergiaAbsenceType,
    SomEnergiaOccurrence,
    SomEnergiaAbsence,
    VacationPolicy
)
from rest_framework import viewsets
from .serializers import (
    WorkerSerializer,
    MemberSerializer,
    TeamSerializer,
    SomEnergiaAbsenceTypeSerializer,
    SomEnergiaOccurrenceSerializer,
    CreateSomEnergiaOccurrenceSerializer,
    VacationPolicySerializer
)
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework import serializers
import datetime
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


WORKER_PROTECTED_FIELDS = settings.WORKER_PROTECTED_FIELDS


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all().order_by('id')
    serializer_class = WorkerSerializer

    def get_serializer_context(self):
        context = super(WorkerViewSet, self).get_serializer_context()
        context.update({'is_superuser': self.request.user.is_superuser})
        return context

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            # TODO: Add create_by, modified_time...

    def user_can_update(self):
        if not self.request.user == self.get_object():
            return False
        for field in self.request._data.keys():
            if field in WORKER_PROTECTED_FIELDS:
                return False

        return True

    def perform_update(self, serializer):
        if self.request.user.is_superuser or self.user_can_update():
            serializer.save()
            # TODO: modified_time...
        else:
            raise PermissionDenied()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(WorkerViewSet, self).update(request, *args, **kwargs)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().filter(
        deleted_at__isnull=True
    ).order_by('id')
    serializer_class = TeamSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user
        )

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.datetime.now()
        instance.save()


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = Member.objects.all().order_by('id')
        team = self.request.query_params.get('team')
        worker = self.request.query_params.get('worker')

        if team:
            queryset = queryset.filter(team=team)
        elif worker:
            queryset = queryset.filter(worker=worker)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = MemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer, request):
        if (self.request.user.is_superuser or
           int(self.request.user.pk) == int(self.request.data['worker'])):
            serializer.save(
                created_by=self.request.user,
                updated_by=self.request.user
            )
        else:
            raise PermissionDenied()

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.datetime.now()
        instance.save()


class VacationPolicyViewSet(viewsets.ModelViewSet):
    queryset = VacationPolicy.objects.filter(
        deleted_at__isnull=True
    ).order_by('id')
    serializer_class = VacationPolicySerializer

    def perform_create(self, serializer):

        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user
        )

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.datetime.now()
        instance.save()


class SomEnergiaAbsenceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = SomEnergiaAbsenceTypeSerializer

    def get_queryset(self):
        queryset = SomEnergiaAbsenceType.objects.all().filter(
            deleted_at__isnull=True
        ).order_by('id')
        global_date = self.request.query_params.get('global_date')

        if global_date:
            queryset = queryset.filter(global_date=global_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user
        )

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.datetime.now()
        instance.save()


class SomEnergiaOccurrenceViewSet(viewsets.ModelViewSet):
    serializer_class = SomEnergiaOccurrenceSerializer

    def get_queryset(self):
        queryset = SomEnergiaOccurrence.objects.all().filter(
            deleted_at__isnull=True
        )
        worker = self.request.query_params.get('worker')
        team = self.request.query_params.get('team')
        start_period = self.request.query_params.get('start_period')
        end_period = self.request.query_params.get('end_period')

        if worker:
            absences = SomEnergiaAbsence.objects.all().filter(worker=worker)
            queryset = queryset.filter(absence__in=absences)
        elif team:
            members = Member.objects.all().filter(team=team)
            workers = [member.worker for member in members]
            absences = SomEnergiaAbsence.objects.all().filter(worker__in=workers)
            queryset = queryset.filter(absence__in=absences)
        if start_period:
            queryset = queryset.filter(
                end_time__gte=start_period
            )
        if end_period:
            queryset = queryset.filter(
                start_time__lte=end_period
            )

        return queryset.order_by('start_time')

    def create(self, request, *args, **kwargs):
        serializer = CreateSomEnergiaOccurrenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer, request):
        if self.request.user.is_superuser or (str(self.request.user.pk) in self.request.data['worker']):
            serializer.save(
                created_by=self.request.user,
                updated_by=self.request.user,
                request=request
            )
            # TODO: Add create_by, modified_time...
        else:
            raise PermissionDenied()

    def perform_update(self, serializer):
        if self.request.user == self.get_object().absence.worker or self.request.user.is_superuser:
            serializer.save()
            # TODO: modified_time...

    def perform_destroy(self, instance):
        if self.request.user == instance.absence.worker or self.request.user.is_superuser:
            if instance.start_time < datetime.datetime.now():
                raise serializers.ValidationError(_('Can not remove a started occurrence'))
            try:
                occurrence_compute = instance.absence.absence_type.spend_days != 0 and \
                    instance.start_time.year == instance.end_time.year == \
                    datetime.datetime.now().year
                if occurrence_compute:
                    instance.absence.worker.holidays -= Decimal(instance.day_counter())
                    instance.absence.worker.save()
                instance.deleted_at = datetime.datetime.now()
                instance.save()
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
        else:
            raise PermissionDenied()
