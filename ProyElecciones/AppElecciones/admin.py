from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import GroupObjectPermission, assign_perm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from leaflet.admin import LeafletGeoAdmin
from unidecode import unidecode

from AppElecciones.models import (
    CdoGrlElect,
    Distrito,
    Subdistrito,
    Seccion,
    Circuito,
    EstadosLocal,
    Local,
    HoraControlVoto,
    ControlDeVotos,
    TransmisionTelegramas,
    EstadosMesas,
    MesasEnLocal,
    TipoNovedadLocal,
    NovedadesEnLocal,
    Reparticion,
    Fuerza,
    FuerzaSeguridad,
    SegExternaLocal,
    Jerarquia,
    Grado,
    Persona,
    SegInternaLocal,
    Unidad,
    Medios,
    TipoVehiculoProvisto,
    Tareas,
    TipoCombustible,
    VehiculosPropios,
    TipoVehiculoCivil,
    NovedadesGenerales,
    TipoMovimiento,
    Movimientos,
    TipoLed,
    Led,
    SegEnLedFuerzaArmada,
    SegEnLedFuerzaSeguridad,
    Cargo,
    DistribucionPersonalCdoGrlElect,
    ReservaCdoGrlElect,
    VehiculosPropiosCdoGrlElect,
    VehiculosContratadosCdoGrlElect,
    DistribucionPersonalDistrito,
    ReservaDistrito,
    VehiculosPropiosDistrito,
    VehiculosContratadosDistrito,
    DistribucionPersonalSubdistrito,
    ReservaSubdistrito,
    VehiculosPropiosSubdistrito,
    VehiculosContratadosSubdistrito,
    DistribucionPersonalSeccion,
    VehiculosPropiosSeccion,
    VehiculosContratadosSeccion,
    VehiculosContratados,
    AuxiliarLocal,
    SACASPuntosRecoleccion,
    SACASHistorialPuntosRecoleccion,
    SACASHistorialCircuitosRecoleccion,
    SACACircuitoRecoleccion,
    Circuito_Punto,
    Sed,
    TipoLugarInteres,
    LugarInteres,
    GuiaAutoridades,
    PuestoGuiaAutoridades,
    CgeGuia,
    DistritoGuia,
    SubdistritoPersona

)
#Permisos solo para ver el grupo cge
listado_modelos_cge = [Distrito,Circuito,Seccion,Subdistrito,NovedadesGenerales, Led, Movimientos, VehiculosContratados,
                       VehiculosPropios, Persona, MesasEnLocal, Sed,Local, SACASPuntosRecoleccion, SACACircuitoRecoleccion, LugarInteres]

listado_modelos_distritos = [NovedadesGenerales, Led, SegEnLedFuerzaArmada, SegEnLedFuerzaSeguridad,
                             Movimientos, VehiculosContratados, VehiculosPropios, Persona, Local,
                             Circuito, MesasEnLocal, Sed, LugarInteres ]

listado_modelos_subdistritos = [Subdistrito,Seccion,Circuito,NovedadesGenerales, VehiculosContratados, VehiculosPropios, Persona, Local,
                                Circuito, MesasEnLocal]

################################################################################################################
# Registrar en el Admin el modelo CdoGrlElect que es un singleton, solo se permite la creación de un solo objeto

def crear_grupos_cge_y_permisos(modeladmin, request, queryset):
    cge = CdoGrlElect.objects.get(id=1)
    GroupObjectPermission.objects.filter(object_pk=cge.pk, content_type=ContentType.objects.get_for_model(CdoGrlElect)).delete()

    assign_perm('view_cdogrlelect', cge.grupo, cge)
    cge.grupo.permissions.add(
        Permission.objects.get(content_type__model=NovedadesGenerales.__name__.lower(),
                               codename='ver_novedades_generales_novedadesgenerales'))
    cge.grupo.permissions.add(Permission.objects.get(content_type__model=Subdistrito.__name__.lower(),
                                codename='ver_subdistrito_subdistrito'))
    try:
        for g in queryset:
            grupo1, creado = Group.objects.get_or_create(name='personal-CGE')

            [grupo1.permissions.add(Permission.objects.get(content_type__model=Persona.__name__.lower(),
                                                           name__contains=x)) for x in ['view', 'add']]
            [grupo1.permissions.add(
                Permission.objects.get(content_type__model=DistribucionPersonalCdoGrlElect.__name__.lower(),
                                       name__contains=x)) for x in ['view', 'add']]
            [grupo1.permissions.add(
                Permission.objects.get(content_type__model=ReservaCdoGrlElect.__name__.lower(),
                                       name__contains=x)) for x in ['view', 'add']]
            grupo1.permissions.add(
                Permission.objects.get(content_type__model=Persona.__name__.lower(),
                                       codename='ver_personas_no_validados_persona'))

            [assign_perm(x + CdoGrlElect.__name__.lower(), grupo1, cge) for x in ['view_', "admin_pers_cge_"]]
            grupo1.parent = g.grupo
            grupo1.save()

            grupo2, creado = Group.objects.get_or_create(name='material-CGE')
            [grupo2.permissions.add(Permission.objects.get(content_type__model=VehiculosPropios.__name__.lower(),
                                                           name__contains=x)) for x in ['view', 'add']]
            [grupo2.permissions.add(Permission.objects.get(content_type__model=VehiculosContratados.__name__.lower(),
                                                           name__contains=x)) for x in ['view', 'add']]
            [grupo2.permissions.add(Permission.objects.get(content_type__model=Persona.__name__.lower(),
                                                           name__contains=x)) for x in ['view']]

            [grupo2.permissions.add(
                Permission.objects.get(content_type__model=VehiculosPropiosCdoGrlElect.__name__.lower(),
                                       name__contains=x)) for x in ['view', 'add']]
            [grupo2.permissions.add(
                Permission.objects.get(content_type__model=VehiculosContratadosCdoGrlElect.__name__.lower(),
                                       name__contains=x)) for x in ['view', 'add']]

            [assign_perm(x + CdoGrlElect.__name__.lower(), grupo2, cge) for x in ['view_',"admin_veh_cge_"]]

            grupo2.parent = g.grupo
            grupo2.save()

            [g.grupo.permissions.add(Permission.objects.get(content_type__model=x.__name__.lower(),
                                                            name__contains='view')) for x in listado_modelos_cge]

            # print(Permission.objects.get(content_type__model=NovedadesGenerales.__name__.lower(),
            #                            codename='ver_novedades_generales_novedadesgenerales'))

        messages.success(request, "Se crearon los grupos y se asignaron los permisos correctamente")
    except:
        messages.error(request, "No se pudo hacer nada")


crear_grupos_cge_y_permisos.short_description = 'Crear grupos Personal-cge y Material-cge y asignar permisos'


class CGERecurso(resources.ModelResource):
    class Meta:
        model = CdoGrlElect


class CGEAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = CGERecurso
    list_display = ('nombre', 'grupo')
    search_fields = ['nombre', 'grup']
    actions = [crear_grupos_cge_y_permisos]


admin.site.register(CdoGrlElect, CGEAdmin)


###########Registrar en el Admin el modelo Distrito ######################
# ********Se registre de esta forma para user Importar/Exportar en Excel***

