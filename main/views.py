import datetime
import random
import string
from typing import Literal

from django.conf import settings
from django.http import Http404, HttpRequest
from django.shortcuts import render, redirect
from django.core.exceptions import BadRequest
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail

from .forms import *
from .models import *


def get_random_string(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

def save_with_new_user(request: HttpRequest, cls: forms.ModelForm, type_user: Literal['participant', 'judge', 'sponsor'], check_championship=False, need_send_mail=False):
    championship: Championship = None
    if check_championship:
        championship = Championship.objects.filter(last_date_registration__gte=datetime.date.today()).first()
        if not championship:
            raise Http404('Championship is not active')

    form = cls(request.POST, request.FILES)
    if not form.is_valid():
        raise BadRequest(form.errors.as_text())
    
    password = get_random_string(10)
    user = User.objects.create_user(
        username=form.cleaned_data['email'],
        email=form.cleaned_data['email'],
        password=password,
    )
    user.groups.add(Group.objects.get(name=type_user+'s'))
    user.save()

    model = form.save(commit=False)
    model.user = user
    model.save()

    if championship:
        championship.__getattribute__(type_user+'s').add(user)
        championship.save()

    if need_send_mail:
        send_mail(
            "Заявка на чемпионат",
            "Ваша заявка на чемпионат принята!\n\nИспользуйте для входа:\n"
            f"логин: {form.cleaned_data['email']}\nпароль: {password}",
            settings.EMAIL_HOST_USER,
            [form.cleaned_data['email']],
            fail_silently=False,
        )


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

def uchastie(request):
    if request.method == 'POST':
        save_with_new_user(request, UchastieForm, 'participant', check_championship=True, need_send_mail=True)
        return redirect('index') # TODO: redirect to profile participant

    return render(request, 'uchastie.html')
