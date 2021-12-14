#-*- coding: utf-8 -*-
# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    tel = models.CharField(max_length=20)
    email_sent_register_notification = models.BooleanField(default=False, verbose_name=u"Отправка уведомления на почту при регистрации")
    common_check_needed = models.BooleanField(default=False, verbose_name=u"Требуется общая проверка")
    check_preliminary_refuse = models.BooleanField(default=False, verbose_name=u"Требуется проверка первичного отказа")
    check_preliminary_ez = models.BooleanField(default=False, verbose_name=u"Требуется проверка первичного ЭЗ")
    check_preliminary_temp_stop = models.BooleanField(default=False, verbose_name=u"Требуется проверка приостановки")
    check_after_temp_stop_refuse = models.BooleanField(default=False, verbose_name=u"Требуется проверка отказа по документам после возобновления")
    check_after_temp_stop_refuse_by_date = models.BooleanField(default=False,
                                                               verbose_name=u"Требуется проверка отказа по сроку после возобновления")
    check_after_temp_stop_ez = models.BooleanField(default=False, verbose_name=u"Требуется проверка ЭЗ после возобновления")
    user_added = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile_created_by', default=None, null=True)

    def __str__(self):
        return self.user.username
