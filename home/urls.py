from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    # ex: /polls/
    path('', views.IndexView, name='index'),
    path('showcase/', views.ShowcaseView, name='Showcase'),
]
