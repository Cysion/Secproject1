from django.urls import path

from . import views

app_name = 'info'
urlpatterns = [
    # ex: /polls/
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.menu_view, name="menu"),
    path('about/', views.about_view, name="about"),
    path('howto/', views.how_to_view, name="how-to"),
    path('privacy_gdpr/', views.privacy_gdpr_view, name="privacy-gdpr"),
    path('volunteering_disclaimer/', views.volunteering_disclaimer_view, name="volunteering-disclaimer"),
    path('tos/', views.tos_view, name="terms-of-service")
]
