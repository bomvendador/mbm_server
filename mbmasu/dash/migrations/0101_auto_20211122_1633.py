# Generated by Django 3.2.8 on 2021-11-22 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0100_auto_20211122_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='check_after_temp_stop_files_uploaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='check_after_temp_stop_for_check_returned_by_expert',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='check_after_temp_stop_for_check_uploaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='check_preliminary_files_for_check_returned_by_expert',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='check_preliminary_files_for_check_uploaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='check_preliminary_finals_files_uploaded',
            field=models.BooleanField(default=False),
        ),
    ]
