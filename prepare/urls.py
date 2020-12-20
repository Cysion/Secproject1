from django.urls import path

from . import views

app_name = 'prepare'
urlpatterns = [
    # ex: /polls/
    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/edit/<int:id>', views.edit_contact_view, name='edit-contact'),
    path('memory/add/', views.add_memory_view, name='add-memory'),
    path('memory/<int:id>/', views.memory_view, name='memory'),
    path('<int:page>/', views.Menu_view, name='menu-page'),
    path('7/<int:id>/', views.remove_diary_view, name='removeDiary-page'),
    path('', views.Menu_view, name='menu'),
    #path('1/', views.HowToView, name='How-To'),
    #path('2/', views.PracticeBreathingView, name='Practice-Breathing'),
    #path('3/', views.SupportiveMemoriesView, name='Supportive-Memories'),
    #path('4/', views.DestructiveMemoriesView, name='Destructive-Memories'),
]
