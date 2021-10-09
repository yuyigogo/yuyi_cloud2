from django.urls import path

from .apis.user_apis import LoginView, LogOutView

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="user_login"),
    path("logout/", LogOutView.as_view(), name="logout"),
]
