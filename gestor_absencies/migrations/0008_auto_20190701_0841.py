# Generated by Django 2.1.7 on 2019-07-01 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_absencies', '0007_auto_20190628_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='gender',
            field=models.CharField(choices=[('Tècnic', 'Tècnic'), ('Especialista', 'Especialista'), ('Gerència', 'Especialista')], max_length=50, verbose_name='Gender'),
        ),
    ]