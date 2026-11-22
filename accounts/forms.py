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


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            "city",
            "address",
        ]
