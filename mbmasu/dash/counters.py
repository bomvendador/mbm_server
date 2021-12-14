from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.apps import apps
from .models import Order, OrderStatus, Applier, PPnumber, ResponsibleForOrderPreliminary, \
    ResponsibleForOrderAfterTempStop, Counters
from django.db.models import Q

userprofile = apps.get_model('login', 'UserProfile')


@login_required(redirect_field_name=None, login_url='/')
def counters(request):
    user_ = request.user
    user_profile = userprofile.objects.get(user=user_)
    user_role_name = user_profile.role.name
    # print('user_role_name - ' + user_role_name)
    # new_orders_cnt = None
    all_orders_cnt = None
    orders_in_work = None

    temp_stop_date = None

    return HttpResponse('ff')

