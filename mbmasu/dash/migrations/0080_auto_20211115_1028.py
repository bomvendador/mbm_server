# Generated by Django 3.2.8 on 2021-11-15 10:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dash', '0079_alter_order_date_ez'),
    ]

    operations = [
        migrations.AddField(
            model_name='refuse',
            name='is_refuse_after_temp_stop',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AfterTempStopDecision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(verbose_name='Описание')),
                ('order', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='dash.order')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]