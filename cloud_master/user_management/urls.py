from django.urls import path, re_path

from .apis.user_actions_apis import UsersView, CurrentUserView
from .apis.user_auth import LoginView, LogOutView

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="user_login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("users/", UsersView.as_view(), name="users_actions"),
    path("users/current/", CurrentUserView.as_view(), name="current_user",),
]
