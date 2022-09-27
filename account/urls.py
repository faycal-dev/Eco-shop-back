from django.urls import path
from .views import RegisterView, LoadUserView

app_name = "account"

urlpatterns = [
    # routes for jwt auth
    path('register/', RegisterView.as_view()),
    path('user/', LoadUserView.as_view()),
    
        
    # routes for csrf coockies auth
    # path("csrf/", views.get_csrf, name="api-csrf"),
    # path("login/", views.loginView, name="api-login"),
    # path("whoami/", views.WhoAmIView.as_view(), name="whoami"),
]
