from django.urls import path

from . import views

app_name = 'login'
urlpatterns = [
    # ex: /polls/
    path('register/', views.RegisterView, name='Register'),
]
