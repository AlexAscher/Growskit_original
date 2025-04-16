import datetime
import json
import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import BadRequest
from django.db import models
from django.forms import ValidationError
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse

from .forms import (
    AddManagerForm,
    AwardRequestForm,
    ChampionshipForm,
    JournaRequestForm,
    SertificateForm,
    SponsorstvoForm,
    SudeystvoForm,
    UchastieForm,
    UchastieTeamForm,
)
from .models import (
    STATUS_APPROVED,
    AwardRequest,
    Championship,
    JournalRequest,
    Mark,
    PhotoList,
    ProfileJudge,
    ProfileLeader,
    ProfileManager,
    ProfileParticipant,
    ProfileSponsor,
    Team,
)
from .support import (
    TYPE_USER,
    create_user,
    get_group_tg,
    get_random_string,
    marks_to_form_value,
    notify_admin,
    notify_new_user,
    notify_user,
)


def get_active_championship(fail_silently=True):
    championship = Championship.objects.filter(last_date_registration__gte=datetime.date.today()).first()
    if not championship and not fail_silently:
        raise Http404('Championship is not active')

    return championship


def get_or_create_by_user[T](model: type[T] | models.Model, user: User, **data) -> tuple[T, bool]:
    obj = model.objects.filter(user=user).first()
    if obj:
        return obj, False

    return model.objects.create(user=user, **data), True


def add_profile_to_championship(championship: Championship, profile, type_user: TYPE_USER):
    try:
        field = getattr(championship, type_user + 's')
    except AttributeError:
        return
    field.add(profile)
    championship.save()


def save_with_new_user[T](
    request: HttpRequest,
    cls: type[T] | forms.ModelForm,
    type_user: TYPE_USER,
    check_championship=False,
    need_notify=False,
) -> tuple[T, bool]:
    championship: Championship = None
    if check_championship:
        championship = get_active_championship(False)

    form = cls(request.POST, request.FILES)
    if not form.is_valid():
        raise BadRequest(form.errors.as_text())

    user, password, created = create_user(form.cleaned_data['email'], type_user)

    model = form.save(commit=False)
    exited_model = model.__class__.objects.filter(user=user).first()
    if exited_model:
        model.id = exited_model.id
    model.user = user
    model.save()

    if championship:
        add_profile_to_championship(championship, model, type_user)

    if need_notify:
        notify_new_user(form.cleaned_data['email'], password)  # , tg=form.cleaned_data.get('telegram'))

    return model, created


def index(request):
    return render(request, 'index.html')


def magazine(request: HttpRequest):
    if request.method == 'POST':
        request.POST = request.POST.copy()

        packet = request.POST.get('packet')

        if packet == 'default':
            request.POST.setdefault('count_pages', 1)
        elif packet == 'default2':
            request.POST.setdefault('count_pages', 2)
        elif packet == 'default3':
            request.POST.setdefault('need_cover', True)
            request.POST.setdefault('count_pages', 2)
        elif packet == 'minimagazine':
            request.POST.setdefault('count_pages', 1)
            request.POST.setdefault('need_cup_and_elite', True)
            request.POST.setdefault('need_journal', True)
        elif packet == 'platinummagazine':
            request.POST.setdefault('count_pages', 2)
            request.POST.setdefault('need_cup_and_elite', True)
            request.POST.setdefault('need_journal', True)
        elif packet == 'goldmagazine':
            request.POST.setdefault('count_pages', 2)
            request.POST.setdefault('need_cup_and_elite', True)
            request.POST.setdefault('need_journal', True)
            request.POST.setdefault('need_cover', True)

        form = JournaRequestForm(request.POST, request.FILES)
        
        if not packet:
            form.add_error('packet', ValidationError("Выберите пакет"))

        if not form.is_valid():
            raise BadRequest(form.errors.as_text())
        
        model = form.save(commit=False)
        
        def save_business_awards():
            data = request.POST.copy()
            data.setdefault('bio', '<Создано автоматически>')
            data.setlist('nomination', ['growing_business_awards'])
            business = AwardRequestForm(data)
            if not business.is_valid():
                if not (len(business.errors) == 1 and 'photo' in business.errors):
                    raise BadRequest(business.errors.as_text())
                business.errors.clear()
            business.instance.photo = model.photo
            business.save()


        if packet == 'minimagazine':
            save_business_awards()
        elif packet == 'platinummagazine':
            save_business_awards()  
        elif packet == 'goldmagazine':
            save_business_awards()       

        form.save()

        notify_admin(
            'Заявка на место в журнале', f'{model}' + '\nПодробности в личном кабинете', 'ALL', tg=get_group_tg()
        )

    return render(request, 'magazine.html')


