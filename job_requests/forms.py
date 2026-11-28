from django import forms
from .models import JobRequest


class JobRequestForm(forms.ModelForm):

    class Meta:
        model = JobRequest
        fields = [
            "title",
            "description",
            "city",
            "address",
            "budget_min",
            "budget_max",
            "services",
            "deadline",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Например: Ремонт на баня"
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Опиши подробно каква работа трябва да се извърши..."
            }),
            "city": forms.TextInput(attrs={
                "placeholder": "Например: Бургас"
            }),
            "address": forms.TextInput(attrs={
                "placeholder": "Адрес на обекта"
            }),
            "budget_min": forms.NumberInput(attrs={
                "min": "0",
                "step": "0.01"
            }),
            "budget_max": forms.NumberInput(attrs={
                "min": "0",
                "step": "0.01"
            }),
            "services": forms.CheckboxSelectMultiple(),
            "deadline": forms.DateInput(attrs={
                "type": "date"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        budget_min = cleaned_data.get("budget_min")
        budget_max = cleaned_data.get("budget_max")

        if (
            budget_min is not None
            and budget_max is not None
            and budget_min > budget_max
        ):
            raise forms.ValidationError(
                "Минималният бюджет не може да бъде по-голям от максималния."
            )

        return cleaned_data