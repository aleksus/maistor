from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/<int:request_id>/",
        views.create_offer,
        name="create_offer"
    ),
    path(
        "request/<int:request_id>/",
        views.request_offers,
        name="request_offers"
    ),
    path(
        "accept/<int:offer_id>/",
        views.accept_offer,
        name="accept_offer"
    ),
    path(
        "my-orders/",
        views.master_orders,
        name="master_orders"
    ),
    path(
        "complete/<int:request_id>/",
        views.complete_order,
        name="complete_order"
    ),
]
