from django.urls import path
from . import views

app_name = 'legislators'
urlpatterns = [
	path('', views.index, name='index'),
	path('<int:legislator_id>', views.detail, name='detail')
]
