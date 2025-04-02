from django import forms

from .models import ProfileParticipant


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
