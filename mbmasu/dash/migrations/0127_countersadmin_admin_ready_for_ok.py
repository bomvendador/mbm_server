# Generated by Django 3.2.8 on 2021-12-07 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0126_order_callback_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='countersadmin',
            name='admin_ready_for_ok',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
