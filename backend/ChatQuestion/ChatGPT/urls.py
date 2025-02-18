from django.urls import path

from . import views
from .views import chat_view
urlpatterns = [
    path("", views.index, name="index"),
    path('chat/', chat_view, name='chat'),
    path('create_user/', views.create_user, name='create_user'),
    path('save_chat/', views.save_chat, name='save_chat'),
    path('save_report/', views.save_report, name='save_report'),
]