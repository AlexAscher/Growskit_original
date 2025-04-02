from django.contrib import admin
from django.contrib.auth.models import Group

from .models import *

admin.site.register(Championship)
admin.site.register(Mark)
admin.site.register(Team)
admin.site.register(PhotoList)
admin.site.register(ProfileParticipant)
admin.site.register(ProfileJudge)
admin.site.register(ProfileSponsor)
