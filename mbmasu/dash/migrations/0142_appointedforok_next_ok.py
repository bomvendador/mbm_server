# Generated by Django 3.2.8 on 2021-12-13 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0141_protocolok'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointedforok',
            name='next_ok',
            field=models.BooleanField(default=False),
        ),
    ]