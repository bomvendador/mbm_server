from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import datetime

from login.models import UserProfile

# Create your models here.


#ПОСТАНОВЛЕНИЯ
class PPnumber(models.Model):
    name = models.CharField(max_length=10, default=None, blank=True, verbose_name='Номер поставновления')

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    pp = models.ForeignKey(PPnumber, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, verbose_name='Номер постановления')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.pp.name + ' - ' + self.name


class OrderStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LotkiContent(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class OrderTypeCheck(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Counters(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=None)
    #первичка новые если требуется проверка
    new_orders_check_is_needed = models.IntegerField(default=0, null=True)
    #проверка
    check_orders_sent_for_check_preliminary = models.IntegerField(default=0, null=True)
    check_orders_to_check_preliminary = models.IntegerField(default=0, null=True)
    check_orders_checked_preliminary = models.IntegerField(default=0, null=True)
    check_orders_to_check_after_temp_stop = models.IntegerField(default=0, null=True)
    check_orders_checked_after_temp_stop = models.IntegerField(default=0, null=True)
    #первичка новые
    new_orders = models.IntegerField(default=0, null=True)
    #приостановка
    temp_stop_date = models.IntegerField(default=0, null=True)
    temp_stop_without_notification = models.IntegerField(default=0, null=True)
    temp_stop_with_notification = models.IntegerField(default=0, null=True)
    temp_stop_remade_order_date = models.IntegerField(default=0, null=True)
    temp_stop_check = models.IntegerField(default=0, null=True)
    temp_stop_on_check = models.IntegerField(default=0, null=True)
    temp_stop_remade_order_decision = models.IntegerField(default=0, null=True)
    #отказы
    refuse_preliminary = models.IntegerField(default=0, null=True)
    refuse_by_docs = models.IntegerField(default=0, null=True)
    refuse_by_date = models.IntegerField(default=0, null=True)
    #ЭЗ
    ez_doc = models.IntegerField(default=0, null=True)
    ez_pdf = models.IntegerField(default=0, null=True)
    ez_doc_remake = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class CountersLotki(models.Model):
    user_role_name = models.CharField(default='Статистика (лотки)', max_length=50)
    #лотки
    statist_refuses_not_preliminary = models.IntegerField(default=0, null=True)
    statist_ez = models.IntegerField(default=0, null=True)
    #на подписи
    statist_temp_stop_on_signing = models.IntegerField(default=0, null=True)
    statist_refuse_on_signing = models.IntegerField(default=0, null=True)
    statist_ez_on_signing = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.user_role_name


class CountersAdmin(models.Model):
    user_role_name = models.CharField(default='Админ', max_length=50)
    all_orders = models.IntegerField(default=0, null=True)
    new_orders = models.IntegerField(default=0, null=True)
    #админ
    #заявки админ
    admin_orders_all = models.IntegerField(default=0, null=True)
    admin_remade_order_date = models.IntegerField(default=0, null=True)
    #проверка
    admin_distribution_preliminary = models.IntegerField(default=0, null=True)
    admin_distribution_after_temp_stop = models.IntegerField(default=0, null=True)
    #ОК
    admin_ready_for_ok = models.IntegerField(default=0, null=True)
    appointed_for_ok = models.IntegerField(default=0, null=True)

    #Протоколы
    admin_protocols_orders = models.IntegerField(default=0, null=True)

    #Выездная проверка
    admin_onsite_checks = models.IntegerField(default=0, null=True)
    admin_onsite_checks_complete = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.user_role_name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='created_by')
    responsible_preliminary = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_preliminary')
    responsible_preliminary_profile = models.ForeignKey(UserProfile, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_preliminary_profile')
    responsible_after_temp_stop = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_after_temp_stop')
    responsible_after_temp_stop_profile = models.ForeignKey(UserProfile, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_after_temp_stop_profile')
    responsible_preliminary_check_expert = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_preliminary_check_expert')
    responsible_after_temp_stop_check_expert = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True,
                      related_name='responsible_after_temp_stop_check_expert')
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    number = models.CharField(max_length=100)
    date_of_appliance = models.DateField(auto_now=False, auto_now_add=False)
    sum_of_appliance = models.DecimalField(max_digits=12, decimal_places=2)
    end_date = models.DateField(default=None, auto_now=False, auto_now_add=False) #крайняя дата 15 РД
    end_date_for_responsible = models.DateField(default=None) #крайняя дата для исполнителя
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_DEFAULT, default=None)
    pp = models.ForeignKey(PPnumber, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    type = models.ForeignKey(OrderTypeCheck, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)#тип завяки при проверке
    marked_for_remake = models.BooleanField(default=False)
    onsite_check = models.BooleanField(blank=True, null=True,  verbose_name='Выездная проверка')#выездная проверка
    onsite_check_complete = models.BooleanField(blank=False, null=True, default=False)#выездная проверка завершена
    aim = models.TextField(blank=True, null=True)#цель из ИАС
    service_name = models.TextField(blank=True, null=True, default=None)#Наименование сервиса из ИАС
    company = models.CharField(max_length=200, blank=True, null=True)
    company_inn = models.CharField(max_length=20, blank=True, null=True)
    lotki_status = models.ForeignKey(LotkiContent, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    lotki_preliminary_temp_stop_date_received = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения документов от исполнителя
    lotki_preliminary_temp_stop_date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения подписанных документов
    lotki_preliminary_refuse_date_received = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения документов от исполнителя
    lotki_preliminary_refuse_date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения подписанных документов
    lotki_after_temp_stop_refuse_date_received = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения документов от исполнителя
    lotki_after_temp_stop_refuse_date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения подписанных документов
    lotki_ez_date_received = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения документов от исполнителя
    lotki_ez_date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) #дата получения подписанных документов
    date_EZ = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True, verbose_name='Дата составления ЭЗ')  # дата составления ЭЗ
    refuse_is_preliminary = models.BooleanField(blank=True, null=True, default=None)
    refuse_is_refuse_by_date = models.BooleanField(blank=True, null=True, default=None)
    refuse_after_temp_stop = models.BooleanField(blank=True, null=True, default=None)
    temp_stop = models.BooleanField(blank=True, null=True, default=None)#проистановлена ли заявка
    temp_stop_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, default=None)#дата подписания уведомления
    remade_order_received_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, default=None)

    check_preliminary_refuse = models.BooleanField(default=False, verbose_name=u"Требуется проверка первичного отказа")
    check_preliminary_ez = models.BooleanField(default=False, verbose_name=u"Требуется проверка первичного ЭЗ")
    check_preliminary_temp_stop = models.BooleanField(default=False, verbose_name=u"Требуется проверка приостановки")
    check_preliminary_files_for_check_uploaded = models.BooleanField(default=False)#файлы на проверку загружены подрядчиком
    check_preliminary_finals_files_uploaded = models.BooleanField(default=False)#финальные версии файлов загружены
    check_preliminary_returned_after_correction = models.BooleanField(default=False)#финальные версии файлов загружены
    check_preliminary_files_for_check_returned_by_expert = models.BooleanField(default=False)#файлы возвращены экспертом на доработку
    check_preliminary_last_date_sent_for_check = models.DateTimeField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True, verbose_name='Дата отправки документов на проверку')

    check_preliminary_pass_without_check = models.BooleanField(default=False, verbose_name=u"Предварительная проверка пропущена")

    check_after_temp_stop_refuse = models.BooleanField(default=False, verbose_name=u"Требуется проверка отказа по документам после возобновления")
    check_after_temp_stop_refuse_by_date = models.BooleanField(default=False, verbose_name=u"Требуется проверка отказа по сроку после возобновления")
    check_after_temp_stop_ez = models.BooleanField(default=False, verbose_name=u"Требуется проверка ЭЗ после возобновления")
    check_after_temp_stop_files_for_check_uploaded = models.BooleanField(default=False)#файлы на проверку загружены подрядчиком
    check_after_temp_stop_finals_files_uploaded = models.BooleanField(default=False)#финальные версии файлов загружены
    check_after_temp_stop_returned_after_correction = models.BooleanField(default=False)#финальные версии файлов загружены
    check_after_temp_stop_files_for_check_returned_by_expert = models.BooleanField(default=False)#файлы возвращены экспертом на доработку
    check_after_temp_stop_last_date_sent_for_check = models.DateTimeField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True, verbose_name='Дата отправки документов на проверку')

    check_after_temp_stop_pass_without_check = models.BooleanField(default=False, verbose_name=u"Проверка после возобновления пропущена")
    callback_date = models.DateTimeField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True, verbose_name='Дата отзыва заявки')

    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.number + ' - ' + self.company + ' - ' + self.status.name


