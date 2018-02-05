from django import forms
from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login,)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import (LoginView, PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView,
                                       PasswordChangeView, PasswordChangeDoneView)
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, resolve_url
from django.views import View
from django.views.generic import TemplateView

from .forms import (CreateProfileForm_profile, CreateProfileForm_user, UserCreationForm,
                    PasswordResetCustomForm)
from .models import User
from .tokens import account_activation_token


class Register(View):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    activation_email_template = 'registration/account_activation_email.html'

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
            user = form.save()
            user.profile.email_confirmed = False
            user.save()
            subject = 'Aktywuj konto na pracor.pl'
            message = render_to_string(self.activation_email_template, {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
            user.email_user(subject, message)
            #email = form.cleaned_data.get('email')
            #raw_password = form.cleaned_data.get('password1')
            #user = authenticate(email=email, password=raw_password)
            #login(request, user)
            return redirect('account_activation_sent')

        else:
            return render(request, self.template_name, {'form': form})


class AccountActivationSentView(TemplateView):
    template_name = 'registration/account_activation_sent.html'

class AccountActivateView(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.profile.email_confirmed = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.add_message(request, messages.SUCCESS, 'E-mail potwierdzony!')
            return redirect('create_profile')
        else:
            return render(request, 'registration/account_activation_invalid.html')            
            

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


class LoginCustomView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Prevent redirect loop when logged-in user tries to log in again.
        Required if LOGOUT_REDIRECT_URL is 'login'.
        /logged_out/ should never be shown to logged in users.
        """
        redirect_to = super().get_success_url()
        if redirect_to == self.request.path or redirect_to == '/logged_out/':
            redirect_to = resolve_url('home')
        return redirect_to


    def form_valid(self, form):
        """
        Check if user activated email. If not redirect to a web-page with message.
        """
        user = form.get_user()
        print(user.profile.email_confirmed)
        print(user)
        if not user.profile.email_confirmed:
            return redirect('email_confirm_reminder')
        else:
            return super().form_valid(form)
    
class PasswordResetCustomView(PasswordResetView):
    form_class = PasswordResetCustomForm
    template_name = 'registration/password_reset.html'


class PasswordResetDoneCustomView(PasswordResetDoneView):
    template_name = 'registration/password_done.html'

    
class PasswordResetConfirmCustomView(PasswordResetConfirmView):
    template_name = 'registration/password_confirm.html'

    
class PasswordResetCompleteCustomView(PasswordResetCompleteView):
    template_name = 'registration/password_complete.html'

    
class PasswordChangeCustomView(PasswordChangeView):
    template_name = 'registration/password_change.html'

    
class PasswordChangeDoneCustomView(PasswordChangeDoneView):
    template_name = 'registration/password_changed.html'

    
class LoggedOutView(TemplateView):
    template_name = 'registration/loggedout.html'

    def get(self, request, *args, **kwargs):
        """
        Make sure this template is not shown to logged in users.
        """
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class EmailConfirmReminderView(TemplateView):
    template_name = 'registration/email_confirm_reminder.html'
