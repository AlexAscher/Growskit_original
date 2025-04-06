import datetime
import logging

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest


"""
БД:

участник (ProfileParticipant) включая его фото, и количество работ на последний чемпионат (то есть участник может участвовать только в одном сразу)
отдельно есть список его фото/проектов (PhotoList) в конкретном чемпионате

есть команды (Team) - это просто лидер и участники в конкретном чемпионате

оценки (Mark) - каждого судьи на конкретного участника

чемпионат (Championship) - это список участников, список судий, список оценок и критерии для этого чемпионата
есть два поля даты - дата самого чемпионата и дата окончания регистрации
"""

# TODO: есть вариант добавить логирование запросов через django-request

def items_key_key(dict: dict):
    return [(key, key) for key in dict if key != 'NOTSET']

class Log(models.Model):
    STATUSES = items_key_key(logging.getLevelNamesMapping())

    created = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=20, choices=STATUSES)
    message = models.TextField()
    description = models.TextField(null=True, blank=True)
    src = models.TextField(null=True, blank=True)
    context = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.created} - {self.status}: {self.message}'


def user_directory_path_championship(instance, filename):
    championship = Championship.objects.filter(participants=instance.user, last_date_registration__gte=datetime.date.today()).first()
    if not championship:
        championship = Championship.objects.filter(judges=instance.user, last_date_registration__gte=datetime.date.today()).first()
        if not championship:
            raise BadRequest('User not in championship')

    return f'media/main/championships/{championship.id}/{instance.user.id}/{filename}'


def user_directory_path(instance, filename):
    return f'media/main/users/{instance.user.id}/{filename}'

# Фотографии/проекты пользоваталя. Django неявно создаст ManyToMany связь
class PhotoList(models.Model):
    CHAMPIONSHIP_NOMINATIONS = (
        ("hand_painted_nails", "художественная роспись. типсы"),
        ("salon_designs", "салонные дизайны на типсах"),
        ("pedicure_designs", "дизайн на педикюрных типсах"),
        ("object_designs", "дизайн на предмете"),
        ("clothing_designs", "дизайн одежды/обуви/головных уборов"),
        ("free_style", "свободный стиль"),
        ("mannequin_hand", "манекен-рука"),
        ("modeling", "моделирование"),
        ("poster", "постер"),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    championship = models.ForeignKey('Championship', on_delete=models.CASCADE, null=True)
    photo = models.FileField(upload_to=user_directory_path_championship) # фото или видео
    nomination = models.CharField(max_length=150, choices=CHAMPIONSHIP_NOMINATIONS, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.championship}) {self.photo.name} - {self.nomination}'


STATUS_APPROVED = (
    ("approved", "Одобрено"),
    ("refused", "Отказано"),
    ("wait", "На рассмотрении"),
    ("blocked", "Заблокировано")
)


class ProfileParticipant(models.Model):
    CATEGORY_PARTICIPANT = (
        ("individual", "Индивидуальный участник"),
        ("team-leader", "Руководитель команды"),
        ("junior", "Юниор"),
        ("professional", "Профессионал"),
    )

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
    approved = models.CharField(max_length=150, choices=STATUS_APPROVED, default='approved')

    def __str__(self):
        return self.fio
    

class ProfileJudge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)

    fio = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    bio = models.TextField()
    approved = models.CharField(max_length=150, choices=STATUS_APPROVED, default='wait')

    def __str__(self):
        return 'Судья ' + self.fio

class ProfileSponsor(models.Model):
    CATEGORY_PARTICIPANT = (
        ("individual", "Индивидуальный участник"),
        ("team-leader", "Руководитель команды")
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fio = models.CharField(max_length=150)
    participant = models.CharField(max_length=150, choices=CATEGORY_PARTICIPANT)
    phone = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    bio = models.TextField()
    need_mark_and_dogovor = models.BooleanField(default=False)
    approved = models.CharField(max_length=150, choices=STATUS_APPROVED, default='wait')

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
    championship = models.ForeignKey('Championship', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(ProfileLeader, on_delete=models.CASCADE, null=True)
    members = models.ManyToManyField(ProfileParticipant)

    def __str__(self):
        return self.name

# Оценка судьи
class Mark(models.Model):
    judge = models.ForeignKey(ProfileJudge, on_delete=models.CASCADE, related_name='mu_judge', null=True)
    participant = models.ForeignKey(ProfileParticipant, on_delete=models.CASCADE, related_name='mu_participant', null=True)
    mark = models.FloatField()

    def __str__(self):
        return f'({self.mark:.2f}) {self.participant} ({self.judge})'

# Чемпионат
class Championship(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(null=False)
    last_date_registration = models.DateField(null=False)
    participants = models.ManyToManyField(ProfileParticipant, blank=True)
    judges = models.ManyToManyField(User, blank=True, related_name='cu_judges')
    marks = models.ManyToManyField(Mark, blank=True)
    criteries = models.TextField()

    def __str__(self):
        return self.name + ' ' + str(self.date)
    
    # Получение списка средних оценок по пользователям
    def get_marks_average(self, user: User | None = None) -> list[dict[str, float]]: #  [{'user': user.email, 'average': average}]
        def average(user: User):
            marks = self.marks.filter(User=user)
            res = sum(mark.mark for mark in marks)

            return res / marks.count()

        if user:
            return [{'user': user.email, 'average': average(user)}]

        return [{'user': user.email, 'average': average(user)} for user in self.participants.all()]
    
    def get_days_left(self):
        return (self.last_date_registration - datetime.date.today()).days
    
class AwardRequest(models.Model):
    AWARD_NOMINATIONS = (
        ("best_company", "Лучшая компания"),
        ("best_entrepreneur", "Лучший предприниматель"),
        ("innovation_of_the_year", "Инновация года"),
        ("startup_of_the_year", "Стартап года"),
        ("leader_of_the_year", "Лидер года"),
        ("best_brand", "Лучший бренд"),
        ("best_beauty_product", "Лучший бьюти продукт"),
        ("best_salon", "Лучший салон"),
        ("best_eco_initiative", "Лучшая эко-инициатива"),
        ("best_instructor", "Лучший инструктор"),
        ("best_master", "Лучший мастер"),
        ("best_beauty_blogger", "Лучший бьюти-блогер"),
        ("legend_of_the_year", "Легенда года"),
        ("best_speaker", "Лучший спикер"),
        ("best_expert", "Лучший эксперт"),
        ("best_trainer", "Лучший тренер"),
        ("best_beauty_project", "Лучший бьюти проект"),
        ("best_sponsor", "Лучший спонсор"),
        ("best_online_offline_school", "Лучшая онлайн/оффлайн школа"),
        ("growskit_growth_agility", "GROWSKIT ловкость роста"),
        ("growing_business_awards", "GROWING BUSINESS AWARDS"),
    )
    fio = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    address_sdek = models.CharField(max_length=150)
    vk = models.URLField(null=True, blank=True)
    telegram = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to=user_directory_path)
    bio = models.TextField()
    nomination = models.CharField(max_length=150, choices=AWARD_NOMINATIONS)
    from_journal = models.ForeignKey('JournalRequest', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Award {self.fio} - {self.nomination}'

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
    need_instance = models.BooleanField(default=False)
    need_nomination = models.BooleanField(default=False)
    need_cup_and_elite = models.BooleanField(default=False)

    def __str__(self):
        return f'Journal {self.fio}'
