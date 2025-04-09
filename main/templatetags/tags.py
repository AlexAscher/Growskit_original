from django import template
from django.contrib.auth.models import User

from main.models import ProfileParticipant, Sertificate


register = template.Library()

@register.filter('get')
def get(d: dict, k: str):
    return d.get(k)

@register.filter('has_sertificate')
def has_sertificate(user: User, championship_id: int):
    if not user or not championship_id:
        return False
    
    return Sertificate.objects.filter(user=user, championship__id=championship_id).exists()
