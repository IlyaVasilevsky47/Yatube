from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "password_change/",
        LoginView.as_view(template_name="users/password_change_form.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        LoginView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        LoginView.as_view(template_name="users/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        LoginView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uid64>/<token>/",
        LoginView.as_view(template_name="users/password_reset_confirm.html"),
        name="reset_confirm",
    ),
    path(
        "reser/done/",
        LoginView.as_view(template_name="users/password_reset_complete.html"),
        name="reset_complete",
    ),
]