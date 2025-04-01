from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Profile. Разделяем авторизацию и информацию о пользователях, для упращения разработки

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='photo')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# end Profile

# Комманда
class Team(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leader_team')
    members = models.ManyToManyField(User)


# Оценка судьи
class Mark(models.Model):
    Judge = models.ForeignKey(User, on_delete=models.CASCADE, related_name='judge_marks')
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_marks')
    mark = models.FloatField()

# Чемпионат
class Championship(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(null=False)
    last_date_registration = models.DateField(null=False)
    participants = models.ManyToManyField(User, related_name='participants_championship')
    judges = models.ManyToManyField(User, related_name='judges_championship')
    marks = models.ManyToManyField(Mark)
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
