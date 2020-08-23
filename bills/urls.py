from django.urls import path
from . import views

app_name = 'bills'
urlpatterns = [
	path('', views.index, name='index'),
	path('<str:state>/<int:session>/<str:bill_id>', views.detail, name='detail'),
	path('<str:state>/<int:session>/<str:bill_id>/vote/', views.vote, name='vote'),
]
