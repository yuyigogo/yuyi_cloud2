from django.urls import path

from .apis.user_apis import LoginView

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="user_login"),
]
