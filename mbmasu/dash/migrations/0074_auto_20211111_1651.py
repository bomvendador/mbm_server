# Generated by Django 3.2.8 on 2021-11-11 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0073_auto_20211111_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempstop',
            name='file_notification',
            field=models.FileField(default=None, null=True, upload_to='temp_stop'),
        ),
        migrations.AlterField(
            model_name='tempstop',
            name='file_pez',
            field=models.FileField(default=None, null=True, upload_to='temp_stop'),
        ),
    ]
