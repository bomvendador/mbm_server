# Generated by Django 3.2.8 on 2021-12-10 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0139_readyforok_appointed_ok'),
    ]

    operations = [
        migrations.AddField(
            model_name='countersadmin',
            name='appointed_for_ok',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
