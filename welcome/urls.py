#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/12/7
# Time: 16:58
from django.conf.urls import url

from welcome import views

urlpatterns = [
    url(r'^welcome/$', views.welcome, name='welcome'),
]
