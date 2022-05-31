from django.urls import path, re_path

from .apis.user_actions_apis import CurrentUserView, UserActionView, UsersView
from .apis.user_auth import LoginView, LogOutView

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="user_login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("users/", UsersView.as_view(), name="users_actions"),
    path("users/current/", CurrentUserView.as_view(), name="current_user",),
    re_path(
        r"^user/(?P<user_id>[a-zA-Z0-9]+)/$",
        UserActionView.as_view(),
        name="user_actions",
    ),
]
