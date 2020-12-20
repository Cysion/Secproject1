from django.urls import path

from . import views

app_name = 'userprofile'
urlpatterns = [
    # ex: /polls/
    path('', views.profile_view, name='Profile'),
    path('edit/', views.edit_profile_view, name='Edit-profile'),
    path('backupkey/', views.backup_key_view, name="Backupkey"),
    path('changepassword/', views.change_pass_view, name="Change-password"),
    path('relations/', views.relations_view, name="Relations"),
    path('relations/add/', views.add_relations_view, name="Add-relations"),
    path('gdpr/', views.gdpr_view, name="GDPR"),
    path('gdpr/researchdata/', views.research_data_view, name="Research-data"),
    path('relations/manage/', views.manage_relations_view, name="Manage-relations")
]
