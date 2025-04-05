import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    championship = models.ForeignKey('Championship', on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to=user_directory_path_championship)


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
