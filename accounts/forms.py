from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, MasterProfile, ClientProfile


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "role",
            "password1",
            "password2",
        ]

    def clean_role(self):
        role = self.cleaned_data["role"]

        if role not in [User.Role.CLIENT, User.Role.MASTER]:
            raise forms.ValidationError(
                "Невалидна потребителска роля."
            )

        return role



class MasterProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="Потребителско име",
        disabled=True,
        required=False,
    )
    email = forms.EmailField(
        label="Имейл адрес",
        disabled=True,
        required=False,
    )

    class Meta:
        model = MasterProfile
        fields = [
            "description",
            "experience_years",
            "city",
            "address",
            "price_from",
            "services",
        ]
        labels = {
            "description": "Описание на услугите",
            "experience_years": "Години опит",
            "city": "Град",
            "address": "Адрес",
            "price_from": "Начална цена (лв.)",
            "services": "Предлагани услуги",
        }
        help_texts = {
            "description": "Опишете опита си и услугите, които предлагате.",
            "experience_years": "Посочете броя години професионален опит.",
            "price_from": "Посочете минималната цена за услугите си.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email



class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "city",
            "address",
        ]