listado_modelos_distritos_solo_lectura = [SACASPuntosRecoleccion, SACACircuitoRecoleccion]
def crear_grupos_dis(modeladmin, request, queryset):

    try:
        grupo_CGE = CdoGrlElect.objects.all()[0]
        for x in queryset:
            sin_espacios = str(x.distrito).replace(" ", "").lower()
            nombre_grupo_temp = unidecode(sin_espacios)
            nombre_grupo = nombre_grupo_temp
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            grupo.parent = grupo_CGE.grupo
            grupo.save()
            permisos = ['view', 'add']
            [grupo.permissions.add(Permission.objects.get(content_type__model=i.__name__.lower(), name__contains='view')) for i in [Distrito,Seccion,Subdistrito]]

            for m in listado_modelos_distritos:
                for p in permisos:
                    grupo.permissions.add(
                        Permission.objects.get(content_type__model=m.__name__.lower(), name__contains=p))
            grupo.permissions.add(
                Permission.objects.get(content_type__model=Local.__name__.lower(),
                                       codename='ver_locals_no_validados_local'))
            grupo.permissions.add(
                Permission.objects.get(content_type__model=Persona.__name__.lower(),
                                       codename='ver_personas_no_validados_persona'))

            grupo.permissions.add(
                Permission.objects.get(content_type__model=Local.__name__.lower(),
                                       codename='ver_locals_a_validar_en_mapa_local'))

            grupo.permissions.add(
                Permission.objects.get(content_type__model=NovedadesGenerales.__name__.lower(),
                                       codename='ver_novedades_generales_novedadesgenerales'))



            [grupo.permissions.add(Permission.objects.get(content_type__model=x.__name__.lower(),
                                                            name__contains='view')) for x in listado_modelos_distritos_solo_lectura]
            if Subdistrito.objects.filter(distrito=x).exists():
                grupo.permissions.remove(Permission.objects.get(content_type__model='local', name__contains='add'))
            Distrito.objects.filter(id=x.id).update(grupo=grupo)

        messages.success(request, "Se crearon los grupos correctamente")
    except:
        messages.error(request, "No fue posible crear los grupos")


crear_grupos_dis.short_description = 'Crear grupos y asignar permisos'


class DistritoRecurso(resources.ModelResource):
    class Meta:
        model = Distrito


def permisos_dis(modeladmin, request, queryset):
    distritos = Distrito.objects.exclude(distrito='NO POSEE').annotate(pk_id=Cast('id', output_field=CharField()))
    GroupObjectPermission.objects.filter(object_pk__in=distritos.values_list('pk_id'),
                                         content_type=ContentType.objects.get_for_model(Distrito)).delete()
    for dis in distritos:
        [assign_perm(x + Distrito.__name__.lower(), dis.grupo, dis) for x in ['view_','change_']]
        [assign_perm(x + Distrito.__name__.lower(), dis.grupo.parent, dis) for x in ['view_']]


permisos_dis.short_description = 'asignar permisos del arbol de dependencia'


class DistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = DistritoRecurso
    list_display = ('distrito', 'cge')
    search_fields = ['distrito', 'cge']
    actions = [crear_grupos_dis, permisos_dis]


admin.site.register(Distrito, DistritoAdmin)


###########Registrar en el Admin el modelo Subdistrito ######################
# ********Se registre de esta forma para user Importar/Exportar en Excel***

def crear_grupos_sub(modeladmin, request, queryset):
    try:
        for x in queryset:
            distrito = x.distrito
            if not distrito:
                messages.error(request, "no fue posible crear los grupos, faltan crear grupos de distrito")
                pass

            sin_espacios = str(x.subdistrito).replace(" ", "").lower()
            nombre_grupo_temp = unidecode(sin_espacios)
            nombre_grupo = nombre_grupo_temp
            grupo, creado = Group.objects.get_or_create(name='sub-' + nombre_grupo + '-distrito' + str(distrito.id),
                                                        parent=distrito.grupo)
            permisos = ['view', 'add']

            for m in listado_modelos_subdistritos:
                for p in permisos:
                    grupo.permissions.add(
                        Permission.objects.get(content_type__model=m.__name__.lower(), name__contains=p))

            grupo.permissions.add(
                Permission.objects.get(content_type__model=Local.__name__.lower(),
                                       codename='ver_locals_no_validados_local'))
            grupo.permissions.add(
                Permission.objects.get(content_type__model=Persona.__name__.lower(),
                                       codename='ver_personas_no_validados_persona'))

            grupo.permissions.add(
                Permission.objects.get(content_type__model=Local.__name__.lower(),
                                       codename='ver_locals_a_validar_en_mapa_local'))
            # grupo.permissions.add(
            #     Permission.objects.get(content_type__model=Subdistrito.__name__.lower(),
            #                            codename='ver_subdistrito_subdistrito'))

            Subdistrito.objects.filter(id=x.id).update(grupo=grupo)

        messages.success(request, "Se crearon los grupos correctamente")
    except:
        messages.error(request, "No fue posible crear los grupos")


crear_grupos_sub.short_description = 'Crear grupos y asignar permisos'


class SubdistritoRecurso(resources.ModelResource):
    class Meta:
        model = Subdistrito


def permisos_sub(modeladmin, request, queryset):
    subdistritos = Subdistrito.objects.exclude(subdistrito='-').annotate(pk_id=Cast('id', output_field=CharField()))
    GroupObjectPermission.objects.filter(object_pk__in=subdistritos.values_list('pk_id'),
                                         content_type=ContentType.objects.get_for_model(Subdistrito)).delete()
    for sub in subdistritos:
        [assign_perm(x + Subdistrito.__name__.lower(), sub.grupo, sub) for x in ['view_', 'change_']]
        [assign_perm(x + Subdistrito.__name__.lower(), sub.distrito.grupo, sub) for x in ['view_']]
        [assign_perm(x + Subdistrito.__name__.lower(), sub.distrito.grupo.parent, sub) for x in ['view_']]


permisos_sub.short_description = 'asignar permisos del arbol de dependencia'


class SubdistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SubdistritoRecurso
    list_display = ('subdistrito', 'distrito', 'detalle')
    search_fields = ['subdistrito', 'distrito__distrito']
    actions = [crear_grupos_sub, permisos_sub]


admin.site.register(Subdistrito, SubdistritoAdmin)


###########Registrar en el Admin el modelo Seccion ######################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SeccionRecurso(resources.ModelResource):
    class Meta:
        model = Seccion


def permisos_seccion(modeladmin, request, queryset):
    subdistritos = Subdistrito.objects.exclude(subdistrito='-')
    for sub in subdistritos:
        Seccion_sub = Seccion.objects.filter(subdistrito=sub).annotate(pk_id=Cast('id', output_field=CharField()))
        GroupObjectPermission.objects.filter(object_pk__in=Seccion_sub.values_list('pk_id'),
                                             content_type=ContentType.objects.get_for_model(Seccion)).delete()
        [assign_perm(x + Seccion.__name__.lower(), sub.grupo, Seccion_sub) for x in ['view_' ,'change_']]
        [assign_perm(x + Seccion.__name__.lower(), sub.distrito.grupo, Seccion_sub) for x in ['view_']]
        [assign_perm(x + Seccion.__name__.lower(), sub.distrito.grupo.parent, Seccion_sub) for x in ['view_']]
    distritos = Distrito.objects.exclude(distrito='NO POSEE').filter(distrito_electoral__isnull=True)
    # [print(x) for x in distritos.values_list('distrito',flat=True)]
    for dis in distritos:
        Seccion_dis = Seccion.objects.filter(distrito=dis).annotate(pk_id=Cast('id', output_field=CharField()))
        [assign_perm(x + Seccion.__name__.lower(), dis.grupo, Seccion_dis) for x in ['view_','change_']]
        [assign_perm(x + Seccion.__name__.lower(), dis.grupo.parent, Seccion_dis) for x in ['view_']]


