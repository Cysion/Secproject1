from django.urls import path

from . import views

app_name = 'userprofile'
urlpatterns = [
    # ex: /polls/
    path('', views.ProfileView, name='Profile'),
    path('edit/', views.EditProfileView, name='Edit-profile'),
    path('backupkey/', views.BackupKeyView, name="Backupkey"),
    path('changepassword/', views.changePassView, name="Change-password")
]
