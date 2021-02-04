""" testapp.api URL Configuration """
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('whoami/', views.WhoAmIView.as_view(), name='whoami'),
]
