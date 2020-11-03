from django.urls import path

from . import views

app_name = 'userprofile'
urlpatterns = [
    # ex: /polls/
    path('', views.ProfileView, name='Profile'),
]
