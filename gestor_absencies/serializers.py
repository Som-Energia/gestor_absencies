from .models import *
from rest_framework import serializers


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    firstname = serializers.CharField(required=True, max_length=50)
    secondname = serializers.CharField(required=True, max_length=50)
    email = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = Employee
        fields = ['id', 'firstname', 'secondname', 'email']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['name']
