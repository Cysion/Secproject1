from django.urls import path

from . import views

app_name = 'login'
urlpatterns = [
    path('', views.login_view, name='Login'),
    path('register/', views.register_view, name='Register'),
    path('forgotpassword/', views.forgot_password_view, name='Forgot-Password')
]
