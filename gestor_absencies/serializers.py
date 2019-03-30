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

    label = serializers.CharField(required=False, max_length=50)

    class Meta:
        model = SomEnergiaAbsenceType
        fields = [
            'id',
            'abbr',
            'label',
            'spend_days',
            'max_duration',
            'min_duration'
        ]


class SomEnergiaOccurrenceSerializer(serializers.HyperlinkedModelSerializer):
    
    absence = serializers.PrimaryKeyRelatedField( # Todo SomEnergiaAbsenseType and Worker pk
        queryset=SomEnergiaAbsence.objects,
        required=True
    )

    class Meta:
        model = SomEnergiaOccurrence
        fields = ['id', 'absence', 'start_time', 'end_time']


class CreateSomEnergiaOccurrenceSerializer(serializers.HyperlinkedModelSerializer):

    absence = serializers.PrimaryKeyRelatedField(
        queryset=SomEnergiaAbsence.objects,
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
            'absence',
            'start_time',
            'end_time',
            'start_morning',
            'start_afternoon',
            'end_morning',
            'end_afternoon'
        ]

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

        occurrence = SomEnergiaOccurrence(
            start_time=start_datetime,
            end_time=end_datetime,
            absence=validated_data['absence'],
        )

        try:
            occurrence.save()
        except ValidationError:
            raise serializers.ValidationError('Invalid duration')

        return occurrence