permisos_seccion.short_description = 'asignar permisos del arbol de dependencia'


class SeccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SeccionRecurso
    list_display = ('seccion', 'subdistrito', 'distrito', 'detalle')
    search_fields = ['seccion', 'subdistrito__subdistrito', 'distrito__distrito', 'detalle']
    actions = [permisos_seccion]


admin.site.register(Seccion, SeccionAdmin)


###########Registrar en el Admin el modelo Circuito ######################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class CircuitoRecurso(resources.ModelResource):
    class Meta:
        model = Circuito


def permisos_circuito(modeladmin, request, queryset):
    subdistritos = Subdistrito.objects.exclude(subdistrito='-')
    for sub in subdistritos:
        Circuitos_sub = Circuito.objects.filter(seccion__subdistrito=sub).annotate(
            pk_id=Cast('id', output_field=CharField()))
        GroupObjectPermission.objects.filter(object_pk__in=Circuitos_sub.values_list('pk_id'),
                                             content_type=ContentType.objects.get_for_model(Circuito)).delete()
        [assign_perm(x + Circuito.__name__.lower(), sub.grupo, Circuitos_sub) for x in ['view_', 'change_', 'delete_']]
        [assign_perm(x + Circuito.__name__.lower(), sub.distrito.grupo, Circuitos_sub) for x in ['view_']]
        [assign_perm(x + Circuito.__name__.lower(), sub.distrito.grupo.parent, Circuitos_sub) for x in ['view_']]
    distritos = Distrito.objects.exclude(distrito='NO POSEE').filter(distrito_electoral__isnull=True)
    # [print(x) for x in distritos.values_list('distrito',flat=True)]
    for dis in distritos:
        Circuitos_dis = Circuito.objects.filter(seccion__distrito=dis).annotate(
            pk_id=Cast('id', output_field=CharField()))
        [assign_perm(x + Circuito.__name__.lower(), dis.grupo, Circuitos_dis) for x in ['view_', 'change_', 'delete_']]
        [assign_perm(x + Circuito.__name__.lower(), dis.grupo.parent, Circuitos_dis) for x in ['view_']]


permisos_circuito.short_description = 'asignar permisos del arbol de dependencia'

def resetear_circuitos(modeladmin, request, queryset):
    Circuito.objects.all().update(entrego_urna_en_led=False, situacion='Actividades no iniciadas')


resetear_circuitos.short_description = 'resetear circuitos'


class CircuitoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = CircuitoRecurso
    list_display = ('circuito', 'seccion', 'obtener_subdistrito', 'detalle', 'situacion', 'entrego_urna_en_led',
                    'get_distrito')
    search_fields = ['circuito', 'seccion__seccion', 'seccion__distrito__distrito', 'seccion__subdistrito__subdistrito']
    actions = [permisos_circuito,resetear_circuitos]
    list_filter = ('seccion__distrito__distrito', 'seccion__subdistrito__subdistrito',)

    def get_distrito(self, obj):
        return obj.seccion.distrito.distrito

    get_distrito.short_description = 'Distrito'

    def obtener_subdistrito(self, obj):
        return obj.seccion.subdistrito.subdistrito

    obtener_subdistrito.short_description = 'Subdistrito'

admin.site.register(Circuito, CircuitoAdmin)


###########Registrar en el Admin el modelo Estados del local ######################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class EstadosLocalRecurso(resources.ModelResource):
    class Meta:
        model = EstadosLocal


class EstadosLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = EstadosLocalRecurso
    list_display = ('estado', 'causa')
    search_fields = ['estado', 'causa']


admin.site.register(EstadosLocal, EstadosLocalAdmin)


###########Registrar en el Admin el modelo Local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class LocalRecurso(resources.ModelResource):
    class Meta:
        model = Local


def permisos_local(modeladmin, request, queryset):
    subdistritos = Subdistrito.objects.exclude(subdistrito='-')
    for sub in subdistritos:
        Locales_sub = Local.objects.filter(circuito__seccion__subdistrito=sub).annotate(
            pk_id=Cast('id', output_field=CharField()))
        GroupObjectPermission.objects.filter(object_pk__in=Locales_sub.values_list('pk_id'),
                                             content_type=ContentType.objects.get_for_model(Local)).delete()
        [assign_perm(x + Local.__name__.lower(), sub.grupo, Locales_sub) for x in ['view_', 'change_', 'delete_']]
        [assign_perm(x + Local.__name__.lower(), sub.distrito.grupo, Locales_sub) for x in ['view_']]
        [assign_perm(x + Local.__name__.lower(), sub.distrito.grupo.parent, Locales_sub) for x in ['view_']]
    distritos = Distrito.objects.exclude(distrito='NO POSEE').filter(distrito_electoral__isnull=True)

    for dis in distritos:
        Locales_dis = Local.objects.filter(circuito__seccion__distrito=dis).annotate(
            pk_id=Cast('id', output_field=CharField()))
        [assign_perm(x + Local.__name__.lower(), dis.grupo, Locales_dis) for x in ['view_', 'change_', 'delete_']]
        [assign_perm(x + Local.__name__.lower(), dis.grupo.parent, Locales_dis) for x in ['view_']]


permisos_local.short_description = 'Asignar permisos del arbol de dependencia'


def resetear_validacion_local(modeladmin, request, queryset):
    Local.objects.all().update(validado=0, recepciono_mat_elec=False, entrego_urna=False, transmite_telegrama=False, estado=1)


resetear_validacion_local.short_description = 'Resetear estados de todos los locales OJO!!!!!'

def resetear_validacion_de_un_local(modeladmin, request, queryset):
    queryset.update(validado=0, recepciono_mat_elec=False, entrego_urna=False, transmite_telegrama=False, estado=1)

resetear_validacion_de_un_local.short_description = 'Resetear estado de el/los locales seleccionados'

class LocalAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = LocalRecurso

    list_display = ['nombre', 'direccion', 'validado', 'transmite_telegrama','localidad', 'estado', 'recepciono_mat_elec', 'entrego_urna',
                    'get_distrito', 'get_subdistrito', 'get_seccion', 'circuito', 'fecha_creacion']
    search_fields = ['nombre', 'direccion', 'localidad', 'fecha_creacion','validado', 'recepciono_mat_elec', 'entrego_urna',
                     'transmite_telegrama']
    actions = [resetear_validacion_local, resetear_validacion_de_un_local, permisos_local]

    def get_seccion(self, obj):
        return obj.circuito.seccion

    get_seccion.short_description = 'Seccion'
    get_seccion.admin_order_field = 'circuito__seccion'

    def get_distrito(self, obj):
        return obj.circuito.seccion.distrito

    get_distrito.short_description = 'Distrito'
    get_distrito.admin_order_field = 'circuito__seccion__distrito'

    def get_subdistrito(self, obj):
        return obj.circuito.seccion.subdistrito

    get_subdistrito.short_description = 'Subistrito'
    get_subdistrito.admin_order_field = 'circuito__seccion__subdistrito'


