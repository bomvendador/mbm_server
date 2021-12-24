# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.apps import apps
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Order, OrderStatus, Applier, PPnumber, ResponsibleForOrderPreliminary, \
    ResponsibleForOrderAfterTempStop, \
    Category, CategoriesByOrder, StatusChange, NotificationRefuse, NotificationTempStop, RefuseReasonsPreliminary, \
    RefuseReasonsAfterTempStop, \
    RefuseReasonsPreliminaryByOrders, Refuse, TempStop, Counters, TempStopFiles, AfterTempStopDecision, \
    RefuseReasonsAfterTempStopByOrders, RefuseFiles, LotkiContent, CountersLotki, EZdoc, EZpdf, OrderTypeCheck, \
    CheckPreliminary, CheckPreliminaryFileToCheck, CountersAdmin, CheckPreliminaryFileToCheckFinal, \
    CheckPreliminaryFileToCheckReturned, CheckAfterTempStopFileToCheck, CheckAfterTempStop, \
    CheckAfterTempStopFileToCheckReturned, CheckAfterTempStopFileToCheckFinal, ReadyForOK
from django.contrib.auth.models import User
from .views import date_to_db, get_counter, status_change, check_order, dash_get_info, set_order_status, \
    status_change_without_order_status
from .counters import counters
from django.core import serializers
# from dash.views import dash_get_info

from django.core.files.storage import FileSystemStorage
from datetime import datetime

import json
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

userprofile = apps.get_model('login', 'UserProfile')


@login_required(redirect_field_name=None, login_url='/')
def get_info_responsible(request):
    context = dash_get_info(request)
    counters_ = counters(request)
    context.update({
        'counters': counters_
    })
    return context


@login_required(redirect_field_name=None, login_url='/')
def check_if_user_appointed_for_order(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        print('id = ' + data['order_id'])
        order = Order.objects.get(id=data['order_id'])
        if (order.responsible_preliminary == user_ or order.responsible_preliminary_check_expert == user_) \
            or (not order.temp_stop and order.responsible_after_temp_stop or order.responsible_after_temp_stop_check_expert == user_):
            return HttpResponse('ok')
        else:
            return HttpResponse('deny')


# nav_new_orders_list_expert
@login_required(redirect_field_name=None, login_url='/')
def new_orders_ready_to_proceed_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    new_orders = ''
    # if not user_profile.common_check_needed:
        # new_orders = Order.objects.filter(
        #     status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке'),
        #     responsible_preliminary=user_)
    new_orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                                              Q(responsible_preliminary=user_) &
                                 ((

                                      ((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(
                                     check_preliminary_temp_stop=True)) &
                                       (Q(check_preliminary_files_for_check_uploaded=True) & Q(
                                             check_preliminary_finals_files_uploaded=True))) |

                                   (Q(check_preliminary_refuse=False) & Q(check_preliminary_ez=False) & Q(
                                       check_preliminary_temp_stop=False))) |

                                  Q(check_preliminary_pass_without_check=True)))

    print(new_orders)

    context.update({
        'new_orders': new_orders,
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/new_orders_ready_to_proceed_list.html', context)


# prelimenaryCheck_new_order
@login_required(redirect_field_name=None, login_url='/')
def order_ready_to_proceed(request, order_id):
    print('order_ready_to_proceed')
    user_ = request.user
    order = Order.objects.get(id=order_id)
    context = get_info_responsible(request)
    context.update({'counter': get_counter(request.user)})
    if order.responsible_preliminary == user_:
        if order.status.name != 'Регистрация/На предварительной проверке':
            error = "Заявка находится в другом статусе - " + order.status.name
            context.update({
                'error': error,
                'modal_error_title': 'Ошибка при загрузке'
            })
            # return redirect('/dash/')
            return render(request, 'dash/dash_base.html', context)
        else:
            user_profile = context['user_profile']
            user_role = user_profile.role.name
            categories = Category.objects.filter(pp=order.pp)
            if order.lotki_status is not None:
                if order.lotki_preliminary_temp_stop_date_received is not None and order.lotki_preliminary_temp_stop_date_signed is not None:
                    if order.lotki_status.name == 'Приостановка':
                        notification = NotificationTempStop.objects.filter(order=order).latest('added')
                        context.update({
                            'notification': notification
                        })
                if order.lotki_after_temp_stop_refuse_date_received is not None and order.lotki_after_temp_stop_refuse_date_signed is not None:
                    if order.lotki_status.name == 'Отказ':
                        notification = NotificationRefuse.objects.filter(order=order).latest('added')
                        refuse_reasons = RefuseReasonsPreliminary.objects.filter(pp=order.pp)
                        refuse_reasons_common = RefuseReasonsPreliminary.objects.filter(common_reason=True)

                        context.update({
                            'notification': notification,
                            'refuse_reasons': refuse_reasons,
                            'refuse_reasons_common': refuse_reasons_common
                        })
            show_categories = order.lotki_status is None and order.lotki_preliminary_temp_stop_date_received is None and order.lotki_preliminary_temp_stop_date_signed is None and order.lotki_preliminary_refuse_date_received is None and order.lotki_preliminary_refuse_date_signed is None or \
                              order.lotki_status is not None and order.lotki_preliminary_temp_stop_date_received != None and order.lotki_preliminary_temp_stop_date_signed != None or \
                              order.lotki_status is not None and order.lotki_preliminary_refuse_date_received != None and order.lotki_preliminary_refuse_date_signed != None
            print('show_categories = ' + str(show_categories))
            try:
                check_preliminary_file_to_check_final = CheckPreliminaryFileToCheckFinal.objects.filter(
                    check_preliminary_file_to_check=CheckPreliminaryFileToCheck.objects.filter(
                        check_preliminary=CheckPreliminary.objects.filter(order=order).latest('added')).latest(
                        'added')).latest('added')
            except CheckPreliminaryFileToCheckFinal.DoesNotExist:
                check_preliminary_file_to_check_final = None

            context.update({
                'order': order,
                'categories': categories,
                'show_categories': show_categories,
                'check_preliminary_file_to_check_final': check_preliminary_file_to_check_final
            })
            return render(request, 'dash/menu/responsible/order_ready_to_proceed.html', context)
    else:
        error = "Заявка назначена на другого исполнителя"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке'
        })
        # return redirect('/dash/')
        return render(request, 'dash/dash_base.html', context)


# получение списка категорий
@login_required(redirect_field_name=None, login_url='/')
def get_categories_list(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['order_id'])
        response = CategoriesByOrder.objects.filter(category=Category.objects.get(pp=order.pp)).only('name')
        res = serializers.serialize('json', response)
        return HttpResponse(res, 'application/json')


