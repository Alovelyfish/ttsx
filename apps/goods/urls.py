
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from apps.goods import views
urlpatterns = [
   url(r'^$', view=views.index, name='index')

]