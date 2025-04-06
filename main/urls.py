from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('magazine/', views.magazine, name='magazine'),
    path('participants/', views.participants, name='participants'),
    path('premiya/', views.premiya, name='premiya'),
    path('sponsorstvo/', views.sponsorstvo, name='sponsorstvo'),
    path('sudeystvo/', views.sudeystvo, name='sudeystvo'),
    path('uchastie/', views.uchastie, name='uchastie'),
    path('participants_list/', views.participants_list, name='participants_list'),
    path('redirect/', views.custom_redirect, name='custom_redirect'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("judges/", views.judges_list, name="judges_list"),
    path("judges/add/", views.add_judge, name="add_judge"),
    path("sponsors/", views.sponsors_list, name="sponsors_list"),
    path("sponsors/add/", views.add_sponsor, name="add_sponsor"),
    path("managers/", views.managers_list, name="managers_list"),
    path("managers/add/", views.add_manager, name="add_manager"),
    path("championship/", views.championship_admin, name="championship_admin"),
    
    path('api/send_notify_of_days_left_registration/', views.send_notify_of_days_left_registration, name='send_notify_of_days_left_registration'),
    path("api/send_auth/", views.send_auth, name="send_auth"),
]
