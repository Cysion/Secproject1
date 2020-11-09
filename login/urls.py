from django.urls import path

from . import views

app_name = 'login'
urlpatterns = [
    # ex: /polls/
    path('', views.LoginView, name='Login'),
    path('register/', views.RegisterView, name='Register'),
    path('forgotpassword/', views.forgotPasswordView, 'Forgot-Password')
]
