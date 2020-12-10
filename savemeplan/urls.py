from django.urls import path

from . import views

app_name = 'savemeplan'
urlpatterns = [
    path('', views.StartView, name='Start'),
    path('<int:step>/', views.StepView, name="Step")
]
