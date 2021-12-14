# Generated by Django 3.2.8 on 2021-11-24 10:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0107_alter_checkpreliminaryresponsibleexpert_end_date_for_expert'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkaftertempstop',
            name='type',
        ),
        migrations.AddField(
            model_name='checkaftertempstop',
            name='order_type_check',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='dash.ordertypecheck'),
        ),
        migrations.AddField(
            model_name='checkpreliminaryfiletocheckfinal',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkpreliminaryfiletocheckfinal',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]