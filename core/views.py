from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views import generic

from astrophotography.forms import *


class IndexView(generic.TemplateView):
    template_name = 'index.html'


class Success(generic.TemplateView):
    template_name = 'success.html'


class SignUpView(generic.FormView):
    # form_class = SignUpForm
    template_name = 'registration/register_form.html'
    success_url = '/success/'

    # return empty form
    def get(self, request, *args, **kwargs):
        user_form = UserForm(prefix='user')
        cmdr_form = CommanderForm(prefix='cmdr')
        return render(request, self.template_name, {'user_form': user_form, 'cmdr_form': cmdr_form})

    # process submitted form
    def post(self, request, *args, **kwargs):
        # process user portion of form
        user_form = UserForm(request.POST, prefix='user')
        cmdr_form = CommanderForm(request.POST, prefix='cmdr')  # created here in case user_form fails validation
        if user_form.is_valid() and cmdr_form.is_valid():  # validate
            # signal receiver creates and links a new Commander object on user_form.save(). The cmdr_form is
            # re-initialized with an instance of user.commander and its data is saved to that object.
            user = user_form.save()
            cmdr_form = CommanderForm(request.POST, prefix='cmdr', instance=user.commander)  # includes instance
            cmdr_form.save()  # save commander data
            user.save()

            # authenticate
            raw_pw = user_form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_pw)
            login(request, user)
            return redirect(self.success_url)

        # if both forms are not valid, drop out of if clause and re-render form with errors
        return render(request, self.template_name, {'user_form': user_form, 'cmdr_form': cmdr_form})