# Generated by Django 3.2.8 on 2021-12-13 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0143_auto_20211213_1025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='readyforok',
            old_name='appointed_next_ok',
            new_name='appointed_ok',
        ),
    ]
