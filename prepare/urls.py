from django.urls import path

from . import views

app_name = 'prepare'
urlpatterns = [
    # ex: /polls/
<<<<<<< HEAD
    path('', views.MenuView, name='Menu')
    #path('1/', views.HowToView, name='How-To'),
    #path('2/', views.PracticeBreathingView, name='Practice-Breathing'),
    #path('3/', views.SupportiveMemoriesView, name='Supportive-Memories'),
    #path('4/', views.DestructiveMemoriesView, name='Destructive-Memories'),
    #path('', views.IndexView, name='index'),
=======
    path('memory/add/', views.addMemoryView, name='add-memory')
>>>>>>> 295096ec73674334b1399817c3b09867ba94311d
]
