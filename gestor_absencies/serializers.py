from .models import *
from rest_framework import serializers


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

    class Meta:
        model = Worker
        fields = [
            'id', 'first_name', 'last_name', 'email', 'username', 'password'
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
