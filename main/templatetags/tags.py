import uuid
from typing import Any, Literal

from django import template
from django.contrib.auth.models import User

from main.models import Championship, ProfileParticipant, Sertificate

register = template.Library()


@register.filter('get')
def get(d: dict | list, k: str | int):
    if isinstance(d, list):
        return d[k]
    v = d.get(k)
    if v is None:
        return ''
    return v


@register.simple_tag
def format(fmt, *args, **kwargs):
    return fmt.format(*args, **kwargs)


@register.filter('has_sertificate')
def has_sertificate(user: User, championship_id: int):
    if not user or not championship_id:
        return False

    return Sertificate.objects.filter(user=user, championship__id=championship_id).exists()


@register.simple_tag
def false():
    return False


@register.simple_tag
def true():
    return True


STATE = {}


@register.simple_tag
def state(key, value=None):
    if value is None:
        return STATE.get(key)
    STATE[key] = value
    return value


@register.filter('get_marks_average')
def get_marks_average(championship: Championship, work_id: str | uuid.UUID | None = None):
    return championship.get_marks_average(work_id)
