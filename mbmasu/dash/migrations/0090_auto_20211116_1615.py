# Generated by Django 3.2.8 on 2021-11-16 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0089_alter_lotkicontent_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='lotki_ez_date_received',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='lotki_ez_date_signed',
            field=models.DateField(blank=True, null=True),
        ),
    ]