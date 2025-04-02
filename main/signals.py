from django.apps import apps
from .apps import MainConfig
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_groups(sender, **kwargs):
    GROUPS_PERMISSIONS: dict[str, list[str]] = {}

    for group_name in GROUPS_PERMISSIONS:
        group, created = Group.objects.get_or_create(name=group_name)
        if not created:
            continue
        
        permissions = Permission.objects.filter(name__in=GROUPS_PERMISSIONS[group_name])
        group.permissions.add(*permissions)
