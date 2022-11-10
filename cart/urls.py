from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.GetCartView.as_view(), name="cart"),
    path("get_orders/", views.GetOrdersView.as_view(), name="orders"),
    path("Chekout/", views.Chekout.as_view(), name="Chekout"),
    path("add_item_to_cart/", views.AddItemToCart.as_view(),
         name="add_item_to_cart"),
    path("modify_cart_item/", views.ModifyCartItem.as_view(),
         name="modify_cart_item"),
]
