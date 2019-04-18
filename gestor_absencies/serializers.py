from .models import (
    Worker,
    Member,
    Team,
    SomEnergiaAbsenceType,
    SomEnergiaOccurrence,
    SomEnergiaAbsence,
    VacationPolicy
)
from rest_framework import serializers
from gestor_absencies.common.datetime_calculator import calculate_datetime
from django.core.exceptions import ValidationError


class WorkerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Worker
        fields = [
            'id', 'first_name', 'last_name', 'email', 'username'
        ]

    # def update(self, instance, validated_data):
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.firstname = validated_data.get('firstname', instance.firstname)
    #     instance.secondname = validated_data.get('secondname', instance.secondname)

    #     print(validated_data.get('password', instance.password))
    #     instance.password = validated_data.get('password', instance.password)
    #     instance.save()
    #     return instance


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
        )

        try:
            occurrence.save()
        except ValidationError:
            raise serializers.ValidationError('Incorrect occurrence')

        occurrence.worker = validated_data['worker']
        occurrence.absence_type = validated_data['absence_type']
        return occurrence
