# Generated by Django 3.2.8 on 2021-12-13 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0142_appointedforok_next_ok'),
    ]

    operations = [
        migrations.RenameField(
            model_name='readyforok',
            old_name='appointed_ok',
            new_name='appointed_next_ok',
        ),
        migrations.RemoveField(
            model_name='appointedforok',
            name='next_ok',
        ),
    ]
