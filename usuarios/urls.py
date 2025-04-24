from django.urls import path
from . import views

urlpatterns = [
    #Empleados
    path('', views.usuarios, name='usuarios'),
    path('empleados/', views.mostrarUsuarios, name='empleados'),
    path('addUsers/', views.addUsuarios, name='addUsers'),
    path('actUsers/<id>/', views.actUsuarios, name='actUsers'),
    path('dltUsers/<id>/', views.dltUsuarios, name='dltUsers'),
    path('verEmpleado/<id>/', views.tarjetaUsuarios, name='viewUser'),
    path('user/<int:user_id>/asignar_permiso/<int:permission_id>/', views.asignar_permiso, name='asignar_permiso'),
    path('user/quitar_permiso/<int:user_id>/', views.quitar_permiso, name='quitar_permiso'),
    path('user/<int:user_id>/permissions/', views.view_user_permissions, name='view_user_permissions'),
    path('cuentaBloqueada/', views.cuenta_bloqueada, name='cuenta_bloqueada'),
    path('actualizar_perfil/', views.actualizar_perfil_empleado, name='actualizar_perfil_empleado'),
    
    #Cargos
    path('cargos/', views.Cargos, name='cargos'),
    path('actCargos/<id>/', views.actCargos, name='actCargos'),
    path('dltCargos/<id>/', views.dltCargos, name='dltCargos'),
]
