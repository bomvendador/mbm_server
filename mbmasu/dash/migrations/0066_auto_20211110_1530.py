# Generated by Django 3.2.8 on 2021-11-10 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0065_auto_20211110_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='check_after_temp_stop_ez',
            field=models.BooleanField(default=False, verbose_name='Требуется проверка ЭЗ после возобновления'),
        ),
        migrations.AddField(
            model_name='order',
            name='check_after_temp_stop_refuse',
            field=models.BooleanField(default=False, verbose_name='Требуется проверка отказа после возобновления'),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_ez',
            field=models.BooleanField(default=False, verbose_name='Требуется проверка первичного ЭЗ'),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_refuse',
            field=models.BooleanField(default=False, verbose_name='Требуется проверка первичного отказа'),
        ),
        migrations.AddField(
            model_name='order',
            name='check_preliminary_temp_stop',
            field=models.BooleanField(default=False, verbose_name='Требуется проверка приостановки'),
        ),
    ]
