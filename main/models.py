import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import BadRequest

def user_directory_path(instance, filename):
    championship = Championship.objects.filter(participants=instance.user, last_date_registration__gte=datetime.date.today()).first()
    if not championship:
        raise BadRequest('User not in championship')

    return f'media/main/championships/{championship.id}/{instance.user.id}/{filename}'

# Фотографии пользоваталя. Django неявно создаст ManyToMany связь
class PhotoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path)

# Комманда
class Team(models.Model):
    championship = models.ForeignKey('Championship', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tu_leader')
    members = models.ManyToManyField(User)

# Оценка судьи
class Mark(models.Model):
    judge = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mu_judge', null=True)
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mu_participant', null=True)
    mark = models.FloatField()

# Чемпионат
class Championship(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(null=False)
    last_date_registration = models.DateField(null=False)
    participants = models.ManyToManyField(User, blank=True, related_name='cu_participants')
    judges = models.ManyToManyField(User, blank=True, related_name='cu_judges')
    marks = models.ManyToManyField(Mark, blank=True)
    criteries = models.TextField()

    def __str__(self):
        return self.name
    
    # Получение списка средних оценок по пользователям
    def get_marks_average(self, user: User | None = None) -> list[dict[str, float]]: #  [{'user': user.email, 'average': average}]
        def average(user: User):
            marks = self.marks.filter(User=user)
            res = sum(mark.mark for mark in marks)

            return res / marks.count()

        if user:
            return [{'user': user.email, 'average': average(user)}]

        return [{'user': user.email, 'average': average(user)} for user in self.participants.all()]
