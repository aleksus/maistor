from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/<int:request_id>/",
        views.CreateOfferView.as_view(),
        name="create_offer"
    ),
    path(
        "request/<int:request_id>/",
        views.RequestOffersView.as_view(),
        name="request_offers"
    ),
    path(
        "accept/<int:offer_id>/",
        views.AcceptOfferView.as_view(),
        name="accept_offer"
    ),
    path(
        "my-orders/",
        views.MasterOrdersView.as_view(),
        name="master_orders"
    ),
    path(
        "complete/<int:request_id>/",
        views.CompleteOrderView.as_view(),
        name="complete_order"
    ),
]
