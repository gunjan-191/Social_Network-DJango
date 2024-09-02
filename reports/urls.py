from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('summary/', views.summary_report, name='summary_report'),
    path('settings/', views.settings, name='settings'),
    path('notification-settings/', views.notification_settings, name='notification_settings'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('accounts/login/', views.custom_login, name='custom_login'),
    path('weather/', views.weather_report, name='weather_report'),
    path('currency/', views.currency_conversion, name='currency_conversion'),
    path('send-message/', views.send_message_view, name='send_message'),  
    path('generate-report/', views.generate_report_view, name='generate_report'),
    path('send-report/', views.send_report_view, name='send_report'),





] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
