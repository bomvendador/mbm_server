# Generated by Django 3.2.8 on 2021-11-03 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0047_order_date_ez_ww'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date_EZ_ww',
            new_name='date_EZ',
        ),
        migrations.AlterField(
            model_name='lotkiez',
            name='date_EZ',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='lotkirefuse',
            name='date_EZ',
            field=models.DateField(default=None, null=True),
        ),
    ]
