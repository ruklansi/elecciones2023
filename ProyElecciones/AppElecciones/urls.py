from django.urls import path

from .funciones_comunes import *
from .views.CdoGrlElect import *
from .views.LED import *
from .views.circuitos import *
from .views.distrito import *
from .views.inicio import *
from .views.locales import *
from .views.movimientos import *
from .views.novedadesgenerales import *
from .views.personas import *
from .views.reportes import *
from .views.resumen_general import exportarResumenGeneral
from .views.secciones import *
from .views.subdistrito import *
from .views.vehiculoscontratados import *
from .views.vehiculospropios import *
from .views.SACAS import *
from .views.SED import *
from .views.lugar_interes import *
from .views.GuiaAutoridades import *
from .views.Tableros import *


urlpatterns = [
    # Inicio
    path('', login_required(Inicio.as_view()), name='inicio'),

    # Cdo Grl Elect
    path('cdogrlelect/detalles/<int:pk>',
         login_required(DetalleCdoGrlElect.as_view()), name='detalles-cdogrlelect'),

    # Distribucion de personal ajax en Cdo Grl Elect

    path('listardistribucioncge/', login_required(ListarDistribucionCdoGrlElectAjax.as_view()),
         name='listar-distribucion-en-cge'),
    path('cge/distribucion/crear/', login_required(CrearDistribucionEnCdoGrlElect.as_view()),
         name='crear-distribucion-en-cge'),
    path('cge/distribucion/actualizar/<int:pk>',
         login_required(ActualizarDistribucionEnCdoGrlElect.as_view()), name='actualizar-distribucion-en-cge'),
    path('cge/distribucion/eliminar/<int:pk>',
         login_required(EliminarDistribucionEnCdoGrlElect.as_view()), name='eliminar-distribucion-en-cge'),

    # Reserva de personal ajax en Cdo Grl Elect

    path('listarreservacge/', login_required(ListarReservaCdoGrlElectAjax.as_view()),
         name='listar-reserva-en-cge'),
    path('cge/reserva/crear/', login_required(CrearReservaEnCdoGrlElect.as_view()),
         name='crear-reserva-en-cge'),
    path('cge/reserva/actualizar/<int:pk>',
         login_required(ActualizarReservaEnCdoGrlElect.as_view()), name='actualizar-reserva-en-cge'),
    path('cge/reserva/eliminar/<int:pk>',
         login_required(EliminarReservaEnCdoGrlElect.as_view()), name='eliminar-reserva-en-cge'),

    # Vehiculos propios ajax en Cdo Grl Elect

    path('listarvhpropioscge/', login_required(ListarVehiculosPropiosCdoGrlElectAjax.as_view()),
         name='listar-vhpropios-en-cge'),
    path('cge/vhpropios/crear/', login_required(CrearVehiculoPropioEnCdoGrlElect.as_view()),
         name='crear-vhpropios-en-cge'),
    path('cge/vhpropios/actualizar/<int:pk>',
         login_required(ActualizarVehiculoPropioEnCdoGrlElect.as_view()), name='actualizar-vhpropios-en-cge'),
    path('cge/vhpropios/eliminar/<int:pk>',
         login_required(EliminarVehiculosPropiosEnCdoGrlElect.as_view()), name='eliminar-vhpropios-en-cge'),

    # Vehiculos contratados ajax en Cdo Grl Elect

    path('listarvhcontratadoscge/', login_required(ListarVehiculosContratadosCdoGrlElectAjax.as_view()),
         name='listar-vhcontratados-en-cge'),
    path('cge/vhcontratados/crear/', login_required(CrearVehiculoContratadoEnCdoGrlElect.as_view()),
         name='crear-vhcontratados-en-cge'),
    path('cge/vhcontratados/actualizar/<int:pk>',
         login_required(ActualizarVehiculoContratadoEnCdoGrlElect.as_view()), name='actualizar-vhcontratados-en-cge'),
    path('cge/vhcontratados/eliminar/<int:pk>',
         login_required(EliminarVehiculosContratadosEnCdoGrlElect.as_view()), name='eliminar-vhcontratados-en-cge'),

    path('resumencge/', login_required(ResumenDelCGEAjax.as_view()),
         name='resumn-del-cge-ajax'),

    # Distritos

    path('distrito/', login_required(ListadoDistritos.as_view()), name='listado-de-distritos'),
    path('distrito/detalles/<int:pk>', login_required(DetalleDistrito.as_view()), name='detalles-distito'),

    # Distribucion de personal ajax en distritos

    path('listardistribuciondistrito/', login_required(ListarDistribucionDistritoAjax.as_view()),
         name='listar-distribucion-en-distrito'),
    path('distrito/distribucion/crear/', login_required(CrearDistribucionEnDistrito.as_view()),
         name='crear-distribucion-en-distrito'),
    path('distrito/distribucion/actualizar/<int:pk>',
         login_required(ActualizarDistribucionEnDistrito.as_view()), name='actualizar-distribucion-en-distrito'),
    path('distrito/distribucion/eliminar/<int:pk>',
         login_required(EliminarDistribucionEnDistrito.as_view()), name='eliminar-distribucion-en-distrito'),

    # Reserva de personal ajax en Distritos

    path('listarreservadistrito/', login_required(ListarReservaDistritoAjax.as_view()),
         name='listar-reserva-en-distrito'),
    path('distrito/reserva/crear/', login_required(CrearReservaEnDistrito.as_view()),
         name='crear-reserva-en-distrito'),
    path('distrito/reserva/actualizar/<int:pk>',
         login_required(ActualizarReservaEnDistrito.as_view()), name='actualizar-reserva-en-distrito'),
    path('distrito/reserva/eliminar/<int:pk>',
         login_required(EliminarReservaEnDistrito.as_view()), name='eliminar-reserva-en-distrito'),

    # Vehiculos propios ajax en Distritos

    path('listarvhpropiosdistrito/', login_required(ListarVehiculosPropioEnDistritosAjax.as_view()),
         name='listar-vhpropios-distrito'),
    path('distrito/vhpropios/crear/', login_required(CrearVehiculoPropioEnDistrito.as_view()),
         name='crear-vhpropios-distrito'),
    path('distrito/vhpropios/actualizar/<int:pk>',
         login_required(ActualizarVehiculoPropioEnDistrito.as_view()), name='actualizar-vhpropios-distrito'),
    path('distrito/vhpropios/eliminar/<int:pk>',
         login_required(EliminarVehiculosPropiosEnDistrito.as_view()), name='eliminar-vhpropios-distrito'),

    # Vehiculos contratados ajax en Distritos

    path('listarvhcontratadosdistrito/', login_required(ListarVehiculosContratadosDistritoAjax.as_view()),
         name='listar-vhcontratados-en-distrito'),
    path('distrito/vhcontratados/crear/', login_required(CrearVehiculoContratadoEnDistrito.as_view()),
         name='crear-vhcontratados-distrito'),
    path('distrito/vhcontratados/actualizar/<int:pk>',
         login_required(ActualizarVehiculoContratadoEnDistrito.as_view()), name='actualizar-vhcontratados-distrito'),
    path('distrito/vhcontratados/eliminar/<int:pk>',
         login_required(EliminarVehiculosContratadosEnDistrito.as_view()), name='eliminar-vhcontratados-distrito'),
    path('obtenervhcontratadosdistrito/', login_required(ObtenerVehiculosContratadosDistritoAjax.as_view()),
         name='obtener-vhcontratados-distrito'),

    path('resumendistrito/', login_required(ResumenDelDistritoAjax.as_view()),
         name='resumn-del-distrito-ajax'),

    # Subdistritos

    path('subdistrito/', login_required(ListadoSubdistritos.as_view()), name='listado-de-subdistritos'),
    path('subdistrito/detalles/<int:pk>', login_required(DetalleSubdistrito.as_view()), name='detalles-subdistito'),

    # Distribucion de personal ajax en subdistritos

    path('listardistribucionsubdistrito/', login_required(ListarDistribucionSubdistritoAjax.as_view()),
         name='listar-distribucion-en-subdistrito'),
    path('subdistrito/distribucion/crear/', login_required(CrearDistribucionEnSubdistrito.as_view()),
         name='crear-distribucion-en-subdistrito'),
    path('subdistrito/distribucion/actualizar/<int:pk>',
         login_required(ActualizarDistribucionEnSubdistrito.as_view()), name='actualizar-distribucion-en-subdistrito'),
    path('subdistrito/distribucion/eliminar/<int:pk>',
         login_required(EliminarDistribucionEnSubdistrito.as_view()), name='eliminar-distribucion-en-subdistrito'),

    # Reserva de personal ajax en Subdistritos

    path('listarreservasubdistrito/', login_required(ListarReservaSubdistritoAjax.as_view()),
         name='listar-reserva-en-subdistrito'),
    path('subdistrito/reserva/crear/', login_required(CrearReservaEnSubdistrito.as_view()),
         name='crear-reserva-en-subdistrito'),
    path('subdistrito/reserva/actualizar/<int:pk>',
         login_required(ActualizarReservaEnSubdistrito.as_view()), name='actualizar-reserva-en-subdistrito'),
    path('subdistrito/reserva/eliminar/<int:pk>',
         login_required(EliminarReservaEnSubdistrito.as_view()), name='eliminar-reserva-en-subdistrito'),

    # Vehiculos propios ajax en Subdistritos

    path('listarvhpropiossubdistrito/', login_required(ListarVehiculosPropioEnSubdistritosAjax.as_view()),
         name='listar-vhpropios-subdistrito'),
    path('subdistrito/vhpropios/crear/', login_required(CrearVehiculoPropioEnSubdistrito.as_view()),
         name='crear-vhpropios-subdistrito'),
    path('subdistrito/vhpropios/actualizar/<int:pk>',
         login_required(ActualizarVehiculoPropioEnSubdistrito.as_view()), name='actualizar-vhpropios-subdistrito'),
    path('subdistrito/vhpropios/eliminar/<int:pk>',
         login_required(EliminarVehiculosPropiosEnSubdstrito.as_view()), name='eliminar-vhpropios-subdistrito'),

    # Vehiculos contratados ajax en Subdistritos

    path('listarvhcontratadossubdistrito/', login_required(ListarVehiculosContratadosSubdistritoAjax.as_view()),
         name='listar-vhcontratados-en-subdistrito'),
    path('subdistrito/vhcontratados/crear/', login_required(CrearVehiculoContratadoEnSubdistrito.as_view()),
         name='crear-vhcontratados-subdistrito'),
    path('subdistrito/vhcontratados/actualizar/<int:pk>',
         login_required(ActualizarVehiculoContratadoEnSubdistrito.as_view()),
         name='actualizar-vhcontratados-subdistrito'),
    path('subdistrito/vhcontratados/eliminar/<int:pk>',
         login_required(EliminarVehiculosContratadoEnSubdistrito.as_view()), name='eliminar-vhcontratados-subdistrito'),

    # Funciones ajax para cargar tarjetas de resumen en el subdistrito
    path('resumensubdistrito/', login_required(ResumenDelSubdistritoAjax.as_view()),
         name='resumn-del-subdistrito-ajax'),

    # Secciones

    path('seccion/', login_required(ListadoSecciones.as_view()), name='listado-de-secciones'),
    path('seccion/detalles/<int:pk>', login_required(DetalleSeccion.as_view()), name='detalles-seccion'),

    # Distribución de personal ajax en secciones

    path('listarorganizacionseccion/', login_required(ListarDistibucionPersonalSeccionAjax.as_view()),
         name='listar-organizacion-en-seccion'),
    path('seccion/organizacion/crear/', login_required(CrearDistribucionPersonalEnSeccion.as_view()),
         name='crear-organizacion-seccion'),
    path('seccion/organizacion/actualizar/<int:pk>',
         login_required(ActualizarDistribucionPersonalEnSeccion.as_view()), name='actualizar-organizacion-en-seccion'),
    path('seccion/organizacion/eliminar/<int:pk>',
         login_required(EliminarDistribucionPersonalEnSeccion.as_view()), name='eliminar-organizacion-en-seccion'),

    # Vehiculos propios ajax en Secciones

    path('listarvhpropiosseccion/', login_required(ListarVehiculosPropioEnSeccionesAjax.as_view()),
         name='listar-vhpropios-seccion'),
    path('seccion/vhpropios/crear/', login_required(CrearVehiculoPropioEnSeccion.as_view()),
         name='crear-vhpropios-seccion'),
    path('seccion/vhpropios/actualizar/<int:pk>',
         login_required(ActualizarVehiculoPropioEnSeccion.as_view()), name='actualizar-vhpropios-seccion'),
    path('seccion/vhpropios/eliminar/<int:pk>',
         login_required(EliminarVehiculosPropiosEnSeccion.as_view()), name='eliminar-vhpropios-seccion'),

    # Vehiculos contratados ajax en Secciones

    path('listarvhcontratadosseccion/', login_required(ListarVehiculosContratadosSeccionAjax.as_view()),
         name='listar-vhcontratados-en-seccion'),
    path('seccion/vhcontratados/crear/', login_required(CrearVehiculoContratadoEnSeccion.as_view()),
         name='crear-vhcontratados-seccion'),
    path('seccion/vhcontratados/actualizar/<int:pk>',
         login_required(ActualizarVehiculoContratadoEnSeccion.as_view()), name='actualizar-vhcontratados-seccion'),
    path('seccion/vhcontratados/eliminar/<int:pk>',
         login_required(EliminarVehiculosContratadoEnSeccion.as_view()), name='eliminar-vhcontratados-seccion'),

    # url ajax en Secciones

    path('resumenseccion/', login_required(ResumenDeLaSeccionAjax.as_view()),
         name='resumn-de-la-seccion-ajax'),

    # Circuitos

    path('circuito/crear/', login_required(CrearCircuito.as_view()), name='crear-circuito'),
    path('circuito/actualizar/<int:pk>', login_required(ActualizarCircuito.as_view()), name='actualizar-circuito'),
    path('circuito/eliminar/<int:pk>', login_required(EliminarCircuito.as_view()), name='eliminar-circuito'),
    path('circuito/detalles/<int:pk>', login_required(DetalleCircuito.as_view()), name='detalles-circuito'),
    path('listadocircuitofiltrado/', login_required(ListadoCircuitosFiltrados.as_view()),
         name='listado-de-circuitos-filtrados'),
    path('avanzarestado/', login_required(CircuitoAdelante.as_view()),
         name='avanzar-estado-circuitos'),
    path('detallescircuito/', login_required(DetallesDelCircuitoAjax.as_view()),
         name='detalles-del-circuito-ajax'),

    path('desplegarcircuito/', login_required(CircuitoDesplegar.as_view()),
         name="desplegar-circuito"),

    # url ajax en Circuitos

    path('filtracamposcircuitoajax/', login_required(FiltraCamposCircuitoAjax.as_view()),
         name='filtra-campos-circuito-ajax'),
    path('localesdelcircuito/', login_required(ListarLocalesDelCircuito.as_view()),
         name='listar-locales-del-circuito-ajax'),
    path('detallescircuito/', login_required(DetallesDelCircuitoAjax.as_view()),
         name='detalles-del-circuito-ajax'),

    # Locales

    path('listadolocalvalidado/', login_required(ListadoLocalesValidados.as_view()),
         name='listado-de-locales-validados'),
    path('listadolocalnovalidado/', login_required(ListadoLocalesNoValidados.as_view()),
         name='listado-de-locales-novalidados'),
    path('local/crear/', login_required(CrearLocal.as_view()), name='crear-local'),
    path('local/actualizar/<int:pk>',
         login_required(ActualizarLocal.as_view()), name='actualizar-local'),
    path('local/eliminar/<int:pk>/<str:tipo_local>/', login_required(EliminarLocal.as_view()), name='eliminar-local'),
    path('local/detalles/<int:pk>', login_required(DetalleLocal.as_view()), name='detalles-local'),
    path('detalleslocal/', login_required(DetallesDelLocalAjax.as_view()),
         name='detalles-del-local-ajax'),
    path('filtracamposlocalajax/', login_required(FiltraCamposLocalAjax.as_view()),
         name='filtra-campos-local-ajax'),
    path('usoajax/', login_required(EntradaAjax.as_view()), name='uso-ajax'),
    path('listadolocalurnas/', login_required(ListadoLocalesParaMaterialVotacionyUrnas.as_view()),
         name='listado-de-locales-urnas'),
    path('usoajaxurnas/', login_required(EntradaAjaxUrnas.as_view()), name='uso-ajax-urnas'),
    path('listartodaslasnovedadesenlocales/', login_required(ListarTodasLasNovedadesEnLocales.as_view()),
         name='listado-de-todas-novedades-en-locales'),

    # crud de SED
    path('listasucursal/', login_required(ListaDeSed.as_view()), name='listado-de-sed'),
    path('sucursal/crear/', login_required(CrearSed.as_view()), name='crear-sed'),
    path('cucursal/actualizar/<int:pk>', login_required(ActualizarSed.as_view()), name='actualizar-sed'),
    path('sucursal/eliminar/<int:pk>', login_required(EliminarSed.as_view()), name='eliminar-sed'),

    # Para mapa

    path('listadolocalesenmapa/', login_required(ListadoLocalesEnMapa.as_view()),
         name='listado-de-locales-enmapa'),
    path('localesparamapa/', login_required(EnviarLocalesPorAjax.as_view()),
         name='enviar-locales-por-ajax'),

    # Mesas

    path('listarmesasparainiciar/', login_required(ListarMesasParaIniciarAjax.as_view()),
         name='listado-de-mesas-en-local-para-iniciar'),
    path('usoajaxmesas/', login_required(EntradaAjaxMesas.as_view()), name='uso-ajax-mesas'),
    path('cargarcausasnoinicioparafiltroajax/', login_required(CargarCausaNoInicioMesasAjax.as_view()),
         name='cargar-causas-noinicio-para-filtro'),

    # Crud de seguridad interna en los locales

    path('listarseginterna/', login_required(ListarSegInterna.as_view()),
         name='listado-de-seguridad-interna'),
    path('crearseginterna/', login_required(CrearSegInterna.as_view()),
         name='agregar-seguridad-interna'),
    path('actualizarseginterna/<int:pk>/', login_required(ActualizarSegInterna.as_view()),
         name='actualizar-seguridad-interna'),
    path('eliminarseginterna/<int:pk>/', login_required(EliminarSegInterna.as_view()),
         name='eliminar-seguridad-interna'),
    path('mostrarauxiliares/<int:pk>/',
         login_required(MostrarAuxiliares.as_view()), name='mostrar-auxiliares'),

    # Crud de seguridad externa en los locales

    path('listarsergexterna/', login_required(ListarSegExterna.as_view()),
         name='listado-de-seguridad-externa'),
    path('agregarsegexterna/', login_required(CrearSegExterna.as_view()),
         name='agregar-seg-externa'),
    path('actualizarsegexterna/<int:pk>/', login_required(ActualizarSegExterna.as_view()),
         name='actualizar-seg-externa'),
    path('eliminarsegexterna/<int:pk>/',
         login_required(EliminarSegExterna.as_view()), name='eliminar-seg-externa'),

    # Crud de novedades en el local

    path('listarnovedadesenlocal/', login_required(ListarNovedadesEnLocal.as_view()),
         name='listado-de-novedades-local'),
    path('agregarnovedad/', login_required(CrearNovedadesEnLocal.as_view()),
         name='agregar-novedad-local'),
    path('actualizarnovedad/<int:pk>/', login_required(ActualizarNovedadesEnLocal.as_view()),
         name='actualizar-novedad-local'),
    path('eliminarnovedad/<int:pk>/',
         login_required(EliminarNovedadesEnLocal.as_view()), name='eliminar-novedad-local'),

    # Crud de mesas en el local

    path('listarmesas/', login_required(ListarMesasEnLocalAjax.as_view()),
         name='listado-de-mesas-en-local'),
    path('agregarmesas/', login_required(CrearMesaEnLocal.as_view()),
         name='agregar-mesas-en-local'),
    path('actualizarmesas/<int:pk>/', login_required(ActualizarMesaEnLocal.as_view()),
         name='actualizar-mesas-en-local'),
    path('eliminarmesas/<int:pk>/', login_required(EliminarMesaEnLocal.as_view()),
         name='eliminar-mesas-en-local'),
    path('listarmesasparainiciar/', login_required(ListarMesasParaIniciarAjax.as_view()),
         name='listado-de-mesas-en-local-para-iniciar'),
    path('cargarcausasnoinicioparafiltroajax/', login_required(CargarCausaNoInicioMesasAjax.as_view()),
         name='cargar-causas-noinicio-para-filtro'),
    path('usoajaxmesas/', login_required(EntradaAjaxMesas.as_view()), name='uso-ajax-mesas'),

    # Personal

    path('personalvalidado/', login_required(ListadoPersonalValidado.as_view()), name='listado-de-personas'),
    path('personalnovalidado/', login_required(ListadoPersonalNoValidado.as_view()),
         name='listado-de-personal-no-validado'),
    path('persona/crear/', login_required(CrearPersona.as_view()), name='crear-persona'),
    path('persona/actualizar/<int:pk>',
         login_required(ActualizarPersona.as_view()), name='actualizar-persona'),
    path('persona/eliminar/<int:pk>',
         login_required(EliminarPersona.as_view()), name='eliminar-persona'),
    path('persona/detalles/<int:pk>',
         login_required(DetallePersona.as_view()), name='detalles-persona'),

    path('persona/detelle/conductor/<int:pk>',
         login_required(DetallePersonaComoConductor.as_view()), name='detalles-persona-como-conductor'),

    path('listarfuerza/', login_required(ListarFuerzaAjax.as_view()),
         name='listar-fuerza-para-personal'),

    # Funciones ajax para personas

    path('filtrosparapersonas/', login_required(FiltrosParaPersonasAjax.as_view()),
         name='filtros-para-personas'),
    path('listarfuerza/', login_required(ListarFuerzaAjax.as_view()),
         name='listar-fuerza-para-personal'),

    # Vehículos propios

    path('vehiculospropios/', login_required(ListadoVehiculosPropios.as_view()),
         name='listado-de-vehiculos-propios'),
    path('vehiculospropios/crear/', login_required(CrearVehiculoPropio.as_view()),
         name='crear-vehiculo-propio'),
    path('vehiculospropios/actualizar/<int:pk>',
         login_required(ActualizarVehiculoPropio.as_view()), name='actualizar-vehiculo-propio'),
    path('vehiculospropios/eliminar/<int:pk>',
         login_required(EliminarVehiculoPropio.as_view()), name='eliminar-vehiculo-propio'),
    path('vehiculospropios/detalles/<int:pk>',
         login_required(DetalleVehiculoPropio.as_view()), name='detalles-vehiculo-propio'),

    # Funciones ajax vehículos propios

    path('filtrosparavhpropios/', login_required(FiltrosParaVehPropiosAjax.as_view()),
         name='filtros-para-vehpropios'),

    # # Vehículos contratados
    #
    path('vehiculoscontratados/', login_required(ListadoVehiculosContratados.as_view()),
         name='listado-vehiculos-contratados'),
    path('crearvehcontratado/', login_required(CrearVehiculoContratado.as_view()), name='crear-veh-contratado'),
    path('actualizvehcontratado/<int:pk>/', login_required(ActualizarVehiculoContratado.as_view()),
         name='actualizar-veh-contratado'),
    path('eliminarvehcontratado/<int:pk>/', login_required(EliminarVehiculoContratado.as_view()),
         name='eliminar-veh-contratado'),
    path('vehiculoscontratados/detalles/<int:pk>',
         login_required(DetalleVehiculoContratado.as_view()), name='detalles-vehiculo-contratado'),

    # Novedades generales

    path('todaslasnovedades/', login_required(ListadoNovGeneralesGenerales.as_view()),
         name='listado-de-novedades-generales'),
    path('todaslasnovedades/crear/', login_required(CrearNovedadesGenerales.as_view()),
         name='crear-novedades-generales'),
    path('todaslasnovedades/actualizar/<int:pk>',
         login_required(ActualizarNovedadesGenerales.as_view()), name='actualizar-novedades-generales'),
    path('todaslasnovedades/eliminar/<int:pk>',
         login_required(EliminarNovedadesGenerales.as_view()), name='eliminar-novedades-generales'),
    path('todaslasnovedades/detalles/<int:pk>',
         login_required(DetalleNovedadesGenerales.as_view()), name='detalles-novedades-generales'),
    path('listadonovtiemporeal/', login_required(NovedadesTiempoReal.as_view()),
         name='listado-de-novedades-tiempo-real'),
    path('novtiemporeal/', login_required(ListarNoveTiempoRealPorAjax.as_view()),
         name='novedades-tiempo-real'),

    # crud de Movimientos
    path('movimientos/', login_required(ListadoMovimientos.as_view()),
         name='listado-de-movimientos'),
    path('movimientos/crear/', login_required(CrearMovimiento.as_view()), name='crear-movimiento'),
    path('movimientos/actualizar/<int:pk>',
         login_required(ActualizarMovimiento.as_view()), name='actualizar-movimiento'),
    path('movimientos/eliminar/<int:pk>',
         login_required(EliminarMovimiento.as_view()), name='eliminar-movimiento'),
    path('movimientos/detalles/<int:pk>',
         login_required(DetalleMovimiento.as_view()), name='detalles-movimiento'),

    # crud de LED
    path('todoslosled/', login_required(ListadoLed.as_view()),
         name='listado-de-led'),
    path('todoslosled/crear/', login_required(CrearLed.as_view()), name='crear-led'),
    path('todoslosled/actualizar/<int:pk>',
         login_required(ActualizarLed.as_view()), name='actualizar-led'),
    path('todoslosled/eliminar/<int:pk>',
         login_required(EliminarLed.as_view()), name='eliminar-led'),
    path('todoslosled/detalles/<int:pk>',
         login_required(DetalleLed.as_view()), name='detalles-led'),

    # Puntos de recolección de SACAS
    path('listarpuntosrecoleccionsacas/', login_required(ListarPuntosRecoleccionSACAS.as_view()),
         name='listado-puntos-recoleccion-sacas'),
    path('puntosrecoleccionsacas/crear/', login_required(CrearPuntosRecoleccionSACAS.as_view()),
         name='crear-punto-recoleccion-sacas'),
    path('puntosrecoleccionsacas/actualizar/<int:pk>',
         login_required(ActualizarPuntoRecoleccionSACAS.as_view()), name='actualizar-punto-recoleccion-sacas'),
    path('puntosrecoleccionsacas/eliminar/<int:pk>',
         login_required(EliminarPuntoRecoleccionSACAS.as_view()), name='eliminar-punto-recoleccion-sacas'),
    path('puntosrecoleccionpdf/', login_required(PuntosRecoleccionPDF.as_view()), name='lista-puntos-recoleccion-pdf'),
    path('cambiarestadoprs/', login_required(CambiarEstadoPuntorRecoleccionSACAS.as_view()),
         name='cambiar-estado-prs'),

    # Circuitos de recolección de SACAS
    path('listarcircuitosrecoleccionsacas/', login_required(ListarCircuitosRecoleccionSACAS.as_view()),
         name='listado-circuitos-recoleccion-sacas'),
    path('circuitosrecoleccionsacas/crear/', login_required(CrearCircuitoRecoleccionSACAS.as_view()),
         name='crear-circuitos-recoleccion-sacas'),
    path('circuitosrecoleccionsacas/actualizar/<int:pk>',
         login_required(ActualizarCircuitoRecoleccionSACAS.as_view()), name='actualizar-circuito-recoleccion-sacas'),
    path('circuitosrecoleccionsacas/eliminar/<int:pk>',
         login_required(EliminarCircuitoRecoleccionSACAS.as_view()), name='eliminar-circuito-recoleccion-sacas'),
    path('circuitosrecoleccionpdf/', login_required(CircuitosRecoleccionPDF.as_view()), name='lista-circuitos-recoleccion-pdf'),
    path('cambiarestadocrs/', login_required(CambiarEstadoCircuitoRecoleccionSACAS.as_view()),
         name='cambiar-estado-crs'),
    path('mostrarhijosctrs/', login_required(MostrarHijosCircutoRecoleccionSACAS.as_view()),
         name='mostrar-hijos-ctrs'),


    # crud de Seg LED Fuerzas Armadas
    path('listarsegledffaa/', login_required(ListarSegLedFFAAAjax.as_view()),
         name='listado-seg-led-ffaa'),
    path('agregarsegledffaa/', login_required(CrearSegLedFFAA.as_view()),
         name='agregar-seg-led-ffaa'),
    path('actualizarsegledffaa/<int:pk>/', login_required(ActualizarSegLedFFAA.as_view()),
         name='actualizar-seg-led-ffaa'),
    path('eliminarsegledffaa/<int:pk>/', login_required(EliminarSegLedFFAA.as_view()),
         name='eliminar-seg-led-ffaa'),

    # crud de Seg LED Fuerzas de Seguridad
    path('listarsegledffseg/', login_required(ListarSegLedFFSegAjax.as_view()),
         name='listado-seg-led-ffseg'),
    path('agregarsegledffseg/', login_required(CrearSegLedFFSeg.as_view()),
         name='agregar-seg-led-ffseg'),
    path('actualizarsegledffseg/<int:pk>/', login_required(ActualizarSegLedFFSeg.as_view()),
         name='actualizar-seg-led-ffseg'),
    path('eliminarsegledffseg/<int:pk>/', login_required(EliminarSegLedFFSeg.as_view()),
         name='eliminar-seg-led-ffseg'),

    # crud de lugares de interés
    path('listarlugares/', login_required(ListaLugarInteres.as_view()),
         name='listado-lugar-interes'),
    path('agregarlugar/', login_required(CrearLugarInteres.as_view()),
         name='crear-lugar-interes'),
    path('actualizarlugar/<int:pk>/', login_required(ActualizarLugarInteres.as_view()),
         name='actualizar-lugar-interes'),
    path('eliminarlugar/<int:pk>/', login_required(EliminarLugarInteres.as_view()),
         name='eliminar-lugar-interes'),
    path('detallelugar/detalles/<int:pk>',
         login_required(DetalleLugarInteres.as_view()), name='detalles-lugar-interes'),

    # crud de la Guia de autoridades en el CdoGrlElect
    path('listarguiacge/', login_required(ListarGuiaCge.as_view()), name='listado-guia-cge'),
    path('agregarpersonaguiacge/', login_required(CrearGuiaCge.as_view()), name='agregar-persona-guia-cge'),
    path('actualizarguiacge/<int:pk>', login_required(ActualizarGuiaCge.as_view()), name='actualizar-persona-guia-cge'),
    path('eliminarpersonaguiacge/<int:pk>', login_required(EliminarGuiaCge.as_view()), name='eliminar-persona-guia-cge'),

    # crud de la Guia de autoridades en el Distrito
    path('listarguiadistrito/', login_required(ListarGuiaDistrito.as_view()), name='listado-guia-distrito'),
    path('agregarpersonaguiadistrito/', login_required(CrearGuiaDistrito.as_view()), name='agregar-persona-guia-distrito'),
    path('actualizarguiadistrito/<int:pk>', login_required(ActualizarGuiaDistrito.as_view()), name='actualizar-persona-guia-distrito'),
    path('eliminarpersonaguiadistrito/<int:pk>', login_required(EliminarGuiaDistrito.as_view()), name='eliminar-persona-guia-distrito'),

    # Listado y reportes
    path('reportes/', Reportes.as_view(), name='reportes'),

    # En excel
    path('exportarlocales/', login_required(reporteLocales), name='reporte-locales'),
    path('exportarnovlocales/', login_required(exportarNovedadEnLocal), name='exportar-nov-en-locales-excel'),
    path('exportarvehpropios/', login_required(exportarVehPropios), name='exportar-veh-propios-excel'),
    path('exportarvehpropiosempleo/', login_required(exportarVehPropiosEmpleo), name='exportar-veh-propios-empleo-excel'),
    path('exportarmovimientos/', login_required(exportarMovimientos), name='exportar-movimientos-excel'),
    #Lo que sigue por ahora sale normal no formato asincrono hasta tanto lo terminemos bien
    path('exportarresumenpersonal/', login_required(exportarResumenPersonalJerarquiaTipo.as_view()), name='exportar-resumen-pers-jerarquia-tipo-excel'),
    path('exportarresumengeneral/', login_required(exportarResumenGeneral.as_view()), name='exportar-resumen-general'),
    path('exportarlugar/', login_required(exportarLugar), name='exportar-lugar-interes'),
    path('exportarguia/', login_required(exportarGuia), name='exportar-guia'),
    path('exportarnovgenerales/', login_required(exportarNovedadesGenerales), name='exportar-nov-grl-excel'),
    path('exportarpersonal/', login_required(exportarPersonas), name='exportar-personal-excel'),
    path('exportarvehcontratados/', login_required(exportarVehContratados), name='exportar-veh-contratados-excel'),
    path('exportarvehcontratadosempleo/', login_required(exportarVehContratadosEmpleo),
         name='exportar-veh-contratados-empleo-excel'),
    path('exportarled/', login_required(exportarLED), name='exportar-led-excel'),
    path('exportarsed/', login_required(exportarSED), name='exportar-sed-excel'),

    # En Pdf
    path('novlocalpdf/<int:pk>/', login_required(NovedadesEnLocalesPdf.as_view()), name='generar-novedades-en-local-pdf'),
    path('todasnovlocalpdf/', login_required(TodasNovedadesEnLocalesPdf.as_view()), name='generar-todas-novedades-en-local-pdf'),
    path('movpdf/', login_required(MovimientosPdf.as_view()), name='listar-movimientos-pdf'),
    path('todosmovpdf/', login_required(TodosMovimientosPdf.as_view()), name='listar-todos-movimientos-pdf'),
    path('novgrlpdf/', login_required(NovedadesGeneralesPdf.as_view()), name='listar-novedades-pdf'),
    path('todasnovgrlpdf/', login_required(TodasNovedadesGeneralesPdf.as_view()), name='listar-todas-novedades-pdf'),
    path('exportarresumenpersonalpdf/', login_required(exportarResumenPersonalJerarquiaTipoPdf.as_view()), name='exportar-resumen-pers-jerarquia-tipo-pdf'),

    ######### Funciones comunes a la AppElecciones #############

    # Obtener personas para los autocomplete - única función
    path('obtenerpersonas/', login_required(ObtenerPersonasAjax.as_view()),
         name='obtener-personas'),
    # Obtener vehículos propios para los autocomplete - única función
    path('obtenervehpropios/', login_required(ObtenerVehiculosPropiosAjax.as_view()),
         name='obtener-veh-propios'),
    # Obtener vehículos contratados para los autocomplete - única función
    path('obtenervehcontratados/', login_required(ObtenerVehiculosContratadosAjax.as_view()),
         name='obtener-veh-contratados'),
    # Obtener Distritos, Subdistritos, Secciones, Circuitos y Locales para los autocomplete - única función
    path('iltroparaprganizaciones/', login_required(FiltroParaOrganizaciones.as_view()),
         name='filtro-para-organizaciones'),
    # Obtener Tipo de novedades para el filtro de listado de novedades en local y generales
    path('cargarnovedadesparafiltroajax/', login_required(CargarNovParaFiltrosAjax.as_view()),
         name='cargar-nov-para-filtros'),
    # Obtener personas para el buscador general de personas
    path('obtenerpersonasencge/', login_required(ObtenerCualquierPersonasAjax.as_view()),
         name='buscar-en-todo-el-cge'),
    # Validador genérico: valida personal, locales y pasa a estado no validado a una persona
    path('validar/', login_required(ValidadorGenericoAjax.as_view()),
         name='validar_informacion'),

    ######### Tableros de control #############

   path('tablerovehiculos/', login_required(TableroVehiculos.as_view()),
         name='tablero_vehiculos'),
   path('tablerolocales/', login_required(TableroLocales.as_view()),
        name='tablero_locales'),
   path('tablerosms/', login_required(TableroNovedades.as_view()),
       name='tablero_sms'),
   path('tablerorepliegue/', login_required(TableroRepliegue.as_view()),
        name='tablero_repliegue'),  
   path('tablerodespliegue/', login_required(TableroDespliegue.as_view()),
        name='tablero_despliegue'),    
   path('tablerorecepcion_material/', login_required(TableroRecepMatElec.as_view()),
        name='tablero_res_mat_elec'),
   path('tablerodespliegue_pc/', login_required(TableroDesplieguePC.as_view()),
        name='tablero_despliegue_pc') ,
   path('tablerorepliegue_pc/', login_required(TableroReplieguePC.as_view()),
        name='tablero_repliegue_pc'),    
   path('distribucionpersonal/', login_required(TableroPersonal.as_view()),
        name='distribucion_personal'),   
   path('tablero_resumen_general/', login_required(TableroResumenGeneral.as_view()),
        name='tablero_resumn_general'),   
   path('tablero_novedades/', login_required(TableroNovedades.as_view()),
        name='tablero_novedades'),    
   path('tablero_led/', login_required(TableroLED.as_view()),
        name='tablero_led'),  
   path('tablero_telegramas/', login_required(TableroTelegramas.as_view()),
        name='tablero_tele'),           

]
