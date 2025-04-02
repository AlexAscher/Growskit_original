from django import forms

from .models import *


class UchastieForm(forms.ModelForm):
    class Meta:
        model = ProfileParticipant
        fields = [
            'photo',
            'fio',
            'city',
            'category_participant',
            'fio_trainer',
            'phone',
            'email',
            'vk',
            'telegram',
            'address',
            'address_sdek',
            'bio',
            'count_work',
        ]


class SudeystvoForm(forms.ModelForm):
    class Meta:
        model = ProfileJudge
        fields = [
            'photo',
            'fio',
            'phone',
            'email',
            'address',
            'address_sdek',
            'vk',
            'telegram',
            'bio',
        ]


class SponsorstvoForm(forms.ModelForm):
    class Meta:
        model = ProfileSponsor
        fields = [
            'fio',
            'participant',
            'phone',
            'email',
            'address',
            'address_sdek',
            'vk',
            'telegram',
            'bio',
            'need_mark_and_dogovor',
        ]
