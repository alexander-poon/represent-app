from django import forms

from constituents.models import Vote


class VoteForm(forms.ModelForm):

	class Meta:
		model = Vote
		fields = ('position',)