# сохранение данных при нажатии кнопки при первичном отказе
@login_required(redirect_field_name=None, login_url='/')
def save_data_preliminary_check(request):
    if request.method == 'POST':
        data = request.POST
        comments = data.get('comments')
        print(data)
        pp741 = False
        order = Order.objects.get(id=data['orderID'])
        btn_id = data['btnID']
        if order.pp.name != '741-ПП':
            pp741 = True
        # if pp741:
        category_arr = json.loads(data.get('categoryArr'))
        # else:
        #     category_arr = data['categoryArr[]']

        choose_equipment_compensation = data.get('choose_equipment_compensation')

        # print(btn_id)
        print(category_arr)
        # print(choose_equipment_compensation)

        if category_arr:
            # if pp741:
            for category in category_arr:
                print(category)
                category_db = CategoriesByOrder()
                category_db.user = request.user
                category_db.category = Category.objects.get(name=category[0])
                category_db.name = category[1]
                category_db.order = order
                category_db.save()
                order.category = Category.objects.get(name=category[0])
            # else:
            #    category_db = CategoriesByOrder()
            #    category_db.user = request.user
            #    category_db.category = Category.objects.get(name=category_arr)
            #    category_db.name = 'Без названия'
            #    category_db.order = order
            #    category_db.save()


        counters_db, created = Counters.objects.get_or_create(user=request.user)
        if created:
            counters_db.save()

        if btn_id == 'btnPrelimenaryCheckSuccess':
            order.status = OrderStatus.objects.get(name='В работе')
            order.lotki_status = LotkiContent.objects.get(name='ЭЗ')
            order.save()
            if choose_equipment_compensation == 'Да':
                order.onsite_check = True
            else:
                order.onsite_check = False
            order.save()
            new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке'), \
                    responsible_preliminary=request.user).count()
            ez_doc_preliminary = Order.objects.filter(status=OrderStatus.objects.get(name='В работе'), \
                    responsible_after_temp_stop=request.user).count()
            ez_doc_after_temp_stop = Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), \
                    responsible_after_temp_stop=request.user).count()
            counters_db.new_orders = new_orders
            counters_db.ez_doc = ez_doc_preliminary + ez_doc_after_temp_stop

        if btn_id == 'btnPrelimenaryCheckTempStop':
            order.status = OrderStatus.objects.get(name='Приостановлено (без даты приостановки)')
            temp_stop_db = TempStop.objects.get(
                notification=NotificationTempStop.objects.filter(order=order).latest('added'))
            temp_stop_db.description = comments
            temp_stop_db.user = request.user
            temp_stop_db.save()
            if choose_equipment_compensation == 'Да':
                order.onsite_check = True
            else:
                order.onsite_check = False
            order.save()
            temp_stop_date = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (без даты приостановки)'), \
                    responsible_preliminary=request.user).count()
            counters_db.temp_stop_date = temp_stop_date

        if btn_id == 'btnPrelimenaryCheckRefuse':
            refuse_reasons_arr = json.loads(data.get('refuse_reasons_arr'))
            order.status = OrderStatus.objects.get(name='Отказ первичный (без загрузки в ИАС)')
            for refuse_reason in refuse_reasons_arr:
                refuse_reason_by_orders_db = RefuseReasonsPreliminaryByOrders()
                refuse_reason_by_orders_db.user = request.user
                refuse_reason_by_orders_db.order = order
                refuse_reason_by_orders_db.refuse_reason = RefuseReasonsPreliminary.objects.get(id=refuse_reason)
                refuse_reason_by_orders_db.save()
                refuse_db = Refuse.objects.get(
                    notification=NotificationRefuse.objects.filter(order=order).latest('added'))
                refuse_db.description = comments
                refuse_db.save()
            order.save()
            refuse_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ первичный (без загрузки в ИАС)'), \
                responsible_preliminary=request.user).count()
            counters_db.refuse_preliminary = refuse_cnt
            print(refuse_reason)

        new_orders = Order.objects.filter(
            Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
            Q(responsible_preliminary=request.user) &
            ((

                     ((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(
                         check_preliminary_temp_stop=True)) &
                      (Q(check_preliminary_files_for_check_uploaded=True) & Q(
                          check_preliminary_finals_files_uploaded=True))) |

                     (Q(check_preliminary_refuse=False) & Q(check_preliminary_ez=False) & Q(
                         check_preliminary_temp_stop=False))) |

             Q(check_preliminary_pass_without_check=True))).count()

        # new_orders = Order.objects.filter(
        #     Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
        #     (((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True))
        #       & (Q(check_preliminary_files_for_check_uploaded=True) & Q(
        #                 check_preliminary_finals_files_uploaded=True))) |
        #      (Q(check_preliminary_refuse=False) | Q(check_preliminary_ez=False) | Q(
        #          check_preliminary_temp_stop=False)))).count()
        counters_db.new_orders = new_orders

        status_change(request.user, order)

        counters_db.save()

        return HttpResponse('ok')


# nav_orders_temp_stop_stop_date
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_date_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (без даты приостановки)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Необходимое действие по заявкам: сохранение даты приостановки',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_date_list.html', context)


# order-temp-stop-no-notification-date
@login_required(redirect_field_name=None, login_url='/')
def order_temp_stop_date(request, order_id):
    user_ = request.user
    order = Order.objects.get(id=order_id)
    context = get_info_responsible(request)

    if order.responsible_preliminary == user_:
        if order.status.name != 'Приостановлено (без даты приостановки)':
            error = "Заявка находится в другом статусе - " + order.status.name
            context.update({
                'error': error,
                'modal_error_title': 'Ошибка при загрузке',
                'counter': get_counter(request.user)
            })
            return render(request, 'dash/dash_base.html', context)
        else:
            user_profile = context['user_profile']
            user_role = user_profile.role.name
            context.update({
                'order': order,
                'counter': get_counter(request.user)
            })
            return render(request, 'dash/menu/responsible/temp_stop_date.html', context)
    else:
        error = "Заявка назначена на другого исполнителя"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(request.user)
        })
        return render(request, 'dash/dash_base.html', context)


# сохранение даты приостановки
@login_required(redirect_field_name=None, login_url='/')
def save_temp_stop_date(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)
        temp_stop_date = date_to_db(data['tempStopDate'])
        end_date_for_notification = date_to_db(data['endDateForNotification'])
        notification_temp_stop_db = NotificationTempStop.objects.filter(order=order).latest('added')
        temp_stop_db = TempStop.objects.get(notification=notification_temp_stop_db)
        temp_stop_db.date_IAS = temp_stop_date
        temp_stop_db.end_date_for_notification = end_date_for_notification
        temp_stop_db.save()

        order.status = OrderStatus.objects.get(name='Приостановлено (уведомление не отправлено)')
        order.save()

        set_order_status(order, 'Приостановлено (уведомление не отправлено)', request.user)

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()
        counters_db.temp_stop_without_notification = int(counters_db.temp_stop_without_notification or 0) + 1
        counters_db.temp_stop_date = int(counters_db.temp_stop_date or 0) - 1

        counters_db.save()
        return HttpResponse('ok')


# nav_orders_temp_stop_stop_date
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_without_notification_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (уведомление не отправлено)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (уведомление не отправлено)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_without_notification_list.html', context)


# order-temp-stop-no-notification
@login_required(redirect_field_name=None, login_url='/')
def order_without_notification(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)

    check_order_bool = check_order('Приостановлено (уведомление не отправлено)', order_id, user_, request)
    print('check_order_bool = ' + str(check_order_bool))

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)
        context.update({
            'counter': get_counter(user_),
            'temp_stop': TempStop.objects.get(notification=NotificationTempStop.objects.filter(order=order).latest('added')),
            'order': order,
            'notification': NotificationTempStop.objects.filter(order=order).latest('added')
        })
        return render(request, 'dash/menu/responsible/order_temp_stop_without_notification.html', context)
    else:
        return check_order_bool

    # if order.responsible_preliminary == user_:
    #     if order.status.name != 'Приостановлено (уведомление не отправлено)':
    #         error = "Заявка находится в другом статусе - " + order.status.name
    #         context.update({
    #             'error': error,
    #             'modal_error_title': 'Ошибка при загрузке',
    #             'counter': get_counter(request.user)
    #                         })
    #         return render(request, 'dash/dash_base.html', context)
    #     else:
    #         context.update({
    #             'order': order,
    #             'counter': get_counter(request.user)
    #         })
    #         return render(request, 'dash/menu/responsible/order_temp_stop_without_notification.html', context)
    # else:
    #     error = "Заявка назначена на другого исполнителя"
    #     context.update({
    #         'error': error,
    #         'modal_error_title': 'Ошибка при загрузке',
    #         'counter': get_counter(request.user)
    #     })
    #     return render(request, 'dash/dash_base.html', context)


# nav_orders_temp_stop_with_notification_sent_for_check
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_with_notification_sent_for_check_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    user_profile = context['user_profile']
    user_role = user_profile.role.name
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (принятие решение по доработке (на проверке))',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_with_notification_sent_for_check_list.html', context)


# order-temp-stop-no-notification
@login_required(redirect_field_name=None, login_url='/')
def save_pez_notification(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        applier = Applier.objects.get(order=order)
        context = get_info_responsible(request)
        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.pdf'
        print(date_for_name)
        temp_stop_db = TempStop.objects.get(notification=NotificationTempStop.objects.filter(order=order).latest('added'))
        temp_stop_files_db = TempStopFiles(temp_stop=temp_stop_db)

        file_pez = request.FILES['pez']
        file_notification = request.FILES['notification']
        notification_sent_date = data['notification_date']
        end_date_for_additional_docs_by_applier = data['end_date_for_additional_docs_by_applier']
        temp_stop_db.notification_sent_date = date_to_db(notification_sent_date)
        temp_stop_db.end_date_for_remade_order = date_to_db(end_date_for_additional_docs_by_applier)

        pez_name = u'ПЭ_(приостановка)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(pez_name, file_pez)
        temp_stop_files_db.file_pez = pez_name

        notification_name = u'УВ_(приостановка)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(notification_name, file_notification)
        temp_stop_files_db.file_notification = notification_name
        temp_stop_files_db.user = request.user
        temp_stop_files_db.save()

        print(temp_stop_files_db.file_pez.path)
        print(temp_stop_files_db.file_notification.path)
        user_profile = context['user_profile']
        user_role_name = user_profile.role.name

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()
        counters_db.temp_stop_without_notification = int(counters_db.temp_stop_without_notification or 0) - 1
        if user_role_name == 'Эксперт подрядчика':
            counters_db.temp_stop_with_notification = int(counters_db.temp_stop_with_notification or 0) + 1
            set_order_status(order, 'Приостановлено (уведомление отправлено)', request.user)

        else:
            counters_db.temp_stop_remade_order_date = int(counters_db.temp_stop_remade_order_date or 0) + 1
            set_order_status(order, 'Приостановлено (дата доработки)', request.user)

        counters_db.save()
        temp_stop_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_remade_order_date_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (уведомление отправлено)'))).count()
        counters_admin_db.admin_remade_order_date = admin_remade_order_date_cnt
        counters_admin_db.save()

        order.temp_stop = True
        order.temp_stop_date = date_to_db(notification_sent_date)
        order.save()

        return HttpResponse('')


# nav_orders_temp_stop_remadeorder_date
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_with_notification_before_remade_date_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (уведомление отправлено)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (уведомление отправлено)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_with_notification_before_remade_date_list.html', context)


# nav_orders_temp_stop_remadeorder_date
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_remadeorder_date_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (дата доработки)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (дата доработки)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_remadeorder_list.html', context)


# order-temp-stop-remadeorder-date
@login_required(redirect_field_name=None, login_url='/')
def order_temp_stop_remadeorder_date(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)

    check_order_bool = check_order('Приостановлено (дата доработки)', order_id, user_, request)

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)

        context.update({
            'counter': get_counter(user_),
            'temp_stop': TempStop.objects.get(notification=NotificationTempStop.objects.filter(order=order).latest('added')),
            'order': order,
            'notification': NotificationTempStop.objects.filter(order=order).latest('added')
        })
        return render(request, 'dash/menu/responsible/temp_stop_remade_order_date.html', context)
    else:
        return check_order_bool


