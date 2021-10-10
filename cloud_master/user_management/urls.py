from django.urls import path

from .apis.user_apis import LoginView, LogOutView,TestView

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="user_login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("test/", TestView.as_view(), name="test"),
]