admin.site.register(Local, LocalAdmin)


###########Registrar en el Admin el modelo Hora de control de votos ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class HorasControlVotosLocalRecurso(resources.ModelResource):
    class Meta:
        model = HoraControlVoto


class HorasControlVotosLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = HorasControlVotosLocalRecurso
    list_display = ('hora',)
    search_fields = ['hora']


admin.site.register(HoraControlVoto, HorasControlVotosLocalAdmin)


###########Registrar en el Admin el modelo Contnrol de votos ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class ControlVotosLocalRecurso(resources.ModelResource):
    class Meta:
        model = ControlDeVotos


class ControlVotosLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = ControlVotosLocalRecurso
    list_display = ('horario', 'local', 'cant_votos')
    search_fields = ['horario', 'local', 'cant_votos']


admin.site.register(ControlDeVotos, ControlVotosLocalAdmin)


###########Registrar en el Admin el modelo Transmision de telegramas ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TransmisionTelegramasRecurso(resources.ModelResource):
    class Meta:
        model = TransmisionTelegramas


class TransmisionTelegramasAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = TransmisionTelegramasRecurso
    # Para listar una relacion manytomany en admin -> https://stackoverflow.com/questions/18108521/many-to-many-in-list-display-django
    list_display = ['local', 'transmite_telegrama', 'get_recepciono_mat_elec', 'get_entrego_urnas']
    search_fields = ['local__nombre', 'transmite_telegrama']
    autocomplete_fields = ['local', ]

    def get_recepciono_mat_elec(self, obj):
        return obj.local.recepciono_mat_elec

    get_recepciono_mat_elec.short_description = 'Recepcionó mat elect?'

    def get_entrego_urnas(self, obj):
        return obj.local.entrego_urna

    get_recepciono_mat_elec.short_description = 'Recepcionó mat elect?'
    get_entrego_urnas.short_description = 'Entregó urnas?'


admin.site.register(TransmisionTelegramas, TransmisionTelegramasAdmin)


###########Registrar en el Admin el modelo Estado de la mesa ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class EstadosMesasRecurso(resources.ModelResource):
    class Meta:
        model = EstadosMesas


class EstadosMesasAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = EstadosMesasRecurso
    list_display = ['estado', 'causa']
    search_fields = ['estado', 'causa']


admin.site.register(EstadosMesas, EstadosMesasAdmin)


###########Registrar en el Admin el modelo Mesas en el Local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class MesasEnLocaRecurso(resources.ModelResource):
    class Meta:
        model = MesasEnLocal


class MesasEnLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = MesasEnLocaRecurso
    list_display = ('mesas', 'local', 'fecha_creacion', 'cant_electores')
    search_fields = ['mesas', 'local__nombre']
    autocomplete_fields = ['local']

    def get_queryset(self, request):
        return super(MesasEnLocalAdmin, self).get_queryset(request).select_related('local')


admin.site.register(MesasEnLocal, MesasEnLocalAdmin)


###########Registrar en el Admin el modelo Tipo de Novedad en el local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TipoNovedaLocalRecurso(resources.ModelResource):
    class Meta:
        model = TipoNovedadLocal


class TipoNovedaLocalAdmin(ImportExportModelAdmin):
    resource_class = TipoNovedaLocalRecurso
    list_display = ('tipo', 'nivel', 'lugar')
    search_fields = ['tipo', 'nivel', 'lugar']


admin.site.register(TipoNovedadLocal, TipoNovedaLocalAdmin)


###########Registrar en el Admin el modelo Novedades en el local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class NovedadesLocalRecurso(resources.ModelResource):
    class Meta:
        model = NovedadesEnLocal


class NovedadesLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = NovedadesLocalRecurso
    list_display = ('local', 'fecha', 'tipo', 'detalle',
                    'subsanada', 'medidas_adoptadas', 'fecha_creacion')
    search_fields = ['local', 'fecha', 'tipo',
                     'detalle', 'subsanada', 'medidas_adoptadas']
    autocomplete_fields = ['local']


admin.site.register(NovedadesEnLocal, NovedadesLocalAdmin)


###########Registrar en el Admin el modelo Reparticion ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class ReparticionRecurso(resources.ModelResource):
    class Meta:
        model = Reparticion


class ReparticionAdmin(ImportExportModelAdmin):
    resource_class = ReparticionRecurso
    list_display = ('reparticion',)
    search_fields = ['reparticion']


admin.site.register(Reparticion, ReparticionAdmin)


###########Registrar en el Admin el modelo Fuerza ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class FuerzaRecurso(resources.ModelResource):
    class Meta:
        model = Fuerza


class FuerzaAdmin(ImportExportModelAdmin):
    resource_class = FuerzaRecurso
    list_display = ('fuerza', 'reparticion')

    search_fields = ['fuerza', 'reparticion']


admin.site.register(Fuerza, FuerzaAdmin)


###########Registrar en el Admin el modelo Fuerza de Seguridad ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class FuerzaSeguridadRecurso(resources.ModelResource):
    class Meta:
        model = FuerzaSeguridad


class FuerzaSeguridadAdmin(ImportExportModelAdmin):
    resource_class = FuerzaSeguridadRecurso
    list_display = ('fuerza_seg', 'reparticion')

    search_fields = ['fuerza_seg', 'reparticion']


admin.site.register(FuerzaSeguridad, FuerzaSeguridadAdmin)


###########Registrar en el Admin el modelo Seguridad externa en el local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SeguridadExternaLocalRecurso(resources.ModelResource):
    class Meta:
        model = SegExternaLocal


class SeguridadExternaLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SeguridadExternaLocalRecurso
    list_display = ('fuerza', 'local', 'cant_efectivos')
    search_fields = ['fuerza', 'local', 'cant_efectivos']
    autocomplete_fields = ['local']


admin.site.register(SegExternaLocal, SeguridadExternaLocalAdmin)


###########Registrar en el Admin el modelo Jerarquía ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class JerarquiaRecurso(resources.ModelResource):
    class Meta:
        model = Jerarquia


class JerarquiaAdmin(ImportExportModelAdmin):
    resource_class = JerarquiaRecurso
    list_display = ('jerarquia',)
    search_fields = ['jerarquia']


admin.site.register(Jerarquia, JerarquiaAdmin)


###########Registrar en el Admin el modelo Grado ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class GradoRecurso(resources.ModelResource):
    class Meta:
        model = Grado


class GradoAdmin(ImportExportModelAdmin):
    resource_class = GradoRecurso
    list_display = ('grado', 'obtener_fuerza', 'jerarquia')
    search_fields = ['grado', 'fuerza__fuerza']

    def obtener_fuerza(self, obj):
        return ", ".join([str(f) for f in obj.fuerza.all()])


