from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path

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
    path("sponsors/", views.sponsors_list, name="sponsors_list"),
    path("managers/", views.managers_list, name="managers_list"),
    path("managers/add/", views.add_manager, name="add_manager"),
    path("championship/", views.championship_admin, name="championship_admin"),
    path('participant/dashboard/', views.participant_dashboard, name='participant_dashboard'),
    path('participant/upload_work/', views.upload_work, name='upload_work'),
    path('participant/upload_work/add_work_count/', views.update_work_count, name='update_work_count'),
    path('leader/participant_list/', views.leader_participant_list, name='leader_participant_list'),
    path('journals/', views.journal_list, name='journal_list'),
    path('awards/', views.award_list, name='award_list'),
    path('judge/welcome/', views.judge_welcome, name='judge_welcome'),
    path('judge/championship/', views.judge_championship, name='judge_championship'),
    path('current_championship/', views.current_championship_admin, name='current_championship_admin'),
    # API
    path(
        'api/send_notify_of_days_left_registration/',
        views.send_notify_of_days_left_registration,
        name='send_notify_of_days_left_registration',
    ),
    path("api/send_auth/", views.send_auth, name="send_auth"),
    path('api/change_status/', views.api_change_status, name='api_change_status'),
    path('api/sertificate_upload/', views.sertificate_upload, name='api_sertificate_upload'),
    path('api/judge_rate_work/', views.api_judge_rate_work, name='api_judge_rate_work'),
    path('api/set_group_tg', views.api_set_group_tg, name='api_set_group_tg'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
