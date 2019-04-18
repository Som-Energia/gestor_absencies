from datetime import timedelta as td, datetime as dt

from django.core.exceptions import ValidationError
from gestor_absencies.common.datetime_calculator import calculate_datetime
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

    class Meta:
        model = Worker
        fields = [
            'id', 'first_name', 'last_name', 'email', 'username'
        ]


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
            'min_spend'
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
    worker = serializers.IntegerField(required=True)
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

    def validate(self, data):

        if (not data['start_morning'] and not data['start_afternoon']) or (
                not data['end_morning'] and not data['end_afternoon']):
                    raise serializers.ValidationError('Incorrect occurrence')

        if (data['end_time'].day - data['start_time'].day >= 1) and (
            data['start_morning'] and not data['start_afternoon'] or
                not data['end_morning'] and data['end_afternoon']):
                    raise serializers.ValidationError('Incorrect occurrence')

        return data

    def create(self, validated_data):

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

        absence = SomEnergiaAbsence.objects.all().filter(
            worker=validated_data['worker'],
            absence_type=validated_data['absence_type']
        )[0]

        occurrence = SomEnergiaOccurrence(
            start_time=start_datetime,
            end_time=end_datetime,
            absence=absence,
            created_by=validated_data['created_by'],
            modified_by=validated_data['modified_by']
        )

        duration = occurrence.day_counter()
        if ((occurrence.absence.absence_type.max_duration != -1 and
             abs(duration) > occurrence.absence.absence_type.max_duration) or
                abs(duration) < occurrence.absence.absence_type.min_duration):
                    raise serializers.ValidationError('Incorrect occurrence')
        elif occurrence.start_time.day < dt.now().day:
                raise serializers.ValidationError('Incorrect occurrence')
        if duration < 0 and occurrence.absence.worker.holidays < abs(duration):
                raise serializers.ValidationError('Incorrect occurrence')


        #Split occurrence
        occurrences = SomEnergiaOccurrence.objects.all().filter(
            start_time__lt=start_datetime,
            end_time__day__gte=end_datetime.day,
            #TODO: add property
        ).all()
        if occurrences:
            for o in occurrences:
                start_occurrence = o.start_time
                end_occurrence = o.end_time
                absence_occurrence = o.absence
                created_by_occurrence = o.created_by
                modified_by_occurrence = o.modified_by
                o.delete()

                if start_occurrence.day < start_datetime.day:
                    first_occurrence = SomEnergiaOccurrence(
                        start_time=start_occurrence,
                        end_time=(start_datetime - td(days=1)).replace(hour=17),
                        absence=absence_occurrence,
                        created_by=created_by_occurrence,
                        modified_by=modified_by_occurrence
                    )
                    first_occurrence.save()
                if end_occurrence.day > end_datetime.day:
                    second_occurrence = SomEnergiaOccurrence(
                        start_time=(end_datetime + td(days=1)).replace(hour=9),
                        end_time=end_occurrence,
                        absence=absence_occurrence,
                        created_by=created_by_occurrence,
                        modified_by=modified_by_occurrence
                    )
                    second_occurrence.save()

        try:
            occurrence.save()
        except ValidationError:
            raise serializers.ValidationError('Incorrect occurrence')

        occurrence.worker = validated_data['worker']
        occurrence.absence_type = validated_data['absence_type']
        return occurrence
