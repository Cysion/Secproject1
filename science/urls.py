from django.urls import path

from . import views

app_name = 'science'
urlpatterns = [
    path('export/', views.export_view, name='export'),
]
