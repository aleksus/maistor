from django import forms

from .models import Offer


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["price", "message", "estimated_days"]

        labels = {
            "price": "Предложена цена (€)",
            "message": "Съобщение до клиента",
            "estimated_days": "Очакван срок (дни)",
        }

        widgets = {
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Например: 250",
                "min": "0.01",
                "step": "0.01",
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Опиши как ще изпълниш работата...",
                "rows": 5,
            }),
            "estimated_days": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Например: 3",
                "min": "1",
            }),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Цената трябва да бъде по-голяма от 0.")
        return price

    def clean_estimated_days(self):
        days = self.cleaned_data["estimated_days"]
        if days <= 0:
            raise forms.ValidationError("Срокът трябва да бъде поне 1 ден.")
        return days
