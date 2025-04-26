import datetime
import json
import logging
import os
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import BadRequest
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .support import get_random_string, parse_criteries

"""
БД:

участник (ProfileParticipant) включая его фото, и количество работ на последний чемпионат (то есть участник может участвовать только в одном сразу)
отдельно есть список его фото/проектов (PhotoList) в конкретном чемпионате

есть команды (Team) - это просто лидер и участники в конкретном чемпионате

оценки (Mark) - каждого судьи на конкретного участника

чемпионат (Championship) - это список участников, список судий, список оценок и критерии для этого чемпионата
есть два поля даты - дата самого чемпионата и дата окончания регистрации
"""


class Log(models.Model):
    try:
        STATUSES = [(key, key) for key in logging.getLevelNamesMapping() if key != logging.getLevelName(logging.NOTSET)]
    except AttributeError:
        STATUSES = [(key, key) for key in ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO','DEBUG']]

    created = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=20, choices=STATUSES)
    message = models.TextField()
    description = models.TextField(null=True, blank=True)
    src = models.TextField(null=True, blank=True)
    context = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.created} - {self.status}: {self.message}'


def user_directory_path(instance, filename):
    user = None if not hasattr(instance, 'user') else instance.user

    if user is None:
        if not hasattr(instance, 'email'):
            raise ValueError("instance должен иметь атрибут user или иметь атрибут email")

        email = instance.email
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(username=email, email=email, password=get_random_string(10))

    return f'media/main/users/{user.id}/{filename}'


def user_directory_path_championship(instance, filename):
    if not isinstance(instance.user, User):
        raise ValueError("instance.user должен быть объектом User")

    championship = Championship.objects.filter(
        participants=instance.user.profileparticipant,  # Используем связанный ProfileParticipant
        last_date_registration__gte=datetime.date.today(),
    ).first()

    if not championship:
        championship = Championship.objects.filter(
            judges=instance.user, last_date_registration__gte=datetime.date.today()
        ).first()
        if not championship:
            raise BadRequest('User not in championship')

    return f'media/main/championships/{championship.id}/{instance.user.id}/{filename}'


def championship_directory_path(instance, filename):
    return f'media/main/championships/{instance.id}/{filename}'


# Фотографии/проекты пользоваталя. Django неявно создаст ManyToMany связь
class PhotoList(models.Model):
    work_id = models.UUIDField()  # Уникальный идентификатор работы
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.FileField(upload_to=user_directory_path_championship)  # фото или видео
    nomination = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.user.username} {self.photo.name} - {self.nomination}'  # pylint: disable=no-member

    def get_nomination_display(self):
        return self.nomination

    @staticmethod
    def get_work(work_id):
        return PhotoList.objects.filter(work_id=work_id)


class Sertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path_championship)

    def __str__(self):
        return f'Sertificate {self.user.username} {self.file.name}'


STATUS = (("approved", "Одобрено"), ("refused", "Отказано"), ("wait", "На рассмотрении"), ("blocked", "Заблокировано"))


class ProfileAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})
    telegram = models.CharField(max_length=150, null=True, blank=True)


@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created:
        ProfileAdmin.objects.get_or_create(user=instance)


CATEGORY_PARTICIPANT = (
    ("junior", "Юниор"),
    ("master", "Мастер"),
    ("top-master", "Топ-Мастер"),
    ("instructor", "Инструктор"),
    ("premium", "Премиум"),
)

class ProfileBase():
    pass

class ProfileParticipant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)

    fio = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    category_participant = models.CharField(max_length=150, choices=CATEGORY_PARTICIPANT)
    fio_trainer = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    bio = models.TextField()
    count_work = models.IntegerField()
    approved = models.CharField(max_length=150, choices=STATUS, default='approved')

    def __str__(self):
        return str(self.fio)


class ProfileJudge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)
    is_leader = models.BooleanField(default=False)

    fio = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    bio = models.TextField()
    approved = models.CharField(max_length=150, choices=STATUS, default='wait')

    def __str__(self):
        return 'Судья ' + self.fio


class ProfileSponsor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path, null=True, blank=True)

    fio = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    bio = models.TextField()
    need_mark_and_dogovor = models.BooleanField(default=False)
    approved = models.CharField(max_length=150, choices=STATUS, default='wait')

    def __str__(self):
        return 'Спонсор ' + self.fio


# Руководитель команды
class ProfileLeader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)

    fio = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    bio = models.TextField()

    def __str__(self):
        return 'Руководитель ' + self.fio


class ProfileManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    referal_key = models.CharField(unique=True, max_length=150)
    fio = models.CharField(max_length=150)
    referals = models.IntegerField(default=0)

    def __str__(self):
        return f'Менеджер {self.fio} ({self.referals} рефералов)'


# Комманда
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(ProfileLeader, on_delete=models.CASCADE)
    members = models.ManyToManyField(ProfileParticipant)

    def __str__(self):
        return str(self.name)


# Оценка судьи
class Mark(models.Model):
    work_id = models.UUIDField()
    critery = models.CharField(max_length=150)
    mark = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    judge = models.ForeignKey(ProfileJudge, on_delete=models.CASCADE)

    def __str__(self):
        return f'({self.mark:.2f}) {self.work_id} ({self.judge})'


# Чемпионат
class Championship(models.Model):
    STAGES = [
        ('preparation', 'Подготовка'),
        ('registration', 'Регистрация'),
        ('judging', 'Судейство'),
        ('finishing', 'Завершение'),
        ('closed', 'Закрыт'),
    ]

    name = models.CharField(max_length=100)
    date = models.DateField(null=False)
    last_date_registration = models.DateField(null=False)
    current_stage = models.CharField(max_length=150, choices=STAGES, default='preparation')
    criteries = models.FileField(upload_to=championship_directory_path, null=True, blank=True)

    works = models.ManyToManyField(PhotoList, blank=True)

    teams = models.ManyToManyField(Team, blank=True)
    participants = models.ManyToManyField(ProfileParticipant, blank=True)
    judges = models.ManyToManyField(ProfileJudge, blank=True)
    sponsors = models.ManyToManyField(ProfileSponsor, blank=True)
    managers = models.ManyToManyField(ProfileManager, blank=True)
    marks = models.ManyToManyField(Mark, blank=True)

    sertificates = models.ManyToManyField(Sertificate, blank=True)
    awards = models.ManyToManyField('AwardRequest', blank=True)
    journals = models.ManyToManyField('JournalRequest', blank=True)

    @property
    def is_active(self):
        return self.current_stage != 'closed'

    @is_active.setter
    def is_active(self, value: bool):
        print(value)
        if value:
            self.current_stage = 'registration'
        else:
            self.current_stage = 'closed'

    @staticmethod
    def get_active():
        return Championship.objects.filter(current_stage__ne='closed').first()

    def __str__(self):
        return self.name + ' ' + str(self.date)

    # Получение списка средних оценок по пользователям
    def get_marks_average(
        self, work_id: str | uuid.UUID | None = None
    ) -> list[dict[str, uuid.UUID | float]]:  #  [{'work_id': work_id, 'average': average}]
        def average(work_id: uuid.UUID):
            marks = self.marks.filter(work_id=work_id)  # pylint: disable=no-member
            print(self.marks)
            res = sum(mark.mark for mark in marks)

            if not marks.count():
                return 0

            return round(res / marks.count(), 2)

        if work_id:
            if not isinstance(work_id, uuid.UUID):
                work_id = uuid.UUID(work_id, version=4)
            return [{'work_id': work_id, 'average': average(work_id)}]

        return [
            {'work_id': mark.work_id, 'average': average(mark.work_id)}
            for mark in self.marks.all()  # pylint: disable=no-member
        ]

    def get_days_left(self):
        return (self.last_date_registration - datetime.date.today()).days
    
    def parse_criteries(self):
        if not self.criteries:
            return {}
        
        path_criteries = self.criteries.path + '.json' # pylint: disable=no-member
        if not os.path.exists(path_criteries):
            parse_criteries(self.criteries.path) # pylint: disable=no-member


        with open(path_criteries, "r", encoding="utf-8") as f:
            return json.load(f).get("Критерии") or {}


class AwardRequest(models.Model):
    fio = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to=user_directory_path)
    bio = models.TextField()
    nomination = models.CharField(max_length=150)

    def get_nomination_display(self):
        return self.nomination

    def __str__(self):
        return f'Award {self.fio} - {self.get_nomination_display()}'


class JournalRequest(models.Model):
    fio = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to=user_directory_path)

    count_pages = models.IntegerField()
    need_journal = models.BooleanField(default=False)
    need_cover = models.BooleanField(default=False)
    nomination = models.ForeignKey(AwardRequest, on_delete=models.SET_NULL, null=True, default=None)
    need_cup_and_elite = models.BooleanField(default=False)

    def __str__(self):
        return f'Journal {self.fio}'
