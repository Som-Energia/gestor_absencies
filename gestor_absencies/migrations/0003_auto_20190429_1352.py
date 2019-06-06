# Generated by Django 2.1.7 on 2019-04-29 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_absencies', '0002_auto_20190417_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='somenergiaabsence',
            name='absence_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absence', to='gestor_absencies.SomEnergiaAbsenceType', verbose_name='Absence Type'),
        ),
        migrations.AlterField(
            model_name='somenergiaabsence',
            name='worker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='absence', to=settings.AUTH_USER_MODEL, verbose_name='Worker'),
        ),
        migrations.AlterField(
            model_name='somenergiaoccurrence',
            name='absence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occurrence', to='gestor_absencies.SomEnergiaAbsence', verbose_name='Absence'),
        ),
    ]
