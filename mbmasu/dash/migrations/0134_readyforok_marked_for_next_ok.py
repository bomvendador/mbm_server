# Generated by Django 3.2.8 on 2021-12-09 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0133_appointedforok_commission_commissiondate'),
    ]

    operations = [
        migrations.AddField(
            model_name='readyforok',
            name='marked_for_next_ok',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
