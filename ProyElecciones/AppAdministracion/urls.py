from django.contrib.auth.decorators import login_required
from django.urls import path
from .views.usuarios import *
from .views.auditoria import *


urlpatterns = [
    # Usuarios
    path('usuarios/', login_required(ListadoUsuarios.as_view()), name='listado-de-usuarios'),
    path('usuario/crear/', login_required(CrearUsuario.as_view()), name='crear-usuario'),
    path('usuario/actualizar/<int:pk>', login_required(ActualizarUsuario.as_view()), name='actualizar-usuario'),
    path('usuario/eliminar/<int:pk>', login_required(EliminarUsuario.as_view()), name='eliminar-usuario'),
    path('listadousertiemporeal/', login_required(UsuariosTiempoReal.as_view()),
         name='listado-de-user-tiempo-real'),
    # Usuarios
    path('exportarusuarios/', login_required(exportarUsuarios), name='exportar-usuarios-excel'),

    # Auditoria
    path('auditoria/', login_required(ListadoAuditorias.as_view()), name='listado-de-auditorias'),

    # Manuales
    path('manuallectorcge/', login_required(DescargarManualLectorCGE), name='manual-lector-cge'),
    path('manualpersonalcge/', login_required(DescargarManualPersonalCGE), name='manual-personal-cge'),
    path('manuallogisticacge/', login_required(DescargarManualLogisticaCGE), name='manual-logistica-cge'),
    path('manualdistrito/', login_required(DescargarManualDistrito), name='manual-distrito'),
    path('manualsubdistrito/', login_required(DescargarManualSubdistrito), name='manual-subdistrito'),
    path('manualtableros/', login_required(DescargarManualTableros), name='manual-tableros'),
]
