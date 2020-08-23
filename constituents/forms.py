from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Constituent


class ConstituentCreationForm(UserCreationForm):
	address = forms.CharField(
		widget=forms.TextInput(),
		help_text='Optional. We use this to identify your legislators and legislation '
		'affecting local issues in your town/city/county.',
		required=False
	)

	class Meta:
		model = Constituent
		fields = ('username', 'address')


class ConstituentChangeForm(UserChangeForm):

	class Meta:
		model = Constituent
		fields = ('username', 'address')