class ResponsibleForOrderPreliminary(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='responsible_for_order_preliminary_created_by')
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='responsible_for_order_preliminary_responsible')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    company = models.CharField(max_length=200, blank=True, null=True, default=None)

    def __str__(self):
        return self.order.company + ' - ' + self.responsible.username


class ResponsibleForOrderAfterTempStop(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='responsible_for_order_aftertempstop_created_by')
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='responsible_for_order_aftertempstop_responsible')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    company = models.CharField(max_length=200, blank=True, null=True, default=None)


class Applier(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    applier_email = models.CharField(max_length=50)
    applier_tel = models.CharField(max_length=20)
    applier_fio = models.CharField(max_length=200)
    applier_type = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.order.company


## ПРИОСТАНОВКИ
class NotificationTempStop(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    notification_date = models.DateField(auto_now=False, auto_now_add=False)
    notification_number = models.CharField(max_length=20, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return self.order.company


class TempStop(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date_IAS = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)#дата загрузки уведомления
    description = models.TextField(blank=True, null=True)
    notification_sent_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)#дата подписания уведомления
    end_date_for_remade_order = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    end_date_for_notification = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    remade_order_received_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    remade_order_sent_to_subcontractor_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    end_date_after_temp_stop = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True) #крайняя дата для отправки ЭЗ/отказа
    end_date_after_temp_stop_for_responsible = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True) #крайняя дата для отправки ЭЗ/отказа для подрядчика
    notification = models.OneToOneField(NotificationTempStop, on_delete=models.CASCADE, primary_key=True, default=None)

    def __str__(self):
        return self.notification.order.company


class TempStopFiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    temp_stop = models.ForeignKey(TempStop, on_delete=models.CASCADE, default=None, null=True)
    file_pez = models.FileField(upload_to='temp_stop', default=None, null=True)
    file_notification = models.FileField(upload_to='temp_stop', default=None, null=True)


## ОТКАЗЫ
class NotificationRefuse(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    notification_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    notification_number = models.CharField(max_length=20, blank=True, null=True)
    sent_to_applier_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return self.order.company


class Refuse(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_preliminary = models.BooleanField(blank=True, null=True)
    is_refuse_by_date = models.BooleanField(blank=True, null=True)
    is_refuse_after_temp_stop = models.BooleanField(blank=True, null=True)
    date_IAS = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notification_sent_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    notification = models.OneToOneField(NotificationRefuse, on_delete=models.CASCADE, primary_key=True, default=None)

    def __str__(self):
        return self.notification.order.company


class RefuseFiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    refuse = models.ForeignKey(Refuse, on_delete=models.CASCADE, default=None, null=True)
    file_ez = models.FileField(upload_to='refuse', default=None, null=True)
    file_notification = models.FileField(upload_to='refuse', default=None, null=True)

    def __str__(self):
        return self.refuse.notification.order.company


## ЭЗ
class EZdoc(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creation_date = models.DateField(auto_now=False, auto_now_add=False)
    max_sum = models.DecimalField(max_digits=12, decimal_places=2)
    decision = models.BooleanField(default=False)
    file = models.FileField(upload_to='EZ/doc')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    signed_bool = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.file.name


class EZpdf(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    ez_doc = models.ForeignKey(EZdoc, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='EZ/pdf')

    def __str__(self):
        return self.file.name


## Отраслевая комиссия Готово для ОК
class ReadyForOK(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creation_date = models.DateField(auto_now=False, auto_now_add=False)
    max_sum = models.DecimalField(max_digits=12, decimal_places=2)
    decision = models.BooleanField(default=False)
    doc_file = models.FileField(upload_to='EZ/doc')
    pdf_file = models.FileField(upload_to='EZ/doc')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    marked_for_next_ok = models.BooleanField(default=False)
    appointed_ok = models.BooleanField(blank=False, null=True, default=False)


    def __str__(self):
        return self.order.number + ' - ' + self.order.company

##Данные о комиссии
class CommissionDate(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return str(self.date)


## Отраслевая комиссия Рассмотрено на ОК
class AppointedForOK(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    decision = models.BooleanField(default=False, null=True, blank=True)
    ready_for_OK = models.ForeignKey(ReadyForOK, on_delete=models.CASCADE, default=None)
    commission_date = models.ForeignKey(CommissionDate, on_delete=models.CASCADE, default=None)
    marked_for_next_ok = models.BooleanField(blank=False, null=True, default=False)
    protocol_issued = models.BooleanField(blank=False, null=True, default=False)

    def __str__(self):
        return self.ready_for_OK.order.number + ' - ' + self.ready_for_OK.order.company


class Protocol(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    protocol_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    protocol_number = models.IntegerField(default=0, null=True)

    def __str__(self):
        return str(self.protocol_number) + ' - ' + str(self.protocol_date)


##Протокол
class ProtocolOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    appointed_for_ok = models.ForeignKey(AppointedForOK, on_delete=models.CASCADE)
    max_sum = models.DecimalField(max_digits=12, decimal_places=2)
    decision = models.CharField(max_length=100, blank=True, null=True, default=None)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, default=None, null=True)
    points = models.DecimalField(max_digits=12, decimal_places=2, default=0)


##Выездная проверка
class OnsiteCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)#дата проведния ВП
    act = models.FileField()

    def __str__(self):
        return str(self.order.number) + ' - ' + str(self.order.company)


## ОТЗЫВЫ
class OrderCalledBack(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)


## ЛОТКИ
class LotkiTempStop(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date_received = models.DateField(auto_now=False, auto_now_add=False) #дата получения документов от исполнителя
    date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True)

    def __str__(self):
        return self.order.number + ' - ' + self.order.company


class LotkiRefuse(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date_received = models.DateField(auto_now=False, auto_now_add=False) #дата получения документов от исполнителя
    date_EZ = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True) #дата составления ЭЗ
    date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True)


class LotkiEZ(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date_received = models.DateField(auto_now=False, auto_now_add=False) #дата получения документов от исполнителя
    date_signed = models.DateField(auto_now=False, auto_now_add=False, null=True)
    date_EZ = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True) #дата составления ЭЗ


## Предварительная проверка
class CheckPreliminary(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_type_check = models.ForeignKey(OrderTypeCheck, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return self.order.number + ' - ' + self.order.company


class CheckPreliminaryResponsibleExpert(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='preliminary_check_modified_by')
    check_preliminary = models.ForeignKey(CheckPreliminary, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    end_date_for_expert = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True)
    responsible_expert = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='preliminary_check_responsible_expert')

    def __str__(self):
        return self.check_preliminary.order.number + ' - ' + self.check_preliminary.order.company


class CheckPreliminaryFileToCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_preliminary = models.ForeignKey(CheckPreliminary, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    file_1 = models.FileField(upload_to='preliminary_check/to_check', default=None)
    file_2 = models.FileField(upload_to='preliminary_check/to_check', default=None)

    def __str__(self):
        return self.check_preliminary.order.number + ' - ' + self.check_preliminary.order.company


class CheckPreliminaryFileToCheckReturned(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_preliminary_file_to_check = models.ForeignKey(CheckPreliminaryFileToCheck, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    file_1 = models.FileField(upload_to='preliminary_check/to_check', default=None)
    file_2 = models.FileField(upload_to='preliminary_check/to_check', default=None)

    def __str__(self):
        return self.check_preliminary_file_to_check.check_preliminary.order.number + ' - ' + self.check_preliminary_file_to_check.check_preliminary.order.company


class CheckPreliminaryFileToCheckFinal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_preliminary_file_to_check = models.ForeignKey(CheckPreliminaryFileToCheck, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    file_1 = models.FileField(upload_to='preliminary_check/to_check', default=None)
    file_2 = models.FileField(upload_to='preliminary_check/to_check', default=None)

    def __str__(self):
        return self.check_preliminary_file_to_check.check_preliminary.order.number + ' - ' + self.check_preliminary_file_to_check.check_preliminary.order.company


## Проверка после возобновления
class CheckAfterTempStop(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_type_check = models.ForeignKey(OrderTypeCheck, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return self.order.number + ' - ' + self.order.company


class CheckAfterTempStopResponsibleExpert(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='after_temp_stop_check_modified_by')
    check_after_temp_stop = models.ForeignKey(CheckAfterTempStop, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    end_date_for_expert = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True)
    responsible_expert = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, related_name='after_temp_stop_check_responsible_expert')

    def __str__(self):
        return self.check_after_temp_stop.order.number + ' - ' + self.check_after_temp_stop.order.company


class CheckAfterTempStopFileToCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_after_temp_stop = models.ForeignKey(CheckAfterTempStop, on_delete=models.CASCADE, default=None)
    type = models.CharField(max_length=200)
    file_1 = models.FileField(upload_to='', default=None)
    file_2 = models.FileField(upload_to='', default=None)

    def __str__(self):
        return self.check_after_temp_stop.order.number + ' - ' + self.check_after_temp_stop.order.company


class CheckAfterTempStopFileToCheckReturned(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_after_temp_stop_file_to_check = models.ForeignKey(CheckAfterTempStopFileToCheck, on_delete=models.CASCADE, default=None)
    type = models.CharField(max_length=100)
    file_1 = models.FileField(upload_to='preliminary_check/to_check', default=None)
    file_2 = models.FileField(upload_to='preliminary_check/to_check', default=None)

    def __str__(self):
        return self.check_after_temp_stop_file_to_check.check_after_temp_stop.order.number + ' - ' + self.check_after_temp_stop_file_to_check.check_after_temp_stop.order.company


class CheckAfterTempStopFileToCheckFinal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    check_after_temp_stop_file_to_check = models.ForeignKey(CheckAfterTempStopFileToCheck, on_delete=models.CASCADE, default=None)
    type = models.CharField(max_length=200)
    file_1 = models.FileField(upload_to='preliminary_check/to_check', default=None)
    file_2 = models.FileField(upload_to='preliminary_check/to_check', default=None)

    def __str__(self):
        return self.check_after_temp_stop_file_to_check.check_after_temp_stop.order.number + ' - ' + self.check_after_temp_stop_file_to_check.check_after_temp_stop.order.company


#ПРИЧИНЫ ОТКАЗА первичка (список причин)
class RefuseReasonsPreliminary(models.Model):
    description = models.TextField(verbose_name='Название')
    common_reason = models.BooleanField(default=False, verbose_name='Общая причина')
    pp = models.ForeignKey(PPnumber, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, verbose_name='Номер постановления')

    def __str__(self):
        if self.pp:
            return self.description + ' общая - ' + str(self.common_reason) + ' ПП - ' + self.pp.name
        else:
            return self.description + ' общая - ' + str(self.common_reason)


#ПРИЧИНЫ ОТКАЗА первичка по заявкам
class RefuseReasonsPreliminaryByOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    refuse_reason = models.ForeignKey(RefuseReasonsPreliminary, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.order.number + ' - ' + self.order.company


#ПРИЧИНЫ ОТКАЗА после приостановки (список причин)
class RefuseReasonsAfterTempStop(models.Model):
    description = models.TextField(verbose_name='Название')
    common_reason = models.BooleanField(default=False)
    pp = models.ForeignKey(PPnumber, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, verbose_name='Номер постановления')

    def __str__(self):
        return self.description


#ПРИЧИНЫ ОТКАЗА первичка по заявкам
class RefuseReasonsAfterTempStopByOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    refuse_reason = models.ForeignKey(RefuseReasonsAfterTempStop, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.order.number + ' - ' + self.order.company


#ЗАЯВКИ, ОТПРАВЛЕННЫЕ НА ПЕРЕДЕЛКУ
class SentToCorrection(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.order


#КАТЕГОРИИ


class CategoriesByOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        # return self.name
        return self.order.number + ' - ' + self.name


#ИЗМЕНЕНИЕ СТАТУСА
class StatusChange(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, verbose_name='Статус')

    def __str__(self):
        return str(self.added) + ' - ' + self.order.number + ' - ' + self.status.name + ' - ' + self.user.first_name + ' ' + self.user.last_name


#ИЗМЕНЕНИЕ СТАТУСА ЛОТКИ
class LotkiStatusChange(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
    status = models.ForeignKey(LotkiContent, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, verbose_name='Статус лотки')

    def __str__(self):
        return str(self.added) + ' - ' + self.order.number + ' - ' + self.status.name + ' - ' + self.user.first_name + ' ' + self.user.last_name


#РЕШЕНИЕ ПОСЛЕ ПРИОСТАНОВКИ
class AfterTempStopDecision(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    description = models.TextField(verbose_name='Описание')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
