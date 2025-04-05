import datetime
import random
import string
from typing import Literal

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
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

def notify_user(subject, message, recipient, fail_silently=False):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient if isinstance(recipient, list) else [recipient],
        fail_silently=fail_silently,
    )

def notify_new_user(email, password):
    notify_user(
        "Заявка на чемпионат",
        "Ваша заявка на чемпионат принята!\n\nИспользуйте для входа:\n"
        f"логин: {email}\nпароль: {password}",
        email,
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


def api_manager(request: HttpRequest):
    if request.method == 'POST':
        if not request.POST.get('referal_key'):
            request.POST.setdefault('referal_key', get_random_string(100))
        save_with_new_user(request, ManagerForm, 'manager', check_championship=False, need_send_mail=False)

    raise BadRequest

def api_notify_user(request: HttpRequest):
    if request.method == 'POST':
        recipient = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        notify_user(subject, message, recipient)
    
    raise BadRequest

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

@user_passes_test(is_admin)
def judges_list(request):
    judges = ProfileJudge.objects.all()
    latest_championship = Championship.objects.order_by('-id').first()

    if request.method == "POST" and "update_criteries" in request.POST:
        criteries = request.POST.get("criteries")
        if latest_championship:
            latest_championship.criteries = criteries
            latest_championship.save()
        return redirect("judges_list")

    return render(request, "admin/judges_list.html", {"judges": judges, "latest_championship": latest_championship})

@user_passes_test(is_admin)
def add_judge(request):
    if request.method == "POST":
        form = AddJudgeForm(request.POST)
        if form.is_valid():
            # Создаем временного пользователя
            temp_user = User.objects.create_user(
                username=f"temp_{User.objects.count() + 1}",  # Уникальное имя пользователя
                email=form.cleaned_data['email'],
                password="temporarypassword123"  # Временный пароль
            )
            # Сохраняем судью с привязкой к созданному пользователю
            judge = form.save(commit=False)
            judge.user = temp_user
            judge.save()
            return redirect("judges_list")
    else:
        form = AddJudgeForm()

    return render(request, "admin/add_judge.html", {"form": form})

@user_passes_test(is_admin)
def sponsors_list(request):
    sponsors = ProfileSponsor.objects.all()

    if request.method == "POST" and "delete_sponsor" in request.POST:
        sponsor_id = request.POST.get("sponsor_id")
        sponsor = get_object_or_404(ProfileSponsor, id=sponsor_id)
        sponsor.user.delete()  # Удаляем связанного пользователя
        sponsor.delete()  # Удаляем запись спонсора
        return redirect("sponsors_list")

    return render(request, "admin/sponsors_list.html", {"sponsors": sponsors})

@user_passes_test(is_admin)
def add_sponsor(request):
    if request.method == "POST":
        form = AddSponsorForm(request.POST)
        if form.is_valid():
            # Создаем временного пользователя
            temp_user = User.objects.create_user(
                username=f"temp_sponsor_{User.objects.count() + 1}",  # Уникальное имя пользователя
                email=form.cleaned_data['email'],
                password="temporarypassword123"  # Временный пароль
            )
            # Сохраняем спонсора с привязкой к созданному пользователю
            sponsor = form.save(commit=False)
            sponsor.user = temp_user
            sponsor.save()
            return redirect("sponsors_list")
    else:
        form = AddSponsorForm()

    return render(request, "admin/add_sponsor.html", {"form": form})

@user_passes_test(is_admin)
def managers_list(request):
    managers = ProfileManager.objects.all()

    if request.method == "POST" and "delete_manager" in request.POST:
        manager_id = request.POST.get("manager_id")
        manager = get_object_or_404(ProfileManager, id=manager_id)
        manager.delete()  # Удаляем запись менеджера
        return redirect("managers_list")

    return render(request, "admin/managers_list.html", {"managers": managers})


@user_passes_test(is_admin)
def add_manager(request):
    if request.method == "POST":
        form = AddManagerForm(request.POST)
        if form.is_valid():
            # Создаем временного пользователя
            temp_user = User.objects.create_user(
                username=f"temp_manager_{User.objects.count() + 1}",
                email=f"temp_manager_{User.objects.count() + 1}@example.com",
                password="temporarypassword123"
            )
            # Сохраняем менеджера с привязкой к созданному пользователю
            manager = form.save(commit=False)
            manager.user = temp_user
            manager.save()
            return redirect("managers_list")
    else:
        form = AddManagerForm()

    return render(request, "admin/add_manager.html", {"form": form})

@user_passes_test(is_admin)
def championship_admin(request):
    championships = Championship.objects.all()

    if request.method == "POST" and "add_date" in request.POST:
        # Добавление новой даты проведения чемпионата
        name = request.POST.get("name")
        date = request.POST.get("date")
        last_date_registration = request.POST.get("last_date_registration")

        if name and date and last_date_registration:
            Championship.objects.create(
                name=name,
                date=date,
                last_date_registration=last_date_registration,
                criteries="Критерии пока не указаны"
            )
            return redirect("championship_admin")

    return render(request, "admin/championship_admin.html", {"championships": championships})