def participants(request):
    return render(request, 'participants.html')


def popup(request):
    return render(request, 'popup.html')


def premiya(request: HttpRequest):
    if request.method == 'POST':
        form = AwardRequestForm(request.POST, request.FILES)
        packet = request.POST.get('packet')
        if not packet:
            form.add_error('packet', ValidationError("Выберите пакет"))
        
        if not form.is_valid():
            raise BadRequest(form.errors.as_text())
        
        
        model = form.save(commit=False)
        
        def save_business_awards():
            data = request.POST.copy()
            data.setlist('nomination', ['growing_business_awards'])
            business = AwardRequestForm(data)
            if not business.is_valid():
                if not (len(business.errors) == 1 and 'photo' in business.errors):
                    raise BadRequest(business.errors.as_text())
                business.errors.clear()
            business.instance.photo = model.photo
            business.save()
        
        def save_journal(count_pages, need_journal, need_cover, need_cup_and_elite):
            data = request.POST.copy()
            data.setdefault('count_pages', count_pages)
            data.setdefault('need_journal', need_journal)
            data.setdefault('need_cover', need_cover)
            data.setdefault('need_cup_and_elite', need_cup_and_elite)
            journal = JournaRequestForm(data)
            if not journal.is_valid():
                if not (len(journal.errors) == 1 and 'photo' in journal.errors):
                    raise BadRequest(journal.errors.as_text())
                journal.errors.clear()
            journal.instance.photo = model.photo
            journal.save()


        if packet == 'default':
            save_business_awards()
        elif packet == 'mini':
            save_business_awards()
            save_journal(1, True, False, True)
        elif packet == 'platinum':
            save_business_awards()
            save_journal(2, True, False, True)  
        elif packet == 'gold':
            save_business_awards()
            save_journal(2, True, True, True)       

        form.save()

        notify_admin('Заявка на премию', f'{model}' + '\nПодробности в личном кабинете', 'ALL', tg=get_group_tg())

    return render(request, 'premiya.html')


def sponsorstvo(request):
    if request.method == 'POST':
        model, created = save_with_new_user(
            request, SponsorstvoForm, 'sponsor', check_championship=False, need_notify=False
        )

        if created:
            notify_admin(
                'Заявка на спонсорство', f'{model}' + '\nПодробности в личном кабинете', 'ALL', tg=get_group_tg()
            )
        return redirect('index')  # TODO: redirect to profile sponsor

    return render(request, 'sponsorstvo.html')


def sudeystvo(request):
    if request.method == 'POST':
        model, created = save_with_new_user(request, SudeystvoForm, 'judge', check_championship=False, need_notify=True)

        if created:
            notify_admin('Заявка на судью', f'{model}' + '\nПодробности в личном кабинете', 'ALL', tg=get_group_tg())
        return redirect('index')  # TODO: redirect to profile judge

    return render(request, 'sudeystvo.html')