# сохранение даты получения доработатной заявки btn_add_prelimenary_remadeorder_date
@login_required(redirect_field_name=None, login_url='/')
def save_temp_stop_remadeorder_date(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST

        remadeorderDate = date_to_db(data['remadeorderDate'])
        endDateForConclusionDocs = date_to_db(data['endDateForConclusionDocs'])
        endDateForConclusionRespincible = date_to_db(data['endDateForConclusionRespincible'])

        order = Order.objects.get(id=data['orderID'])
        order.temp_stop = False
        order.remade_order_received_date = remadeorderDate
        order.save()


        notification_temp_stop_db = NotificationTempStop.objects.filter(order=order).latest('added')
        temp_stop_db = TempStop.objects.get(notification=notification_temp_stop_db)
        temp_stop_db.remade_order_received_date = remadeorderDate
        temp_stop_db.end_date_after_temp_stop = endDateForConclusionDocs
        temp_stop_db.end_date_after_temp_stop_for_responsible = endDateForConclusionRespincible
        temp_stop_db.save()

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()

        if order.check_after_temp_stop_refuse or order.check_after_temp_stop_ez:
            set_order_status(order, 'Приостановлено (принятие решение по доработке (проверка))', request.user)
            temp_stop_remade_order_date_send_for_check = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (проверка))')) &
                                         Q(responsible_after_temp_stop=user_) &
                                              ((Q(check_after_temp_stop_files_for_check_uploaded=False) & Q(check_after_temp_stop_files_for_check_returned_by_expert=False)) |
                                               (Q(check_after_temp_stop_files_for_check_uploaded=False) & Q(check_after_temp_stop_files_for_check_returned_by_expert=True)))).count()
            counters_db.temp_stop_check = temp_stop_remade_order_date_send_for_check

        else:
            set_order_status(order, 'Приостановлено (принятие решения по доработке)', request.user)

            temp_stop_remade_order_decision = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)'), \
                                      responsible_after_temp_stop=user_).count()
            counters_db.temp_stop_remade_order_decision = temp_stop_remade_order_decision

        temp_stop_remade_order_date = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (дата доработки)'), \
                                  responsible_after_temp_stop=user_).count()
        counters_db.temp_stop_remade_order_date = temp_stop_remade_order_date

        counters_db.save()
        return HttpResponse('ok')


# nav_orders_temp_stop_remadeorder_date
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_remade_order_decision_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)'), \
                                  responsible_after_temp_stop=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (принятие решения по доработке)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_remade_order_decision_list.html', context)


# order-temp-stop-remadeorder-date
@login_required(redirect_field_name=None, login_url='/')
def order_temp_stop_remade_order_decision(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)

    check_order_bool = check_order('Приостановлено (принятие решения по доработке)', order_id, user_, request)

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)

        refuse_reasons = RefuseReasonsAfterTempStop.objects.filter(pp=order.pp)
        refuse_reasons_common = RefuseReasonsAfterTempStop.objects.filter(common_reason=True)
        try:
            check_after_temp_stop = CheckAfterTempStop.objects.filter(order=order).latest('added')
            check_after_temp_stop_file_to_check = CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop=check_after_temp_stop).latest('added')
        except CheckAfterTempStop.DoesNotExist:
            check_after_temp_stop = None
            check_after_temp_stop_file_to_check = None
        try:
            check_after_temp_stop_file_to_check_final = CheckAfterTempStopFileToCheckFinal.objects.filter(check_after_temp_stop_file_to_check=check_after_temp_stop_file_to_check).latest('added')
        except CheckAfterTempStopFileToCheckFinal.DoesNotExist:
            check_after_temp_stop_file_to_check_final = None
        # check_after_temp_stop_file_to_check = CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop=check_after_temp_stop).latest('added')
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'refuse_reasons': refuse_reasons,
            'refuse_reasons_common': refuse_reasons_common,
            'check_after_temp_stop_file_to_check_final': check_after_temp_stop_file_to_check_final,
            'check_after_temp_stop_file_to_check': check_after_temp_stop_file_to_check
        })
        return render(request, 'dash/menu/responsible/order_temp_stop_remade_order_decision.html', context)
    else:
        return check_order_bool


# сохранение пешения после возобновления
@login_required(redirect_field_name=None, login_url='/')
def save_temp_stop_remade_order_decision(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])

        remadeOrderDocumentsComments = data['remadeOrderDocumentsComments']
        btnID = data['btnID']

        after_temp_stop_decision_db = AfterTempStopDecision()
        after_temp_stop_decision_db.user = request.user
        after_temp_stop_decision_db.description = remadeOrderDocumentsComments
        after_temp_stop_decision_db.order = order
        after_temp_stop_decision_db.save()

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()
        counters_lotki_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_lotki_db.save()

        if btnID == 'btnRemadeOrderOK':
            set_order_status(order, 'В работе после приостановления', request.user)
            ez_doc_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), \
                                      responsible_preliminary=user_).count()
            temp_stop_remade_order_decision = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)'), \
                                  responsible_preliminary=user_).count()
            counters_db.temp_stop_remade_order_decision = temp_stop_remade_order_decision
            counters_db.ez_doc = ez_doc_cnt
            order.lotki_status = LotkiContent.objects.get(name='ЭЗ после приостановки')
            ez_doc_preliminary = Order.objects.filter(status=OrderStatus.objects.get(name='В работе'), \
                    responsible_after_temp_stop=request.user).count()
            ez_doc_after_temp_stop = Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), \
                    responsible_after_temp_stop=request.user).count()
            counters_db.ez_doc = ez_doc_preliminary + ez_doc_after_temp_stop
        if btnID == 'btnRemadeOrderRefuseNoDocs':
            refuse_reasons_arr = json.loads(data.get('refuse_reasons_arr'))

            set_order_status(order, 'Отказ по приостановке (по документам_без загрузки в ИАС)', request.user)
            refuse_by_docs = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)'), \
                                      responsible_preliminary=user_).count()
            temp_stop_remade_order_decision = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)'), \
                                  responsible_preliminary=user_).count()
            counters_db.temp_stop_remade_order_decision = temp_stop_remade_order_decision
            counters_db.refuse_by_docs = refuse_by_docs
            for refuse_reason in refuse_reasons_arr:
                refuse_reason_by_orders_db = RefuseReasonsAfterTempStopByOrders()
                refuse_reason_by_orders_db.user = request.user
                refuse_reason_by_orders_db.order = order
                refuse_reason_by_orders_db.refuse_reason = RefuseReasonsAfterTempStop.objects.get(id=refuse_reason)
                refuse_reason_by_orders_db.save()

                print(refuse_reason)
            refuse_after_temp_stop_statist = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)'),
                        lotki_after_temp_stop_refuse_date_received__isnull=True, lotki_after_temp_stop_refuse_date_signed__isnull=True).count()
            print('refuse_preliminary_statist' + str(refuse_after_temp_stop_statist))
            counters_lotki_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
            if created:
                counters_lotki_db.save()
            counters_lotki_db.statist_refuses_not_preliminary = refuse_after_temp_stop_statist
            order.lotki_status = LotkiContent.objects.get(name='Отказ после приостановки')
        order.save()
        counters_db.save()
        counters_lotki_db.save()
        return HttpResponse('ok')


# nav_refuse_prelimenary
@login_required(redirect_field_name=None, login_url='/')
def orders_refuse_preliminary_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ первичный (без загрузки в ИАС)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Отказ первичный (без загрузки в ИАС)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_refuse_preliminary_list.html', context)


# order-temp-stop-remadeorder-date
@login_required(redirect_field_name=None, login_url='/')
def order_refuse_preliminary(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Отказ первичный (без загрузки в ИАС)', order_id, user_, request)

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)

        context.update({
            'refuse': Refuse.objects.get(notification=NotificationRefuse.objects.filter(order=order).latest('added')),
            'notification': NotificationRefuse.objects.filter(order=order).latest('added'),
            'counter': get_counter(user_),
            'order': order,

        })
        return render(request, 'dash/menu/responsible/order_refuse_preliminary.html', context)
    else:
        return check_order_bool


