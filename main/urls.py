from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path('upload', upload, name='upload')
]

urlpatterns += [
    path('login', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout', auth_views.logout, {'template_name': 'logout.html'}, name='logout'),
    path('registration', reg, name="registration")
]

urlpatterns += [
    path('', main, name='main')
]

urlpatterns += [
    path('apikeys', ApiKeyCreateView.as_view(), name='apikey-create'),
    path('apikey/<uuid:pk>', test, name='api-key-details'),
    path('test/<int:pk>', testab, name='test-details'),
    path('testab/<int:pk>', videos_view, name='testab-details'),
    path('video/<int:pk>', video_details, name='video-details')
]

urlpatterns += [
    path('video/<int:pk>/file', video_file, name='video-file')
]