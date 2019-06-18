# from datetime import timedelta as td, datetime as dt
# import datetime.datetime as dt
import datetime
from datetime import timedelta as td
import dateutil.rrule as rrule
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from gestor_absencies.common.datetime_calculator import calculate_datetime
from rest_framework import serializers
from gestor_absencies.common.utils import computable_days_between_dates, find_concurrence_dates
from .models import (
    Member,
    SomEnergiaAbsence,
    SomEnergiaAbsenceType,
    SomEnergiaOccurrence,
    Team,
    VacationPolicy,
    Worker
)
from django.db import transaction

class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

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
            'working_week'
        ]

    def update(self, instance, validated_data):
        super(WorkerSerializer, self).update(instance, validated_data)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        instance.save()
        return instance


class CreateWorkerSerializer(serializers.HyperlinkedModelSerializer):
    vacation_policy = serializers.PrimaryKeyRelatedField(
        queryset=VacationPolicy.objects,
        required=True
    )

    class Meta:
        model = Worker
        fields = [
            'id', 'first_name', 'last_name', 'email', 'username', 'password', 'vacation_policy'
        ]

    def create(self, validated_data):
        """Create and return a new worker."""

        worker = Worker(**validated_data)
        if validated_data['password']:
            worker.set_password(validated_data['password'])
        else:
            raise serializers.ValidationError({
                'password': 'This field is required.'
            })
        worker.save()
        return worker


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True) #TODO: REMOVE ID!!!
    name = serializers.CharField(required=True, max_length=50)

    class Meta:
        model = Team
        fields = ['id', 'name']


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    worker = serializers.PrimaryKeyRelatedField(queryset=Worker.objects, required=False) #TODO: id_worker
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects, required=False) #TODO: id:team

    class Meta:
        model = Member
        fields = ['id', 'worker', 'team', 'is_referent', 'is_representant']

    def create(self, validated_data): #TODO: Validation worker and team exist
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

    def get_global_dates_occurrences(self, worker, start_period, end_period):
        return SomEnergiaOccurrence.objects.filter(
            absence__worker=worker,
            absence__absence_type__global_date=True,
            start_time__gte=start_period,
            end_time__lte=end_period
        )

    def create_occurrence(self, worker, start_datetime, end_datetime, user, absence):

        occurrence = SomEnergiaOccurrence(
            start_time=start_datetime,
            end_time=end_datetime,
            absence=absence,
            created_by=user,
            modified_by=user
        )
        duration = occurrence.day_counter()
        global_dates = self.get_global_dates_occurrences(
            worker=worker,
            start_period=start_datetime,
            end_period=end_datetime
        )
        global_dates_duration = 0
        for global_date in global_dates:
            global_dates_duration += global_date.day_counter()
        duration -= global_dates_duration
        if ((occurrence.absence.absence_type.max_duration != -1 and
             abs(duration) > occurrence.absence.absence_type.max_duration) or
                abs(duration) < occurrence.absence.absence_type.min_duration):
                    raise serializers.ValidationError('Incorrect duration')
        elif occurrence.start_time < datetime.datetime.now().replace(hour=0, minute=0):
                raise serializers.ValidationError('Can\'t create a passade occurrence')
        if duration < 0 and occurrence.absence.worker.holidays < abs(duration):
                raise serializers.ValidationError('Not enough holidays')

        #Split occurrence
        occurrences = SomEnergiaOccurrence.objects.filter(
            start_time__lte=start_datetime,
            end_time__gte=end_datetime,
            absence__worker__id=worker
        ).all()
        if occurrences:
            for o in occurrences:
                start_occurrence = o.start_time
                end_occurrence = o.end_time
                absence_occurrence = o.absence
                created_by_occurrence = o.created_by
                modified_by_occurrence = o.modified_by
                o.delete()
                if start_occurrence < start_datetime:
                    if start_datetime.hour == 13:
                        first_occurrence = SomEnergiaOccurrence(
                            start_time=start_occurrence,
                            end_time=start_datetime.replace(hour=13),
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        first_occurrence.save()
                    else:
                        first_occurrence = SomEnergiaOccurrence(
                            start_time=start_occurrence,
                            end_time=(start_datetime - td(days=1)).replace(hour=17),
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        first_occurrence.save()
                if end_occurrence > end_datetime:
                    if end_datetime.hour == 13:
                        second_occurrence = SomEnergiaOccurrence(
                            start_time=end_datetime.replace(hour=13),
                            end_time=end_occurrence,
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        second_occurrence.save()
                    else:
                        second_occurrence = SomEnergiaOccurrence(
                            start_time=(end_datetime + td(days=1)).replace(hour=9),
                            end_time=end_occurrence,
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        second_occurrence.save()

        # Override occurrences
        occurrences = SomEnergiaOccurrence.objects.filter(
            (
                (
                    Q(start_time__gt=start_datetime) &
                    Q(start_time__lt=end_datetime)
                ) | (
                    Q(end_time__gt=start_datetime) &
                    Q(end_time__lt=end_datetime)
                ) | (
                    Q(start_time__gt=start_datetime) &
                    Q(end_time__lt=end_datetime)
                )
            ) & Q(absence__worker__id=worker)
        ).all()
        if occurrences:
            for o in occurrences:
                start_concurrence, end_concurrence = find_concurrence_dates(
                    occurrence,
                    o
                )
                start_occurrence = o.start_time
                end_occurrence = o.end_time
                absence_occurrence = o.absence
                created_by_occurrence = o.created_by
                modified_by_occurrence = o.modified_by
                o.delete()
                if end_occurrence > end_datetime:
                    if end_datetime.hour == 13:
                        first_occurrence = SomEnergiaOccurrence(
                            start_time=end_datetime.replace(hour=13),
                            end_time=end_occurrence,
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        first_occurrence.save()
                    else:
                        first_occurrence = SomEnergiaOccurrence(
                            start_time=(end_datetime + td(days=1)).replace(hour=9),
                            end_time=end_occurrence,
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        first_occurrence.save()
                if start_occurrence < start_datetime:
                    if start_datetime.hour == 13:
                        second_occurrence = SomEnergiaOccurrence(
                            start_time=start_occurrence,
                            end_time=end_concurrence.replace(hour=13),
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        second_occurrence.save()
                    else:
                        second_occurrence = SomEnergiaOccurrence(
                            start_time=start_occurrence,
                            end_time=(end_concurrence - td(days=1)).replace(hour=17),
                            absence=absence_occurrence,
                            created_by=created_by_occurrence,
                            modified_by=modified_by_occurrence
                        )
                        second_occurrence.save()

        try:
            occurrence.save()
        except ValidationError:
            raise serializers.ValidationError('Incorrect occurrence')

        return occurrence

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

            occurrence = self.create_occurrence(
                worker,
                start_datetime,
                end_datetime,
                user,
                absence
            )

        occurrence.worker = validated_data['worker']
        occurrence.absence_type = validated_data['absence_type']
        return occurrence
