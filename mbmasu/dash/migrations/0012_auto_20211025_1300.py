# Generated by Django 3.2.8 on 2021-10-25 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0011_auto_20211025_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='PPnumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=10, verbose_name='Номер поставновления')),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='pp',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='dash.ppnumber'),
        ),
        migrations.AlterField(
            model_name='refusereasonsaftertempstop',
            name='pp',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='dash.ppnumber', verbose_name='Номер поставновления'),
        ),
        migrations.AlterField(
            model_name='refusereasonspreliminary',
            name='pp',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='dash.ppnumber', verbose_name='Номер поставновления'),
        ),
    ]