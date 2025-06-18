from django.urls import path
from . import views

urlpatterns = [
    path('', views.estudiantes, name='estudiantes'),
    path('listadoEstudiantes/', views.listaEstudiantes, name='lista_estudiantes'),
    path('agregarEstudiante/', views.agregarEstudiante, name='addEstudiante'),
    path('actualizarEstudiante/<id>/', views.actualizarEstudiante, name='actEstudiante'),
    path('eliminarEstudiante/<id>/', views.eliminarEstudiante, name='dltEstudiante'),
    path('verEstudiante/<id>/', views.mostrarEstudiante, name='verEstudiante'),
    path('subir_documentos/', views.subir_documentos, name='subir_documentos'),
    path('actualizar_documentos/<id>/', views.actualizar_documentos, name='actualizar_documentos'),
    path('documentos_pendientes/', views.documentos_pendientes, name='documentos_pendientes'),
    path('documentos_aprobados/', views.documentos_aprobados, name='documentos_aprobados'),
    path('documentos_rechazados/', views.documentos_rechazados, name='documentos_rechazados'),
    path('visualizar_documento/<id>/', views.visualizarDocumentos, name='visualizarDocumento'),
    path('cambiar-estado-inscripcion/<id>/', views.cambiar_estado_inscripcion, name='cambiar_estado_inscripcion'),
    path('actualizar_perfil/', views.actualizar_perfil_estudiante, name='actualizar_perfil_estudiante'),
    path('eliminarDocumentos/<id>/', views.eliminarRegistros, name='eliminarDocumentos'),
    path('subir_archivo_ajax/', views.subir_archivo_ajax, name='subir_archivo_ajax'),
]
