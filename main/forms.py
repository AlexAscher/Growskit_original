from django import forms

from .models import (
    AwardRequest,
    Championship,
    JournalRequest,
    ProfileJudge,
    ProfileManager,
    ProfileParticipant,
    ProfileSponsor,
    Sertificate,
)


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
        fields = ['photo', 'fio', 'phone', 'email', 'address', 'address_sdek', 'vk', 'telegram', 'bio']


class SponsorstvoForm(forms.ModelForm):
    class Meta:
        model = ProfileSponsor
        fields = [
            'fio',
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
        cleaned_data.update(self.files)  # super().clean()
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

        if len(participants) < 5:
            raise forms.ValidationError('Команда должна состоять минимум из 5 участников')

        # Создание словаря с данными команды
        team_data = {
            'is_team': cleaned_data.get('is_team'),
            'team_name': cleaned_data.get('team_name'),
            'team_count': cleaned_data.get('team_count'),
            'leader': leader_data,
            'participants': participants,
        }

        return team_data


class ManagerForm(forms.ModelForm):
    class Meta:
        model = ProfileManager
        fields = ['fio', 'referal_key']


class AwardRequestForm(forms.ModelForm):
    class Meta:
        model = AwardRequest
        fields = [
            'fio',
            'email',
            'phone',
            'address',
            'address_sdek',
            'vk',
            'telegram',
            'photo',
            'bio',
            'nomination',
        ]


class JournaRequestForm(forms.ModelForm):
    class Meta:
        model = JournalRequest
        fields = [
            'fio',
            'email',
            'phone',
            'address',
            'address_sdek',
            'vk',
            'telegram',
            'photo',
            'count_pages',
            'need_journal',
            'need_cover',
            'need_cup_and_elite',
        ]


class SertificateForm(forms.ModelForm):
    class Meta:
        model = Sertificate
        fields = ['user', 'file']


class AddManagerForm(forms.ModelForm):
    class Meta:
        model = ProfileManager
        fields = ['fio', 'referal_key']
        widgets = {
            'fio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ФИО'}),
            'referal_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите реферальный ключ'}),
        }
        labels = {'fio': 'ФИО', 'referal_key': 'Реферальный ключ'}


class ChampionshipForm(forms.ModelForm):
    class Meta:
        model = Championship
        fields = ['id', 'name', 'date', 'last_date_registration']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название чемпионата'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Введите дату начала'}),
            'last_date_registration': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Введите дату окончания регистрации'}
            ),
        }
        labels = {'name': 'Название', 'date': 'Дата начала', 'last_date_registration': 'Дата окончания регистрации'}

class ProcessedPhotoForm(forms.ModelForm):
    class Meta:
        model = ProfileParticipant
        fields = ['processed_photo']
        widgets = {
            'processed_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'processed_photo': 'Фото для сайта',
        }

class ProcessedPhotoFormJudges(forms.ModelForm):
    class Meta:
        model = ProfileJudge
        fields = ['processed_photo']
        widgets = {
            'processed_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'processed_photo': 'Фото для сайта',
        }