import datetime
from datetime import timedelta as td

import dateutil.rrule as rrule
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from gestor_absencies.common.datetime_calculator import calculate_datetime
from gestor_absencies.common.utils import (computable_days_between_dates,
                                           find_concurrence_dates)

from .models import (CategoryChoices, GenderChoices, Member, SomEnergiaAbsence,
                     SomEnergiaAbsenceType, SomEnergiaOccurrence, Team,
                     VacationPolicy, Worker)


class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    vacation_policy = serializers.PrimaryKeyRelatedField(
        queryset=VacationPolicy.objects,
        required=False,
    )
    category = serializers.ChoiceField(
        choices=CategoryChoices.choices,
        required=False
    )
    gender = serializers.ChoiceField(
        choices=GenderChoices.choices,
        required=False
    )
    contract_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Worker
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'category',
            'gender',
            'holidays',
            'password',
            'contract_date',
            'working_week',
            'vacation_policy'
        ]

    def create(self, validated_data):
        """Create and return a new worker."""

        worker = Worker(**validated_data)
        if not validated_data.get('vacation_policy', None):
            raise serializers.ValidationError({
                'vacation_policy': ['This field is required.']
            })
        if not validated_data.get('email', None):
            raise serializers.ValidationError({
                'email': ['This field is required.']
            })
        if validated_data['password']:
            worker.set_password(validated_data['password'])
        else:
            raise serializers.ValidationError({
                'password': 'This field is required.'
            })
        worker.save()
        return worker

    def update(self, instance, validated_data):
        super(WorkerSerializer, self).update(instance, validated_data)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        # if validated_data.get('contract_date'):
        #     instance.contract_date = validated_data.get('contract_date').strftime("%Y-%m-%d")
        instance.save()
        return instance


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=50)

    class Meta:
        model = Team
        fields = ['id', 'name']


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    worker = serializers.PrimaryKeyRelatedField(queryset=Worker.objects, required=False)
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects, required=False)

    class Meta:
        model = Member
        fields = ['id', 'worker', 'team', 'is_referent', 'is_representant']

    def create(self, validated_data):
        member = Member(
            worker=validated_data['worker'],
            team=validated_data['team'],
            created_by=validated_data['created_by'],
            modified_by=validated_data['modified_by']
        )
        member.save()
        return member


class VacationPolicySerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(required=True, max_length=50)
    description = serializers.CharField(required=False, max_length=250)
    holidays = serializers.IntegerField(required=True)

    class Meta:
        model = VacationPolicy
        fields = ['id', 'name', 'description', 'holidays']


class SomEnergiaAbsenceTypeSerializer(serializers.HyperlinkedModelSerializer):

    description = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

    class Meta:
        model = SomEnergiaAbsenceType
        fields = [
            'id',
            'name',
            'description',
            'spend_days',
            'max_duration',
            'min_duration',
            'max_spend',
            'min_spend',
            'color',
            'global_date',
        ]


class SomEnergiaOccurrenceSerializer(serializers.HyperlinkedModelSerializer):

    absence_type = serializers.SerializerMethodField()
    worker = serializers.SerializerMethodField()

    class Meta:
        model = SomEnergiaOccurrence
        fields = ['id', 'absence_type', 'worker', 'start_time', 'end_time']

    def get_absence_type(self, object):
        return object.absence.absence_type.pk

    def get_worker(self, object):
        return object.absence.worker.pk


class CreateSomEnergiaOccurrenceSerializer(serializers.HyperlinkedModelSerializer):

    absence_type = serializers.IntegerField(required=True)
    worker = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        required=True
    )
    start_morning = serializers.BooleanField(default=False, write_only=True)
    start_afternoon = serializers.BooleanField(default=False, write_only=True)
    end_morning = serializers.BooleanField(default=False, write_only=True)
    end_afternoon = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = SomEnergiaOccurrence
        fields = [
            'id',
            'absence_type',
            'worker',
            'start_time',
            'end_time',
            'start_morning',
            'start_afternoon',
            'end_morning',
            'end_afternoon'
        ]

    def extract_body_params(self, validated_data):
        request = validated_data.get('request')
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        start_datetime = calculate_datetime(
            dt=validated_data['start_time'],
            morning=validated_data['start_morning'],
            afternoon=validated_data['start_afternoon'],
            is_start=True
        )
        end_datetime = calculate_datetime(
            validated_data['end_time'],
            morning=validated_data['end_morning'],
            afternoon=validated_data['end_afternoon'],
            is_start=False
        )

        return user, start_datetime, end_datetime

    def get_absence(self, worker, absence_type):
        return SomEnergiaAbsence.objects.filter(
            worker=worker,
            absence_type=absence_type
        )[0]

    def validate(self, data):

        if ((not data['start_morning'] and not data['start_afternoon']) or
           (not data['end_morning'] and not data['end_afternoon'])):
            raise serializers.ValidationError('Incorrect format occurrence')

        if (data['end_time'].day - data['start_time'].day >= 1) and (
            data['start_morning'] and not data['start_afternoon'] or
                not data['end_morning'] and data['end_afternoon']):
                    raise serializers.ValidationError('Incorrect format occurrence')

        return data

    @transaction.atomic
    def create(self, validated_data):

        user, start_datetime, end_datetime = self.extract_body_params(validated_data)

        for worker in validated_data['worker']:

            try:
                absence = self.get_absence(
                    worker,
                    validated_data['absence_type']
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError('Absence not found')

            new_occurrence = SomEnergiaOccurrence(
                start_time=start_datetime,
                end_time=end_datetime,
                absence=absence,
                created_by=user,
                modified_by=user
            )
            try:
                new_occurrence.full_clean()
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict['__all__'][0])

            splited_new_occurrence = new_occurrence.occurrence_splitter_with_global_dates(new_occurrence)

            for occurrence_element in splited_new_occurrence:
                new_occurrence.override_occurrence(
                        worker,
                        user,
                        absence,
                        occurrence_element
                    )
                try:
                    occurrence_element.save()
                except ValidationError:
                    raise serializers.ValidationError('Incorrect occurrence')

        new_occurrence.worker = validated_data['worker']
        new_occurrence.absence_type = validated_data['absence_type']
        return new_occurrence
