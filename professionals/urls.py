from django.urls import path

from . import views

app_name = 'professionals'
urlpatterns = [
    # ex: /polls/
    path('', views.ClientsView, name='clients'),
    path('<int:UserId>/profile/', views.profileView, name="profile"),
    path('<int:UserId>/savemeplan/', views.saveMePlanView, name="savemeplan"),
    path('<int:UserId>/check/', views.CheckView, name="check"),
]