# order-temp-stop-no-notification
@login_required(redirect_field_name=None, login_url='/')
def save_order_refuse_preliminary(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.pdf'
        print(date_for_name)
        refuse_db = Refuse.objects.get(notification=NotificationRefuse.objects.filter(order=order).latest('added'))
        refuse_files_db = RefuseFiles(refuse=refuse_db)

        file_ez = request.FILES['ez']
        file_notification = request.FILES['notification']
        notification_sent_date = data['notification_date']
        refuse_db.date_IAS = date_to_db(notification_sent_date)

        ez_name = u'ЭЗ_(первичный отказ)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(ez_name, file_ez)
        refuse_files_db.file_ez = ez_name

        notification_name = u'УВ_(первичный отказ)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(notification_name, file_notification)
        refuse_files_db.file_notification = notification_name

        refuse_files_db.save()

        print(refuse_files_db.file_ez.path)
        print(refuse_files_db.file_notification.path)
        user_profile = context['user_profile']
        user_role_name = user_profile.role.name

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()
        set_order_status(order, 'Отказ первичный (с загрузкой в ИАС)', request.user)
        refuse_preliminary = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ первичный (без загрузки в ИАС)'), \
                responsible_preliminary=request.user).count()
        counters_db.refuse_preliminary = refuse_preliminary

        counters_db.save()
        refuse_db.save()

        return HttpResponse('')


# nav_refuse_remade_order
@login_required(redirect_field_name=None, login_url='/')
def orders_refuse_remade_order_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Отказ по приостановке (по документам_без загрузки в ИАС)',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_refuse_remade_order_list.html', context)


# order-temp-stop-remadeorder-date
@login_required(redirect_field_name=None, login_url='/')
def order_refuse_remade_order(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Отказ по приостановке (по документам_без загрузки в ИАС)', order_id, user_, request)

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)
        try:
            notification = NotificationRefuse.objects.filter(order=order).latest('added')
            refuse = Refuse.objects.get(notification=notification)
        except NotificationRefuse.DoesNotExist:
            notification = None
            refuse = None

        # try:
        #     refuse = Refuse.objects.get(notification=notification)
        # except Refuse.DoesNotExist:
        #     refuse = None
        try:
            notification_temp_stop = NotificationTempStop.objects.filter(order=order).latest('added')
            temp_stop = TempStop.objects.get(notification=notification_temp_stop)

        except NotificationTempStop.DoesNotExist:
            temp_stop = None

        # try:
        #     temp_stop = TempStop.objects.get(notification=notification_temp_stop)
        # except Refuse.DoesNotExist:
        #     refuse = None
        context.update({
            'refuse': refuse,
            'notification': notification,
            'counter': get_counter(user_),
            'order': order,
            'temp_stop': temp_stop

        })
        return render(request, 'dash/menu/responsible/order_refuse_remade_order.html', context)
    else:
        return check_order_bool


# order-temp-stop-no-notification
@login_required(redirect_field_name=None, login_url='/')
def save_remade_order_refuse(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.pdf'
        print(date_for_name)
        refuse_db = Refuse.objects.get(notification=NotificationRefuse.objects.filter(order=order).latest('added'))
        refuse_files_db = RefuseFiles(refuse=refuse_db)

        file_ez = request.FILES['ez']
        file_notification = request.FILES['notification']
        notification_sent_date = data['notification_date']
        refuse_comments = data['refuse_comments']
        refuse_db.notification_sent_date = date_to_db(notification_sent_date)
        refuse_db.description = refuse_comments

        ez_name = u'ЭЗ_(отказ после приостановки)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(ez_name, file_ez)
        refuse_files_db.file_ez = ez_name

        notification_name = u'УВ_(отказ после приостановки)_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(notification_name, file_notification)
        refuse_files_db.file_notification = notification_name

        refuse_files_db.user = request.user
        refuse_files_db.save()

        print(refuse_files_db.file_ez.path)
        print(refuse_files_db.file_notification.path)
        user_profile = context['user_profile']
        user_role_name = user_profile.role.name

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()
        set_order_status(order, 'Отказ по приостановке (по документам_с загрузкой в ИАС)', request.user)
        refuse_after_temp_stop = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ по приостановке (по документам_без загрузки в ИАС)'), \
                responsible_after_temp_stop=request.user).count()
        counters_db.refuse_by_docs = refuse_after_temp_stop

        counters_db.save()
        refuse_db.save()

        return HttpResponse('')


# nav_add_conclusion
@login_required(redirect_field_name=None, login_url='/')
def orders_ez_doc_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='В работе'), responsible_after_temp_stop=user_) | \
            Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), responsible_after_temp_stop=user_)

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Добавление экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_add_ez_doc_list.html', context)


# order-add-ez-doc
@login_required(redirect_field_name=None, login_url='/')
def order_ez_doc(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool1 = check_order('В работе', order_id, user_, request)
    check_order_bool2 = check_order('В работе после приостановления', order_id, user_, request)
    print('------------')
    print(check_order_bool1)
    print(check_order_bool2)
    print('------------')

    if check_order_bool1 is True or check_order_bool2 is True:
        order = Order.objects.get(id=order_id)
        try:
            ez_doc = EZdoc.objects.filter(order=order).latest('added')
        except EZdoc.DoesNotExist:
            ez_doc = None
        try:
            notification_temp_stop = NotificationTempStop.objects.filter(order=order).latest('added')
            temp_stop = TempStop.objects.get(notification=notification_temp_stop)

        except NotificationTempStop.DoesNotExist:
            temp_stop = None

        context.update({
            'counter': get_counter(user_),
            'order': order,
            'ez_doc': ez_doc,
            'temp_stop': temp_stop

        })
        return render(request, 'dash/menu/responsible/order_ez_doc.html', context)
    else:
        return check_order_bool1


# add_conclusion
@login_required(redirect_field_name=None, login_url='/')
def save_ez_doc(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.doc'
        print(date_for_name)

        file_ez = request.FILES['ezFile']
        ez_creation_date = data['dateCreated']
        conclusion_decision = data['conclusionDecision']
        max_sum = data['maxSum']
        if order.temp_stop is not None:
            ez_name = u'ЭЗ_(после приостановки)_' + file_name.replace(' ', '')
        else:
            ez_name = u'ЭЗ_(первичное)_' + file_name.replace(' ', '')

        ez_db = EZdoc()
        fs = FileSystemStorage()
        fs.save(ez_name, file_ez)
        ez_db.file = ez_name
        ez_db.user = request.user
        ez_db.creation_date = date_to_db(ez_creation_date)
        ez_db.max_sum = max_sum.replace(',', '.')
        if conclusion_decision == 'Положительное':
            ez_db.decision = True
        else:
            ez_db.decision = False
        ez_db.order = order
        ez_db.signed_bool = False

        ez_db.save()

        print(ez_db.file.path)
        user_profile = context['user_profile']

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()

        set_order_status(order, 'Готово для подписи', request.user)

        ez_doc1_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='В работе'), responsible_after_temp_stop=user_).count()
        ez_doc2_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), responsible_after_temp_stop=user_).count()
        ez_pdf_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'), responsible_after_temp_stop=user_).count()
        counters_db.ez_doc = ez_doc1_cnt + ez_doc2_cnt
        counters_db.ez_pdf = ez_pdf_cnt

        counters_db.save()

        counters_lotki_db, created = CountersLotki.objects.get_or_create(user_role_name='Статистика (лотки)')
        if created:
            counters_lotki_db.save()

        ez_pdf_lotki_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'), lotki_ez_date_received__isnull=True).count()
        counters_lotki_db.statist_ez = ez_pdf_lotki_cnt
        counters_lotki_db.save()
        return HttpResponse('')


# nav_add_conclusion
@login_required(redirect_field_name=None, login_url='/')
def orders_ez_pdf_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'), responsible_after_temp_stop=user_)

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Добавление подписанного экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_add_ez_pdf_list.html', context)


