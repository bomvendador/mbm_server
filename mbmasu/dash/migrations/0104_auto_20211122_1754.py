# Generated by Django 3.2.8 on 2021-11-22 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0103_counters_check_orders_sent_for_check_preliminary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='check_after_temp_stop_for_check_returned_by_expert',
            new_name='check_after_temp_stop_files_for_check_returned_by_expert',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='check_after_temp_stop_for_check_uploaded',
            new_name='check_after_temp_stop_files_for_check_uploaded',
        ),
    ]
