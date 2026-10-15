from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('edit/<int:pk>/', views.edit_log, name='edit_log'),
]