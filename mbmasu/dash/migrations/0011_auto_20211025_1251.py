# Generated by Django 3.2.8 on 2021-10-25 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0010_alter_refusereasonsaftertempstop_pp'),
    ]

    operations = [
        migrations.AddField(
            model_name='refusereasonspreliminary',
            name='pp',
            field=models.CharField(blank=True, default=None, max_length=10, verbose_name='Номер поставновления'),
        ),
        migrations.AlterField(
            model_name='refusereasonsaftertempstop',
            name='description',
            field=models.TextField(verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='refusereasonsaftertempstop',
            name='pp',
            field=models.CharField(blank=True, default=None, max_length=10, verbose_name='Номер поставновления'),
        ),
        migrations.AlterField(
            model_name='refusereasonspreliminary',
            name='common_reason',
            field=models.BooleanField(default=False, verbose_name='Общая причина'),
        ),
        migrations.AlterField(
            model_name='refusereasonspreliminary',
            name='description',
            field=models.TextField(verbose_name='Название'),
        ),
    ]
