from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('magazine/', views.magazine, name='magazine'),
    path('participants/', views.participants, name='participants'),
    path('premiya/', views.premiya, name='premiya'),
    path('sponsorstvo/', views.sponsorstvo, name='sponsorstvo'),
    path('sudeystvo/', views.sudeystvo, name='sudeystvo'),
    path('uchastie/', views.uchastie, name='uchastie'),
]
