
from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service


DATA = {
    "Шпакловка и боядисване": [
        "Шпакловка",
        "Боядисване с латекс",
        "Полагане на декоративна мазилка",
        "Монтаж на гипсокартон",
    ],

    "Фаянс и теракот": [
        "Лепене на фаянс",
        "Лепене на теракот",
        "Полагане на гранитогрес",
        "Фугиране",
    ],

    "Електроуслуги": [
        "Изграждане на електроинсталация",
        "Монтаж на контакти",
        "Монтаж на осветление",
        "Ремонт на електроинсталация",
    ],

    "ВиК услуги": [
        "Монтаж на водопровод",
        "Ремонт на тръби",
        "Монтаж на санитария",
        "Отпушване на канали",
    ],

    "Отопление": [
        "Монтаж на радиатори",
        "Монтаж на котли",
        "Изграждане на отоплителна система",
        "Поддръжка на отопление",
    ],

    "Замазки и подове": [
        "Циментова замазка",
        "Саморазливна замазка",
        "Полагане на ламинат",
        "Полагане на паркет",
    ],
}


class Command(BaseCommand):
    help = "Добавя примерни категории и услуги"

    def handle(self, *args, **kwargs):

        for category_name, services in DATA.items():

            category, created = (
                ServiceCategory.objects.get_or_create(
                    name=category_name
                )
            )

            for service_name in services:
                Service.objects.get_or_create(
                    category=category,
                    name=service_name
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Категориите и услугите са добавени успешно!"
            )
        )
