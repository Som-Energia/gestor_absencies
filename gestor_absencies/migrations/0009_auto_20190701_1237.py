# Generated by Django 2.1.7 on 2019-07-01 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_absencies', '0008_auto_20190701_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='category',
            field=models.CharField(choices=[('Technical', 'Tècnic'), ('Specialist', 'Especialista'), ('Manager', 'Gerència')], max_length=50, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='gender',
            field=models.CharField(choices=[('Male', 'Home'), ('Female', 'Dona'), ('Intersex', 'Intersex'), ('Trans', 'Trans'), ('Queer', 'Queer'), ('Other', 'Altre')], max_length=50, verbose_name='Gender'),
        ),
    ]
