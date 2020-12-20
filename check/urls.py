from django.urls import path

from . import views

app_name = 'check'
urlpatterns = [
    # ex: /polls/
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.green_case_view, name="redir-green"),
    path('1/', views.green_case_view, name="green-case"),
    path('2/', views.well_feeling_view, name="well-feeling"),
    path('3/', views.save_me_plan_view, name="save-me-plan"),
    path('4/', views.practice_self_care_view, name="practice-self-care"),
    path('checkup/', views.checkup_view, name='checkup')

]
