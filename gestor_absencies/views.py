import logging

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
    CreateWorkerSerializer,
    WorkerSerializer,
    MemberSerializer,
    TeamSerializer,
    SomEnergiaAbsenceTypeSerializer,
    SomEnergiaOccurrenceSerializer,
    CreateSomEnergiaOccurrenceSerializer,
    VacationPolicySerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework import serializers

from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateWorkerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            # TODO: Add create_by, modified_time...

    def perform_update(self, serializer):
        if self.request.user == self.get_object() or self.request.user.is_superuser:
            serializer.save()
            # TODO: modified_time...
        else:
            raise PermissionDenied()


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            modified_by=self.request.user
        )


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = Member.objects.all()
        team = self.request.query_params.get('team')
        worker = self.request.query_params.get('worker')

        if team:
            queryset = queryset.filter(team=team)
        elif worker:
            queryset = queryset.filter(worker=worker)

        return queryset


class VacationPolicyViewSet(viewsets.ModelViewSet):
    queryset = VacationPolicy.objects.all()
    serializer_class = VacationPolicySerializer

    def perform_create(self, serializer):

        serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            modified_by=self.request.user
        )


class SomEnergiaAbsenceTypeViewSet(viewsets.ModelViewSet):
    queryset = SomEnergiaAbsenceType.objects.all()
    serializer_class = SomEnergiaAbsenceTypeSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            modified_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            modified_by=self.request.user
        )


class SomEnergiaOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = SomEnergiaOccurrence.objects.all()
    serializer_class = SomEnergiaOccurrenceSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateSomEnergiaOccurrenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        if self.request.user.is_superuser or self.request.user.pk == self.request.data['worker']:
            serializer.save(
                created_by=self.request.user,
                modified_by=self.request.user
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
            try:
                instance.delete()
            except ValidationError:
                raise serializers.ValidationError('Can not delete')
        else:
            raise PermissionDenied()
