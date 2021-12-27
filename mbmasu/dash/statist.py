from django.shortcuts import render, redirect
from django.apps import apps
from django.http import HttpResponse, JsonResponse, QueryDict
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Order, OrderStatus, Applier, PPnumber, ResponsibleForOrderPreliminary, \
    ResponsibleForOrderAfterTempStop, Category, \
    CategoriesByOrder, LotkiTempStop, LotkiRefuse, LotkiEZ, LotkiContent, NotificationRefuse, NotificationTempStop, \
    TempStop, Refuse, Counters, CountersLotki, EZdoc
from django.contrib.auth.models import User
from .views import dash_get_info, get_counter, lotki_status_change, status_change_without_order_status
from . counters import counters
from django.core import serializers
from login.models import UserProfile
from datetime import datetime
from django.db.models import Q


import json
userprofile = apps.get_model('login', 'UserProfile')


@login_required(redirect_field_name=None, login_url='/')
def get_user_info(request):
    context = dash_get_info(request)
    return context


#nav_satist_boxes_prelimenary
@login_required(redirect_field_name=None, login_url='/')
def new_orders_preliminary_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    new_orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                      (((((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True))
                                               & (Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=True))) |
                                      (Q(check_preliminary_refuse=False) | Q(check_preliminary_ez=False) | Q(check_preliminary_temp_stop=False))) &
                                      (Q(lotki_preliminary_temp_stop_date_received__isnull=True) & Q(lotki_preliminary_refuse_date_received__isnull=True)) &
                                      Q(type__isnull=False)) |
                                       (Q(responsible_preliminary_profile__role__name='Эксперт МБМ') & (Q(lotki_preliminary_temp_stop_date_received__isnull=False) |
                                                                                                         Q(lotki_preliminary_refuse_date_received__isnull=False)))
                                       ))
    print(new_orders)
    context.update({
        'new_orders': new_orders,
        'big_title': 'Список заявок на предварительной проверке',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_new_orders_preliminary_list.html', context)


#prelimenaryCheck_new_order
@login_required(redirect_field_name=None, login_url='/')
def order_preliminary_check(request, order_id):
    print('order_ready_to_proceed')
    user_ = request.user
    order = Order.objects.get(id=order_id)
    context = get_user_info(request)
    # if order.responsible_preliminary == user_:
    #     user_profile = context['user_profile']
    #     user_role = user_profile.role.name
    #     categories = Category.objects.filter(pp=order.pp)
    context.update({
        'order': order,
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_preliminary_order.html', context)
    # else:
    #     context.update({'error': "Заявка назначена на другого исполнителя"})
    #     return render(request, 'dash/dash_base.html', context)


#сохранение данных при нажатии кнопки при первичном приеме документов
@login_required(redirect_field_name=None, login_url='/')
def save_data_preliminary_check_statist(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        document_type = data['documentType']
        document_received_date = data.get('documentReceivedDate')

        print(data)
        counters_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_db.save()

        if document_type == 'Приостановка':
            lotki_temp_stop_db = LotkiTempStop()
            lotki_temp_stop_db.order = order
            lotki_temp_stop_db.date_received = document_received_date
            lotki_temp_stop_db.user = request.user
            lotki_temp_stop_db.save()
            order.lotki_preliminary_temp_stop_date_received = document_received_date
            counters_db.statist_temp_stop_on_signing = int(counters_db.statist_temp_stop_on_signing or 0) + 1
            lotki_status_change(order, 'Приостановка', request.user)

        if document_type == 'Отказ':
            document_EZ_date = document_received_date
            lotki_refuse = LotkiRefuse()
            lotki_refuse.user = request.user
            lotki_refuse.order = order
            lotki_refuse.date_received = document_received_date
            lotki_refuse.date_EZ = document_EZ_date
            lotki_refuse.save()
            order.lotki_preliminary_refuse_date_received = document_received_date
            order.date_EZ = document_EZ_date
            counters_db.statist_refuse_on_signing = int(counters_db.statist_refuse_on_signing or 0) + 1
            lotki_status_change(order, 'Отказ', request.user)

        order.lotki_status = LotkiContent.objects.get(name=document_type)
        order.save()

        counters_db.save()

        status_change_without_order_status(order,
                                           OrderStatus.objects.get(name='Лотки (документы получены от исполнителя)'),
                                           request.user)

        return HttpResponse('ok')


#nav_satist_boxes_for_signing_temp_stop
@login_required(redirect_field_name=None, login_url='/')
def statist_temp_stop_orders_for_singing_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    new_orders = ''
    if not user_profile.common_check_needed:
        new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке'),
                    lotki_preliminary_temp_stop_date_received__isnull=False, lotki_preliminary_temp_stop_date_signed=None)

    print(new_orders)
    context.update({
        'new_orders': new_orders,
        'big_title': 'Список заявок на подписи (приостановка)',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_temp_stop_orders_for_singing_list.html', context)


#nav_satist_boxes_for_signing_temp_stop
@login_required(redirect_field_name=None, login_url='/')
def statist_refuse_orders_for_singing_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    new_orders = ''
    if not user_profile.common_check_needed:
        new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке'),
                    lotki_preliminary_refuse_date_received__isnull=False, lotki_preliminary_refuse_date_signed=None) | \
        Order.objects.filter(status=OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)'),
                             lotki_after_temp_stop_refuse_date_received__isnull=False,
                             lotki_preliminary_refuse_date_signed=None)

    print(new_orders)
    context.update({
        'new_orders': new_orders,
        'big_title': 'Список заявок на подписи (Отказ)',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_temp_stop_orders_for_singing_list.html', context)


#prelimenaryCheck_new_order
@login_required(redirect_field_name=None, login_url='/')
def statist_docs_singed(request, order_id):
    print('temp_stop_docs_singed')
    user_ = request.user
    user_profile = get_user_info(request)['user_profile']
    # user_profile = context['user_profile']

    if user_profile.role.name != 'Статистика (лотки)':
        context = {
            'user_profile': user_profile,
            'counter': get_counter(request.user),
            'error': 'Ваша роль не имеет доступа к данному контенту'
        }
        return redirect('/dash/')
    else:
        order = Order.objects.get(id=order_id)

        context = get_user_info(request)
        # if order.responsible_preliminary == user_:
        #     user_profile = context['user_profile']
        #     user_role = user_profile.role.name
        #     categories = Category.objects.filter(pp=order.pp)
        context.update({
            'order': order,
            'counter': get_counter(request.user)

        })
        return render(request, 'dash/menu/statist/statist_documents_signed.html', context)
        # else:
        #     context.update({'error': "Заявка назначена на другого исполнителя"})
        #     return render(request, 'dash/dash_base.html', context)


#сохранение данных при получении подписанных документов
@login_required(redirect_field_name=None, login_url='/')
def save_data_documents_signed_statist(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        document_signed_received_date = data['signed_document_received_date']
        document_signed_received_date_split = document_signed_received_date.split('-')
        document_signed_received_date_ru = document_signed_received_date_split[2] + '.' + document_signed_received_date_split[1] + '.' + document_signed_received_date_split[0]
        response = {}
        counters_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_db.save()

        if order.lotki_status.name == 'Приостановка':
            order.lotki_preliminary_temp_stop_date_signed = document_signed_received_date

            lotki_db = LotkiTempStop.objects.filter(order=order).latest('date_received')
            lotki_db.date_signed = document_signed_received_date
            lotki_db.save()
            notification = NotificationTempStop()
            notification.notification_date = document_signed_received_date
            notification.order = order
            notification.save()
            notification_with_date_cnt = NotificationTempStop.objects.filter(notification_date=document_signed_received_date).count()
            document_signed_received_date_split = document_signed_received_date.split('-')
            notification_number = str(document_signed_received_date_split[2]) + str(document_signed_received_date_split[1]) + '/' + str(notification_with_date_cnt) + '-21-ПР'
            notification.notification_number = notification_number
            notification.user = request.user
            notification.save()
            temp_stop_db = TempStop()
            temp_stop_db.user = request.user
            temp_stop_db.notification = notification
            temp_stop_db.save()
            response['modalTitle'] = 'Данные уведомления о приостановке'
            statist_temp_stop_on_signing = counters_db.statist_temp_stop_on_signing - 1
            counters_db.statist_temp_stop_on_signing = statist_temp_stop_on_signing
            order.save()
            status_change_without_order_status(order,
                                               OrderStatus.objects.get(
                                                   name='Лотки (номер уведомления о приостановке присвоен)'),
                                               request.user)

        if order.lotki_status.name == 'Отказ' or order.lotki_status.name == 'Отказ после приостановки':
            if order.lotki_status.name == 'Отказ':
                order.lotki_preliminary_refuse_date_signed = document_signed_received_date
                order.refuse_is_preliminary = True
            else:
                order.lotki_after_temp_stop_refuse_date_signed = document_signed_received_date
                order.refuse_after_temp_stop = True
            lotki_db = LotkiRefuse.objects.filter(order=order).latest('date_received')
            lotki_db.date_signed = document_signed_received_date
            lotki_db.save()
            notification = NotificationRefuse()
            notification.notification_date = document_signed_received_date
            notification.order = order
            notification.user = request.user
            notification.save()
            notification_with_date_cnt = NotificationRefuse.objects.filter(notification_date=document_signed_received_date).count()
            document_signed_received_date_split = document_signed_received_date.split('-')
            notification_number = str(document_signed_received_date_split[2]) + str(document_signed_received_date_split[1]) + '/' + str(notification_with_date_cnt) + '-21-ОТ'
            notification.notification_number = notification_number
            notification.save()
            refuse_db = Refuse()
            status_change_without_order_status(order,
                                               OrderStatus.objects.get(
                                                   name='Лотки (номер уведомления об отказе присвоен)'),
                                               request.user)

            if order.lotki_status.name == 'Отказ':
                refuse_db.is_preliminary = True
            else:
                refuse_db.is_refuse_after_temp_stop = True
            refuse_db.user = request.user
            refuse_db.notification = notification
            refuse_db.save()
            response['modalTitle'] = 'Данные уведомления об отказе'

            statist_refuse_on_signing = counters_db.statist_refuse_on_signing - 1
            counters_db.statist_refuse_on_signing = statist_refuse_on_signing
            order.save()
        if order.lotki_status.name == 'ЭЗ' or order.lotki_status.name == 'ЭЗ после приостановки':
            order.lotki_ez_date_signed = document_signed_received_date
            order.save()
            ez_on_signing_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'),
                                                      lotki_ez_date_received__isnull=False, lotki_ez_date_signed__isnull=True).count()
            counters_db.statist_ez_on_signing = ez_on_signing_cnt
            status_change_without_order_status(order,
                                               OrderStatus.objects.get(
                                                   name='Лотки (подписанное ЭЗ получено)'),
                                               request.user)

        else:
            # print(notification_number)
            response['notificationNumber'] = notification_number
            response['notificationDate'] = document_signed_received_date_ru

        counters_db.save()

        return JsonResponse(response)


#nav_satist_boxes_refuses
@login_required(redirect_field_name=None, login_url='/')
def statist_refuse_orders_not_preliminary_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = ''
    if not user_profile.common_check_needed:
        status1 = OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)')
        status2 = OrderStatus.objects.get(name='Отказ по приостановке (по сроку_без загрузки в ИАС)')
        orders = Order.objects.filter(status=status1, lotki_after_temp_stop_refuse_date_received__isnull=True, lotki_after_temp_stop_refuse_date_signed__isnull=True) | \
                 Order.objects.filter(status=status2, lotki_after_temp_stop_refuse_date_received__isnull=True, lotki_after_temp_stop_refuse_date_signed__isnull=True)
        print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Список заявок на подпись (Отказ)',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_refuses_not_preliminary_list.html', context)


#.statist_order_refuse_not_preliminary
@login_required(redirect_field_name=None, login_url='/')
def statist_refuse_order_not_preliminary(request, order_id):
    user_ = request.user
    user_profile = get_user_info(request)['user_profile']
    # user_profile = context['user_profile']

    if user_profile.role.name != 'Статистика (лотки)':
        context = {
            'user_profile': user_profile,
            'counter': get_counter(request.user),
            'error': 'Ваша роль не имеет доступа к данному контенту'
        }
        return redirect('/dash/')
    else:
        order = Order.objects.get(id=order_id)
        notification_temp_stop_db = NotificationTempStop.objects.filter(order=order).latest('added')
        temp_stop_db = TempStop.objects.get(notification=notification_temp_stop_db)

        context = get_user_info(request)
        context.update({
            'order': order,
            'counter': get_counter(request.user),
            'temp_stop': temp_stop_db

        })
        return render(request, 'dash/menu/statist/statist_refuse_order_not_preliminary.html', context)


#сохранение данных при нажатии кнопки при первичном приеме документов
@login_required(redirect_field_name=None, login_url='/')
def save_data_refuse_order_not_preliminary_statist(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        document_received_date = data['documentReceivedDate']
        print(data)
        counters_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_db.save()

        document_EZ_date = data['documentCreatedDate']
        lotki_refuse = LotkiRefuse()
        lotki_refuse.user = request.user
        lotki_refuse.order = order
        lotki_refuse.date_received = document_received_date
        lotki_refuse.date_EZ = document_EZ_date
        lotki_refuse.save()
        order.lotki_after_temp_stop_refuse_date_received = document_received_date
        order.date_EZ = document_EZ_date
        counters_db.statist_refuse_on_signing = int(counters_db.statist_refuse_on_signing or 0) + 1
        counters_db.statist_refuses_not_preliminary = int(counters_db.statist_refuses_not_preliminary or 0) - 1

        order.lotki_status = LotkiContent.objects.get(name='Отказ после приостановки')
        lotki_status_change(order, 'Отказ после приостановки', request.user)
        order.save()

        counters_db.save()


        return HttpResponse('ok')


#nav_satist_boxes_refuses
@login_required(redirect_field_name=None, login_url='/')
def statist_ez_for_signing_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = ''
    if not user_profile.common_check_needed:
        status = OrderStatus.objects.get(name='Готово для подписи')
        orders = Order.objects.filter(status=status, lotki_ez_date_received__isnull=True, lotki_ez_date_signed__isnull=True)
        print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Список заявок на подпись (ЭЗ)',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_ez_for_singing_list.html', context)


#.statist_order_refuse_not_preliminary
@login_required(redirect_field_name=None, login_url='/')
def statist_ez_for_signing(request, order_id):
    user_ = request.user
    user_profile = get_user_info(request)['user_profile']
    # user_profile = context['user_profile']

    if user_profile.role.name != 'Статистика (лотки)':
        context = {
            'user_profile': user_profile,
            'counter': get_counter(request.user),
            'error': 'Ваша роль не имеет доступа к данному контенту'
        }
        return redirect('/dash/')
    else:
        order = Order.objects.get(id=order_id)
        ez_doc_db = EZdoc.objects.filter(order=order).latest('added')
        context = get_user_info(request)
        context.update({
            'order': order,
            'counter': get_counter(request.user),
            'ez_doc': ez_doc_db

        })
        return render(request, 'dash/menu/statist/statist_ez_for_singing.html', context)


#btn_add_conclusion_static_boxes
@login_required(redirect_field_name=None, login_url='/')
def save_data_ez_for_singing_statist(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        document_received_date = data['documentReceivedDate']
        print(data)
        counters_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_db.save()

        document_EZ_date = data['documentCreatedDate']

        lotki_ez_db = LotkiEZ()
        lotki_ez_db.user = request.user
        lotki_ez_db.order = order
        lotki_ez_db.date_received = document_received_date
        lotki_ez_db.date_EZ = document_EZ_date
        lotki_ez_db.save()

        ez_db = EZdoc.objects.filter(order=order).latest('added')
        ez_db.creation_date = document_EZ_date
        ez_db.save()

        order.lotki_ez_date_received = document_received_date
        order.date_EZ = document_EZ_date

        order.save()

        ez_on_signing_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'),
                                                 lotki_ez_date_received__isnull=False,
                                                 lotki_ez_date_signed__isnull=True).count()
        ez_for_signing_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'),
                                                  lotki_ez_date_received__isnull=True,
                                                  lotki_ez_date_signed__isnull=True).count()

        counters_db.statist_ez = ez_for_signing_cnt
        counters_db.statist_ez_on_signing = ez_on_signing_cnt
        if order.temp_stop is None:
            lotki_status_change(order, 'ЭЗ', request.user)
        else:
            lotki_status_change(order, 'ЭЗ после приостановки', request.user)

        counters_db.save()
        status_change_without_order_status(order,
                                           OrderStatus.objects.get(name='Лотки (ЭЗ на подпись после возобновления получено)'),
                                           request.user)
        return HttpResponse('ok')


#nav_satist_boxes_for_signing_conclusion
@login_required(redirect_field_name=None, login_url='/')
def statist_ez_on_signing_list(request):
    user_ = request.user
    context = get_user_info(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = ''
    if not user_profile.common_check_needed:
        status = OrderStatus.objects.get(name='Готово для подписи')
        orders = Order.objects.filter(status=status, lotki_ez_date_received__isnull=False, lotki_ez_date_signed__isnull=True)
        print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Список заявок на подписи (ЭЗ)',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/statist/statist_ez_on_singing_list.html', context)


#prelimenaryCheck_new_order
@login_required(redirect_field_name=None, login_url='/')
def statist_ez_singed(request, order_id):
    print('temp_stop_docs_singed')
    user_ = request.user
    user_profile = get_user_info(request)['user_profile']
    # user_profile = context['user_profile']

    if user_profile.role.name != 'Статистика (лотки)':
        context = {
            'user_profile': user_profile,
            'counter': get_counter(request.user),
            'error': 'Ваша роль не имеет доступа к данному контенту'
        }
        return redirect('/dash/')
    else:
        order = Order.objects.get(id=order_id)

        context = get_user_info(request)
        # if order.responsible_preliminary == user_:
        #     user_profile = context['user_profile']
        #     user_role = user_profile.role.name
        #     categories = Category.objects.filter(pp=order.pp)
        context.update({
            'order': order,
            'counter': get_counter(request.user)

        })


        return render(request, 'dash/menu/statist/statist_ez_signed.html', context)
        # else:
        #     context.update({'error': "Заявка назначена на другого исполнителя"})
        #     return render(request, 'dash/dash_base.html', context)
