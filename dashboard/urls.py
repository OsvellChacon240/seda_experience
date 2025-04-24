from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('error404/', views.error404, name='E404'), 
    path('error404/', views.error403, name='E403'), 
    path('buscar/', views.buscar, name='buscar'),   
    path('change_language/<str:lang_code>/', views.change_language, name='change_language'),
    path('estudiantesDashboard/', views.estudiante_dashboard ,name='estudiante_dashboard')
]