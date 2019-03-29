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
    VacationPolicySerializer
)
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

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

    # def get_object(self):
    #     obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
    #     logger.debug(self.kwargs["pk"])
    #     self.check_object_permissions(self.request, obj)
    #     logger.debug(self.check_object_permissions(self.request, obj))
    #     logger.debug(self.request.data)
    #     logger.debug(self.request.user)
    #     for p in self.get_permissions():
    #         logger.debug(p)
    #         logger.debug(p.perms_map)
    #         logger.debug(p.get_required_permissions('GET', obj))
    #     logger.debug(len(self.get_permissions()))
    #     return obj


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


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


class SomEnergiaAbsenceTypeViewSet(viewsets.ModelViewSet):
    queryset = SomEnergiaAbsenceType.objects.all()
    serializer_class = SomEnergiaAbsenceTypeSerializer


class SomEnergiaOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = SomEnergiaOccurrence.objects.all()
    serializer_class = SomEnergiaOccurrenceSerializer

