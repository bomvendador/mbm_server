# Generated by Django 3.2.8 on 2021-11-30 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0120_applier_inn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applier',
            name='inn',
        ),
    ]
