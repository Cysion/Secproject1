from django.urls import path

from . import views

app_name = 'prepare'
urlpatterns = [
    # ex: /polls/
    path('memory/add/', views.addMemoryView, name='add-memory'),
    path('memory/', views.MemoryView, name='memory')
]
