from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ConstituentCreationForm, ConstituentChangeForm
from .models import Constituent


class ConstituentAdmin(UserAdmin):
    add_form = ConstituentCreationForm
    form = ConstituentChangeForm
    model = Constituent
    list_display = ('username',)
    list_display_links = ('username',)


admin.site.register(Constituent, ConstituentAdmin)
