# Generated by Django 3.2.8 on 2021-11-12 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0078_auto_20211112_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_EZ',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='Дата составления ЭЗ'),
        ),
    ]
