from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

        labels = {
            "rating": "Оценка",
            "comment": "Твоят отзив",
        }

        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Отлично"),
                    (4, "★★★★ - Много добро"),
                    (3, "★★★ - Добро"),
                    (2, "★★ - Незадоволително"),
                    (1, "★ - Лошо"),
                ],
                attrs={"class": "form-select"}
            ),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Сподели впечатленията си от работата на майстора..."
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]

        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                "Оценката трябва да бъде между 1 и 5."
            )

        return rating
