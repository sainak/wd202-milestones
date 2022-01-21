from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView


class UserLoginView(LoginView):
    template_name = "accounts/login.html"


class UserSignupView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = "/login/"
