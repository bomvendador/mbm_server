import os, io
from django.shortcuts import render, HttpResponseRedirect
from django.apps import apps
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from login.models import Role, Company, UserProfile
from .models import Order, OrderStatus, Applier, PPnumber, ResponsibleForOrderPreliminary, \
    ResponsibleForOrderAfterTempStop, Counters, StatusChange, CountersLotki, CountersAdmin, LotkiStatusChange, \
    LotkiContent, CheckPreliminary, CheckPreliminaryResponsibleExpert, NotificationTempStop, TempStop, \
    CheckAfterTempStop, CheckAfterTempStopResponsibleExpert, CheckAfterTempStopFileToCheck, CheckPreliminaryFileToCheck, \
    CheckPreliminaryFileToCheckReturned, CheckPreliminaryFileToCheckFinal, CheckAfterTempStopFileToCheckReturned, \
    CheckAfterTempStopFileToCheckFinal, TempStopFiles, Refuse, NotificationRefuse, RefuseFiles, EZdoc, EZpdf, \
    ReadyForOK, AppointedForOK, CommissionDate, ProtocolOrders, Protocol, OnsiteCheck, \
    RefuseReasonsAfterTempStopByOrders, RefuseReasonsPreliminaryByOrders
from django.contrib.auth.models import User
from .counters import counters

from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime

from django.db.models import Q

import json
from django.conf import settings

import zipfile

from wsgiref.util import FileWrapper
from shutil import make_archive, copy, rmtree
from django.core.files.storage import FileSystemStorage

import mimetypes

userprofile = apps.get_model('login', 'UserProfile')

from login.views import login_index

# Create your views here.


