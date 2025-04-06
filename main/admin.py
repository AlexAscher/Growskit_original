from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import *

admin.site.register(Championship)
admin.site.register(Mark)
admin.site.register(Team)
admin.site.register(PhotoList)
admin.site.register(ProfileParticipant)
admin.site.register(ProfileJudge)
admin.site.register(ProfileSponsor)
admin.site.register(ProfileLeader)
admin.site.register(ProfileManager)
admin.site.register(AwardRequest)
admin.site.register(JournalRequest)


class DateFieldListFilter(admin.DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        
        links = list(self.links)
        links = links[:1] + [
            (_("Past hour"), {
                self.lookup_kwarg_since: now - datetime.timedelta(hours=1),
                self.lookup_kwarg_until: now
            }),
            (_("This hour"), {
                self.lookup_kwarg_since: now.replace(minute=0, second=0, microsecond=0),
                self.lookup_kwarg_until: now
            })
        ] + links[1:] # set before Today
        self.links = tuple(links)

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_filter = ["status", ("created", DateFieldListFilter)]
