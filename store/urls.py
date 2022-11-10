from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("api/", views.ProductListView.as_view(), name="store_home"),
    path("api/category/", views.CategoryListView.as_view(), name="categories"),
    path("api/brands/", views.ProductBrandListView.as_view(), name="brands"),
    path("api/<slug:slug>/", views.Product.as_view(), name="product"),
    path("api/category/<slug:slug>/", views.CategoryItemView.as_view(), name="category_item"),
    path("api/wishlist", views.WishlistView.as_view(), name="wishlist"),
    path("api/toggle_to_wishlist/<int:id>", views.ToggleProductToWishlistView.as_view(), name="user_wishlist"),
]
