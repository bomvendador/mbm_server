# Generated by Django 3.2.8 on 2021-11-25 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0109_auto_20211124_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempstop',
            name='remade_order_subcontractor_end_date_for_docs',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]