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

class UchastieTeamForm(forms.Form):
    is_team = forms.CharField(required=True)
    team_name = forms.CharField(required=True)
    team_count = forms.CharField(required=False)
    team_trainer = forms.CharField(required=False)

    class Meta:
        fields = [
            'photo',
            'fio',
            'city',
            'phone',
            'email',
            'vk',
            'telegram',
            'address',
            'address_sdek',
            'bio',
            'fio_trainer',
            'category_participant',
            'count_work',
        ]

    def clean(self):
        cleaned_data = self.data.copy()
        cleaned_data.update(self.files) # super().clean()
        cleaned_data = cleaned_data.copy()

        # Создание словаря с данными руководителя
        leader_data = {}
        for field in UchastieForm.Meta.fields:
            if field in ['fio_trainer', 'category_participant', 'count_work']:
                continue
            leader_data[field] = cleaned_data.getlist(field)[0]

        # Создание словаря с данными участников
        participants = []
        for i in range(1, len(cleaned_data.getlist('fio'))):
            participant = {}
            for field in UchastieForm.Meta.fields:
                ii = i
                if field in ['fio_trainer', 'category_participant', 'count_work']:
                    ii -= 1
                participant[field] = cleaned_data.getlist(field)[ii]
            
            participants.append(participant)

        # Создание словаря с данными команды
        team_data = {
            'is_team': cleaned_data.get('is_team'),
            'team_name': cleaned_data.get('team_name'),
            'team_count': cleaned_data.get('team_count'),
            'leader': leader_data,
            'participants': participants
        }

        return team_data
