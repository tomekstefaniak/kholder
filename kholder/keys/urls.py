from django.urls import path
from . import views


urlpatterns = [
    path('', views.key_list, name='key_list'),
	path('<str:label>', views.key_detail, name='key_detail'),
    path('decrypt/<str:label>', views.key_detail_decrypt, name='key_detail_decrypt'),
]
