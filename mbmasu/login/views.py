from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

import json
# Create your views here.


def login_index(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        user_login = json_data['login']
        user_password = json_data['password']
        user = authenticate(username=user_login, password=user_password)
        if user is not None:
            if user.is_active:
                print(user.id)
                login(request, user)
                return HttpResponse(user.id)
        else:
            print('error')
            return HttpResponse(json.dumps({'response': 'error'}))

    return render(request, 'login/login.html')




