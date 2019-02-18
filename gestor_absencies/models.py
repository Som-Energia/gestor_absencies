from django.db import models


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50)
    secondname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)

    def __repr__(self):
        return self.firstname, self.secondname, self.email

    class Meta:
        ordering = ('firstname', 'secondname', 'email',)


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(Employee)

    def __repr__(self):
        return self.name

    class Meta:
        ordering = ('name',)
