from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=50)

    def __repr__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(Employee)

    def __repr__(self):
        return self.name
