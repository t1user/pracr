from django import forms
from django.contrib.auth import (authenticate, get_user_model, login,)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from .forms import CreateProfileForm_profile, CreateProfileForm_user, UserCreationForm
from .models import User


class Register(View):
    form_class = UserCreationForm
    template_name = "registration/register.html"

    def get(self, request, *args, **kwargs):
        #if user is logged in, they shouldn't be able to register
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name,
                      {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('create_profile')

        else:
            return render(request, self.template_name, {'form': form})


class RegisterSuccess(TemplateView):
    template_name = "registration/register_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['session_data'] = self.request.session['linkedin_data']
        return context

    
class CreateProfileView(LoginRequiredMixin, View):
    """
    View with two forms to fill in missing data in User model and Profile.
    Currently not in use because name is not neccessary.
    """
    user_form_class = CreateProfileForm_user
    profile_form_class = CreateProfileForm_profile
    template_name = "registration/create_profile.html"

    def get(self, request, *args, **kwargs):
        profile_form = self.profile_form_class()
        return render(request, self.template_name,
                      {'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        profile_form = self.profile_form_class(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('register_success')
        return render(request, self.template_name,
                          {'profile_form': profile_form})

    
class LoginErrorView(View):
    """
    Redirected to if there's a social auth login error and the error is not
    caught by the middleware. Currently happens when debug is off.
    """

    template_name = "registration/login_error.html"

    def get(self, request, *args, **kwargs):
        return render(request,self.template_name)