# order-add-ez-doc
@login_required(redirect_field_name=None, login_url='/')
def order_ez_pdf(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Готово для подписи', order_id, user_, request)

    if check_order_bool is True:
        order = Order.objects.get(id=order_id)
        try:
            ez_doc = EZdoc.objects.filter(order=order).latest('added')
        except EZdoc.DoesNotExist:
            ez_doc = None
        try:
            notification_temp_stop = NotificationTempStop.objects.filter(order=order).latest('added')
            temp_stop = TempStop.objects.get(notification=notification_temp_stop)

        except NotificationTempStop.DoesNotExist:
            temp_stop = None

        context.update({
            'counter': get_counter(user_),
            'order': order,
            'ez_doc': ez_doc,
            'temp_stop': temp_stop

        })
        return render(request, 'dash/menu/responsible/order_ez_pdf.html', context)
    else:
        return check_order_bool


# add_conclusion_pdf
@login_required(redirect_field_name=None, login_url='/')
def save_ez_pdf(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.pdf'
        print(date_for_name)

        file_ez = request.FILES['ezFile']
        if order.temp_stop is not None:
            ez_name = u'ЭЗ_(после приостановки)_' + file_name.replace(' ', '')
        else:
            ez_name = u'ЭЗ_(первичное)_' + file_name.replace(' ', '')

        ez_db = EZpdf()
        ez_doc_db = EZdoc.objects.filter(order=order).latest('added')
        fs = FileSystemStorage()
        fs.save(ez_name, file_ez)
        ez_db.file = ez_name
        ez_db.user = request.user
        ez_db.order = order
        ez_doc_db.signed_bool = True
        ez_db.ez_doc = ez_doc_db

        ez_db.save()
        ez_doc_db.save()

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()

        set_order_status(order, 'Готово для ОК', request.user)

        ez_pdf_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для подписи'), responsible_after_temp_stop=user_).count()
        counters_db.ez_pdf = ez_pdf_cnt

        counters_db.save()

        try:
            ReadyForOK.objects.filter(order=order).delete()
            ready_for_ok_db = ReadyForOK()
        except ReadyForOK.DoesNotExist:
            ready_for_ok_db = ReadyForOK()
        ready_for_ok_db.user = request.user
        ready_for_ok_db.creation_date = ez_doc_db.creation_date
        ready_for_ok_db.max_sum = ez_doc_db.max_sum
        ready_for_ok_db.decision = ez_doc_db.decision
        ready_for_ok_db.doc_file = ez_doc_db.file
        ready_for_ok_db.pdf_file = ez_db.file
        ready_for_ok_db.order = order
        ready_for_ok_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        onsite_check_cnt = Order.objects.filter((Q(onsite_check=True) & Q(onsite_check_complete=False)) &
                                  Q(status__name__contains='Готово')).count()
        counters_admin_db.admin_onsite_checks = onsite_check_cnt
        admin_ready_for_ok_cnt = ReadyForOK.objects.filter(appointed_ok=False).count()
        counters_admin_db.admin_ready_for_ok = admin_ready_for_ok_cnt
        counters_admin_db.save()

        return HttpResponse('')


# nav_new_orders_send_for_check
@login_required(redirect_field_name=None, login_url='/')
def orders_new_send_for_check_preliminary_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=user_) &
                                           Q(check_preliminary_files_for_check_uploaded=False))

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Добавление экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/new_orders_send_for_check_preliminary_list.html', context)


# nav-new-orders-send-for-check
@login_required(redirect_field_name=None, login_url='/')
def orders_new_send_for_check_preliminary(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Регистрация/На предварительной проверке', order_id, user_, request)
    order = Order.objects.get(id=order_id)
    if order.check_preliminary_files_for_check_uploaded:
        error = "Документы по данной заявке уже были загружены на проверку"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)

    if check_order_bool is True:
        order = Order.objects.get(id=order_id)
        order_type_check = OrderTypeCheck.objects.all()
        try:
            check_preliminary_file_to_check_returned = CheckPreliminaryFileToCheckReturned.objects.filter(check_preliminary_file_to_check=CheckPreliminaryFileToCheck.objects.filter(check_preliminary=CheckPreliminary.objects.filter(order=order).latest('added')).latest('added')).latest('added')
        except CheckPreliminary.DoesNotExist:
            check_preliminary_file_to_check_returned = None
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'orders_type_check': order_type_check,
            'check_preliminary_file_to_check_returned': check_preliminary_file_to_check_returned

        })
        return render(request, 'dash/menu/responsible/new_order_send_for_check_preliminary.html', context)
    else:
        return check_order_bool



# add_docs_for_check_prelimenary
@login_required(redirect_field_name=None, login_url='/')
def save_order_new_send_for_check_preliminary(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.doc'
        print(date_for_name)
        doc_type = data['docType']
        preliminary_check_db = CheckPreliminary()
        preliminary_check_db.order = order
        preliminary_check_db.order_type_check = OrderTypeCheck.objects.get(name=doc_type)
        preliminary_check_db.user = user_
        check_preliminary_file_to_check_db = CheckPreliminaryFileToCheck(check_preliminary=preliminary_check_db)
        check_passed = False

        if doc_type == 'ЭЗ':
            check_preliminary_file_to_check_db.user = request.user
            check_preliminary_file_to_check_db.type = doc_type
            doc_1_file = request.FILES['doc_1_file']
            ez_name = u'ЭЗ_(на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(ez_name, doc_1_file)
            check_preliminary_file_to_check_db.file_1 = ez_name
            if not order.check_preliminary_ez:
                order.check_preliminary_pass_without_check = True
                check_passed = True
        if doc_type == 'Пред ЭЗ + Уведомление о приостановке':
            check_preliminary_file_to_check_db.user = request.user
            check_preliminary_file_to_check_db.type = doc_type
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ПЭЗ_(приостановка_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_preliminary_file_to_check_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ_(приостановка_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_preliminary_file_to_check_db.file_2 = doc_2_file_name
            if not order.check_preliminary_temp_stop:
                order.check_preliminary_pass_without_check = True
                check_passed = True
        if doc_type == 'Отриц ЭЗ + Уведомление об отказе' or doc_type == 'Отриц ЭЗ + Уведомление об отказе (по сроку)':
            check_preliminary_file_to_check_db.user = request.user
            check_preliminary_file_to_check_db.type = doc_type
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ОЭЗ_(отказ первичный_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_preliminary_file_to_check_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ_(отказ первичный_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_preliminary_file_to_check_db.file_2 = doc_2_file_name
            if not order.check_preliminary_refuse:
                order.check_preliminary_pass_without_check = True
                check_passed = True

        preliminary_check_db.save()
        check_preliminary_file_to_check_db.save()
        order.check_preliminary_files_for_check_uploaded = True
        order.check_preliminary_files_for_check_returned_by_expert = False

        order.type = OrderTypeCheck.objects.get(name=doc_type)
        order.check_preliminary_last_date_sent_for_check = datetime.now()
        order.save()

        if order.responsible_preliminary_check_expert:
            counters_responsible_expert_for_check_preliminary_db, created = Counters.objects.get_or_create(user=order.responsible_preliminary_check_expert)
            if created:
                counters_responsible_expert_for_check_preliminary_db.save()

            orders_to_check_cnt = Order.objects.filter(
                Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(
                    responsible_preliminary_check_expert=order.responsible_preliminary_check_expert) &
                Q(check_preliminary_files_for_check_uploaded=True) &
                Q(check_preliminary_finals_files_uploaded=False) &
                Q(check_preliminary_files_for_check_returned_by_expert=False) &
                Q(check_preliminary_pass_without_check=False)
            ).count()

            counters_responsible_expert_for_check_preliminary_db.check_orders_to_check_preliminary = orders_to_check_cnt
            counters_responsible_expert_for_check_preliminary_db.save()

        if not check_passed:
            counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
            if created:
                counters_admin_db.save()
            orders_all_to_sent_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                    Q(check_preliminary_files_for_check_uploaded=True) &
                                    Q(responsible_preliminary_check_expert__isnull=True) &
                                    (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
                                    Q(check_preliminary_pass_without_check=False)
                                  ).count()
            counters_admin_db.admin_distribution_preliminary = orders_all_to_sent_for_check_cnt
            counters_admin_db.save()

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()

        orders_to_send_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=user_) &
                                           Q(check_preliminary_files_for_check_uploaded=False)).count()

        # Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
        # Q(responsible_preliminary=user_) &
        # Q(check_preliminary_files_for_check_uploaded=True) &
        # Q(responsible_preliminary_check_expert__isnull=True) &
        # (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
        # Q(check_preliminary_pass_without_check=False)

        orders_to_sent_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=user_) &
                                           Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=False) &
                                            Q(check_preliminary_files_for_check_returned_by_expert=False) &
                                            Q(check_preliminary_pass_without_check=False)).count()
        if check_passed:
            new_orders_preliminary_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                                              Q(responsible_preliminary=user_) &
                                 ((

                                      ((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(
                                     check_preliminary_temp_stop=True)) &
                                       (Q(check_preliminary_files_for_check_uploaded=True) & Q(
                                             check_preliminary_finals_files_uploaded=True))) |

                                   (Q(check_preliminary_refuse=False) & Q(check_preliminary_ez=False) & Q(
                                       check_preliminary_temp_stop=False))) |

                                  Q(check_preliminary_pass_without_check=True))).count()

            counters_db.new_orders = new_orders_preliminary_cnt

        counters_db.new_orders_check_is_needed = orders_to_send_for_check_cnt
        counters_db.check_orders_sent_for_check_preliminary = orders_to_sent_for_check_cnt
        counters_db.save()

        return HttpResponse('')


