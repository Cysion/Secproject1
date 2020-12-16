from django.urls import path

from . import views

app_name = 'info'
urlpatterns = [
    # ex: /polls/
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.MenuView, name="menu"),
    path('about/', views.AboutView, name="about"),
    path('howto/', views.HowToView, name="how-to"),
    path('privacy_gdpr/', views.PrivacyGDPRView, name="privacy-gdpr"),
    path('volunteering_disclaimer/', views.VolunteeringDisclaimerView, name="volunteering-disclaimer"),
    path('tos/', views.ToSView, name="terms-of-service")
]
