# Generated by Django 3.2.8 on 2021-11-03 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0053_auto_20211103_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refuse',
            name='order',
        ),
        migrations.RemoveField(
            model_name='tempstop',
            name='order',
        ),
        migrations.AddField(
            model_name='notificationrefuse',
            name='order',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='dash.order'),
        ),
        migrations.AddField(
            model_name='notificationtempstop',
            name='order',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='dash.order'),
        ),
    ]