# nav_new_orders_send_for_check
@login_required(redirect_field_name=None, login_url='/')
def orders_new_for_expert_to_check_preliminary_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(Q(responsible_preliminary_check_expert=user_) &
                                Q(check_preliminary_files_for_check_uploaded=True) &
                                  (Q(check_preliminary_finals_files_uploaded=False) & Q(check_preliminary_files_for_check_returned_by_expert=False)))

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Добавление экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_new_for_expert_to_check_preliminary_list.html', context)


# nav-new-orders-send-for-check
@login_required(redirect_field_name=None, login_url='/')
def order_new_for_expert_to_check_preliminary(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Регистрация/На предварительной проверке', order_id, user_, request)
    order = Order.objects.get(id=order_id)
    if not order.check_preliminary_pass_without_check and order.check_preliminary_files_for_check_uploaded and \
            (order.check_preliminary_finals_files_uploaded or order.check_preliminary_files_for_check_returned_by_expert):
        error = "Документы по данной заявке уже были загружены на проверку"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)

    if check_order_bool is True:
        order = Order.objects.get(id=order_id)
        order_type_check = OrderTypeCheck.objects.all()
        check_preliminary_db = CheckPreliminary.objects.filter(order=order).latest('added')
        files_to_check = CheckPreliminaryFileToCheck.objects.filter(check_preliminary=check_preliminary_db)
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'orders_type_check': order_type_check,
            'files_to_check': files_to_check

        })
        return render(request, 'dash/menu/responsible/order_new_for_expert_to_check_preliminary.html', context)
    else:
        return check_order_bool


# add_checked_docs_prelimenary
@login_required(redirect_field_name=None, login_url='/')
def save_checked_docs_preliminary(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.doc'
        print(date_for_name)
        doc_type = data['docType']
        doc_type_final_sendback = data['chooseDocsTypeFinalSendback']
        preliminary_check_db = CheckPreliminary.objects.filter(order=order).latest('added')
        check_preliminary_file_to_check_db = CheckPreliminaryFileToCheck.objects.filter(check_preliminary=preliminary_check_db).latest('added')
        if doc_type_final_sendback == 'Финальная версия':
            check_preliminary_file_to_check_expert_db = CheckPreliminaryFileToCheckFinal()
            file_name_breckets = 'финальная версия'
            order.check_preliminary_finals_files_uploaded = True

        else:
            check_preliminary_file_to_check_expert_db = CheckPreliminaryFileToCheckReturned()
            file_name_breckets = 'возвращено на доработку'
            order.check_preliminary_files_for_check_returned_by_expert = True
            order.check_preliminary_files_for_check_uploaded = False
            order.check_preliminary_returned_after_correction = False

        check_preliminary_file_to_check_expert_db.user = request.user
        check_preliminary_file_to_check_expert_db.check_preliminary_file_to_check = check_preliminary_file_to_check_db
        check_preliminary_file_to_check_expert_db.type = doc_type

        if doc_type == 'ЭЗ':
            doc_1_file = request.FILES['doc_1_file']
            ez_name = u'ЭЗ_(' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(ez_name, doc_1_file)
            check_preliminary_file_to_check_expert_db.file_1 = ez_name
        if doc_type == 'Пред ЭЗ + Уведомление о приостановке':
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ПЭЗ(' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_preliminary_file_to_check_expert_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ(' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_preliminary_file_to_check_expert_db.file_2 = doc_2_file_name
        if doc_type == 'Отриц ЭЗ + Уведомление об отказе' or doc_type == 'Отриц ЭЗ + Уведомление об отказе (по сроку)':
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ОЭЗ(' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_preliminary_file_to_check_expert_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ(' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_preliminary_file_to_check_expert_db.file_2 = doc_2_file_name

        check_preliminary_file_to_check_expert_db.save()
        order.type = OrderTypeCheck.objects.get(name=doc_type)
        order.check_preliminary_last_date_sent_for_check = check_preliminary_file_to_check_expert_db.added
        order.save()

        responsible_for_order_preliminary = order.responsible_preliminary
        counters_responsible_for_order_preliminary_db, created = Counters.objects.get_or_create(user=responsible_for_order_preliminary)
        if created:
            counters_responsible_for_order_preliminary_db.save()

        new_orders_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                            Q(responsible_preliminary=responsible_for_order_preliminary) &
                                 ((

                                      ((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(
                                     check_preliminary_temp_stop=True)) &
                                       (Q(check_preliminary_files_for_check_uploaded=True) & Q(
                                             check_preliminary_finals_files_uploaded=True))) |

                                   (Q(check_preliminary_refuse=False) & Q(check_preliminary_ez=False) & Q(
                                       check_preliminary_temp_stop=False))) |

                                  Q(check_preliminary_pass_without_check=True))).count()
        orders_sent_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                    Q(responsible_preliminary=responsible_for_order_preliminary) &
                                 (Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=False)) &
                                    (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
                                    Q(check_preliminary_pass_without_check=False)).count()
        orders_to_send_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=responsible_for_order_preliminary) &
                                           Q(check_preliminary_files_for_check_uploaded=False)).count()

        counters_responsible_for_order_preliminary_db.new_orders = new_orders_cnt
        counters_responsible_for_order_preliminary_db.new_orders_check_is_needed = orders_to_send_for_check_cnt
        counters_responsible_for_order_preliminary_db.check_orders_sent_for_check_preliminary = orders_sent_for_check_cnt
        counters_responsible_for_order_preliminary_db.save()

        counters_responsible_expert_for_check_preliminary_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_responsible_expert_for_check_preliminary_db.save()

        orders_to_check_cnt = Order.objects.filter(Q(responsible_preliminary_check_expert=user_) &
                                    Q(check_preliminary_files_for_check_uploaded=True) &
                                    (Q(check_preliminary_finals_files_uploaded=False) & Q(check_preliminary_files_for_check_returned_by_expert=False))
                                   ).count()
        orders_checked_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=user_) &
                                           Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=True)).count()



        counters_responsible_expert_for_check_preliminary_db.check_orders_to_check_preliminary = orders_to_check_cnt
        counters_responsible_expert_for_check_preliminary_db.check_orders_checked_preliminary = orders_checked_cnt
        counters_responsible_expert_for_check_preliminary_db.save()

        return HttpResponse('')


# nav_new_orders_send_for_check
@login_required(redirect_field_name=None, login_url='/')
def orders_new_for_expert_to_check_after_temp_stop_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(Q(responsible_after_temp_stop_check_expert=user_) &
                                Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                  (Q(check_after_temp_stop_finals_files_uploaded=False) & Q(check_after_temp_stop_files_for_check_returned_by_expert=False)))

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Проверка документов после возобновления',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_new_for_expert_to_check_after_temp_stop_list.html', context)


# nav-new-orders-send-for-check
@login_required(redirect_field_name=None, login_url='/')
def orders_new_for_expert_to_check_after_temp_stop(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Приостановлено (принятие решение по доработке (на проверке))', order_id, user_, request)
    order = Order.objects.get(id=order_id)
    if order.check_after_temp_stop_files_for_check_uploaded and (order.check_after_temp_stop_finals_files_uploaded or order.check_after_temp_stop_files_for_check_returned_by_expert):
        error = "Документы по данной заявке уже были загружены на проверку"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)

    if check_order_bool is True:
        order = Order.objects.get(id=order_id)
        order_type_check = OrderTypeCheck.objects.all()
        check_after_temp_stop_db = CheckAfterTempStop.objects.filter(order=order).latest('added')
        files_to_check = CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop=check_after_temp_stop_db)
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'orders_type_check': order_type_check,
            'files_to_check': files_to_check

        })
        return render(request, 'dash/menu/responsible/order_new_for_expert_to_check_after_temp_stop.html', context)
    else:
        return check_order_bool


