# Generated by Django 3.2.8 on 2021-11-11 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0069_alter_counters_temp_stop_remade_order_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempstop',
            name='file_notification',
            field=models.FileField(default=None, upload_to='temp_stop/notification'),
        ),
        migrations.AddField(
            model_name='tempstop',
            name='file_pez',
            field=models.FileField(default=None, upload_to='temp_stop/PEZ'),
        ),
    ]