from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import ConstituentCreationForm


class SignUpView(CreateView):
    form_class = ConstituentCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