# add_checked_docs_after_temp_stop
@login_required(redirect_field_name=None, login_url='/')
def save_checked_docs_after_temp_stop(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        context = get_info_responsible(request)

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.doc'
        print(date_for_name)
        doc_type = data['docType']
        doc_type_final_sendback = data['chooseDocsTypeFinalSendback']
        after_temp_stop_check_db = CheckAfterTempStop.objects.filter(order=order).latest('added')
        check_after_temp_stop_file_to_check_db = CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop=after_temp_stop_check_db).latest('added')
        if doc_type_final_sendback == 'Финальная версия':
            check_after_temp_stop_file_to_check_expert_db = CheckAfterTempStopFileToCheckFinal()
            file_name_breckets = 'финальная версия'
            order.check_after_temp_stop_finals_files_uploaded = True
            set_order_status(order, 'Приостановлено (принятие решения по доработке)', request.user)

        else:
            check_after_temp_stop_file_to_check_expert_db = CheckAfterTempStopFileToCheckReturned()
            file_name_breckets = 'возвращено на доработку'
            order.check_after_temp_stop_files_for_check_returned_by_expert = True
            order.check_after_temp_stop_files_for_check_uploaded = False
            order.check_after_temp_stop_returned_after_correction = False
            set_order_status(order, 'Приостановлено (принятие решение по доработке (проверка))', request.user)

        check_after_temp_stop_file_to_check_expert_db.user = request.user
        check_after_temp_stop_file_to_check_expert_db.check_after_temp_stop_file_to_check = check_after_temp_stop_file_to_check_db
        check_after_temp_stop_file_to_check_expert_db.type = doc_type

        if doc_type == 'ЭЗ':
            doc_1_file = request.FILES['doc_1_file']
            ez_name = u'ЭЗ_(после возобновления_' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(ez_name, doc_1_file)
            check_after_temp_stop_file_to_check_expert_db.file_1 = ez_name
        if doc_type == 'Отриц ЭЗ + Уведомление об отказе' or doc_type == 'Отриц ЭЗ + Уведомление об отказе (по сроку)':
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ОЭЗ(отказ после возобновления_' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_after_temp_stop_file_to_check_expert_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ(отказ после возобновления_' + file_name_breckets + ')_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_after_temp_stop_file_to_check_expert_db.file_2 = doc_2_file_name

        check_after_temp_stop_file_to_check_expert_db.save()
        order.type = OrderTypeCheck.objects.get(name=doc_type)
        order.check_after_temp_stop_last_date_sent_for_check = check_after_temp_stop_file_to_check_expert_db.added
        order.save()

        responsible_for_order_after_temp_stop = order.responsible_after_temp_stop

        counters_responsible_for_order_after_temp_stop_db, created = Counters.objects.get_or_create(user=responsible_for_order_after_temp_stop)
        if created:
            counters_responsible_for_order_after_temp_stop_db.save()

        temp_stop_decision_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)')) &
                                            Q(responsible_after_temp_stop=responsible_for_order_after_temp_stop)).count()

        counters_responsible_for_order_after_temp_stop_db.temp_stop_remade_order_decision = temp_stop_decision_cnt

        orders_to_send_for_check_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (проверка))')) & Q(responsible_after_temp_stop=responsible_for_order_after_temp_stop) &
                                           Q(check_after_temp_stop_files_for_check_uploaded=False)).count()

        orders_sent_for_check_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) & Q(responsible_after_temp_stop=responsible_for_order_after_temp_stop) &
                                           Q(check_after_temp_stop_files_for_check_uploaded=True)).count()

        counters_responsible_for_order_after_temp_stop_db.temp_stop_check = orders_to_send_for_check_after_temp_stop_cnt
        counters_responsible_for_order_after_temp_stop_db.temp_stop_on_check = orders_sent_for_check_after_temp_stop_cnt
        counters_responsible_for_order_after_temp_stop_db.save()

        counters_responsible_expert_for_check_after_temp_stop_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_responsible_expert_for_check_after_temp_stop_db.save()

        orders_to_check_cnt = Order.objects.filter(Q(responsible_after_temp_stop_check_expert=user_) &
                                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                    (Q(check_after_temp_stop_finals_files_uploaded=False) & Q(check_after_temp_stop_files_for_check_returned_by_expert=False))
                                   ).count()

        counters_responsible_expert_for_check_after_temp_stop_db.check_orders_to_check_after_temp_stop = orders_to_check_cnt
        counters_responsible_expert_for_check_after_temp_stop_db.save()

        return HttpResponse('')



# nav_orders_temp_stop_with_notification_check
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_with_notification_check_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (проверка))'), \
                                  responsible_preliminary=user_)
    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Статус заявок: Приостановлено (принятие решение по доработке (проверка))',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_temp_stop_with_notification_check_list.html', context)


# nav-new-orders-send-for-check
@login_required(redirect_field_name=None, login_url='/')
def orders_temp_stop_with_notification_check(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    check_order_bool = check_order('Приостановлено (принятие решение по доработке (проверка))', order_id, user_, request)
    order = Order.objects.get(id=order_id)
    if order.check_after_temp_stop_files_for_check_uploaded:
        error = "Документы по данной заявке уже были загружены на проверку"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)

    if check_order_bool is True:
        order = Order.objects.get(id=order_id)
        order_type_check = OrderTypeCheck.objects.all()
        try:
            check_after_temp_stop_file_to_check_returned = CheckAfterTempStopFileToCheckReturned.objects.filter(check_after_temp_stop_file_to_check=CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop=CheckAfterTempStop.objects.filter(order=order).latest('added')).latest('added')).latest('added')
        except CheckAfterTempStop.DoesNotExist:
            check_after_temp_stop_file_to_check_returned = None
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'orders_type_check': order_type_check,
            'check_after_temp_stop_file_to_check_returned': check_after_temp_stop_file_to_check_returned

        })
        return render(request, 'dash/menu/responsible/order_send_for_check_after_temp_stop.html', context)
    else:
        return check_order_bool


# nav_new_orders_sent_for_check
@login_required(redirect_field_name=None, login_url='/')
def orders_sent_for_preliminary_check_list(request):
    user_ = request.user
    context = get_info_responsible(request)

    orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                    Q(responsible_preliminary=user_) &
                                  (Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=False)) &
                                    (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
                                    Q(check_preliminary_pass_without_check=False)
                                  )

    context.update({
        'orders': orders,
        'big_title': 'Заявки, отправленные на проверку',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user)
    })
    return render(request, 'dash/menu/responsible/orders_sent_for_preliminary_check_list.html', context)


# add_docs_for_check_after_temp_stop
@login_required(redirect_field_name=None, login_url='/')
def save_order_send_for_check_after_temp_stop(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.doc'
        print(date_for_name)
        doc_type = data['docType']
        after_temp_stop_check_db = CheckAfterTempStop()
        after_temp_stop_check_db.order = order
        after_temp_stop_check_db.order_type_check = OrderTypeCheck.objects.get(name=doc_type)
        after_temp_stop_check_db.user = user_
        check_after_temp_stop_file_to_check_db = CheckAfterTempStopFileToCheck(check_after_temp_stop=after_temp_stop_check_db)
        check_passed = False

        if doc_type == 'ЭЗ':
            check_after_temp_stop_file_to_check_db.user = request.user
            check_after_temp_stop_file_to_check_db.type = doc_type
            doc_1_file = request.FILES['doc_1_file']
            ez_name = u'ЭЗ_(после возобновления_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(ez_name, doc_1_file)
            check_after_temp_stop_file_to_check_db.file_1 = ez_name
            if not order.check_after_temp_stop_ez:
                order.check_after_temp_stop_pass_without_check = True
                check_passed = True
        if doc_type == 'Отриц ЭЗ + Уведомление об отказе' or doc_type == 'Отриц ЭЗ + Уведомление об отказе (по сроку)':
            check_after_temp_stop_file_to_check_db.user = request.user
            check_after_temp_stop_file_to_check_db.type = doc_type
            doc_1_file = request.FILES['doc_1_file']
            doc_1_file_name = u'ОЭЗ(отказ после возобновления_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_1_file_name, doc_1_file)
            check_after_temp_stop_file_to_check_db.file_1 = doc_1_file_name
            doc_2_file = request.FILES['doc_2_file']
            doc_2_file_name = u'УВ(отказ после возобновления_на проверку)_' + file_name.replace(' ', '')
            fs = FileSystemStorage()
            fs.save(doc_2_file_name, doc_2_file)
            check_after_temp_stop_file_to_check_db.file_2 = doc_2_file_name
            if not order.check_after_temp_stop_refuse:
                order.check_after_temp_stop_pass_without_check = True
                check_passed = True

        after_temp_stop_check_db.save()
        check_after_temp_stop_file_to_check_db.save()

        if order.check_after_temp_stop_files_for_check_returned_by_expert:
            order.check_after_temp_stop_returned_after_correction = True
        order.check_after_temp_stop_files_for_check_uploaded = True
        order.check_after_temp_stop_files_for_check_returned_by_expert = False

        order.type = OrderTypeCheck.objects.get(name=doc_type)

        if not check_passed:
            set_order_status(order, 'Приостановлено (принятие решение по доработке (на проверке))', request.user)

            counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
            if created:
                counters_admin_db.save()
            orders_all_to_distribute_for_check_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
                                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                    Q(responsible_after_temp_stop_check_expert__isnull=True) &
                                    (Q(check_after_temp_stop_refuse=True) | Q(check_after_temp_stop_ez=True)) &
                                    Q(check_after_temp_stop_pass_without_check=False)
                                  ).count()
            counters_admin_db.admin_distribution_after_temp_stop = orders_all_to_distribute_for_check_after_temp_stop_cnt
            counters_admin_db.save()

            if order.responsible_after_temp_stop_check_expert:
                counters_responsible_expert_for_check_after_temp_stop_db, created = Counters.objects.get_or_create(user=order.responsible_after_temp_stop_check_expert)
                if created:
                    counters_responsible_expert_for_check_after_temp_stop_db.save()

                orders_to_check_cnt = Order.objects.filter(
                    Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
                    Q(responsible_after_temp_stop_check_expert=order.responsible_after_temp_stop_check_expert) &
                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                    Q(check_after_temp_stop_finals_files_uploaded=False) &
                    Q(check_after_temp_stop_files_for_check_returned_by_expert=False)).count()

                counters_responsible_expert_for_check_after_temp_stop_db.check_orders_to_check_after_temp_stop = orders_to_check_cnt
                counters_responsible_expert_for_check_after_temp_stop_db.save()
        else:
            set_order_status(order, 'Приостановлено (принятие решения по доработке)', request.user)

        counters_db, created = Counters.objects.get_or_create(user=user_)
        if created:
            counters_db.save()

        orders_to_send_for_check_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (проверка))')) & Q(responsible_preliminary=user_) &
                                           Q(check_after_temp_stop_files_for_check_uploaded=False)).count()

        orders_to_sent_for_check_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) & Q(responsible_preliminary=user_) &
                                           Q(check_after_temp_stop_files_for_check_uploaded=True)).count()
        if check_passed:
            orders_after_temp_stop_decision_cnt = Order.objects.filter(
                Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)')) &
                Q(responsible_after_temp_stop=user_)).count()

            counters_db.temp_stop_remade_order_decision = orders_after_temp_stop_decision_cnt

        counters_db.temp_stop_check = orders_to_send_for_check_after_temp_stop_cnt
        counters_db.temp_stop_on_check = orders_to_sent_for_check_after_temp_stop_cnt
        counters_db.save()

        return HttpResponse('')


