# Generated by Django 3.2.8 on 2021-11-22 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0098_rename_admin_distribution_afetr_temp_stop_countersadmin_admin_distribution_after_temp_stop'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='check_after_temp_stop_files_uploaded',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='check_after_temp_stop_for_check_returned_by_expert',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='check_after_temp_stop_for_check_uploaded',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_files_for_check_returned_by_expert',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_files_for_check_uploaded',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_finals_files_uploaded',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]