admin.site.register(Grado, GradoAdmin)


###########Registrar en el Admin el modelo Persona ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***

def resetear_validacion(modeladmin, request, queryset):
    Persona.objects.all().update(num_cargos=0, num_conductor=0, tiene_cargo=False, es_conductor=False, validado=0, validado_por='Sin Confirmar')


resetear_validacion.short_description = 'Resetear validación de personal A TODOS OJO!!!'

def resetear_validacion_personal_uno_o_algunos(modeladmin, request, queryset):
    try:
        queryset.update(num_cargos=0, num_conductor=0, tiene_cargo=False, es_conductor=False, validado=0, validado_por='Sin Confirmar')
        messages.success(request, "Se reseteó la validación a las personas seleccionadas")
    except:
        messages.error(request, "No se pudo resetear la validación a las personas seleccionadas")


resetear_validacion_personal_uno_o_algunos.short_description = 'Resetear validación a las personas seleccionadas SOLAMENTE!!!!!!!!'



class PersonaRecurso(resources.ModelResource):
    class Meta:
        model = Persona


def permisos_personal(modeladmin, request, queryset):
    grupos_para_asignar = Group.objects.filter(
        Q(gurpo_del_subdistrito__isnull=False) | Q(gurpo_del_distrito__isnull=False) | Q(name='personal-CGE'))
    objeto_a_borrar_permisos = Q(content_type=ContentType.objects.get_for_model(Persona))
    GroupObjectPermission.objects.filter(objeto_a_borrar_permisos).delete()
    [assign_perm('change_' + Persona.__name__.lower(), y, Persona.objects.all()) for y in grupos_para_asignar]


permisos_personal.short_description = 'Asignar permisos de edicion A TODOS OJO!!!!!!!!'

def permisos_personal_uno_o_algunos(modeladmin, request, queryset):
    try:
        grupos_para_asignar = Group.objects.filter(
            Q(gurpo_del_subdistrito__isnull=False) | Q(gurpo_del_distrito__isnull=False) | Q(name='personal-CGE'))
        for p in queryset:
            objeto_a_borrar_permisos = Q(content_type=ContentType.objects.get_for_model(p))
            GroupObjectPermission.objects.filter(objeto_a_borrar_permisos).delete()
            [assign_perm('change_' + Persona.__name__.lower(), y, p) for y in grupos_para_asignar]

        messages.success(request, "Se reseteó los permisos a las personas seleccionadas")
    except:
        messages.error(request, "No se pudo resetear los permisos a las personas seleccionadas")


permisos_personal_uno_o_algunos.short_description = 'Crear grupos y asignar permisos a las personas seleccionadas SOLAMENTE!!!!!!!!'


class PersonaAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = PersonaRecurso
    list_display = (
        'grado', 'nombre', 'apellido', 'dni', 'fuerza', 'tiene_cargo', 'num_cargos', 'num_conductor', 'es_conductor',
        'fecha_creacion', 'validado', 'validado_por')
    search_fields = ['grado__grado', 'nombre', 'apellido', 'dni', 'fuerza__fuerza', 'tiene_cargo', 'fecha_creacion',
                     'validado']
    actions = [resetear_validacion, permisos_personal, permisos_personal_uno_o_algunos, resetear_validacion_personal_uno_o_algunos]

    # radio_fields = {'reparticion': admin.HORIZONTAL, 'tipo_armamento': admin.HORIZONTAL}  # admin.VERTICAL

    # necesita modificar el método get_queryset en PersonAdmin, por ejemplo:
    # Antes: 73 consultas en 36.02ms (67 consultas duplicadas en admin)
    # Después: 6 consultas en 10.81ms.
    def get_queryset(self, request):
        return super(PersonaAdmin, self).get_queryset(request).select_related('fuerza')


admin.site.register(Persona, PersonaAdmin)


###########Registrar en el Admin el modelo Seguridad interna en el local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SeguridadInternaLocalRecurso(resources.ModelResource):
    class Meta:
        model = SegInternaLocal


class SeguridadInternaLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SeguridadInternaLocalRecurso
    list_display = ('jefe_local', 'local')
    search_fields = ['jefe_local', 'local']
    autocomplete_fields = ['local', 'jefe_local', ]
    # filter_horizontal = ('auxiliares',)


admin.site.register(SegInternaLocal, SeguridadInternaLocalAdmin)


###########Registrar en el Admin el modelo Unidades ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class UnidadRecurso(resources.ModelResource):
    class Meta:
        model = Unidad


class UnidadAdmin(ImportExportModelAdmin):
    resource_class = UnidadRecurso
    list_display = ('nombre', 'abreviatura')
    search_fields = ['nombre', 'abreviatura']


admin.site.register(Unidad, UnidadAdmin)


###########Registrar en el Admin el modelo Medios ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class MediosRecurso(resources.ModelResource):
    class Meta:
        model = Medios


class MediosAdmin(ImportExportModelAdmin):
    resource_class = MediosRecurso
    list_display = ('medios_transporte',)
    search_fields = ['medios_transporte', ]


admin.site.register(Medios, MediosAdmin)


###########Registrar en el Admin el modelo Tipo de Vehículos Provisto ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TipoVehiculoProvistoRecurso(resources.ModelResource):
    class Meta:
        model = TipoVehiculoProvisto


class TipoVehiculoProvistoAdmin(ImportExportModelAdmin):
    resource_class = TipoVehiculoProvistoRecurso
    list_display = ('tipo_vehiculo_provisto',)
    search_fields = ['tipo_vehiculo_provisto']


admin.site.register(TipoVehiculoProvisto, TipoVehiculoProvistoAdmin)


###########Registrar en el Admin el modelo Tareas ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TareasRecurso(resources.ModelResource):
    class Meta:
        model = Tareas


class TareasAdmin(ImportExportModelAdmin):
    resource_class = TareasRecurso
    list_display = ('tareas',)
    search_fields = ['tareas']


admin.site.register(Tareas, TareasAdmin)


###########Registrar en el Admin el modelo Tipo de Combustible ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***
class TipoCombustibleRecurso(resources.ModelResource):
    class Meta:
        model = TipoCombustible


class TipoCombustibleAdmin(ImportExportModelAdmin):
    resource_class = TipoCombustibleRecurso
    list_display = ('tipo_combustible',)
    search_fields = ['tipo_combustible']


admin.site.register(TipoCombustible, TipoCombustibleAdmin)


###########Registrar en el Admin el modelo Vehículos Propios ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosPropiosRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosPropios


class VehiculosPropiosAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosPropiosRecurso
    list_display = (
        'ni_patente_matricula', 'tipo_vehiculo_provisto', 'fecha_creacion', 'posee_sensor_rastreo', 'troncal',
        'tiene_destino', 'cantidad_empleos')
    search_fields = ['ni_patente_matricula', 'tipo_vehiculo_provisto__tipo_vehiculo_provisto', 'fecha_creacion',
                     'posee_sensor_rastreo', 'troncal', 'tiene_destino']


admin.site.register(VehiculosPropios, VehiculosPropiosAdmin)


###########Registrar en el Admin el modelo Tipo de Vehículos Civiles ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TipoVehiculoCivilRecurso(resources.ModelResource):
    class Meta:
        model = TipoVehiculoCivil


