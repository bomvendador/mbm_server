# Generated by Django 3.2.8 on 2021-11-10 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0062_auto_20211110_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='counters',
            name='admin_distribution_afetr_temp_stop',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='counters',
            name='admin_distribution_preliminary',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='counters',
            name='admin_orders_all',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='counters',
            name='admin_remade_order_date',
            field=models.IntegerField(default=None),
        ),
    ]