# Generated by Django 3.2.8 on 2021-11-03 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0043_alter_order_date_ez'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='date_EZ',
        ),
    ]