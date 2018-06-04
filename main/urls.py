from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path('upload', upload, name='upload')
]

urlpatterns += [
    path('login', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout', auth_views.logout, name='logout'),
    path('registration', reg, name="registration")
]

urlpatterns += [
    path('', main, name='main')
]

urlpatterns += [
    path('apikey', ApiKeyCreateView.as_view(), name='apikey-create'),
    path('test/<uuid:pk>', test, name='api-key-details'),
    path('testab/<int:pk>', testab, name='test-details'),
    path('video/<int:pk>', video, name='testab-details'),
]