def download_file(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            print(os.path.basename(path))
            return response
    raise Http404


def status_change(user, order):
    status_change_db = StatusChange()
    status_change_db.user = user
    status_change_db.order = order
    status_change_db.status = order.status
    status_change_db.save()


def status_change_without_order_status(order, status_instance, user):
    status_change_db = StatusChange()
    status_change_db.user = user
    status_change_db.order = order
    status_change_db.status = status_instance
    status_change_db.save()


def get_counter(user_obj):
    user_profile = userprofile.objects.get(user=user_obj)
    if user_profile.role.name == 'Статистика (лотки)':
        try:
            counter = CountersLotki.objects.get(user_role_name='Статистика (лотки)')
        except CountersLotki.DoesNotExist:
            counter = None
    else:
        if user_profile.role.name == 'Админ' or user_profile.role.name == 'Суперадмин':
            print('админ')
            try:
                counter = CountersAdmin.objects.get(user_role_name='Админ')
            except CountersAdmin.DoesNotExist:
                counter = None

        else:
            try:
                counter = Counters.objects.get(user=user_obj)
            except Counters.DoesNotExist:
                counter = None
    print(counter)
    return counter


def date_to_db(date):
    date_split = date.split('.')
    date_db = date_split[2] + '-' + date_split[1] + '-' + date_split[0]
    return date_db


@login_required(redirect_field_name=None, login_url='/')
def dash_get_info(request):
    user_profile = userprofile.objects.get(user=request.user)

    context = {
        'user_profile': user_profile,
        'counter': get_counter(request.user)
    }
    return context


@login_required(redirect_field_name=None, login_url='/')
def dash_index(request):
    user = request.user
    print('user.id - ' + str(user.id))
    # userprofile = apps.get_model('login', 'UserProfile')
    user_profile = userprofile.objects.get(user=user)
    counter = get_counter(request.user)

    context = {
        'user_profile': user_profile,
        'counter': counter
    }
    return render(request, 'dash/dash_panel.html', context)


@login_required(redirect_field_name=None, login_url='/')
def dash_logout(request):
    print('logout')

    logout(request)

    return HttpResponse('')
    # return render(request, 'login/login.html')


@login_required(redirect_field_name=None, login_url='/')
def dash_add_xlsx_file(request):
    if request.method == 'POST':
        data = request.POST
        orders = json.loads(data['orders'])
        # print(orders[0][0]['Номер заявки'])
        # print(orders)
        #982-ПП
        cnt = 0
        existing_orders = []
        response = {}
        for order in orders[0]:
            orders_cnt = Order.objects.filter(number=order['Номер заявки']).count()
            if orders_cnt == 0:
            #     print('----------------------')
                print(
                'номер - ' + order['Номер заявки'] + 'сумма - ' + order['Сумма запрашиваемой субсидии, рублей'].replace(',',
                                                                                                                        '.'))
                new_order = Order()
                new_order.user = request.user
                new_order.added = datetime.now
                new_order.number = order['Номер заявки']
                new_order.date_of_appliance = order['Дата завершения (фактическая)']
                new_order.pp = PPnumber.objects.get(name=order['Номер НПА'])
                new_order.sum_of_appliance = order['Сумма запрашиваемой субсидии, рублей'].replace(',', '.')
                new_order.status = OrderStatus.objects.get(name='Новая')
                new_order.end_date = order['Крайняя дата ЭЗ']
                new_order.end_date_for_responsible = order['Крайняя дата ЭЗ для эксперта']
                new_order.aim = order['Цель поддержки']
                new_order.company = order['Наименование заявителя']
                new_order.company_inn = order['ИНН заявителя']
                new_order.service_name = order['Наименование сервиса']
                new_order.save()

                new_order_applier = Applier()
                new_order_applier.user = request.user
                new_order_applier.order = new_order
                new_order_applier.applier_email = order['Email заявителя']
                new_order_applier.applier_tel = order['Телефон заявителя']
                new_order_applier.applier_fio = order['ФИО заявителя']
                new_order_applier.save()
                cnt = cnt + 1

                status_change_db = StatusChange()
                status_change_db.user = request.user
                status_change_db.order = new_order
                status_change_db.status = OrderStatus.objects.get(name='Новая')
                status_change_db.save()

            else:
                print('существующая заявка - ' + order['Номер заявки'])
                existing_orders.append([order['Номер заявки'], order['Наименование заявителя']])
        #741-ПП
        for order in orders[1]:
            orders_cnt = Order.objects.filter(number=order['Номер заявки']).count()
            if orders_cnt == 0:
                #     print('----------------------')
            #     print(order['Номер заявки'])
                print(
                'номер - ' + order['Номер заявки'] + 'сумма - ' + order['Сумма запрашиваемой субсидии, рублей'].replace(',',
                                                                                                                        '.'))

                new_order = Order()
                new_order.user = request.user
                new_order.added = datetime.now
                new_order.number = order['Номер заявки']
                new_order.date_of_appliance = order['Дата завершения (фактическая)']
                new_order.pp = PPnumber.objects.get(name=order['Номер НПА'])
                new_order.sum_of_appliance = order['Сумма запрашиваемой субсидии, рублей'].replace(',','.')
                new_order.status = OrderStatus.objects.get(name='Новая')
                new_order.end_date = order['Крайняя дата ЭЗ']
                new_order.end_date_for_responsible = order['Крайняя дата ЭЗ для эксперта']
                new_order.aim = order['Цель']
                new_order.company = order['Наименование заявителя']
                new_order.company_inn = order['ИНН заявителя']
                new_order.service_name = order['Наименование сервиса']
                new_order.save()

                new_order_applier = Applier()
                new_order_applier.user = request.user
                new_order_applier.order = new_order
                new_order_applier.applier_email = order['Email заявителя']
                new_order_applier.applier_tel = order['Телефон заявителя']
                new_order_applier.applier_fio = order['ФИО заявителя']
                new_order_applier.applier_type = order['Категория заявителя']
                new_order_applier.save()
                cnt = cnt + 1

                status_change_db = StatusChange()
                status_change_db.user = request.user
                status_change_db.order = new_order
                status_change_db.status = OrderStatus.objects.get(name='Новая')
                status_change_db.save()

                #
                #     print(el['Дата подачи'].split(' ')[0])
                # cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Новая')).count()
            else:
                print('существующая заявка - ' + order['Номер заявки'])

                existing_orders.append([order['Номер заявки'], order['Наименование заявителя']])
        if len(existing_orders) > 0:
            response['existing_orders'] = existing_orders

        new_orders_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Новая')).count()
        counter_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counter_db.save()
        print('new_orders_cnt - ' + str(new_orders_cnt))
        counter_db.new_orders = new_orders_cnt
        counter_db.all_orders = Order.objects.all().count()
        counter_db.save()


        response['modalTitle'] = 'Данные по загрузке'
        response['cnt'] = cnt
        return JsonResponse(response)

    # try:
    #     counter = Counters.objects.get(user=request.user)
    # except Counters.DoesNotExist:
    #     counter = None

    context = dash_get_info(request)
    # context.update({'counters': counter})

    return render(request, 'dash/menu/admin/dash_add_xlsx_file.html', context)


@login_required(redirect_field_name=None, login_url='/')
def get_menu_content(request):
    if request.method == 'POST':
        print(request.POST)
        context = dash_get_info(request)
        menu_id = request.POST['menu_id']
        menu_type = request.POST['menu_type']
        user_ = request.user
        user_profile = context['user_profile']
        user_role = user_profile.role.name
        if menu_id == 'nav_satistics':
            # if user_role == 'Админ' or user_role == 'Суперадмин':

            context.update({'counter': get_counter(request.user)})

            return render(request, 'dash/dash_panel.html', context)
            # return HttpResponse('dash/dash_panel.html')
        if menu_id == 'nav_new_orders_list':
            if user_role == 'Админ' or user_role == 'Суперадмин':
                new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Новая'))
                responsibles = User.objects.all()
                list_ = []
                list_.append(new_orders)
                context = {
                    'new_orders': new_orders,
                    'menu_id': menu_id,
                    'responsibles': responsibles
                }
                return render(request, 'dash/menu/admin/dash_admin_new_orders_list.html', context)


        # return HttpResponse('ok')
# nav_new_orders_list
@login_required(redirect_field_name=None, login_url='/')
def appoint_responsible_for_order_list(request):
    context = dash_get_info(request)
    user_profile = context['user_profile']

    new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Новая'))
    responsibles = UserProfile.objects.filter(Q(role__name='Эксперт МБМ') | Q(role__name='Эксперт подрядчика'))
    context.update({
        'new_orders': new_orders,
        'responsibles': responsibles
    })
    return render(request, 'dash/menu/admin/dash_admin_new_orders_list.html', context)


@login_required(redirect_field_name=None, login_url='/')
def appoint_responsible_for_order(request):
    if request.method == 'POST':
        data = request.POST
        responsible_id = data['responsibleID']
        order_id = data['orderID']
        is_expert_appointed_for_conclusion = data['isExpertAppointedForConclusion']
        responsible_user = User.objects.get(id=responsible_id)
        user_profile = userprofile.objects.get(user=responsible_user)
        order_db = Order.objects.get(id=order_id)
        order_db.status = OrderStatus.objects.get(name='Регистрация/На предварительной проверке')
        responsible_preliminary_db = ResponsibleForOrderPreliminary()
        responsible_preliminary_db.user = request.user
        responsible_preliminary_db.added = datetime.now
        if is_expert_appointed_for_conclusion == 'true':
            responsible_after_temp_stop_db = ResponsibleForOrderAfterTempStop()
            order_db.responsible_preliminary = responsible_user
            order_db.responsible_after_temp_stop = responsible_user
            order_db.responsible_preliminary_profile = UserProfile.objects.get(user=responsible_user)
            order_db.responsible_after_temp_stop_profile = UserProfile.objects.get(user=responsible_user)
            order_db.save()
            responsible_preliminary_db.responsible = responsible_user
            responsible_after_temp_stop_db.responsible = responsible_user
            responsible_preliminary_db.order = order_db
            responsible_after_temp_stop_db.order = order_db
            responsible_after_temp_stop_db.company = user_profile.company.name
            responsible_after_temp_stop_db.user = request.user
            responsible_after_temp_stop_db.save()

        else:
            order_db.responsible_preliminary = responsible_user
            order_db.responsible_preliminary_profile = UserProfile.objects.get(user=responsible_user)
            order_db.save()
            responsible_preliminary_db.responsible = responsible_user
            responsible_preliminary_db.order = order_db
        if user_profile.check_preliminary_refuse:
            order_db.check_preliminary_refuse = user_profile.check_preliminary_refuse
        if user_profile.check_preliminary_ez:
            order_db.check_preliminary_ez = user_profile.check_preliminary_ez
        if user_profile.check_preliminary_temp_stop:
            order_db.check_preliminary_temp_stop = user_profile.check_preliminary_temp_stop
        if user_profile.check_after_temp_stop_refuse:
            order_db.check_after_temp_stop_refuse = user_profile.check_after_temp_stop_refuse
        if user_profile.check_after_temp_stop_refuse_by_date:
            order_db.check_after_temp_stop_refuse_by_date = user_profile.check_after_temp_stop_refuse_by_date
        if user_profile.check_after_temp_stop_ez:
            order_db.check_after_temp_stop_ez = user_profile.check_after_temp_stop_ez

        order_db.save()
        print(data)
        responsible_preliminary_db.company = user_profile.company.name
        responsible_preliminary_db.save()
        counter_db, created = Counters.objects.get_or_create(user=responsible_user)
        if created:
            counter_db.save()
            cnt = 1
        else:
            if user_profile.check_preliminary_refuse or user_profile.check_preliminary_ez or user_profile.check_preliminary_temp_stop:
                cnt = int(counter_db.new_orders_check_is_needed or 0) + 1
            else:
                cnt = int(counter_db.new_orders or 0) + 1

        if user_profile.common_check_needed:
            counter_db.new_orders_check_is_needed = cnt
        else:
            counter_db.new_orders = cnt
        counter_db.save()

        new_orders_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Новая')).count()

        counter_admin_db = CountersAdmin.objects.get(user_role_name='Админ')
        counter_admin_db.new_orders = new_orders_cnt
        counter_admin_db.save()

        status_change_without_order_status(order_db, OrderStatus.objects.get(name='Ответственный по заявке назначен'), request.user)

        return HttpResponse('ok')


def check_order(status_to_check, order_id, user_, request):
    context = dash_get_info(request)
    user_role = userprofile.objects.get(user=request.user).role.name

    try:
        Order.objects.get(id=order_id)
    except ObjectDoesNotExist:
        error = "Заявка отсутствует"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)
    order = Order.objects.get(id=order_id)

    print('check_order - ' + status_to_check)
    print('order - ' + order.status.name)
    if (order.responsible_preliminary == user_ or order.responsible_preliminary_check_expert == user_
        or order.responsible_after_temp_stop_check_expert == user_ or order.responsible_preliminary_check_expert == user_) \
            or user_role == 'Админ' \
            or user_role == 'Суперадмин':
        print('user checked')
        if order.status.name != status_to_check:
            print('error')
            error = "Заявка находится в другом статусе - " + order.status.name
            context.update({
                'error': error,
                'modal_error_title': 'Ошибка при загрузке',
                'counter': get_counter(user_)
                            })
            return render(request, 'dash/dash_base.html', context)
        else:
            return True
    else:
        print('user error')
        error = "Заявка назначена на другого исполнителя"
        context.update({
            'error': error,
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)


def set_order_status(order, status, user):
    order.status = OrderStatus.objects.get(name=status)
    status_change(user, order)
    order.save()


def lotki_status_change(order, lotki_status, user):
    lotki_db = LotkiStatusChange()
    lotki_db.user = user
    lotki_db.order = order
    lotki_db.status = LotkiContent.objects.get(name=lotki_status)
    lotki_db.save()


# nav_add_conclusion
@login_required(redirect_field_name=None, login_url='/')
def users_list(request):
    user_ = request.user
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()

    context.update({
        'big_title': 'Добавление подписанного экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'roles': Role.objects.all(),
        'companies': Company.objects.all()
    })
    return render(request, 'dash/menu/admin/dash_admin_users_list.html', context)


@login_required(redirect_field_name=None, login_url='/')
def save_user(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        user_email = data['user_email']
        user_password = data['user_password']
        user_lastname = data['user_lastname']
        user_firstname = data['user_firstname']
        user_tel = data['user_tel']
        user_role = data['user_role']
        user_company = data['user_company']
        preliminary_refuse_check = data['preliminary_refuse_check']
        preliminary_ez_check = data['preliminary_ez_check']
        temp_stop_check = data['temp_stop_check']
        after_temp_stop_refuse_check = data['after_temp_stop_refuse_check']
        after_temp_stop_refuse_by_date_check = data['after_temp_stop_refuse_by_date_check']
        after_temp_stop_ez_check = data['after_temp_stop_ez_check']

        user_id = data.get('user_id')
        response = {}
        if user_id:
            user_ = User.objects.get(id=user_id)
        else:
            existing_usernames = User.objects.filter(username=user_email).count()
            if existing_usernames > 0:
                response['error'] = 'Пользователь с указанным email уже существует'
                return JsonResponse(response)
            else:
                user_ = User()
        user_profile = userprofile(user=user_)
        if preliminary_refuse_check == 'true':
            user_profile.check_preliminary_refuse = True
            user_profile.common_check_needed = True
        if preliminary_ez_check == 'true':
            user_profile.check_preliminary_ez = True
            user_profile.common_check_needed = True
        if temp_stop_check == 'true':
            user_profile.check_preliminary_temp_stop = True
            user_profile.common_check_needed = True
        if after_temp_stop_refuse_check == 'true':
            user_profile.check_after_temp_stop_refuse = True
            user_profile.common_check_needed = True
        if after_temp_stop_refuse_by_date_check == 'true':
            user_profile.check_after_temp_stop_refuse_by_date = True
            user_profile.common_check_needed = True
        if after_temp_stop_ez_check == 'true':
            user_profile.check_after_temp_stop_ez = True
            user_profile.common_check_needed = True

        user_.username = user_email
        user_.email = user_email
        user_.set_password(user_password)
        user_.first_name = user_firstname
        user_.last_name = user_lastname
        user_.role_name = user_role
        user_.save()
        user_profile.role = Role.objects.get(name=user_role)
        user_profile.tel = user_tel
        user_profile.company = Company.objects.get(name=user_company)
        user_profile.user = user_
        user_profile.user_added = request.user

        user_profile.save()
        response['success'] = 'Пользователь успешно добавлен'
        response['user_id'] = user_.id
        response['user_fio'] = user_.first_name + ' ' + user_.last_name
        response['login'] = user_.username
        response['role'] = user_role
        response['company'] = user_company

        return JsonResponse(response)


@login_required(redirect_field_name=None, login_url='/')
def save_company(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        company_name = data['company_name']
        response = {}
        user_ = request.user
        existing_companies = Company.objects.filter(name=company_name).count()
        if existing_companies > 0:
            response['error'] = 'Компания с таким названием уже существует'
            return JsonResponse(response)
        else:
            company_db = Company()
            company_db.name = company_name
            company_db.user = user_
            company_db.save()
            response['success'] = 'Компания успешно добавлена'

        return JsonResponse(response)


@login_required(redirect_field_name=None, login_url='/')
def save_company_changes(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        company_name = data['company_name']
        comapny_id = data['companyID']

        response = {}
        user_ = request.user
        company_db = Company.objects.get(id=comapny_id)
        company_db.name = company_name
        company_db.user = user_
        company_db.save()
        response['success'] = 'Компания успешно добавлена'

        return JsonResponse(response)


# company
@login_required(redirect_field_name=None, login_url='/')
def company(request, company_id):
    user_ = request.user
    context = dash_get_info(request)
    user_profile = UserProfile.objects.get(user=user_)

    if user_profile.role.name == 'Админ' or user_profile.role.name == 'Суперадмин':

        company = Company.objects.get(id=company_id)

        context.update({
            'counter': get_counter(user_),
            'company': company,
            'title': 'Информация о компании',
            'users': UserProfile.objects.filter(company=company)
        })
        return render(request, 'dash/menu/admin/dash_admin_company.html', context)
    else:
        context.update({
            'error': 'Ваша роль не позволяет просматривать данный контент',
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_),

        })
        return render(request, 'dash/dash_base.html', context)


# user
@login_required(redirect_field_name=None, login_url='/')
def user(request, user_id):
    user_ = request.user
    user_profile = UserProfile.objects.get(user=user_)
    context = dash_get_info(request)

    if user_profile.role.name == 'Админ' or user_profile.role.name == 'Суперадмин':

        user_to_save = User.objects.get(id=user_id)
        user_profile_to_save = UserProfile.objects.get(user=user_to_save)

        context.update({
            'counter': get_counter(user_),
            'user_profile_to_save': user_profile_to_save,
            'title': 'Информация о пользователе',
            'roles': Role.objects.all(),
            'companies': Company.objects.all()

        })
        return render(request, 'dash/menu/admin/dash_admin_user.html', context)
    else:
        context.update({
            'error': 'Ваша роль не позволяет просматривать данный контент',
            'modal_error_title': 'Ошибка при загрузке',
            'counter': get_counter(user_)
        })
        return render(request, 'dash/dash_base.html', context)


# nav_new_orders_for_experts_to_check
@login_required(redirect_field_name=None, login_url='/')
def appoint_expert_for_order_check_list(request):
    user_ = request.user
    context = dash_get_info(request)
    orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                    Q(check_preliminary_files_for_check_uploaded=True) &
                                    Q(responsible_preliminary_check_expert__isnull=True) &
                                    (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
                                    Q(check_preliminary_pass_without_check=False)
                                  )
    experts = userprofile.objects.filter(role__name='Эксперт МБМ')
    context.update({
        'big_title': 'Распределение заявок на первичную проверку',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'orders': orders,
        'experts': experts
    })
    return render(request, 'dash/menu/admin/dash_admin_orders_for_preliminary_check_list.html', context)


# appointExpertMBMToCheckPreliminaryDocs
@login_required(redirect_field_name=None, login_url='/')
def appoint_expert_for_order_check(request):
    if request.method == 'POST':
        data = request.POST
        expertID = data.get('expertID')
        orderID = data.get('orderID')
        order = Order.objects.get(id=orderID)
        expert = User.objects.get(id=expertID)
        response = {}
        print(order.responsible_preliminary_check_expert)
        if order.responsible_preliminary_check_expert is None:
            check_preliminary_db = CheckPreliminary.objects.filter(order=order).latest('added')
            check_preliminary_responsible_expert_db = CheckPreliminaryResponsibleExpert()
            check_preliminary_responsible_expert_db.check_preliminary = check_preliminary_db
            check_preliminary_responsible_expert_db.responsible_expert = expert
            check_preliminary_responsible_expert_db.user = request.user

            check_preliminary_responsible_expert_db.save()
            order.responsible_preliminary_check_expert = expert
            order.save()
            counters_expert_db, created = Counters.objects.get_or_create(user=expert)
            if created:
                counters_expert_db.save()
            check_orders_to_check_preliminary_cnt = Order.objects.filter(Q(responsible_preliminary_check_expert=expert) &
                                                                        Q(check_preliminary_files_for_check_uploaded=True) &
                                                                        Q(check_preliminary_finals_files_uploaded=False) &
                                                                         Q(check_preliminary_pass_without_check=False)).count()
            counters_expert_db.check_orders_to_check_preliminary = check_orders_to_check_preliminary_cnt
            counters_expert_db.save()

            counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
            if created:
                counters_admin_db.save()
            admin_distribution_preliminary_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке')) &
                                                                    Q(check_preliminary_files_for_check_uploaded=True) &
                                                                    Q(responsible_preliminary_check_expert__isnull=True) &
                                                                    (Q(check_preliminary_refuse=True) | Q(check_preliminary_ez=True) | Q(check_preliminary_temp_stop=True)) &
                                                                     Q(check_preliminary_pass_without_check=False)
                                                                  ).count()
            counters_admin_db.admin_distribution_preliminary = admin_distribution_preliminary_cnt
            counters_admin_db.save()
            response['admin_distribution_preliminary_cnt'] = admin_distribution_preliminary_cnt
            status_change_without_order_status(order, OrderStatus.objects.get(name='Проверяющий назначен (первичная проверка)'), request.user)
        else:
            response['error'] = 'По заявке уже назначен проверяющий'
        return JsonResponse(response)


# nav_new_orders_for_experts_to_check
@login_required(redirect_field_name=None, login_url='/')
def remade_order_send_to_subcotractor_date_list(request):
    user_ = request.user
    context = dash_get_info(request)
    orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (уведомление отправлено)')))
    context.update({
        'big_title': 'Фиксация даты отправки возобновления заявки подрядчику',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'orders': orders,
    })
    return render(request, 'dash/menu/admin/dash_admin_remade_order_send_to_subcotractor_date_list.html', context)


# order-temp-stop-remadeorder-date
@login_required(redirect_field_name=None, login_url='/')
def remade_order_send_to_subcotractor_date(request, order_id):
    user_ = request.user
    context = dash_get_info(request)

    check_order_bool = check_order('Приостановлено (уведомление отправлено)', order_id, user_, request)

    if check_order_bool == True:
        order = Order.objects.get(id=order_id)

        context.update({
            'counter': get_counter(user_),
            'order': order,
            'title': 'Информация по возобновлению'
        })
        return render(request, 'dash/menu/admin/dash_admin_remade_order_send_to_subcotractor_date.html', context)
    else:
        return check_order_bool


# сохранение даты приостановки
@login_required(redirect_field_name=None, login_url='/')
def save_remade_order_send_to_subcotractor_date(request):
    if request.method == 'POST':
        user_ = request.user
        data = request.POST
        order = Order.objects.get(id=data['orderID'])
        remade_order_sent_to_subcontractor_date = date_to_db(data['remade_order_sent_to_subcontractor_date'])
        end_date_after_temp_stop_for_responsible = date_to_db(data['remade_order_subcontractor_end_date_for_docs'])

        notification_temp_stop_db = NotificationTempStop.objects.filter(order=order).latest('added')
        temp_stop_db = TempStop.objects.get(notification=notification_temp_stop_db)
        temp_stop_db.remade_order_sent_to_subcontractor_date = remade_order_sent_to_subcontractor_date
        temp_stop_db.end_date_after_temp_stop_for_responsible = end_date_after_temp_stop_for_responsible
        temp_stop_db.save()

        set_order_status(order, 'Приостановлено (дата доработки)', request.user)

        counters_responsible_db, created = Counters.objects.get_or_create(user=order.responsible_preliminary)
        if created:
            counters_responsible_db.save()
        temp_stop_remade_order_date_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (дата доработки)'), \
                                  responsible_preliminary=order.responsible_preliminary).count()
        temp_stop_with_notification_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (уведомление отправлено)'), \
                                  responsible_preliminary=order.responsible_preliminary).count()
        counters_responsible_db.temp_stop_remade_order_date = temp_stop_remade_order_date_cnt
        counters_responsible_db.temp_stop_with_notification = temp_stop_with_notification_cnt
        counters_responsible_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_remade_order_date_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (уведомление отправлено)'))).count()
        counters_admin_db.admin_remade_order_date = admin_remade_order_date_cnt
        counters_admin_db.save()

        status_change_without_order_status(order,
                                           OrderStatus.objects.get(name='Дата возобновления отправлена исполнителю'),
                                           request.user)
        return HttpResponse('ok')


# nav_new_orders_for_experts_to_check_after_temp_stop
@login_required(redirect_field_name=None, login_url='/')
def appoint_expert_for_order_after_temp_stop_check_list(request):
    user_ = request.user
    context = dash_get_info(request)
    orders = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
                                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                    Q(responsible_after_temp_stop_check_expert__isnull=True) &
                                    (Q(check_after_temp_stop_refuse=True) | Q(check_after_temp_stop_ez=True)) &
                                    Q(check_after_temp_stop_pass_without_check=False)
                                  )
    experts = userprofile.objects.filter(role__name='Эксперт МБМ')
    context.update({
        'big_title': 'Проверка докментов после возобновления',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'orders': orders,
        'experts': experts

    })
    return render(request, 'dash/menu/admin/dash_admin_orders_for_after_temp_stop_check_list.html', context)


# appointExpertMBMToCheckAfterTempStopDocs
@login_required(redirect_field_name=None, login_url='/')
def appoint_expert_for_order_after_temp_stop_check(request):
    if request.method == 'POST':
        data = request.POST
        expertID = data.get('expertID')
        orderID = data.get('orderID')
        order = Order.objects.get(id=orderID)
        expert = User.objects.get(id=expertID)
        check_after_temp_stop_db = CheckAfterTempStop.objects.filter(order=order).latest('added')
        check_preliminary_after_temp_stop_expert_db = CheckAfterTempStopResponsibleExpert()
        check_preliminary_after_temp_stop_expert_db.check_after_temp_stop = check_after_temp_stop_db
        check_preliminary_after_temp_stop_expert_db.responsible_expert = expert
        check_preliminary_after_temp_stop_expert_db.user = request.user

        check_preliminary_after_temp_stop_expert_db.save()
        order.responsible_after_temp_stop_check_expert = expert
        order.save()
        counters_expert_db, created = Counters.objects.get_or_create(user=expert)
        if created:
            counters_expert_db.save()
        check_orders_to_check_after_temp_stop_cnt = Order.objects.filter(Q(responsible_after_temp_stop_check_expert=expert) &
                                                                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                                                    Q(check_after_temp_stop_finals_files_uploaded=False)).count()
        counters_expert_db.check_orders_to_check_after_temp_stop = check_orders_to_check_after_temp_stop_cnt
        counters_expert_db.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_distribution_after_temp_stop_cnt = Order.objects.filter(Q(status=OrderStatus.objects.get(name='Приостановлено (принятие решение по доработке (на проверке))')) &
                                    Q(check_after_temp_stop_files_for_check_uploaded=True) &
                                    Q(responsible_after_temp_stop_check_expert__isnull=True) &
                                    (Q(check_after_temp_stop_refuse=True) | Q(check_after_temp_stop_ez=True)) &
                                    Q(check_after_temp_stop_pass_without_check=False)
                                  ).count()
        counters_admin_db.admin_distribution_after_temp_stop = admin_distribution_after_temp_stop_cnt
        counters_admin_db.save()
        status_change_without_order_status(order,
                                           OrderStatus.objects.get(name='Проверяющий назначен (проверка после возобновления)'),
                                           request.user)
        return HttpResponse(admin_distribution_after_temp_stop_cnt)


# nav_companies
@login_required(redirect_field_name=None, login_url='/')
def companies_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()

    context.update({
        'big_title': 'Компании',
        'title': 'Выберите компанию',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'roles': Role.objects.all(),
        'companies': Company.objects.all()
    })
    return render(request, 'dash/menu/admin/dash_admin_companies_list.html', context)


# nav_all_orders_list_admin
@login_required(redirect_field_name=None, login_url='/')
def all_orders_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()

    context.update({
        'big_title': 'Добавление подписанного экспертного заключения',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'orders': Order.objects.all()
    })
    return render(request, 'dash/menu/admin/dash_admin_all_orders_list.html', context)


# nav_new_orders_send_for_check
@login_required(redirect_field_name=None, login_url='/')
def order_info(request, order_id):

    context = dash_get_info(request)
    order = Order.objects.get(id=order_id)
    applier = Applier.objects.get(order=order)
    responsibles_for_order_preliminary = ResponsibleForOrderPreliminary.objects.filter(order=order)
    responsibles_for_order_after_temp_stop = ResponsibleForOrderAfterTempStop.objects.filter(order=order)
    check_preliminary_responsible_experts = CheckPreliminaryResponsibleExpert.objects.filter(check_preliminary__order=order)
    check_preliminary_files_to_check = CheckPreliminaryFileToCheck.objects.filter(check_preliminary__order=order)
    check_preliminary_files_returned_check = CheckPreliminaryFileToCheckReturned.objects.filter(check_preliminary_file_to_check__check_preliminary__order=order)
    check_preliminary_files_final_check = CheckPreliminaryFileToCheckFinal.objects.filter(check_preliminary_file_to_check__check_preliminary__order=order)

    check_after_temp_stop_responsible_experts = CheckAfterTempStopResponsibleExpert.objects.filter(check_after_temp_stop__order=order)
    check_after_temp_stop_files_to_check = CheckAfterTempStopFileToCheck.objects.filter(check_after_temp_stop__order=order)
    check_after_temp_stop_files_returned_check = CheckAfterTempStopFileToCheckReturned.objects.filter(check_after_temp_stop_file_to_check__check_after_temp_stop__order=order)
    check_after_temp_stop_files_final_check = CheckAfterTempStopFileToCheckFinal.objects.filter(check_after_temp_stop_file_to_check__check_after_temp_stop__order=order)
    try:
        temp_stop_notification = NotificationTempStop.objects.filter(order=order)
    except NotificationTempStop.DoesNotExist:
        temp_stop_notification = None
    if temp_stop_notification:
        temp_stop = TempStop.objects.filter(notification=temp_stop_notification.latest('added')).latest('added')
        temp_stop_files = TempStopFiles.objects.filter(temp_stop=temp_stop)
    else:
        temp_stop = None
        temp_stop_files = None

    try:
        notification_refuse = NotificationRefuse.objects.filter(order=order)
    except Refuse.DoesNotExist:
        notification_refuse = None
    if notification_refuse:
        refuse = Refuse.objects.filter(notification=notification_refuse.latest('added')).latest('added')
        refuse_files = RefuseFiles.objects.filter(refuse=refuse)
    else:
        refuse = None
        refuse_files = None

    try:
        refuse_reasons_after_temp_stop = RefuseReasonsAfterTempStopByOrders.objects.filter(order=order)
    except ObjectDoesNotExist:
        refuse_reasons_after_temp_stop = None

    try:
        refuse_reasons_preliminary = RefuseReasonsPreliminaryByOrders.objects.filter(order=order)
    except ObjectDoesNotExist:
        refuse_reasons_preliminary = None


    try:
        ez_doc = EZdoc.objects.filter(order=order)
    except EZdoc.DoesNotExist:
        ez_doc = None

    if ez_doc:
        ez_pdf = EZpdf.objects.filter(ez_doc__order=order)
    else:
        ez_pdf = None

    try:
        appointed_for_ok = AppointedForOK.objects.filter(ready_for_OK__order=order)
    except AppointedForOK.DoesNotExist:
        appointed_for_ok = None

    try:
        protocol_orders = ProtocolOrders.objects.filter(appointed_for_ok__ready_for_OK__order=order)
    except ProtocolOrders.DoesNotExist:
        protocol_orders = None



    status_change_history = StatusChange.objects.filter(order=order).order_by('-added')
    print(order)
    context.update({
        'order': order,
        'counter': get_counter(request.user),
        'applier': applier,
        'responsibles_for_order_preliminary': responsibles_for_order_preliminary,
        'responsibles_for_order_after_temp_stop': responsibles_for_order_after_temp_stop,
        'check_preliminary_responsible_experts': check_preliminary_responsible_experts,
        'check_after_temp_stop_responsible_experts': check_after_temp_stop_responsible_experts,
        'check_after_temp_stop_files_to_check': check_after_temp_stop_files_to_check,
        'check_after_preliminary_files_to_check': check_preliminary_files_to_check,
        'check_after_temp_stop_files_returned_check': check_after_temp_stop_files_returned_check,
        'check_after_temp_stop_files_final_check': check_after_temp_stop_files_final_check,
        'check_preliminary_files_returned_check': check_preliminary_files_returned_check,
        'check_preliminary_files_final_check': check_preliminary_files_final_check,
        'status_change_history': status_change_history,
        'temp_stop': temp_stop,
        'temp_stop_files': temp_stop_files,
        'temp_stop_notification': temp_stop_notification,
        'notification_refuse': notification_refuse,
        'refuse': refuse,
        'refuse_files': refuse_files,
        'ez_docs': ez_doc,
        'ez_pdfs': ez_pdf,
        'appointed_for_ok': appointed_for_ok,
        'protocol_orders': protocol_orders,
        'refuse_reasons_after_temp_stop': refuse_reasons_after_temp_stop,
        'refuse_reasons_preliminary': refuse_reasons_preliminary
    })
    return render(request, 'dash/menu/admin/dash_admin_order_info.html', context)


# nav_new_orders_send_for_check
@login_required(redirect_field_name=None, login_url='/')
def get_user_role_name(request):
    context = dash_get_info(request)
    userprofile = context['user_profile']
    user_role_name = userprofile.role.name
    return HttpResponse(user_role_name)


@login_required(redirect_field_name=None, login_url='/')
def all_counters_responsible(user_instance):
    orders = Order.objects.filter(Q(responsible_after_temp_stop=user_instance) & Q(responsible_preliminary=user_instance))

    counters_db, created = Counters.objects.get_or_create(user=user_instance)
    if created:
        counters_db.save()
    # предварительная проверка
    new_orders = Order.objects.filter(status=OrderStatus.objects.get(name='Регистрация/На предварительной проверке'), \
                                      responsible_preliminary=user_instance).count()
    ez_doc_preliminary = Order.objects.filter(status=OrderStatus.objects.get(name='В работе'), \
                                              responsible_after_temp_stop=user_instance).count()
    ez_doc_after_temp_stop = Order.objects.filter(status=OrderStatus.objects.get(name='В работе после приостановления'), \
                                                  responsible_after_temp_stop=user_instance).count()

    counters_db.new_orders = new_orders
    counters_db.ez_doc = ez_doc_preliminary + ez_doc_after_temp_stop

    temp_stop_date = Order.objects.filter(status=OrderStatus.objects.get(name='Приостановлено (без даты приостановки)'), \
                                          responsible_preliminary=user_instance).count()
    counters_db.temp_stop_date = temp_stop_date

    refuse_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Отказ первичный (без загрузки в ИАС)'), \
                                      responsible_preliminary=user_instance).count()
    counters_db.refuse_preliminary = refuse_cnt


# nav_all_orders_list_admin
@login_required(redirect_field_name=None, login_url='/')
def ready_for_ok_orders_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()
    orders = ReadyForOK.objects.filter(appointed_ok=False)
    commission_dates = CommissionDate.objects.all()
    context.update({
        'big_title': 'Подготовленные для отраслевой комиссии ЭЗ',
        'title': 'Выберите заявки',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'orders': orders,
        'commission_dates': commission_dates
    })
    return render(request, 'dash/menu/admin/dash_admin_ready_for_ok_orders_list.html', context)


# appointExpertMBMToCheckAfterTempStopDocs
@login_required(redirect_field_name=None, login_url='/')
def ready_for_ok_orders_download(request):
    if request.method == 'POST':
        data = request.POST
        arr = data.getlist('arr')

        files_path = os.path.join(settings.MEDIA_ROOT, u"готово для ОК/")
        if not os.path.exists(files_path):
            os.mkdir(files_path)
            print(files_path)
        for ready_for_ok_id in arr:
            ready_for_ok_db = ReadyForOK.objects.get(id=ready_for_ok_id)
            file_path_order = files_path + ready_for_ok_db.order.number

            os.mkdir(file_path_order)

            try:
                temp_stop_files = TempStopFiles.objects.filter(temp_stop__notification=NotificationTempStop.objects.filter(order=ready_for_ok_db.order).latest('added')).latest('added')
                copy(temp_stop_files.file_notification.path, file_path_order)
            except ObjectDoesNotExist:
                temp_stop_files = None
            copy(ready_for_ok_db.pdf_file.path, file_path_order)
            copy(ready_for_ok_db.doc_file.path, file_path_order)
        path_to_zip = make_archive(files_path, "zip", files_path)
        print(os.path.basename(path_to_zip))
        # response = HttpResponse(FileWrapper(open(path_to_zip, 'rb')), content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename=222.zip'
        rmtree(files_path)
        # os.remove(settings.MEDIA_ROOT + '/' + os.path.basename(path_to_zip))

        return HttpResponse(os.path.basename(path_to_zip))


# сохранение рассметренных на ОК заявок
@login_required(redirect_field_name=None, login_url='/')
def save_ready_for_ok_orders(request):
    if request.method == 'POST':
        data = request.POST
        next_ok_arr = data.getlist('next_ok_arr')
        passed_ok_arr = data.getlist('passed_ok_arr')
        if data.get('ok_date'):
            ok_date = date_to_db(data['ok_date'])
        commission_id = data.get('commissionID')

        try:
            commission_date_db = CommissionDate.objects.get(id=commission_id)
            print(commission_date_db.date)
        except CommissionDate.DoesNotExist:
            commission_date_db = CommissionDate()
            commission_date_db.user = request.user
            commission_date_db.date = ok_date
            commission_date_db.save()

        for ready_for_OK_id in next_ok_arr:
            print(ready_for_OK_id)
            appointed_for_OK = AppointedForOK()
            appointed_for_OK.user = request.user
            appointed_for_OK.commission_date = commission_date_db
            ready_for_OK_db = ReadyForOK.objects.get(id=ready_for_OK_id)
            ready_for_OK_db.marked_for_next_ok = True
            ready_for_OK_db.save()
            appointed_for_OK.ready_for_OK = ready_for_OK_db
            appointed_for_OK.marked_for_next_ok = True

            appointed_for_OK.save()
            status_change_without_order_status(ready_for_OK_db.order,
                                               OrderStatus.objects.get(name='Готово (рассмотрено на ОК_перенос)'),
                                               request.user)

        # print(json.loads(passed_ok_arr[0]))
        for passed_ok in json.loads(passed_ok_arr[0]):
            appointed_for_OK = AppointedForOK()
            appointed_for_OK.user = request.user
            appointed_for_OK.commission_date = commission_date_db
            ready_for_OK_db = ReadyForOK.objects.get(id=passed_ok['ready_for_ok_id'])
            ready_for_OK_db.appointed_ok = True
            ready_for_OK_db.save()
            order = ready_for_OK_db.order
            set_order_status(order, 'Готово (рассмотрено на ОК)', request.user)
            appointed_for_OK.ready_for_OK = ready_for_OK_db
            appointed_for_OK.max_sum = passed_ok['sum']
            if passed_ok['decision'] == u'Положительное':
                appointed_for_OK.decision = True
            else:
                appointed_for_OK.decision = False
            appointed_for_OK.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_ready_for_ok_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово для ОК')).count()
        admin_appointed_for_ok_cnt = AppointedForOK.objects.filter(Q(protocol_issued=False)).count()
        counters_admin_db.admin_ready_for_ok = admin_ready_for_ok_cnt
        counters_admin_db.appointed_for_ok = admin_appointed_for_ok_cnt
        counters_admin_db.save()

        print(data)
        return HttpResponse('')


# nav_all_orders_list_admin
@login_required(redirect_field_name=None, login_url='/')
def appointed_for_ok_orders_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()
    orders = AppointedForOK.objects.filter(Q(protocol_issued=False))
    protocols = Protocol.objects.all()
    context.update({
        'big_title': 'Рассмотренные на ОК заявки',
        'title': 'Выберите заявки',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'orders': orders,
        'protocols': protocols
    })
    return render(request, 'dash/menu/admin/dash_admin_appointed_for_ok_orders_list.html', context)


# сохранение заявок для протокола
@login_required(redirect_field_name=None, login_url='/')
def save_orders_for_protocol(request):
    if request.method == 'POST':
        data = request.POST
        print(data)

        protocol_ok_arr = data.getlist('protocol_ok_arr')
        for order in json.loads(protocol_ok_arr[0]):
            appointed_for_ok_db = AppointedForOK.objects.get(id=order['appointed_for_ok_id'])
            appointed_for_ok_db.protocol_issued = True
            appointed_for_ok_db.save()
            if data.get('protocolID'):
                protocol_db = Protocol.objects.get(id=data.get('protocolID'))
            else:
                protocol_db = Protocol()
                protocol_db.protocol_date = date_to_db(data['protocol_date'])
                protocol_db.protocol_number = data['protocol_number']
                protocol_db.user = request.user
                protocol_db.save()
            protocol_orders_db = ProtocolOrders()
            protocol_orders_db.appointed_for_ok = appointed_for_ok_db
            protocol_orders_db.protocol = protocol_db

            protocol_orders_db.max_sum = order['sum']
            if order['decision'] == u'Положительное':
                protocol_orders_db.decision = True
            else:
                protocol_orders_db.decision = False
            protocol_orders_db.user = request.user
            protocol_orders_db.save()
            set_order_status(appointed_for_ok_db.ready_for_OK.order, 'Готово (протокол выпущен)', request.user)

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        admin_appointed_for_ok_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Готово (рассмотрено на ОК)')).count()
        admin_protocol_orders_cnt = Order.objects.filter(status=OrderStatus.objects.get(name=u'Готово (протокол выпущен)')).count()

        counters_admin_db.appointed_for_ok = admin_appointed_for_ok_cnt
        counters_admin_db.admin_protocols_orders = admin_protocol_orders_cnt
        counters_admin_db.save()

        return HttpResponse('')


# nav_orders_protocols_list
@login_required(redirect_field_name=None, login_url='/')
def protocols_orders_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()
    protocols_orders = ProtocolOrders.objects.all()
    context.update({
        'big_title': 'Протоколы отраслевых комиссий',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'protocols_orders': protocols_orders
    })
    return render(request, 'dash/menu/admin/dash_admin_protocols_orders_list.html', context)


@login_required(redirect_field_name=None, login_url='/')
def save_orders_for_protocol_file(request):
    if request.method == 'POST':
        data = request.POST
        orders = json.loads(data['orders'])

    #     # print(orders[0][0]['Номер заявки'])
        print(data)
    #     #982-ПП
    #     cnt = 0
    #     existing_orders = []
    #     response = {}

        if data.get('protocolID'):
            protocol_db = Protocol.objects.get(id=data.get('protocolID'))
            print(protocol_db.id)
        else:
            protocol_db = Protocol()
            protocol_db.user = request.user
            protocol_db.protocol_date = date_to_db(data.get('protocol_date'))
            protocol_db.protocol_number = date_to_db(data.get('protocol_number'))
            protocol_db.save()
            print(data.get('protocol_number'))
            print(data.get('protocol_date'))
        for order in orders[0]:
            appointed_for_ok = AppointedForOK.objects.filter(ready_for_OK=ReadyForOK.objects.get(order__number=order['Номер заявки'])).earliest('commission_date__date')
            print(appointed_for_ok.ready_for_OK.order.company)
            print(appointed_for_ok.commission_date.date)
            protocol_order_db = ProtocolOrders()
            protocol_order_db.protocol = protocol_db
            protocol_order_db.user = request.user
            protocol_order_db.appointed_for_ok = appointed_for_ok
            protocol_order_db.max_sum = order['Рекомендуемая сумма субсидии, руб.']
            protocol_order_db.decision = order['Решение']
            protocol_order_db.points = order['Балл']

    #         protocol_order
    #         new_order.added = datetime.now
    #         new_order.number = order['Номер заявки']
    #         new_order.date_of_appliance = order['Дата завершения (фактическая)']
    #         new_order.pp = PPnumber.objects.get(name=order['Номер НПА'])
    #         new_order.sum_of_appliance = order['Сумма запрашиваемой субсидии, рублей'].replace(',', '.')
    #         new_order.status = OrderStatus.objects.get(name='Новая')
    #         new_order.end_date = order['Крайняя дата ЭЗ']
    #         new_order.end_date_for_responsible = order['Крайняя дата ЭЗ для эксперта']
    #         new_order.aim = order['Цель поддержки']
    #         new_order.company = order['Наименование заявителя']
    #         new_order.company_inn = order['ИНН заявителя']
    #         new_order.service_name = order['Наименование сервиса']
    #         new_order.save()
    #
    #         new_order_applier = Applier()
    #         new_order_applier.user = request.user
    #         new_order_applier.order = new_order
    #         new_order_applier.applier_email = order['Email заявителя']
    #         new_order_applier.applier_tel = order['Телефон заявителя']
    #         new_order_applier.applier_fio = order['ФИО заявителя']
    #         new_order_applier.save()
    #         cnt = cnt + 1
    #
    #         status_change_db = StatusChange()
    #         status_change_db.user = request.user
    #         status_change_db.order = new_order
    #         status_change_db.status = OrderStatus.objects.get(name='Новая')
    #         status_change_db.save()
    #
    #     if len(existing_orders) > 0:
    #         response['existing_orders'] = existing_orders
    #
    #     new_orders_cnt = Order.objects.filter(status=OrderStatus.objects.get(name='Новая')).count()
    #     counter_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
    #     if created:
    #         counter_db.save()
    #     print('new_orders_cnt - ' + str(new_orders_cnt))
    #     counter_db.new_orders = new_orders_cnt
    #     counter_db.all_orders = Order.objects.all().count()
    #     counter_db.save()
    #
    #
    #     response['modalTitle'] = 'Данные по загрузке'
    #     response['cnt'] = cnt
    #     return JsonResponse(response)
    return HttpResponse()


# nav_onsite_checks_list
@login_required(redirect_field_name=None, login_url='/')
def onsite_checks_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()
    orders = Order.objects.filter((Q(onsite_check=True) & Q(onsite_check_complete=False)) &
                                  Q(status__name__contains='Готово'))
    context.update({
        'big_title': 'Заявки для осуществления выездной проверки',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'orders': orders
    })
    return render(request, 'dash/menu/admin/dash_admin_onsite_checks_list.html', context)


# onsite-check-order
@login_required(redirect_field_name=None, login_url='/')
def onsite_check(request, order_id):
    user_ = request.user
    context = dash_get_info(request)
    order = Order.objects.get(id=order_id)

    context.update({
        'big_title': 'Данные выездной проверки',
        'counter': get_counter(user_),
        'order': order,
        'title': 'Информация по возобновлению'
    })
    return render(request, 'dash/menu/admin/dash_admin_onsite_check.html', context)


# order-temp-stop-no-notification
@login_required(redirect_field_name=None, login_url='/')
def save_onsite_check(request):
    if request.method == 'POST':
        data = request.POST
        order = Order.objects.get(id=data['orderID'])

        date = date_to_db(data['onsite_check_date'])
        comments = data['comments']
        file_act = request.FILES['act_file']

        time_split = str(datetime.now().strftime('%H:%M:%S')).split(':')
        time_for_name = time_split[0] + '_' + time_split[1] + '_' + time_split[2]
        print(data)

        date_split = str(datetime.now().date()).split('-')
        date_for_name = date_split[2] + '_' + date_split[1] + '_' + date_split[0]

        file_name = order.number + '_' + order.company.replace('"', '_').strip() + '_' + date_for_name + '__' + time_for_name + '.pdf'
        print(date_for_name)

        onsite_check_db = OnsiteCheck()

        onsite_check_db.order = order
        onsite_check_db.date = date
        onsite_check_db.comments = comments
        onsite_check_db.user = request.user

        act_name = u'Акт_ВП_' + file_name.replace(' ', '')
        fs = FileSystemStorage()
        fs.save(act_name, file_act)
        onsite_check_db.act = act_name

        onsite_check_db.save()

        order.onsite_check_complete = True
        order.save()

        counters_admin_db, created = CountersAdmin.objects.get_or_create(user_role_name='Админ')
        if created:
            counters_admin_db.save()
        onsite_check_cnt = Order.objects.filter((Q(onsite_check=True) & Q(onsite_check_complete=False)) &
                                  Q(status__name__contains='Готово')).count()
        onsite_check_complete_cnt = Order.objects.filter(Q(onsite_check=True) & Q(onsite_check_complete=True)).count()

        counters_admin_db.admin_onsite_checks = onsite_check_cnt
        counters_admin_db.admin_onsite_checks_complete = onsite_check_complete_cnt
        counters_admin_db.save()

        return HttpResponse('')


# nav_onsite_checks_list
@login_required(redirect_field_name=None, login_url='/')
def onsite_checks_complete_list(request):
    context = dash_get_info(request)
    users_profiles = userprofile.objects.all()
    orders = OnsiteCheck.objects.all()
    context.update({
        'big_title': 'Выездные проверки осуществлены',
        'title': 'Выберите заявку',
        'counter': get_counter(request.user),
        'users_profiles': users_profiles,
        'onsite_check_orders': orders
    })
    return render(request, 'dash/menu/admin/dash_admin_onsite_checks_complete_list.html', context)


# onsite-check-order
@login_required(redirect_field_name=None, login_url='/')
def onsite_check_complete(request, order_id):
    user_ = request.user
    context = dash_get_info(request)
    onsite_check = OnsiteCheck.objects.get(id=order_id)

    context.update({
        'big_title': 'Данные выездной проверки',
        'counter': get_counter(user_),
        'order': onsite_check,
        'title': ''
    })
    return render(request, 'dash/menu/admin/dash_admin_onsite_complete_check.html', context)
