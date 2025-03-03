from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('chat/', views.chat_view, name='chat'),
    path('create_user/', views.create_user, name='create_user'),
    path('save_chat/', views.save_chat, name='save_chat'),
    path('save_report/', views.save_report, name='save_report'),
    path('get_chat_history/', views.get_chat_history, name='get_chat_history'),
    path('report/', views.report_list, name='report-list'),
    path('report/download-all/', views.download_all_reports, name='download-all'),
]