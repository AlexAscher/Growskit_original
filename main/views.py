import datetime
from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.core.exceptions import BadRequest
from django.contrib.auth.models import User

from .forms import *
from .models import *


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
    return render(request, 'sponsorstvo.html')

def sudeystvo(request):
    return render(request, 'sudeystvo.html')

def uchastie(request):
    def get_random_string(length):
        import random
        import string
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

    if request.method == 'POST':
        championship = Championship.objects.filter(last_date_registration__gte=datetime.date.today()).first()
        if not championship:
            raise Http404('Championship is not active')

        form = UchastieForm(request.POST, request.FILES)
        if not form.is_valid():
            raise BadRequest(form.errors.as_text())
        
        password = get_random_string(10)
        user = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=password,
        )
        uchastie = form.save(commit=False)
        uchastie.user = user
        uchastie.save()

        championship.participants.add(user)
        championship.save()

        from django.core.mail import send_mail
        send_mail(
            "Заявка на участие",
            "Ваша заявка на участие принята!\n\nИспользуйте для входа:\n"
            f"логин: {form.cleaned_data['email']}\nпароль: {password}",
            settings.EMAIL_HOST_USER,
            [form.cleaned_data['email']],
            fail_silently=False,
        )

        return redirect('index') # TODO: redirect to profile

    return render(request, 'uchastie.html')
