from django.urls import path

from . import views

app_name = 'prepare'
urlpatterns = [
    # ex: /polls/
    path('contacts/', views.ContactsView, name='contacts'),
    path('contacts/edit/<int:id>', views.editContactView, name='edit-contact'),
    path('memory/add/', views.addMemoryView, name='add-memory'),
    path('memory/<int:id>/', views.MemoryView, name='memory'),
    path('<int:page>/', views.MenuView, name='menu-page'),
    path('7/<int:id>', views.removeDiaryView, name='removeDiary-page'),
    path('', views.MenuView, name='menu'),
    #path('1/', views.HowToView, name='How-To'),
    #path('2/', views.PracticeBreathingView, name='Practice-Breathing'),
    #path('3/', views.SupportiveMemoriesView, name='Supportive-Memories'),
    #path('4/', views.DestructiveMemoriesView, name='Destructive-Memories'),
]