# nav_callback
@login_required(redirect_field_name=None, login_url='/')
def orders_all_callback_list(request):
    user_ = request.user
    context = get_info_responsible(request)
    orders = Order.objects.filter(Q(responsible_preliminary=user_) | Q(responsible_after_temp_stop=user_) &
                                  ~Q(status=OrderStatus.objects.get(name='Отозвана заявка')))

    print(orders)
    context.update({
        'orders': orders,
        'big_title': 'Общий список заявок, исключая отозванные',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
    })
    return render(request, 'dash/menu/responsible/orders_callback_list.html', context)


# nav-new-orders-send-for-check
@login_required(redirect_field_name=None, login_url='/')
def order_callback(request, order_id):
    user_ = request.user
    context = get_info_responsible(request)
    order = Order.objects.get(id=order_id)
    if order.responsible_preliminary == user_ or order.responsible_after_temp_stop == user_:
        context.update({
            'counter': get_counter(user_),
            'order': order,
            'applier': Applier.objects.get(order=order)

        })

        return render(request, 'dash/menu/responsible/order_callback.html', context)
    else:
        error = "Заявка принадлежит другому пользователю"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)


# сохранение даты получения доработатной заявки btn_add_prelimenary_remadeorder_date
@login_required(redirect_field_name=None, login_url='/')
def save_order_callback(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        callback_date = date_to_db(data['callbackDate'])

        order = Order.objects.get(id=data['orderID'])
        order.save()

        return HttpResponse('ok')


# отмена предварительной проверки из распределеения на проверку до приостановки
@login_required(redirect_field_name=None, login_url='/')
def delete_preliminary_check_from_distribution(request):
    if request.method == 'POST':
        data = request.POST
        order_id = data['orderID']
        order_db = Order.objects.get(id=order_id)
        order_db.check_preliminary_pass_without_check = True
        order_db.check_preliminary_refuse = False
        order_db.check_preliminary_ez = False
        order_db.check_preliminary_temp_stop = False
        order_db.save()
        if order_db.responsible_preliminary_check_expert:
            counters_expert_db, created = Counters.objects.get_or_create(user=order_db.responsible_preliminary_check_expert)
            if created:
                counters_expert_db.save()
            check_orders_to_check_preliminary_cnt = Order.objects.filter(Q(responsible_preliminary_check_expert=order_db.responsible_preliminary_check_expert) &
                                                                        Q(check_preliminary_files_for_check_uploaded=True) &
                                                                        Q(check_preliminary_finals_files_uploaded=False) &
                                                                         Q(check_preliminary_pass_without_check=False)).count()
            counters_expert_db.check_orders_to_check_preliminary = check_orders_to_check_preliminary_cnt
            counters_expert_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_distribution_preliminary_cnt = Order.objects.filter(
            Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
            Q(check_preliminary_files_for_check_uploaded=True) &
            Q(responsible_preliminary_check_expert__isnull=True) &
            (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
            Q(check_preliminary_pass_without_check=False)
            ).count()

        counters_admin_db.admin_distribution_preliminary = admin_distribution_preliminary_cnt
        counters_admin_db.save()

        counters_db, created = Counters.objects.get_or_create(user=order_db.responsible_preliminary)
        if created:
            counters_db.save()

        orders_to_send_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=order_db.responsible_preliminary) &
                                           Q(check_preliminary_files_for_check_uploaded=False)).count()

        orders_to_sent_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) & Q(responsible_preliminary=order_db.responsible_preliminary) &
                                           Q(check_preliminary_files_for_check_uploaded=True) & Q(check_preliminary_finals_files_uploaded=False) &
                                            Q(check_preliminary_files_for_check_returned_by_expert=False) &
                                            Q(check_preliminary_pass_without_check=False)).count()
        new_orders_preliminary_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                                          Q(responsible_preliminary=order_db.responsible_preliminary) &
                             ((

                                  ((Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) |
                                    Q(check_preliminary_temp_stop=True)) &
                                   (Q(check_preliminary_files_for_check_uploaded=True) &
                                    Q(check_preliminary_finals_files_uploaded=True))) |

                               (Q(check_preliminary_refuse=False) & Q(check_preliminary_ez=False) &
                                Q(check_preliminary_temp_stop=False))) |
                              Q(check_preliminary_pass_without_check=True))).count()

        counters_db.new_orders = new_orders_preliminary_cnt

        counters_db.new_orders_check_is_needed = orders_to_send_for_check_cnt
        counters_db.check_orders_sent_for_check_preliminary = orders_to_sent_for_check_cnt
        counters_db.save()

        status_change_without_order_status(order_db,
                                           OrderStatus.objects.get(name='Первичная проверка отменена'),
                                           request.user)


        return HttpResponse(admin_distribution_preliminary_cnt)


# отмена предварительной проверки из распределеения на проверку после приостановки
@login_required(redirect_field_name=None, login_url='/')
def delete_after_temp_stop_check_from_distribution(request):
    if request.method == 'POST':
        data = request.POST
        order_id = data['orderID']
        order_db = Order.objects.get(id=order_id)
        order_db.check_after_temp_stop_pass_without_check = True
        order_db.check_after_temp_stop_refuse = False
        order_db.check_after_temp_stop_ez = False
        order_db.status = OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)')
        order_db.save()
        if order_db.responsible_after_temp_stop_check_expert:
            counters_expert_db, created = Counters.objects.get_or_create(user=order_db.responsible_after_temp_stop_check_expert)
            if created:
                counters_expert_db.save()
            check_orders_to_check_after_temp_stop_cnt = Order.objects.filter(Q(responsible_after_temp_stop_check_expert=order_db.responsible_after_temp_stop_check_expert) &
                                                                        Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                                                        Q(check_after_temp_stop_finals_files_uploaded=False) &
                                                                         Q(check_after_temp_stop_pass_without_check=False)).count()
            counters_expert_db.check_orders_to_check_after_temp_stop = check_orders_to_check_after_temp_stop_cnt
            counters_expert_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_distribution_after_temp_stop_cnt = Order.objects.filter(
            Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
            Q(check_after_temp_stop_files_for_check_uploaded=True) &
            Q(responsible_after_temp_stop_check_expert__isnull=True) &
            (Q(check_after_temp_stop_refuse=True) | Q(check_after_temp_stop_ez=True)) &
            Q(check_after_temp_stop_pass_without_check=False)
            ).count()

        counters_admin_db.admin_distribution_after_temp_stop = admin_distribution_after_temp_stop_cnt
        counters_admin_db.save()

        counters_db, created = Counters.objects.get_or_create(user=order_db.responsible_after_temp_stop)
        if created:
            counters_db.save()

        orders_sent_for_check_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
                                                         Q(responsible_after_temp_stop=order_db.responsible_after_temp_stop)).count()
        counters_db.temp_stop_on_check = orders_sent_for_check_cnt

        orders_after_temp_stop_decision_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решения по доработке)')) &
                                                         Q(responsible_after_temp_stop=order_db.responsible_after_temp_stop)).count()


        print('orders_after_temp_stop_decision_cnt - ' + str(orders_after_temp_stop_decision_cnt))
        counters_db.temp_stop_remade_order_decision = orders_after_temp_stop_decision_cnt
        counters_db.save()

        status_change_without_order_status(order_db,
                                           OrderStatus.objects.get(name='Проверка после возобновления отменена'),
                                           request.user)

        return HttpResponse(admin_distribution_after_temp_stop_cnt)