def uchastie(request: HttpRequest):
    if request.method == 'POST':
        if not request.POST.get('is_team'):
            model, created = save_with_new_user(
                request, UchastieForm, 'participant', check_championship=True, need_notify=True
            )

            if request.COOKIES.get('refer') and created:
                refer = ProfileManager.objects.filter(referal_key=request.COOKIES['refer']).first()
                if refer:
                    refer.referals += 1
                    refer.save()

            if created:
                notify_admin(
                    'Заявка на участие', f'{model}' + '\nПодробности в личном кабинете', 'ALL', tg=get_group_tg()
                )

            resp_redirect = HttpResponseRedirect(reverse('index'))  # TODO: redirect to profile participant
            resp_redirect.delete_cookie('refer')
            return resp_redirect

        form = UchastieTeamForm(request.POST, request.FILES)
        if not form.is_valid():
            raise BadRequest(form.errors.as_text())

        championship = get_active_championship(False)

        user, password, _ = create_user(form.cleaned_data['leader']['email'], 'leader')
        leader, _ = get_or_create_by_user(ProfileLeader, user, **form.cleaned_data['leader'])
        team = Team.objects.filter(name=form.cleaned_data['team_name']).first()
        if team and team.leader != leader:
            raise BadRequest('Команда с таким названием уже зарегистрирована')
        if not team:
            team = Team.objects.create(name=form.cleaned_data['team_name'], leader=leader, championship=championship)
        
        new_users = []
        real_new = []
        for participant_data in form.cleaned_data['participants']:
            user, password, _ = create_user(participant_data['email'], 'participant')
            new_users.append([participant_data['email'], password, participant_data.get('tg') or participant_data.get('telegram')])
            participant, created = get_or_create_by_user(ProfileParticipant, user, **participant_data)
            team.members.add(participant)
            if created:
                real_new.append(participant)
            add_profile_to_championship(championship, participant, 'participant')

        team.save()

        notify_new_user(form.cleaned_data['leader']['email'], password)  # , tg=form.cleaned_data['leader']['tg'])
        # for user in new_users: # не отправлять доступ участникам
        #    notify_new_user(user[0], user[1], tg=user['tg'])

        if request.COOKIES.get('refer'):
            refer = ProfileManager.objects.filter(referal_key=request.COOKIES['refer']).first()
            if refer:
                refer.referals += len(real_new)
                refer.save()

        notify_admin(
            'Заявка на участие',
            f'Команда: {team}\n' + '\n'.join(real_new) + '\nПодробности в личном кабинете',
            'ALL',
            tg=get_group_tg(),
        )

        return redirect('index')  # TODO: redirect to profile team

    return render(request, 'uchastie.html')


