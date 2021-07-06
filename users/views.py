import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, ContactForm


User = get_user_model()


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    return {
        'year': dt.datetime.now().year
    }


def user_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            return redirect('/thank-you/')

        return render(request, 'contact.html', {'form': form})

    form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def thankyou(request):
    return render(request, 'thank-you.html')
