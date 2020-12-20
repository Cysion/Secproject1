from django.urls import path

from . import views

app_name = 'professionals'
urlpatterns = [
    # ex: /polls/
    path('', views.clients_view, name='clients'),
    path('<int:UserId>/profile/', views.profile_view, name="profile"),
    path('<int:UserId>/prepare/<int:page>/', views.prepare_view, name="prepare"),
    path('<int:UserId>/savemeplan/', views.saveme_plan_view, name="savemeplan"),
    path('<int:UserId>/check/', views.check_view, name="check"),
]
