from django.core.management.base import BaseCommand

from AppElecciones.models import *


class Command(BaseCommand):
    """
    Comando para resetear los modelos para una capacitación/ejercicio.
    Los locales y personas quedan validadas, el resto se limpia al completo.
    Se borra en orden para que no de error de integridad.

    Usage::

        $ python manage.py practicas
        Mensaje

    """
    help = "Prepara el sistema para una capacitación/ejercitación"

    def handle(self, **options):

        # Lugar de interés

        print("Borrando lugar de interes...")
        filters = Q(content_type=ContentType.objects.get_for_model(LugarInteres))
        UserObjectPermission.objects.filter(filters).delete()
        gli = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gli) + ' permisos borrados del modelo LugarInteres')
        reg_lug_interes = LugarInteres.objects.all().delete()
        print(str(reg_lug_interes) + " objetos del modelo LugarInteres borrados")
        print("...")

        # Guia de autoridades

        print('Borrando guia de autoridades...')
        ## Eliminación de permisos solo la guia, al resto no se le asignan al crearse
        filters = Q(content_type=ContentType.objects.get_for_model(GuiaAutoridades))
        UserObjectPermission.objects.filter(filters).delete()
        gpg = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gpg) + 'permisos borrados del modelo GuiaAutoridades')
        reg_puesto_guia_borrados = PuestoGuiaAutoridades.objects.all().delete()
        print(str(reg_puesto_guia_borrados) + " objectos del modelo PuestoGuiaAutoridades borrados")
        reg_guiaCge = CgeGuia.objects.all().delete()
        print(str(reg_guiaCge) + " objetos del modelo CgeGuia borrados")
        reg_guiaDistrito = DistritoGuia.objects.all().delete()
        print(str(reg_guiaDistrito) + " objectos del modelo DistritoGuia borrados")
        reg_guia = GuiaAutoridades.objects.all().delete()
        print(str(reg_guia) + " objetos del modelo GuiaAutoridades borrados")
        print("...")

        #Comando General Electoral

        print("Borrando distribución de personal del Cdo Grl Elect...")
        filters = Q(content_type=ContentType.objects.get_for_model(DistribucionPersonalCdoGrlElect))
        UserObjectPermission.objects.filter(filters).delete()
        gdpcge = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gdpcge) + ' permisos borrados del modelo DistribucionPersonalCdoGrlElect')
        reg_dis_pers_cge = DistribucionPersonalCdoGrlElect.objects.all().delete()
        print(str(reg_dis_pers_cge) + " objetos del modelo DistribucionPersonalCdoGrlElect borrados")
        print("...")

        print("Borrando Reserva de personal en el Cdo Grl Elect...")
        filters = Q(content_type=ContentType.objects.get_for_model(ReservaCdoGrlElect))
        UserObjectPermission.objects.filter(filters).delete()
        grecge = GroupObjectPermission.objects.filter(filters).delete()
        print(str(grecge) + ' permisos borrados del modelo ReservaCdoGrlElect')
        reg_reserva_cge = ReservaCdoGrlElect.objects.all().delete()
        print(str(reg_reserva_cge) + " objetos del modelo ReservaCdoGrlElect borrados")
        print("...")

        print("Borrando Asinación de vehículos provistos a tareas en el Cdo Grl Elect...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosPropiosCdoGrlElect))
        UserObjectPermission.objects.filter(filters).delete()
        gvhpcge = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvhpcge) + ' permisos borrados del modelo VehiculosPropiosCdoGrlElect')
        reg_veh_prov = VehiculosPropiosCdoGrlElect.objects.all().delete()
        print(str(reg_veh_prov) + " objetos del modelo VehiculosPropiosCdoGrlElect borrados")
        print("...")

        print("Borrando Asignación de vehículos contratados a tareas en el Cdo Grl Elect...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosContratadosCdoGrlElect))
        UserObjectPermission.objects.filter(filters).delete()
        gvhccge = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvhccge) + ' permisos borrados del modelo VehiculosContratadosCdoGrlElect')
        reg_veh_cont = VehiculosContratadosCdoGrlElect.objects.all().delete()
        print(str(reg_veh_cont) + " objetos del modelo VehiculosContratadosCdoGrlElect borrados")
        print("...")

        #Distritos

        print("Borrando Distribución de personal en el distrito...")
        filters = Q(content_type=ContentType.objects.get_for_model(DistribucionPersonalDistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gdpd = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gdpd) + ' permisos borrados del modelo DistribucionPersonalDistrito')
        reg_pers_distrito = DistribucionPersonalDistrito.objects.all().delete()
        print(str(reg_pers_distrito) + " objetos del modelo DistribucionPersonalDistrito borrados")
        print("...")

        print("Borrando Reserva de personal en el distrito...")

        filters = Q(content_type=ContentType.objects.get_for_model(ReservaDistrito))
        UserObjectPermission.objects.filter(filters).delete()
        grde = GroupObjectPermission.objects.filter(filters).delete()
        print(str(grde) + ' permisos borrados del modelo ReservaDistrito')


        reg_res_distrito = ReservaDistrito.objects.all().delete()
        print(str(reg_res_distrito) + " objetos del modelo ReservaDistrito borrados")
        print("...")

        print("Borrando Asigación de vehículos provistos a tareas en el distrito...")

        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosPropiosDistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gvhpdel = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvhpdel) + ' permisos borrados del modelo VehiculosPropiosDistrito')

        reg_veh_prov_dis = VehiculosPropiosDistrito.objects.all().delete()
        print(str(reg_veh_prov_dis) + " objetos del modelo VehiculosPropiosDistrito borrados")
        print("...")

        print("Borrando Asignación de vehículos contratados a tareas en el distrito...")

        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosContratadosDistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gvhcde = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvhcde) + ' permisos borrados del modelo VehiculosContratadosDistrito')

        reg_veh_cont_dis = VehiculosContratadosDistrito.objects.all().delete()
        print(str(reg_veh_cont_dis) + " objetos del modelo VehiculosContratadosDistrito borrados")
        print("...")

        # Subdistritos

        print("Borrando Distribución de personal en el subdistrito...")
        filters = Q(content_type=ContentType.objects.get_for_model(DistribucionPersonalSubdistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gdps = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gdps) + ' permisos borrados del modelo DistribucionPersonalSubdistrito')
        reg_pers_subdistrito = DistribucionPersonalSubdistrito.objects.all().delete()
        print(str(reg_pers_subdistrito) + " objetos del modelo DistribucionPersonalSubdistrito borrados")
        print("...")
        print("Borrando Reserva de personal en el subdistrito...")
        filters = Q(content_type=ContentType.objects.get_for_model(ReservaSubdistrito))
        UserObjectPermission.objects.filter(filters).delete()
        grs = GroupObjectPermission.objects.filter(filters).delete()
        print(str(grs) + ' permisos borrados del modelo ReservaSubdistrito')
        reg_res_subdistrito = ReservaSubdistrito.objects.all().delete()
        print(str(reg_res_subdistrito) + " objetos del modelo ReservaSubdistrito borrados")
        print("...")
        print("Borrando Asigación de vehículos provistos a tareas en el subdistrito...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosPropiosSubdistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gvprs = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvprs) + ' permisos borrados del modelo VehiculosPropiosSubdistrito')
        reg_veh_prov_subdis = VehiculosPropiosSubdistrito.objects.all().delete()
        print(str(reg_veh_prov_subdis) + " objetos del modelo VehiculosPropiosSubdistrito borrados")
        print("...")
        print("Borrando Asignación de vehículos contratados a tareas en el subdistrito...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosContratadosSubdistrito))
        UserObjectPermission.objects.filter(filters).delete()
        gvcs = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvcs) + ' permisos borrados del modelo VehiculosContratadosSubdistrito')
        reg_veh_cont_subdis = VehiculosContratadosSubdistrito.objects.all().delete()
        print(str(reg_veh_cont_subdis) + " objetos del modelo VehiculosContratadosSubdistrito borrados")
        print("...")

        # Secciones

        print("Borrando Distribución de personal en la sección...")
        filters = Q(content_type=ContentType.objects.get_for_model(DistribucionPersonalSeccion))
        UserObjectPermission.objects.filter(filters).delete()
        gdpsec = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gdpsec) + ' permisos borrados del modelo DistribucionPersonalSeccion')
        reg_pers_seccion = DistribucionPersonalSeccion.objects.all().delete()
        print(str(reg_pers_seccion) + " objetos del modelo DistribucionPersonalSeccion borrados")
        print("...")
        print("Borrando Asigación de vehículos provistos a tareas en la sección...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosPropiosSeccion))
        UserObjectPermission.objects.filter(filters).delete()
        gvpros = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvpros) + ' permisos borrados del modelo VehiculosPropiosSeccion')
        reg_veh_prov_seccion = VehiculosPropiosSeccion.objects.all().delete()
        print(str(reg_veh_prov_seccion) + " objetos del modelo VehiculosPropiosSeccion borrados")
        print("...")
        print("Borrando Asignación de vehículos contratados a tareas en la sección...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosContratadosSeccion))
        UserObjectPermission.objects.filter(filters).delete()
        gvcsec = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvcsec) + ' permisos borrados del modelo VehiculosContratadosSeccion')
        reg_veh_cont_seccion = VehiculosContratadosSeccion.objects.all().delete()
        print(str(reg_veh_cont_seccion) + " objetos del modelo VehiculosContratadosSeccion borrados")
        print("...")

        # Circuitos

        print("Reseteando circuitos a: entrego_urna_en_led=False, situacion='Actividades no iniciadas'...")
        Circuito.objects.all().update(entrego_urna_en_led=False, situacion='Actividades no iniciadas')
        print("...")

        # Locales

        print("Borrando auxiliares de locales...")
        filters = Q(content_type=ContentType.objects.get_for_model(AuxiliarLocal))
        UserObjectPermission.objects.filter(filters).delete()
        gauxloc = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gauxloc) + ' permisos borrados del modelo AuxiliarLocal')
        reg_aux_local = AuxiliarLocal.objects.all().delete()
        print(str(reg_aux_local) + " objetos del modelo AuxiliarLocal borrados")
        print("...")
        print("Borrando jefes de locales...")
        filters = Q(content_type=ContentType.objects.get_for_model(SegInternaLocal))
        UserObjectPermission.objects.filter(filters).delete()
        gjloc = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gjloc) + ' permisos borrados del modelo SegInternaLocal')
        reg_jef_local = SegInternaLocal.objects.all().delete()
        print(str(reg_jef_local) + " objetos del modelo SegInternaLocal borrados")
        print("...")
        print("Borrando seguridad externa en locales...")
        filters = Q(content_type=ContentType.objects.get_for_model(SegExternaLocal))
        UserObjectPermission.objects.filter(filters).delete()
        gsegextloc = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gsegextloc) + ' permisos borrados del modelo SegExternaLocal')
        reg_seg_ext_local = SegExternaLocal.objects.all().delete()
        print(str(reg_seg_ext_local) + " objetos del modelo SegExternaLocal borrados")
        print("...")
        print("Borrando novedades en locales...")
        filters = Q(content_type=ContentType.objects.get_for_model(NovedadesEnLocal))
        UserObjectPermission.objects.filter(filters).delete()
        gnovloc = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gnovloc) + ' permisos borrados del modelo NovedadesEnLocal')
        reg_nov_local = NovedadesEnLocal.objects.all().delete()
        print(str(reg_nov_local) + " objetos del modelo NovedadesEnLocal borrados")
        print("...")
        print("Borrando mesas de locales...")
        filters = Q(content_type=ContentType.objects.get_for_model(MesasEnLocal))
        UserObjectPermission.objects.filter(filters).delete()
        gmesaloc = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gmesaloc) + ' permisos borrados del modelo MesasEnLocal')
        reg_mesas = MesasEnLocal.objects.all().delete()
        print(str(reg_mesas) + " objetos del modelo MesasEnLocal borrados")
        print("...")
        print("Borrando transmisión de telegramas...")
        reg_telegramas = TransmisionTelegramas.objects.all().delete()
        print(str(reg_telegramas) + " objetos del modelo TransmisionTelegramas borrados")
        print("...")
        print("Reseteando locales a: recepciono_mat_elec=False, entrego_urna=False, transmite_telegrama=False, estado=1...")
        locales_actualizados = Local.objects.all().update(validado=0, recepciono_mat_elec=False, entrego_urna=False, transmite_telegrama=False, estado=1)
        print(str(locales_actualizados) + " objetos del modelo Local actualizados")
        print("...")
        print("Borrando control de votos en el local...")
        reg_votos = ControlDeVotos.objects.all().delete()
        print(str(reg_votos) + " objetos del modelo ControlDeVotos borrados")
        print("...")

        # Sucursal electoral digital (SED)

        print("Borrando registros de SED...")
        filters = Q(content_type=ContentType.objects.get_for_model(Sed))
        UserObjectPermission.objects.filter(filters).delete()
        gsed = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gsed) + ' permisos borrados del modelo Sed')
        reg_sed = Sed.objects.all().delete()
        print(str(reg_sed) + " objetos del modelo Sed borrados")
        print("...")

        # Personal

        print("Reseteando estado del personal a: num_cargos=0, num_conductor=0, tiene_cargo=False, es_conductor=False, validado_por='Sin Confirmar', validado=0...")
        pers_actualizadas = Persona.objects.all().update(num_cargos=0, num_conductor=0, tiene_cargo=False, es_conductor=False,
                                     validado_por='Sin Confirmar', validado=0)
        filters = Q(content_type=ContentType.objects.get_for_model(Persona))
        UserObjectPermission.objects.filter(filters).delete()
        GroupObjectPermission.objects.filter(filters).delete()
        grupos_para_asignar = Group.objects.filter(
            Q(gurpo_del_subdistrito__isnull=False) | Q(gurpo_del_distrito__isnull=False) | Q(name='personal-CGE'))
        [assign_perm('change_' + Persona.__name__.lower(), g, [p for p in Persona.objects.all()]) for g in grupos_para_asignar]

        print(str(pers_actualizadas) + " objetos del modelo Persona actualizados")
        print("...")

        # Vehículos provistos

        print("Borrando creación de vehículos provistos...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosPropios))
        UserObjectPermission.objects.filter(filters).delete()
        gvprop = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvprop) + ' permisos borrados del modelo VehiculosPropios')

        reg_veh_provistos = VehiculosPropios.objects.all().delete()
        print(str(reg_veh_provistos) + " objetos del modelo VehiculosPropios borrados")
        print("...")

        # Vehículos contratados

        print("Borrando creación de vehículos contratados...")
        filters = Q(content_type=ContentType.objects.get_for_model(VehiculosContratados))
        UserObjectPermission.objects.filter(filters).delete()
        gvcon = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gvcon) + ' permisos borrados del modelo VehiculosContratados')


        reg_veh_contratados = VehiculosContratados.objects.all().delete()
        print(str(reg_veh_contratados) + " objetos del modelo VehiculosContratados borrados")
        print("...")

        # Novedades generales

        print("Borrando novedades generales...")
        filters = Q(content_type=ContentType.objects.get_for_model(NovedadesGenerales))
        UserObjectPermission.objects.filter(filters).delete()
        gnovgrl= GroupObjectPermission.objects.filter(filters).delete()
        print(str(gnovgrl) + ' permisos borrados del modelo NovedadesGenerales')


        reg_nov_grles = NovedadesGenerales.objects.all().delete()
        print(str(reg_nov_grles) + " objetos del modelo NovedadesGenerales borrados")
        print("...")

        # Movimientos

        print("Borrando movimientos...")
        filters = Q(content_type=ContentType.objects.get_for_model(Movimientos))
        UserObjectPermission.objects.filter(filters).delete()
        gmov = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gmov) + ' permisos borrados del modelo Movimientos')

        reg_mov = Movimientos.objects.all().delete()
        print(str(reg_mov) + " objetos del modelo Movimientos borrados")
        print("...")

        # Led

        print("Borrando seguridad fuerzas armadas en el LED...")
        filters = Q(content_type=ContentType.objects.get_for_model(SegEnLedFuerzaArmada))
        UserObjectPermission.objects.filter(filters).delete()
        gsegffaaled = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gsegffaaled) + ' permisos borrados del modelo SegEnLedFuerzaArmada')


        reg_seg_ffaa_led = SegEnLedFuerzaArmada.objects.all().delete()
        print(str(reg_seg_ffaa_led) + " objetos del modelo SegEnLedFuerzaArmada borrados")
        print("...")

        print("Borrando seguridad fuerzas de seguridad en el LED...")

        filters = Q(content_type=ContentType.objects.get_for_model(SegEnLedFuerzaSeguridad))
        UserObjectPermission.objects.filter(filters).delete()
        gsegffsegled = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gsegffsegled) + ' permisos borrados del modelo SegEnLedFuerzaSeguridad')

        reg_seg_ffseg_led = SegEnLedFuerzaSeguridad.objects.all().delete()
        print(str(reg_seg_ffseg_led) + " objetos del modelo SegEnLedFuerzaSeguridad borrados")
        print("...")

        print("Borrando LED...")

        filters = Q(content_type=ContentType.objects.get_for_model(Led))
        UserObjectPermission.objects.filter(filters).delete()
        gled = GroupObjectPermission.objects.filter(filters).delete()
        print(str(gled) + ' permisos borrados del modelo Led')

        reg_led = Led.objects.all().delete()
        print(str(reg_led) + " objetos del modelo Led borrados")
        print("...")
        print('Fin del script.')





