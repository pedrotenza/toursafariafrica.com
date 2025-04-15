from django.urls import path
from . import views

urlpatterns = [
    path('', views.safari_list, name='safari_list'),
    path('safari/<int:safari_id>/', views.safari_detail, name='safari_detail'),
]

