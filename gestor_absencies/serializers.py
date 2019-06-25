import datetime
from datetime import timedelta as td

import dateutil.rrule as rrule
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Q
from gestor_absencies.common.datetime_calculator import calculate_datetime
from gestor_absencies.common.utils import (
    computable_days_between_dates,
    find_concurrence_dates
)
from rest_framework import serializers

from .models import (
    Member,
    SomEnergiaAbsence,
    SomEnergiaAbsenceType,
    SomEnergiaOccurrence,
    Team,
    VacationPolicy,
    Worker
)


class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    vacation_policy = serializers.PrimaryKeyRelatedField(
        queryset=VacationPolicy.objects,
        required=False,
        write_only=True
    )
    category = serializers.CharField(max_length=50, required=False)
    gender = serializers.CharField(max_length=50, required=False)
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
            team=validated_data['team']
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

    def get_coincident_global_dates_occurrences(self, worker, start_period, end_period):
        return SomEnergiaOccurrence.objects.filter(
            absence__worker=worker,
            absence__absence_type__global_date=True,
            start_time__gte=start_period,
            end_time__lte=end_period
        )

    def create_frontier_occurrences(self, occurrence_to_override, occurrence_to_overrided):

        first_occurrence = None
        second_occurrence = None
        if occurrence_to_override.start_time < occurrence_to_overrided.start_time:
            if occurrence_to_overrided.start_time.hour == 13:
                first_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_override.start_time,
                    end_time=occurrence_to_overrided.start_time.replace(hour=13),
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
            else:
                first_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_override.start_time,
                    end_time=(occurrence_to_overrided.start_time - td(days=1)).replace(hour=17),
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
        if occurrence_to_override.end_time > occurrence_to_overrided.end_time:
            if occurrence_to_overrided.end_time.hour == 13:
                second_occurrence = SomEnergiaOccurrence(
                    start_time=occurrence_to_overrided.end_time.replace(hour=13),
                    end_time=occurrence_to_override.end_time,
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
            else:
                second_occurrence = SomEnergiaOccurrence(
                    start_time=(occurrence_to_overrided.end_time + td(days=1)).replace(hour=9),
                    end_time=occurrence_to_override.end_time,
                    absence=occurrence_to_override.absence,
                    created_by=occurrence_to_override.created_by,
                    modified_by=occurrence_to_override.modified_by
                )
        return first_occurrence, second_occurrence

    def override_occurrence(self, worker, user, absence, occurrence):

        occurrences = SomEnergiaOccurrence.objects.filter(
            start_time__lte=occurrence.start_time,
            end_time__gte=occurrence.end_time,
            absence__worker__id=worker
        ).all()
        if occurrences:
            for o in occurrences:
                first_occurrence, second_occurrence = self.create_frontier_occurrences(
                    occurrence_to_override=o,
                    occurrence_to_overrided=occurrence
                )
                o.delete()
                if first_occurrence:
                    first_occurrence.save()
                if second_occurrence:
                    second_occurrence.save()

        occurrences = SomEnergiaOccurrence.objects.filter(
            (
                (
                    Q(start_time__gt=occurrence.start_time) &
                    Q(start_time__lt=occurrence.end_time)
                ) | (
                    Q(end_time__gt=occurrence.start_time) &
                    Q(end_time__lt=occurrence.end_time)
                ) | (
                    Q(start_time__gt=occurrence.start_time) &
                    Q(end_time__lt=occurrence.end_time)
                )
            ) & Q(absence__worker__id=worker)
        ).all()
        if occurrences:
            for o in occurrences:
                start_concurrence, end_concurrence = find_concurrence_dates(
                    occurrence,
                    o
                )

                first_occurrence, second_occurrence = self.create_frontier_occurrences(
                    occurrence_to_override=o,
                    occurrence_to_overrided=occurrence
                )
                o.delete()
                if first_occurrence:
                    first_occurrence.save()
                if second_occurrence:
                    second_occurrence.save()

    def occurrence_splitter_with_global_dates(self, occurrence):
        first_occurrence = None
        second_occurrence = None
        global_occurrences = self.get_coincident_global_dates_occurrences(
            worker=occurrence.absence.worker,
            start_period=occurrence.start_time,
            end_period=occurrence.end_time
        )
        if len(global_occurrences) > 0:
            global_occurrence = global_occurrences[0]

            first_occurrence, second_occurrence = self.create_frontier_occurrences(
                occurrence_to_override=occurrence,
                occurrence_to_overrided=global_occurrence
            )

            if first_occurrence and second_occurrence:
                first_call = self.occurrence_splitter_with_global_dates(first_occurrence)
                second_call = self.occurrence_splitter_with_global_dates(second_occurrence)
                first_call.extend(second_call)
                return first_call
            if first_occurrence:
                return self.occurrence_splitter_with_global_dates(first_occurrence)
            if second_occurrence:
                return self.occurrence_splitter_with_global_dates(second_occurrence)
        else:
            return [occurrence]

    def check_duration(self, new_occurrence):
        duration = new_occurrence.day_counter()
        coincident_global_dates = self.get_coincident_global_dates_occurrences(
            worker=new_occurrence.absence.worker,
            start_period=new_occurrence.start_time,
            end_period=new_occurrence.end_time
        )
        global_dates_duration = 0
        for global_date in coincident_global_dates:
            global_dates_duration += global_date.day_counter()
        duration -= global_dates_duration
        if ((new_occurrence.absence.absence_type.max_duration != -1 and
             abs(duration) > new_occurrence.absence.absence_type.max_duration) or
                abs(duration) < new_occurrence.absence.absence_type.min_duration):
                    raise serializers.ValidationError('Incorrect duration')
        elif new_occurrence.start_time < datetime.datetime.now().replace(hour=0, minute=0):
                raise serializers.ValidationError('Can\'t create a passade occurrence')
        if duration < 0 and new_occurrence.absence.worker.holidays < abs(duration):
                raise serializers.ValidationError('Not enough holidays')

    def validate(self, data):

        if (not data['start_morning'] and not data['start_afternoon']) or (
                not data['end_morning'] and not data['end_afternoon']):
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

            self.check_duration(new_occurrence)

            splited_new_occurrence = self.occurrence_splitter_with_global_dates(new_occurrence)

            for occurrence_element in splited_new_occurrence:
                self.override_occurrence(
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
