import random
import string
from typing import Literal

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db.models.query import QuerySet

from main.bot import bot

TYPE_USER = Literal['participant', 'judge', 'sponsor', 'manager', 'leader', 'admin']


def get_random_string(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def create_user(email, type_user: TYPE_USER = ''):
    user = User.objects.filter(email=email).first()
    if user:
        return (user, 'Ранее вы участвали в чемпионате. Проверьте почту или восстановите пароль', False)

    password = get_random_string(10)
    user = User.objects.create_user(username=email, email=email, password=password)

    group = Group.objects.get(name=type_user + 's')
    if group:
        user.groups.add(group)
        user.save()

    return user, password, True


@bot.check_bot
def notify_user_tg(subject: str, message: str, tg: list[str] | str, fail_silently=False):
    if isinstance(tg, str):
        tg = [tg]

    for t in list(set(tg)):
        t = t.strip().split('/')[-1].rstrip('/')
        if not (t.isnumeric() or t.startswith('@') or t.startswith('-') or t.startswith('+')):
            t = '@' + t
        bot.callfunc(bot.bot.send_message, t, f'{subject}\n\n{message}', fail_silently=fail_silently)


def get_group_tg():
    users = User.objects.filter(is_superuser=True)
    return list(set([user.profileadmin.telegram for user in users if user.profileadmin.telegram])) or ['-4713095754']


def notify_user(subject: str, message: str, recipient: list[str] | str, fail_silently=False, tg: list[str] | str = ""):
    if len(recipient) > 0:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            (list(set(recipient)) if isinstance(recipient, list) else [recipient]),
            fail_silently=fail_silently,
        )
    if tg:
        notify_user_tg(subject, message, tg, fail_silently=fail_silently)


def notify_admin(
    subject: str,
    message: str,
    recipient: list[str] | str | Literal['All'],
    fail_silently=True,
    tg: list[str] | str | Literal['ALL'] = "",
):
    need_tg = isinstance(tg, str) and tg == 'ALL'
    tgs = [] if need_tg else (tg if isinstance(tg, list) else [tg])

    if isinstance(recipient, str) and recipient == 'ALL':
        recipient = []
        users = User.objects.filter(is_superuser=True)
        for user in users:
            if need_tg:
                tgs.append(user.profile_admin.telegram)
            recipient.append(user.email)

    notify_user(subject, message, recipient, fail_silently, tg=tgs)


def notify_new_user(email: str, password: str, fail_silently=False, tg: str = ""):
    subject = "Заявка на Чемпионат"
    message = f"Ваша заявка на чемпионат принята!\n\nИспользуйте для входа:\nЛогин: {email}\nПароль: {password}"
    notify_user(subject, message, email, fail_silently=fail_silently)  # , tg=tg)


def marks_to_form_value(marks: QuerySet['Mark', 'Mark']):
    # criteries-<id>-<name>
    # comments-<id>-<name>
    marks_dict = {}

    for mark in marks:
        id, name = mark.critery.split('. ')
        critery = f"criteries-{id}-{name}"
        comment = f"comments-{id}-{name}"
        marks_dict[critery] = int(mark.mark)
        marks_dict[comment] = mark.comment

    return marks_dict
