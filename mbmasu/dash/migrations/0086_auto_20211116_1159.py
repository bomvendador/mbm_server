# Generated by Django 3.2.8 on 2021-11-16 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0085_auto_20211116_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='refuse',
            name='file_ez',
            field=models.FileField(default=None, null=True, upload_to='refuse'),
        ),
        migrations.AddField(
            model_name='refuse',
            name='file_notification',
            field=models.FileField(default=None, null=True, upload_to='refuse'),
        ),
    ]