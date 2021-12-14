# Generated by Django 3.2.8 on 2021-12-13 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0144_rename_appointed_next_ok_readyforok_appointed_ok'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointedforok',
            name='marked_for_next_ok',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='appointedforok',
            name='decision',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='appointedforok',
            name='max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]