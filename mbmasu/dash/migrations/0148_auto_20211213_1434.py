# Generated by Django 3.2.8 on 2021-12-13 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0147_readyforok_onsite_check_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readyforok',
            name='onsite_check_complete',
        ),
        migrations.AddField(
            model_name='order',
            name='onsite_check_complete',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
