"""NLPwebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from sentence import views

urlpatterns = [
    url(r'^lookup_db/', views.lookup_db),
    url(r'^insert_db/', views.insert_db),
    url(r'^delete_db/', views.delete_db),
    url(r'^$', views.test),
    url(r'^process_data/$', views.process_data),
    url(r'^dev/$', views.url_way),
    url(r'^dev_test/$', views.url_way_test),
    url(r'^dev_scene/$', views.url_way_scene),
    url(r'^process_chat/$', views.process_chat),
]
