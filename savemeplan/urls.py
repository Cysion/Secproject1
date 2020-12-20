from django.urls import path

from . import views

app_name = 'savemeplan'
urlpatterns = [
    path('', views.start_view, name='Start'),
    path('<int:step>/', views.step_view, name="Step"),
    path('history/', views.history_view, name="History"),
    path('agreement.pdf', views.download_contract_view, name="agreement")
]
