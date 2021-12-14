from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.login_index, name='login_index'),
    # url(r'^$', views.index, name='login_index'),
    # url(r'^signin', views.signin, name='signin'),

]