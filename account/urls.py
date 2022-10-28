from django.urls import path
from .views import RegisterView, LoadUserView, BlacklistTokenView, VerifyEmail, RequestPasswordResetEmail, PasswordTokenCheckAPI, SetNewPasswordAPIView

app_name = "account"

urlpatterns = [
    # routes for jwt auth
    path('register/', RegisterView.as_view(), name="register"),
    path('user/', LoadUserView.as_view(), name="user"),
    path('logout/', BlacklistTokenView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete')

]
