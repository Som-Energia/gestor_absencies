# Generated by Django 2.1.7 on 2019-06-28 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_absencies', '0006_auto_20190617_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='category',
            field=models.CharField(choices=[('Tècnic', 'Tècnic'), ('Especialista', 'Especialista'), ('Gerència', 'Especialista')], max_length=50, verbose_name='Category'),
        ),
    ]