class TipoVehiculoCivilAdmin(ImportExportModelAdmin):
    resource_class = TipoVehiculoCivilRecurso
    list_display = ('tipo_vehiculo_civil',)
    search_fields = ['tipo_vehiculo_civil']


admin.site.register(TipoVehiculoCivil, TipoVehiculoCivilAdmin)


###########Registrar en el Admin el modelo Novedad general ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class NovedadGrlRecurso(resources.ModelResource):
    class Meta:
        model = NovedadesGenerales


class NovedadesGeneralesAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = NovedadGrlRecurso
    list_display = ['tipo', 'distrito', 'fecha', 'detalle', 'subsanada', 'medidas_adoptadas']
    search_fields = ['tipo', 'distrito', 'fecha', 'detalle', 'subsanada', 'medidas_adoptadas']


admin.site.register(NovedadesGenerales, NovedadesGeneralesAdmin)


###########Registrar en el Admin el modelo Tipo de Movimientos ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TipoMovimientoRecurso(resources.ModelResource):
    class Meta:
        model = TipoMovimiento


class TipoMovimientoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = TipoMovimientoRecurso
    fields = ['tipo', ]
    search_fields = ['tipo', ]


admin.site.register(TipoMovimiento, TipoMovimientoAdmin)


###########Registrar en el Admin el modelo Movimientos ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class MovimientosRecurso(resources.ModelResource):
    class Meta:
        model = Movimientos


class MovimientosAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = MovimientosRecurso
    list_display = ['distrito', 'tipo', 'efectivos', 'vehiculos', 'inicio', 'fin', 'fecha_creacion']
    search_fields = ['distrito', 'tipo', 'efectivos', 'vehiculos''inicio', 'fin', 'fecha_creacion']


admin.site.register(Movimientos, MovimientosAdmin)


###########Registrar en el Admin el modelo Tipo de Led ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class TipoLedRecurso(resources.ModelResource):
    class Meta:
        model = TipoLed


class TipoLedAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = TipoLedRecurso
    list_display = ['tipo', ]
    search_fields = ['tipo', ]


admin.site.register(TipoLed, TipoLedAdmin)


###########Registrar en el Admin el modelo LED ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class LedRecurso(resources.ModelResource):
    class Meta:
        model = Led


class LedAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = LedRecurso
    list_display = ['distrito', 'direccion', 'tipo', 'obs', 'fecha_creacion']
    search_fields = ['distrito', 'direccion', 'tipo', 'obs', 'fecha_creacion']


admin.site.register(Led, LedAdmin)


###########Registrar en el Admin el modelo Seg FFAA en LED ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SegEnLedFuerzaArmadaRecurso(resources.ModelResource):
    class Meta:
        model = SegEnLedFuerzaArmada


class SegEnLedFuerzaArmadaAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SegEnLedFuerzaArmadaRecurso
    list_display = ['led', 'fecha_inicio', 'fecha_fin', 'fuerza_armada', 'cant_personal', 'fecha_creacion']
    search_fields = ['led', 'fecha_inicio', 'fecha_fin', 'fuerza_armada', 'cant_personal', 'fecha_creacion']


admin.site.register(SegEnLedFuerzaArmada, SegEnLedFuerzaArmadaAdmin)


###########Registrar en el Admin el modelo Seg Fuerzas de Seguridad en LED ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SegEnLedFuerzaSeguridadRecurso(resources.ModelResource):
    class Meta:
        model = SegEnLedFuerzaSeguridad


class SegEnLedFuerzaSeguridadAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SegEnLedFuerzaSeguridadRecurso
    list_display = ['led', 'fecha_inicio', 'fecha_fin', 'fuerza_seguridad', 'cant_personal', 'fecha_creacion']
    search_fields = ['led', 'fecha_inicio', 'fecha_fin', 'fuerza_seguridad', 'cant_personal', 'fecha_creacion']


admin.site.register(SegEnLedFuerzaSeguridad, SegEnLedFuerzaSeguridadAdmin)


###########Registrar en el Admin el modelo Cargo ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class CargoRecurso(resources.ModelResource):
    class Meta:
        model = Cargo


class CargoAdmin(ImportExportModelAdmin):
    resource_class = CargoRecurso
    list_display = ['cargo', 'guia', 'prioridad']
    search_fields = ['cargo','guia', 'prioridad']


admin.site.register(Cargo, CargoAdmin)


###########Registrar en el Admin el modelo DistribucionPersonalCdoGrlElect ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class DistribucionPersonalCdoGrlElectRecurso(resources.ModelResource):
    class Meta:
        model = DistribucionPersonalCdoGrlElect


class DistribucionPersonalCdoGrlElectAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = DistribucionPersonalCdoGrlElectRecurso
    list_display = ('cge', 'cargo', 'designacion', 'integrante', 'fecha_creacion')
    search_fields = ['cge', 'cargo', 'designacion', 'fecha_creacion']
    autocomplete_fields = ['integrante',]


admin.site.register(DistribucionPersonalCdoGrlElect,
                    DistribucionPersonalCdoGrlElectAdmin)


###########Registrar en el Admin el modelo ReservaCdoGrlElect ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class ReservaCdoGrlElectRecurso(resources.ModelResource):
    class Meta:
        model = ReservaCdoGrlElect


class ReservaCdoGrlElectAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = ReservaCdoGrlElectRecurso
    list_display = ('cge', 'integrante', 'obs', 'fecha_creacion')
    search_fields = ['cge', 'integrante', 'obs', 'fecha_creacion']
    autocomplete_fields = ['integrante']


admin.site.register(ReservaCdoGrlElect,
                    ReservaCdoGrlElectAdmin)


###########Registrar en el Admin el modelo VehiculosPropiosCdoGrlElect ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosPropiosCdoGrlElectRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosPropiosCdoGrlElect


class VehiculosPropiosCdoGrlElectAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosPropiosCdoGrlElectRecurso
    list_display = (
        'cge', 'veh_propio', 'fecha_creacion', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer',
        'obs')
    search_fields = ['cge', 'veh_propio', 'fecha_creacion', 'desde', 'hasta', 'tareas', 'zona_trabajo',
                     'kilometros_a_recorrer', 'obs']


admin.site.register(VehiculosPropiosCdoGrlElect, VehiculosPropiosCdoGrlElectAdmin)


###########Registrar en el Admin el modelo VehiculosContratadosCdoGrlElect ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosContratadosCdoGrlElectRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosContratadosCdoGrlElect


class VehiculosContratadosCdoGrlElectAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosCdoGrlElectRecurso
    list_display = ('cge', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
                    'kilometros_a_recorrer', 'obs', 'responsable')
    search_fields = ['cge', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
                     'kilometros_a_recorrer', 'obs', 'responsable']


admin.site.register(VehiculosContratadosCdoGrlElect,
                    VehiculosContratadosCdoGrlElectAdmin)


###########Registrar en el Admin el modelo DistribucionPersonalDistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class DistribucionPersonalDistritoRecurso(resources.ModelResource):
    class Meta:
        model = DistribucionPersonalDistrito


class DistribucionPersonalDistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = DistribucionPersonalDistritoRecurso
    list_display = ('distrito', 'cargo', 'designacion', 'integrante')
    search_fields = ['distrito', 'cargo', 'designacion']
    autocomplete_fields = ['integrante']


admin.site.register(DistribucionPersonalDistrito,
                    DistribucionPersonalDistritoAdmin)


###########Registrar en el Admin el modelo ReservaDistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class ReservaDistritoRecurso(resources.ModelResource):
    class Meta:
        model = ReservaDistrito


class ReservaDistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = ReservaDistritoRecurso
    list_display = ('distrito', 'integrante')
    search_fields = ['distrito', 'integrante']
    autocomplete_fields = ['integrante']


admin.site.register(ReservaDistrito,
                    ReservaDistritoAdmin)


###########Registrar en el Admin el modelo VehiculosPropiosDistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosPropiosDistritoRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosPropiosDistrito


class VehiculosPropiosDistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosPropiosDistritoRecurso
    list_display = ('distrito', 'veh_propio', 'conductor', 'fecha_creacion', 'desde', 'hasta', 'tareas', 'zona_trabajo',
                    'kilometros_a_recorrer', 'obs')
    search_fields = ['distrito__distrito', 'veh_propio__ni_patente_matricula', 'veh_propio__conductor__dni',
                     'fecha_creacion', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer', 'obs']

    def get_queryset(self, request):
        return super(VehiculosPropiosDistritoAdmin, self).get_queryset(request).select_related('distrito')

    def get_queryset(self, request):
        return super(VehiculosPropiosDistritoAdmin, self).get_queryset(request).select_related('veh_propio')


admin.site.register(VehiculosPropiosDistrito,
                    VehiculosPropiosDistritoAdmin)


###########Registrar en el Admin el modelo VehiculosContratadosDistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosContratadosDistritoRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosContratadosDistrito


class VehiculosContratadosDistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosDistritoRecurso
    list_display = ('distrito', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
                    'kilometros_a_recorrer', 'obs', 'responsable')
    search_fields = ['distrito', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                     'hasta', 'kilometros_a_recorrer', 'obs', 'responsable']


admin.site.register(VehiculosContratadosDistrito,
                    VehiculosContratadosDistritoAdmin)


###########Registrar en el Admin el modelo DistribucionPersonalSubdistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class DistribucionPersonalSubdistritoRecurso(resources.ModelResource):
    class Meta:
        model = DistribucionPersonalSubdistrito


class DistribucionPersonalSubdistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = DistribucionPersonalSubdistritoRecurso
    list_display = ('subdistrito', 'cargo', 'designacion', 'integrante')
    search_fields = ['subdistrito', 'cargo', 'designacion']
    autocomplete_fields = ['integrante',]


admin.site.register(DistribucionPersonalSubdistrito,
                    DistribucionPersonalSubdistritoAdmin)


###########Registrar en el Admin el modelo ReservaSubdistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class ReservaSubdistritoRecurso(resources.ModelResource):
    class Meta:
        model = ReservaSubdistrito


class ReservaSubdistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = ReservaSubdistritoRecurso
    list_display = ('subdistrito', 'integrante')
    search_fields = ['subdistrito', 'integrante']
    autocomplete_fields = ['integrante',]


admin.site.register(ReservaSubdistrito,
                    ReservaSubdistritoAdmin)


###########Registrar en el Admin el modelo VehiculosPropiosSubdistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosPropiosSubdistritoRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosPropiosSubdistrito


class VehiculosPropiosSubdistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosPropiosDistritoRecurso
    list_display = ('subdistrito', 'veh_propio', 'conductor')
    search_fields = ['subdistrito__subdistrito', 'veh_propio__ni_patente_matricula', 'veh_propio__conductor__dni']

    def get_queryset(self, request):
        return super(VehiculosPropiosSubdistritoAdmin, self).get_queryset(request).select_related('subdistrito')

    def get_queryset(self, request):
        return super(VehiculosPropiosSubdistritoAdmin, self).get_queryset(request).select_related('veh_propio')


admin.site.register(VehiculosPropiosSubdistrito,
                    VehiculosPropiosSubdistritoAdmin)


###########Registrar en el Admin el modelo VehiculosContratadosSubdistrito ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosContratadosSubdistritoRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosContratadosSubdistrito


class VehiculosContratadosSubdistritoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosSubdistritoRecurso
    list_display = (
        'subdistrito', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
        'kilometros_a_recorrer', 'obs', 'responsable')
    search_fields = ['subdistrito', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                     'hasta',
                     'kilometros_a_recorrer', 'obs', 'responsable']


admin.site.register(VehiculosContratadosSubdistrito,
                    VehiculosContratadosSubdistritoAdmin)


###########Registrar en el Admin el modelo OrganizacionSeccion ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class OrcanizacionSeccionRecurso(resources.ModelResource):
    class Meta:
        model = DistribucionPersonalSeccion


class OrganizacionSeccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = OrcanizacionSeccionRecurso
    list_display = ('seccion', 'cargo', 'designacion', 'integrante')
    search_fields = ['seccion', 'cargo', 'designacion', 'integrante']
    autocomplete_fields = ['integrante',]


admin.site.register(DistribucionPersonalSeccion, OrganizacionSeccionAdmin)


###########Registrar en el Admin el modelo VehiculosPropiosSeccion ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosPropiosSeccionRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosPropiosSeccion


class VehiculosPropiosSeccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosPropiosSeccionRecurso
    list_display = ('seccion', 'veh_propio', 'conductor')
    search_fields = ['seccion', 'veh_propio__ni_patente_matricula', 'veh_propio__conductor__dni', 'conductor']

    def get_queryset(self, request):
        return super(VehiculosPropiosSeccionAdmin, self).get_queryset(request).select_related('seccion')

    def get_queryset(self, request):
        return super(VehiculosPropiosSeccionAdmin, self).get_queryset(request).select_related('veh_propio')


admin.site.register(VehiculosPropiosSeccion,
                    VehiculosPropiosSeccionAdmin)


###########Registrar en el Admin el modelo VehiculosContratadosSeccion ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosContratadosSeccionRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosContratadosSeccion


class VehiculosContratadosSeccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosSeccionRecurso
    list_display = ('seccion', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
                    'kilometros_a_recorrer', 'obs', 'responsable')
    search_fields = ['seccion', 'vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta',
                     'kilometros_a_recorrer', 'obs', 'responsable']


admin.site.register(VehiculosContratadosSeccion,
                    VehiculosContratadosSeccionAdmin)


###########Registrar en el Admin el modelo Vehiculos Contratados ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class VehiculosContratadosRecurso(resources.ModelResource):
    class Meta:
        model = VehiculosContratados


class VehiculosContratadosAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosRecurso
    list_display = (
        'tipo_vehiculo_contratado', 'tiene_destino', 'patente_matricula', 'posee_sensor_rastreo', 'troncal',
        'fecha_creacion', 'cantidad_empleos')
    search_fields = ['tiene_destino', 'patente_matricula', 'posee_sensor_rastreo', 'troncal',
                     'tipo_vehiculo_contratado__tipo_vehiculo_civil']


admin.site.register(VehiculosContratados, VehiculosContratadosAdmin)


###########Registrar en el Admin el modelo Auxiliares del local ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class AuxiliarLocalsRecurso(resources.ModelResource):
    class Meta:
        model = AuxiliarLocal


class AuxiliarLocalAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = VehiculosContratadosRecurso
    list_display = ('seg_interna_local', 'auxiliar')
    search_fields = ['seg_interna_local', 'auxiliar']
    autocomplete_fields = ['seg_interna_local', 'auxiliar', ]


admin.site.register(AuxiliarLocal, AuxiliarLocalAdmin)


###########Registrar en el Admin el modelo Historial de estado de los Puntos de Recolección de SACAS ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SACASHistorialPuntosRecoleccionRecurso(resources.ModelResource):
    class Meta:
        model = SACASHistorialPuntosRecoleccion


class SACASHistorialPuntosRecoleccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SACASHistorialPuntosRecoleccionRecurso
    list_display = ['prs', 'estado', 'fecha']
    search_fields = ['estado', 'fecha']

admin.site.register(SACASHistorialPuntosRecoleccion, SACASHistorialPuntosRecoleccionAdmin)

###########Registrar en el Admin el modelo Puntos de recolección de SACAS ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SACASPuntosRecoleccionRecurso(resources.ModelResource):
    class Meta:
        model = SACASPuntosRecoleccion

class SACASPuntosRecoleccionAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = SACASPuntosRecoleccionRecurso
    list_display = ['distrito', 'direccion',
                    'denominacion_puesto', 'fecha_creacion', 'cant_uupp']
    search_fields = ['distrito', 'direccion',
                     'denominacion_puesto', 'fecha_creacion', 'cant_uupp']
    # list_filter =['']


admin.site.register(SACASPuntosRecoleccion, SACASPuntosRecoleccionAdmin)


###########Registrar en el Admin el modelo Historial de estado de los Circuitos de Recolección de SACAS ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SACASHistorialCircuitosRecoleccionRecurso(resources.ModelResource):
    class Meta:
        model = SACASHistorialCircuitosRecoleccion


class SACASHistorialCircuitosRecoleccionAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = SACASHistorialCircuitosRecoleccionRecurso
    list_display = ['crs', 'estado', 'fecha']
    search_fields = ['crs', 'estado', 'fecha']

admin.site.register(SACASHistorialCircuitosRecoleccion, SACASHistorialCircuitosRecoleccionAdmin)

###########Registrar en el Admin el modelo Circuitos de recolección de SACAS ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SACACircuitoRecoleccionRecurso(resources.ModelResource):
    class Meta:
        model = SACACircuitoRecoleccion

class SACACircuitoRecoleccionAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = SACACircuitoRecoleccionRecurso
    list_display = ['distrito', 'ctrs',
                    'cant_personal', 'vehiculo', 'fecha_creacion']
    search_fields = ['distrito', 'ctrs',
                     'cant_personal', 'vehiculo', 'fecha_creacion']
    # list_filter =['']


admin.site.register(SACACircuitoRecoleccion, SACACircuitoRecoleccionAdmin)

###########Registrar en el Admin el modelo que se vinculan Puntos de recolección y Circuitos ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class Circuito_PuntoRecurso(resources.ModelResource):
    class Meta:
        model = Circuito_Punto

class SACACircuitoRecoleccionAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = Circuito_PuntoRecurso
    list_display = ['circuito', 'punto', 'fecha_creacion']
    search_fields = ['circuito', 'punto', 'fecha_creacion']
    # list_filter =['']


admin.site.register(Circuito_Punto, SACACircuitoRecoleccionAdmin)

###########Registrar en el Admin el modelo Sucursal Electoral Digital (SED) ###################
# ********Se registre de esta forma para user Importar/Exportar en Excel***


class SedRecurso(resources.ModelResource):
    class Meta:
        model = Sed


class SedAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = SedRecurso
    list_display = ['distrito', 'direccion', 'sed','localidad', 'telefono']
    search_fields = ['distrito', 'direccion', 'sed','localidad', 'telefono']
    # list_filter =['']


admin.site.register(Sed, SedAdmin)


class TipoLugarInteresRecurso(resources.ModelResource):
    class Meta:
        model = TipoLugarInteres

class TipoLugarInteresAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = TipoLugarInteresRecurso
    list_display = ['tipo', 'clase' ]
    search_fields = ['tipo', 'clase']
    # list_filter =['']


admin.site.register(TipoLugarInteres, TipoLugarInteresAdmin)


class LugarInteresRecurso(resources.ModelResource):
    class Meta:
        model = LugarInteres


class LugarInteresAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = LugarInteresRecurso
    list_display = ['distrito', 'autoridad', 'direccion', 'tipo_lugar', 'telefono', 'fecha_creacion', 'obs' ]
    search_fields = ['distrito', 'autoridad', 'direccion', 'tipo_lugar', 'telefono', 'fecha_creacion', 'obs']
    # list_filter =['']


admin.site.register(LugarInteres, LugarInteresAdmin)

class GuiaAutoridadesRecurso(resources.ModelResource):
    class Meta:
        model = GuiaAutoridades

class GuiaAutoridadesAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = GuiaAutoridadesRecurso
    list_display = ['persona_guia', 'puesto_texto', 'gde_guia', 'tel_guia','org_texto', 'org_id', 'org_control']
    search_fields = ['persona_guia', 'distrito_guia', 'puesto_texto', 'org_texto', 'org_id', 'org_control']
    autocomplete_fields = ['persona_guia',]
    # list_filter =['']

admin.site.register(GuiaAutoridades, GuiaAutoridadesAdmin)

class PuestoGuiaAutoridadesRecurso(resources.ModelResource):
    class Meta:
        model = PuestoGuiaAutoridades

class PuestoGuiaAutoridadesAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = PuestoGuiaAutoridadesRecurso
    list_display = ['guia', 'puesto']
    search_fields = ['guia', 'puesto']
    # autocomplete_fields = [,]
    # list_filter =[,]

admin.site.register(PuestoGuiaAutoridades, PuestoGuiaAutoridadesAdmin)

class CgeGuiaRecurso(resources.ModelResource):
    class Meta:
        model = CgeGuia

class CgeGuiaAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = CgeGuiaRecurso
    list_display = ['guia', 'cge']
    search_fields = ['guia', 'cge']
    # autocomplete_fields = [,]
    # list_filter =[,]

admin.site.register(CgeGuia, CgeGuiaAdmin)


class DistritoGuiaRecurso(resources.ModelResource):
    class Meta:
        model = DistritoGuia

class DistritoGuiaAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = DistritoGuiaRecurso
    list_display = ['guia', 'dist']
    search_fields = ['guia', 'dist']
    # autocomplete_fields = [,]
    # list_filter =[,]

admin.site.register(DistritoGuia,DistritoGuiaAdmin)


class SubdistritoPersonaRecurso(resources.ModelResource):
    class Meta:
        model = SubdistritoPersona

class SubddistritoPersonaAdmin(GuardedModelAdmin, LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = SubdistritoPersonaRecurso
    list_display = ['subdistrito', 'persona']
    search_fields = ['subdistrito', 'persona']
    autocomplete_fields = ['persona',]
    # list_filter =[,]

admin.site.register(SubdistritoPersona,SubddistritoPersonaAdmin)
