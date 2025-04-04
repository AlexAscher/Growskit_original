import datetime
import random
import string
from typing import Literal

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.exceptions import BadRequest
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse

from .forms import *
from .models import *

TYPE_USER = Literal['participant', 'judge', 'sponsor']

def get_random_string(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

def create_user(email, type_user: TYPE_USER):
    user = User.objects.filter(email=email).first()
    if user:
        return user, 'Ранее вы участвали в чемпионате. Проверьте почту или восстановите пароль'

    password = get_random_string(10)
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
    )

    group = Group.objects.get(name=type_user+'s')
    if group:
        user.groups.add(group)
        user.save()
    
    return user, password

def notify_new_user(email, password):
    send_mail(
        "Заявка на чемпионат",
        "Ваша заявка на чемпионат принята!\n\nИспользуйте для входа:\n"
        f"логин: {email}\nпароль: {password}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=True,
    )
    
def get_or_404_active_championship():
    championship = Championship.objects.filter(last_date_registration__gte=datetime.date.today()).first()
    if not championship:
        raise Http404('Championship is not active')

    return championship

def get_or_create(model, user, data):
    obj = model.objects.filter(user=user).first()
    if obj:
        return obj, False

    obj = model(user=user, **data)
    obj.save()
    return obj, True

def add_user_to_championship(championship: Championship, user, type_user: TYPE_USER):
    championship.__getattribute__(type_user+'s').add(user)
    championship.save()

def save_with_new_user(request: HttpRequest, cls: forms.ModelForm, type_user: TYPE_USER, check_championship=False, need_send_mail=False):
    championship: Championship = None
    if check_championship:
        championship = get_or_404_active_championship()

    form = cls(request.POST, request.FILES)
    if not form.is_valid():
        raise BadRequest(form.errors.as_text())
    
    user, password = create_user(form.cleaned_data['email'], type_user)

    model = form.save(commit=False)
    exited_model = model.__class__.objects.filter(user=user).first()
    if exited_model:
        model.id = exited_model.id
    model.user = user
    model.save()

    if championship:
        add_user_to_championship(championship, model, type_user)

    if need_send_mail:
        notify_new_user(form.cleaned_data['email'], password)


def index(request):
    return render(request, 'index.html')

def magazine(request):
    return render(request, 'magazine.html')

def participants(request):
    return render(request, 'participants.html')

def popup(request):
    return render(request, 'popup.html')

def premiya(request):
    return render(request, 'premiya.html')

def sponsorstvo(request):
    if request.method == 'POST':
        save_with_new_user(request, SponsorstvoForm, 'sponsor', check_championship=False, need_send_mail=False)
        return redirect('index') # TODO: redirect to profile sponsor

    return render(request, 'sponsorstvo.html')

def sudeystvo(request):
    if request.method == 'POST':
        save_with_new_user(request, SudeystvoForm, 'judge', check_championship=False, need_send_mail=True)
        return redirect('index') # TODO: redirect to profile judge

    return render(request, 'sudeystvo.html')

def uchastie(request: HttpRequest):
    if request.method == 'POST':
        if not request.POST.get('is_team'):
            save_with_new_user(request, UchastieForm, 'participant', check_championship=True, need_send_mail=True)
                
            if request.COOKIES.get('refer'):
                refer = ProfileManager.objects.filter(referal_key=request.COOKIES['refer']).first()
                if refer:
                    refer.referals += 1
                    refer.save()
        
            resp_redirect = HttpResponseRedirect(reverse('index')) # TODO: redirect to profile participant
            resp_redirect.delete_cookie('refer')
            return resp_redirect
        
        form = UchastieTeamForm(request.POST, request.FILES)
        if not form.is_valid():
            raise BadRequest(form.errors.as_text())
        
        championship = get_or_404_active_championship()
        
        user, password = create_user(form.cleaned_data['leader']['email'], 'leader')
        leader, _ = get_or_create(ProfileLeader, user, form.cleaned_data['leader'])
        team = Team.objects.create(name=form.cleaned_data['team_name'], leader=leader, championship=championship)
        team.leader = leader

        new_users = []
        for participant_data in form.cleaned_data['participants']:
            user, password = create_user(participant_data['email'], 'participant')
            new_users.append([participant_data['email'], password])
            participant, _ = get_or_create(ProfileParticipant, user, participant_data)
            team.members.add(participant)
            add_user_to_championship(championship, participant, 'participant')

        team.save()

        notify_new_user(form.cleaned_data['leader']['email'], password)
        for user in new_users:
            notify_new_user(user[0], user[1])

        return redirect('index') # TODO: redirect to profile team

    return render(request, 'uchastie.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

# Проверка: пользователь должен быть администратором
def is_admin(user):
    return user.is_superuser

@login_required
def custom_redirect(request):
    if request.user.is_superuser:
        return redirect('/participants_list/')  # Для администраторов
    return redirect('/')  # Для остальных пользователей

@user_passes_test(is_admin)
def participants_list(request):
    participants = ProfileParticipant.objects.all()
    return render(request, 'admin/participants_list.html', {'participants': participants})