@login_required
def send_auth(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            data = json.loads(request.body.decode('utf-8') or '{}')
            email = data.get('email')
        user = get_object_or_404(User, email=email)
        password = get_random_string(10)
        user.set_password(password)
        user.save()

        subject = 'Доступ к ЛК Чемпионата'
        message = f'Вам предоставлен доступ к ЛК Чемпионата.\nЛогин: {user.username}\nПароль: {password}'
        notify_user(subject, message, user.email)  # , tg=request.POST.get('telegram'))
        return HttpResponse('{"status": "OK"}')

    raise BadRequest


@login_required
def send_notify_of_days_left_registration(request: HttpRequest):
    if request.method == 'POST':
        data = request.POST
        if not data.get('championship_id'):
            data = json.loads(request.body.decode('utf-8') or '{}')
        
        championship = get_object_or_404(Championship, id=data.get('championship_id'))

        members = championship.participants.all()
        for member in members:
            subject = 'Чемпионат ' + championship.name
            days = championship.get_days_left()
            if days == 0:
                message = 'Сегодня последний день регистрации'
            else:
                message = f'До конца регистрации осталось {days} дней'
            notify_user(subject, message, member.email)  # , tg=member.tg)

        notify_admin(
            'Чемпионат ' + championship.name, f'До конца регистрации осталось {days} дней', 'ALL', tg=get_group_tg()
        )

        return JsonResponse({'status': 'OK', 'notified': members.count()})

    raise BadRequest


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/participants_list/'  # Перенаправление для администраторов

        if hasattr(user, 'profileparticipant'):
            return '/participant/dashboard/'  # Перенаправление для участников

        if hasattr(user, 'profilejudge'):
            return '/judge/welcome/'  # Перенаправление для судей
        return '/'  # Перенаправление для остальных пользователей


# Проверка: пользователь должен быть администратором
def is_admin(user):
    return user.is_superuser


@login_required
def custom_redirect(request):
    user = request.user

    # Проверяем, является ли пользователь администратором
    if user.is_superuser:
        return redirect('/participants_list/')  # Перенаправляем администраторов

    # Проверяем, является ли пользователь участником
    if hasattr(user, 'profileparticipant'):
        return redirect('/participant/dashboard/')  # Перенаправляем участников

    # Проверяем, является ли пользователь судьей
    if hasattr(user, 'profilejudge'):
        return redirect('/judge/welcome/')  # Перенаправляем судей

    if hasattr(user, 'profileleader'):
        return redirect('/leader/participant_list/')

    # Если пользователь не попадает ни в одну из категорий
    return redirect('/')  # Перенаправляем на главную страницу


@login_required
@user_passes_test(is_admin)
def participants_list(request):
    participants = ProfileParticipant.objects.all()
    works_by_participant = {}

    for participant in participants:
        works = PhotoList.objects.filter(user=participant.user).order_by('work_id')
        grouped_works = {}
        for work in works:
            if work.work_id not in grouped_works:
                grouped_works[work.work_id] = {'nomination': work.get_nomination_display(), 'photos': []}
            grouped_works[work.work_id]['photos'].append(work)
        works_by_participant[participant.id] = grouped_works

    return render(
        request,
        'admin/participants_list.html',
        {
            'participants': participants,
            'works_by_participant': works_by_participant,
            'championship': get_active_championship(True),
            'statuses': STATUS_APPROVED,
        },
    )


@login_required
@user_passes_test(is_admin)
def judges_list(request):
    judges = ProfileJudge.objects.all()
    latest_championship = get_active_championship(True)

    if request.method == "POST":
        if "criteries" in request.FILES:
            criteries = request.FILES.get("criteries")
            if latest_championship:
                latest_championship.criteries = criteries
                latest_championship.save()

        if "status" in request.POST:
            judge: ProfileJudge = get_object_or_404(ProfileJudge, id=request.POST.get("id"))
            approved = request.POST.get("status")
            judge.approved = approved
            judge.save()
        return redirect("judges_list")

    return render(
        request,
        "admin/judges_list.html",
        {"judges": judges, "latest_championship": latest_championship, "statuses": STATUS_APPROVED},
    )


@login_required
@user_passes_test(is_admin)
def sponsors_list(request):
    sponsors = ProfileSponsor.objects.all()

    if request.method == "POST":
        sponsor_id = request.POST.get("sponsor_id")
        sponsor = get_object_or_404(ProfileSponsor, id=sponsor_id)

        if "delete_sponsor" in request.POST:
            sponsor.user.delete()  # Удаляем связанного пользователя
            sponsor.delete()  # Удаляем запись спонсора
            return redirect("sponsors_list")

        if 'status' in request.POST:
            status = request.POST.get('status')
            sponsor.approved = status

        if "logo" in request.FILES:
            logo = request.FILES.get("logo")
            sponsor.photo = logo

        sponsor.save()
        return redirect("sponsors_list")

    return render(request, "admin/sponsors_list.html", {"sponsors": sponsors, "statuses": STATUS_APPROVED})


@login_required
@user_passes_test(is_admin)
def managers_list(request):
    managers = ProfileManager.objects.all()

    if request.method == "POST" and "delete_manager" in request.POST:
        manager_id = request.POST.get("manager_id")
        manager = get_object_or_404(ProfileManager, id=manager_id)
        manager.delete()  # Удаляем запись менеджера
        return redirect("managers_list")

    return render(request, "admin/managers_list.html", {"managers": managers})


@login_required
@user_passes_test(is_admin)
def add_manager(request):
    if request.method == "POST":
        form = AddManagerForm(request.POST)
        if form.is_valid():
            # Создаем временного пользователя
            temp_user = User.objects.create_user(
                username=f"temp_manager_{User.objects.count() + 1}",
                email=f"temp_manager_{User.objects.count() + 1}@example.com",
                password="temporarypassword123",
            )
            # Сохраняем менеджера с привязкой к созданному пользователю
            manager = form.save(commit=False)
            manager.user = temp_user
            manager.save()
            return redirect("managers_list")
    else:
        form = AddManagerForm()

    return render(request, "admin/add_manager.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def championship_admin(request):
    championships = Championship.objects.all()

    if request.method == "POST":
        form = ChampionshipForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("championship_admin")
    else:
        form = ChampionshipForm()

    return render(request, "admin/championship_admin.html", {"championships": championships, "form": form})


@user_passes_test(is_admin)
def journal_list(request):
    journals = JournalRequest.objects.all()
    return render(request, 'admin/journal_list.html', {'journals': journals})


@login_required
@user_passes_test(is_admin)
def award_list(request):
    awards = AwardRequest.objects.all()
    return render(request, 'admin/award_list.html', {'awards': awards})


@login_required
def participant_dashboard(request):
    if not request.COOKIES.get('participant_id'):
        participant = ProfileParticipant.objects.get(user=request.user)
    else:
        participant = ProfileParticipant.objects.get(id=request.COOKIES.get('participant_id'))

    awards = AwardRequest.objects.filter(email=participant.email)
    journals = JournalRequest.objects.filter(email=participant.email)

    return render(
        request,
        'participant/dashboard.html',
        {
            'is_leader': (True if request.COOKIES.get('participant_id') else False),
            'participant': participant,
            'awards': awards,
            'journals': journals,
        },
    )


@login_required
def upload_work(request):
    try:
        if not request.COOKIES.get('participant_id'):
            participant = ProfileParticipant.objects.get(user=request.user)
        else:
            participant = ProfileParticipant.objects.get(id=request.COOKIES.get('participant_id'))
    except ProfileParticipant.DoesNotExist:
        messages.error(request, 'Вы не являетесь участником.')
        return redirect('participant_dashboard')

    user = request.user
    if request.COOKIES.get('participant_id'):
        user = User.objects.get(profileparticipant__id=request.COOKIES.get('participant_id'))

    championship = get_active_championship()
    if not championship:
        messages.error(request, 'Чемпионат не активен.')
        return redirect('participant_dashboard')
    
    if request.method == 'POST':
        nomination = request.POST.get('nomination')
        files = request.FILES.getlist('photos')

        uploaded_works_count = (
            PhotoList.objects.filter(user=user, championship=championship).values('work_id').distinct().count()
        )
        if participant.count_work > uploaded_works_count:
            work_id = uuid.uuid4()
            for file in files:
                PhotoList.objects.create(
                    user=user, championship=championship, photo=file, nomination=nomination, work_id=work_id
                )
            messages.success(request, 'Файлы успешно загружены.')
        else:
            messages.error(request, 'Превышен лимит работ. Вы не можете загрузить больше работ, чем оплачено.')

        return redirect('upload_work')

    works = PhotoList.objects.filter(user=user, championship=championship).order_by('work_id')
    grouped_works = {}
    for work in works:
        if work.work_id not in grouped_works:
            grouped_works[work.work_id] = {'nomination': work.get_nomination_display(), 'photos': []}
        grouped_works[work.work_id]['photos'].append(work)

    return render(
        request,
        'participant/upload_work.html',
        {
            'is_leader': (True if request.COOKIES.get('participant_id') else False),
            'participant': participant,
            'grouped_works': grouped_works,
            'nominations': PhotoList.CHAMPIONSHIP_NOMINATIONS,
        },
    )


@login_required
def update_work_count(request):
    if request.method == 'POST':
        add_work_count = request.POST.get('add_work_count')
        participant_id = request.COOKIES.get('participant_id')
        if not participant_id:
            participant_id = request.user.profileparticipant.id

        try:
            participant = ProfileParticipant.objects.get(id=participant_id)
        except ProfileParticipant.DoesNotExist:
            messages.error(request, 'Участник не найден.')
            return redirect('participant_dashboard')

        participant.count_work += int(add_work_count)
        participant.save()

        return redirect('upload_work')

    return redirect('upload_work')


@login_required
def leader_participant_list(request: HttpRequest):
    leader = ProfileLeader.objects.get(user=request.user)
    if not leader:
        messages.error(request, 'Вы не являетесь лидером.')
        return redirect('participant_dashboard')

    participants = ProfileParticipant.objects.filter(
        team__leader=leader, team__championship=get_active_championship(False)
    ).all()
    content = loader.render_to_string(
        'leader/participant_list.html', {"participants": participants} | {'statuses': STATUS_APPROVED}, request, using=None
    )
    resp = HttpResponse(content, None, None)
    resp.delete_cookie('participant_id')
    return resp


@login_required
def judge_welcome(request):
    if not hasattr(request.user, 'profilejudge'):
        messages.error(request, 'Вы не являетесь судьей.')
        return redirect('/')  # Перенаправляем на главную страницу, если пользователь не судья

    return render(request, 'judge/welcome.html', {'judge': request.user.profilejudge})


@login_required
@user_passes_test(is_admin)
def api_change_status(request):
    if request.method == 'POST':
        data = request.POST
        if 'id' not in data:
            data = json.loads(request.body.decode('utf-8') or '{}')

        profile_id = data.get('id')
        status = data.get('status')
        typ: str = data.get('type')

        profileModel = globals()["Profile" + typ.title()]
        if not profileModel:
            return HttpResponse('{"status": "incorrect profile type"}')

        profile = profileModel.objects.get(id=profile_id)
        profile.approved = status
        profile.user.save()
        profile.save()

        return custom_redirect(request)

    raise BadRequest('{"status": "Method not allowed"}')


@login_required
def sertificate_upload(request):
    if request.method == 'POST':
        form = SertificateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('participants_list')

        return BadRequest(form.errors.as_text())

    raise BadRequest("Method not allowed")


@login_required
def judge_championship(request):
    if not hasattr(request.user, 'profilejudge'):
        messages.error(request, 'Вы не являетесь судьей.')
        return redirect('/')  # Перенаправляем на главную страницу, если пользователь не судья

    championship = get_active_championship(False)

    if datetime.date.today() < championship.last_date_registration:
        messages.error(request, 'Регистрация в чемпионате еще не закончена.')
        return redirect('judge_welcome')

    path_criteries = 'main/static/txt/criteries.json'

    with open(path_criteries, "r", encoding="utf-8") as f:
        criteries = json.load(f).get("Критерии")

    works = PhotoList.objects.filter(championship=championship).order_by('work_id')
    grouped_works: dict[str, dict[str, str | list]] = {}
    for work in works:
        if work.work_id not in grouped_works:
            grouped_works[work.work_id] = {'nomination': work.get_nomination_display(), 'photos': []}
        grouped_works[work.work_id]['photos'].append(work)
        grouped_works[work.work_id]['marked'] = marks_to_form_value(
            Mark.objects.filter(work_id=work.work_id, judge=request.user.profilejudge)
        )

    return render(
        request,
        'judge/championship.html',
        {"championship": championship, "criteries": criteries, "grouped_works": grouped_works},
    )


@login_required
def api_judge_rate_work(request: HttpRequest):
    if not hasattr(request.user, 'profilejudge'):
        messages.error(request, 'Вы не являетесь судьей.')
        return redirect('/')  # Перенаправляем на главную страницу, если пользователь не судья

    if request.method == 'POST':
        championship = get_active_championship(False)
        work_id = request.POST.get('work_id')
        work = uuid.UUID(work_id, version=4)
        marks = {}

        for key, value in request.POST.items():
            if not key.startswith('criteries-') and not key.startswith('comments-'):
                continue

            typ, judge_id, block_id, id, name = key.split('-')
            judge = ProfileJudge.objects.get(id=judge_id)

            if typ == 'criteries':
                marks[block_id + ". " + id + ". " + name] = {'mark': int(value), 'judge': judge}

            if typ == 'comments':
                marks[block_id + ". " + id + ". " + name]['comment'] = value

        for critery, mark in marks.items():
            markM = Mark.objects.filter(work_id=work, judge=mark['judge'], critery=critery).first()
            
            if request.POST.get('only_edit') and not markM:
                continue

            if not markM:
                Mark.objects.create(work_id=work, judge=mark['judge'], critery=critery, championship=championship, mark=mark['mark'], comment=mark.get('comment'))
                continue

            markM.mark = mark['mark']
            markM.comment = mark.get('comment') or 'Без комментариев'
            markM.save()


        from_path = request.META.get('HTTP_REFERER')
        if from_path:
            return redirect(from_path)

        return redirect('judge_championship')

    raise BadRequest("Method not allowed")


def is_leader_judge(user):
    return hasattr(user, 'profilejudge') and user.profilejudge.is_leader

@login_required
@user_passes_test(lambda user: is_admin(user) or is_leader_judge(user))
def current_championship_admin(request):
    championship = get_active_championship(False)

    if datetime.date.today() <= championship.last_date_registration:
        messages.error(request, 'Регистрация в чемпионате еще не закончена.')
        return redirect('championship_admin')

    path_criteries = 'main/static/txt/criteries.json'

    with open(path_criteries, "r", encoding="utf-8") as f:
        criteries = json.load(f).get("Критерии")

    works = PhotoList.objects.filter(championship=championship).order_by('work_id')
    grouped_works: dict[str, dict[str, str | list]] = {}
    for work in works:
        if work.work_id not in grouped_works:
            grouped_works[work.work_id] = {'nomination': work.get_nomination_display(), 'photos': []}
        grouped_works[work.work_id]['photos'].append(work)
        grouped_works[work.work_id]['marked'] = marks_to_form_value(
            Mark.objects.filter(work_id=work.work_id)
        )
        grouped_works[work.work_id]['judges'] = set(ProfileJudge.objects.filter(mu_judge__work_id=work.work_id))

    return render(
        request,
        'admin/championship.html',
        {"championship": championship, "criteries": criteries, "grouped_works": grouped_works, 'only_edit': True},
    )


@login_required
@user_passes_test(is_admin)
def api_set_group_tg(request: HttpRequest):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        request.user.profileadmin.telegram = group_id
        request.user.profileadmin.save()
        return redirect('championship_admin')

    raise BadRequest("Method not allowed")
