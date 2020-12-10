from django.urls import path

from . import views

app_name = 'check'
urlpatterns = [
    # ex: /polls/
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.GreenCaseView, name="redir-green"),
    path('1/', views.GreenCaseView, name="green-case"),
    path('2/', views.WellFeelingView, name="well-feeling"),
    path('3/', views.SaveMePlanView, name="save-me-plan"),
    path('4/', views.PracticeSelfCareView, name="practice-self-care")

]
