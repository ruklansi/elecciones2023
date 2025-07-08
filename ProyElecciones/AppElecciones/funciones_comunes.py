import re

from crum import get_current_user
from django.contrib.auth.models import Group
from django.db.models import Q, Value, Case, When, F
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.views import View
from guardian.shortcuts import get_objects_for_user, assign_perm, UserObjectPermission

from AppElecciones.models import Persona, VehiculosPropios, Distrito, Subdistrito, Seccion, Circuito, Local, \
    TipoNovedadLocal, CamposEnMayusculas, VehiculosContratados, CdoGrlElect, SubdistritoPersona
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import GroupObjectPermission

def organizacion_del_usuario(usuario=None):
    if not usuario:
        usuario = get_current_user()
    rol = usuario.rol
    if rol == 3:
        distrito = Distrito.objects.get(grupo__user=usuario)
        if Subdistrito.objects.filter(distrito=distrito):
            tiene_subdistrito = 'si'
        else:
            tiene_subdistrito = 'no'
        return {'org': 'distrito', 'distrito': distrito.distrito, 'instancia': distrito,
                'tiene_subdistrito': tiene_subdistrito, 'distrito_queryset': Distrito.objects.filter(id=distrito.id),}
    elif rol == 4:
        subdistrito = Subdistrito.objects.get(grupo__user=usuario)
        return {'org': 'subdistrito', 'distrito': subdistrito.distrito.distrito,
                'distrito_queryset': Distrito.objects.filter(id=subdistrito.distrito.id),
                'subdistrito': subdistrito.subdistrito, 'instancia': subdistrito, 'tiene_subdistrito': 'no','sub_instancia':subdistrito.distrito}
    elif rol == 2 and CdoGrlElect.objects.filter(grupo__user=usuario).exists():
        return {'org': 'CGE', 'tiene_subdistrito': 'no'}
    elif rol == 9 and Group.objects.filter(name='personal-CGE', user=usuario).exists():
        cge = CdoGrlElect.objects.get(id=1)
        return {'org': 'Personal', 'tiene_subdistrito': 'no', 'instancia_cge': cge}
    elif rol == 10 and Group.objects.filter(name='material-CGE', user=usuario):
        return {'org': 'Material', 'tiene_subdistrito': 'no'}


class ObtenerPersonasAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                term = request.GET.get('term')
                usuario = request.user
                if usuario.rol==10:
                    persona_ = get_objects_for_user(usuario, 'view_persona', Persona).filter(validado=1)
                else:
                    persona_ = get_objects_for_user(usuario, 'change_persona', Persona).filter(validado=1)
                personas = persona_.filter(Q(apellido__icontains=term) | Q(dni__icontains=term),
                                           Q(tiene_cargo=False) | (
                                                       Q(tiene_cargo=True) & Q(es_conductor=True) & Q(num_cargos=0)))[
                           :10]
                datos = list(personas.values('id', 'grado__grado', 'nombre', 'apellido', 'dni'))
                return JsonResponse(datos, safe=False)


class ObtenerCualquierPersonasAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.is_ajax():

                resultado = dict()
                dni = request.POST['dni']
                if not re.match('^[0-9]{8,8}$', dni):
                    resultado['hay_error'] = True
                    resultado[
                        'datos'] = 'El formato del DNI debe contener sólo 8 caracteres numéricos, sin especios ni puntos'
                elif not Persona.objects.filter(dni=dni):
                    resultado['hay_error'] = True
                    resultado['datos'] = 'No ha sido cargada una persona con ese DNI'
                else:

                    persona = Persona.objects.filter(dni=dni).annotate(puesto=
                    Case(

                        When(persona_guia__isnull=False,
                             then=Concat(
                                         F('persona_guia__puesto_texto'),
                                         Value(' en el ') ,
                                         F('persona_guia__org_texto'),
                                         output_field=CamposEnMayusculas())),

                        When(cge_persona__isnull=False,
                             then=Concat(F('cge_persona__cargo__cargo'),
                                         Value(' en el CGE '),
                                         output_field=CamposEnMayusculas())),
                        When(reserva_cge_persona__isnull=False,
                             then=Concat(Value('Reserva en el CGE '),
                                         Value(' '),
                                         output_field=CamposEnMayusculas())),
                        When(veh_pro_cge_persona__isnull=False,
                             then=Concat(Value('Cond vehículo provisto en el CGE '),
                                         Value(' '),
                                         output_field=CamposEnMayusculas())),
                        When(veh_con_cge_persona__isnull=False,
                             then=Concat(Value('Cond vehículo contratado en el CGE '),
                                         Value(' '),
                                         output_field=CamposEnMayusculas())),
                        When(distrito_persona__isnull=False,
                             then=Concat(F('distrito_persona__cargo__cargo'),
                                         Value(' en el Distrito: '),
                                         F('distrito_persona__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(res_dis_personal__isnull=False,
                             then=Concat(Value('Reserva en el Distrito: '),
                                         F('res_dis_personal__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_pro_dis_persona__isnull=False,
                             then=Concat(Value('Cond vehículo provisto en un Distrito '),
                                         F('veh_pro_dis_persona__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_con_dis_personal__isnull=False,
                             then=Concat(Value('Cond vehículo contratado en un Distrito '),
                                         F('veh_con_dis_personal__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(sub_personal__isnull=False,
                             then=Concat(F('sub_personal__cargo__cargo'),
                                         Value(' en el Subdistrito: '),
                                         F('sub_personal__subdistrito__subdistrito'), Value(' '),
                                         Value(' del Distrito: '),
                                         F('sub_personal__subdistrito__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(res_sub_personal__isnull=False,
                             then=Concat(Value('Reserva del Subdistrito: '),
                                         F('res_sub_personal__subdistrito__subdistrito'),
                                         Value(' del Distrito: '),
                                         F('res_sub_personal__subdistrito__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_pro_sub_persona__isnull=False,
                             then=Concat(Value('Cond vehículo provisto en un Subdistrito '),
                                         F('veh_pro_sub_persona__subdistrito__subdistrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_con_sub_personal__isnull=False,
                             then=Concat(Value('Cond vehículo contratado en un Subdistrito '),
                                         F('veh_pro_sub_persona__subdistrito__subdistrito'),
                                         output_field=CamposEnMayusculas())),
                        When(sec_personal__isnull=False,
                             then=Concat(F('sec_personal__cargo__cargo'),
                                         Value(' en la Sección: '),
                                         F('sec_personal__seccion__seccion'),
                                         Value(' del Subdistrito: '),
                                         F('sec_personal__seccion__subdistrito__subdistrito'),
                                         Value(' del Distrito: '),
                                         F('sec_personal__seccion__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_prop_personal_sec__isnull=False,
                             then=Concat(Value('Cond vehículo provisto en una Sección '),
                                         F('veh_prop_personal_sec__seccion__seccion'),
                                         Value(' del Subdistrito: '),
                                         F('veh_prop_personal_sec__seccion__subdistrito__subdistrito'),
                                         Value(' del Distrito: '),
                                         F('veh_prop_personal_sec__seccion__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(veh_cont_personal_sec__isnull=False,
                             then=Concat(Value('Cond vehículo contratado en una Sección '),
                                         F('veh_cont_personal_sec__seccion__seccion'),
                                         Value(' del Subdistrito: '),
                                         F('veh_cont_personal_sec__seccion__subdistrito__subdistrito'),
                                         Value(' del Distrito: '),
                                         F('veh_cont_personal_sec__seccion__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(jefe_local__isnull=False,
                             then=Concat(Value('Jefe del local: '), F('jefe_local__local__nombre'),
                                         Value(' en el Distrito: '),
                                         F('jefe_local__local__circuito__seccion__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(aux_local__isnull=False,
                             then=Concat(Value('Auxiliar del local: '),
                                         F('aux_local__seg_interna_local__local__nombre'),
                                         Value(' en el Distrito: '),
                                         F('aux_local__seg_interna_local__local__circuito__seccion__distrito__distrito'),
                                         output_field=CamposEnMayusculas())),
                        When(Q(validado=True) & ~Q(validado_por='Sin Confirmar'), then=F('validado_por')),
                        default=Value('Sin puesto')))
                    resultado['datos'] = list(
                        persona.values('id', 'grado__grado', 'nombre', 'apellido', 'dni', 'puesto'))
                    resultado['hay_error'] = False
                return JsonResponse(resultado, safe=False)


class ObtenerVehiculosPropiosAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                term = request.GET.get('term')
                usuario = request.user
                veh = get_objects_for_user(usuario, 'view_vehiculospropios', VehiculosPropios, accept_global_perms=False).all()
                vehiculos_propios = veh.filter(
                    Q(tipo_vehiculo_provisto__tipo_vehiculo_provisto__icontains=term) | Q(
                        ni_patente_matricula__icontains=term))
                datos = list(vehiculos_propios.values('id', 'ni_patente_matricula',
                                                      'tipo_vehiculo_provisto__tipo_vehiculo_provisto',
                                                      'unidad__nombre'))
                return JsonResponse(datos, safe=False)


class ObtenerVehiculosContratadosAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                term = request.GET.get('term')
                usuario = request.user
                vehc = get_objects_for_user(usuario, 'view_vehiculoscontratados', VehiculosContratados,accept_global_perms=True).all()
                vehiculos_contratados = vehc.filter(
                    Q(tipo_vehiculo_contratado__tipo_vehiculo_civil__icontains=term) | Q(
                        patente_matricula__icontains=term))
                datos = list(vehiculos_contratados.values('id', 'patente_matricula',
                                                          'tipo_vehiculo_contratado__tipo_vehiculo_civil'))
                return JsonResponse(datos, safe=False)


class FiltroParaOrganizaciones(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        respuesta = dict()
        accion = (request.POST['accion'])
        if accion == 'cargar-distritos':
            if get_current_user().rol == 3 or get_current_user().rol == 4:
                if organizacion_del_usuario()['org'] == 'distrito':
                    d = organizacion_del_usuario()['instancia']
                    data.append({'id': d.id, 'distrito': d.distrito})

            if get_current_user().rol == 2 or get_current_user().rol == 9 or get_current_user().rol == 10:
                for d in Distrito.objects.all().order_by('id'):
                    if d.distrito != 'NO POSEE':
                        data.append({'id': d.id, 'distrito': d.distrito})

            respuesta['datos'] = data
        if accion == 'cargar-subdistritos':
            if get_current_user().rol == 4:

                if organizacion_del_usuario()['org'] == 'subdistrito':
                    sub = organizacion_del_usuario()['instancia']

                    data.append({'id': sub.id, 'subdistrito': sub.subdistrito})
            respuesta['datos'] = data
        if accion == 'filtrar-subdistritos':

            sub = Subdistrito.objects.filter(distrito_id=request.POST['id'])
            if sub:

                data = []
                for s in Subdistrito.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': s.id, 'subdistrito': s.subdistrito})
                respuesta['datos'] = data
                respuesta['hay_subdistrito'] = True

            else:
                data = []
                for t in Seccion.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': t.id, 'seccion': t.seccion})
                respuesta['datos'] = data
                respuesta['hay_subdistrito'] = False
        if accion == 'filtrar-seccion':
            data = []
            # aca el id es un subdistrito
            for s in Seccion.objects.filter(subdistrito_id=request.POST['id']):
                data.append({'id': s.id, 'seccion': s.seccion})
            respuesta['datos'] = data
            respuesta['hay_secciones'] = True
        if accion == 'filtrar-circuito':
            data = []
            for c in Circuito.objects.filter(seccion_id=request.POST['id']):
                data.append({'id': c.id, 'circuito': c.circuito})
            respuesta['datos'] = data
            respuesta['hay_circuitos'] = True
        if accion == 'filtrar-local':
            data = []
            for l in Local.objects.filter(circuito_id=request.POST['id'], mesas_en_local__isnull=False).distinct():
                data.append({'id': l.id, 'local': l.nombre})
            respuesta['datos'] = data
            respuesta['hay_locales'] = True
        return JsonResponse(respuesta, safe=False)


class CargarNovParaFiltrosAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        accion = (request.POST['accion'])

        if accion == 'filtrar_desde_novedades_generales':
            for t in TipoNovedadLocal.objects.filter(tipo_novedad_general__isnull=False).distinct():
                data.append({'id': t.id, 'tipo_novedad': t.tipo})

        if accion == 'filtrar_desde_novedades_en_locales':
            for t in TipoNovedadLocal.objects.filter(tipo_novedad_en_el_local__isnull=False).distinct():
                data.append({'id': t.id, 'tipo_novedad': t.tipo})
        return JsonResponse(data, safe=False)


class ValidadorGenericoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        accion = request.POST['accion']

        if accion == 'validar_personal':
            id_persona = request.POST['id_persona']
            p = Persona.objects.get(id=id_persona)
            org_user = organizacion_del_usuario()
            if org_user['org'] == 'distrito':
                p.distrito = org_user['instancia']
                texto = 'Confirmado en ' + org_user['distrito']
            elif org_user['org'] == 'subdistrito':
                p.distrito = org_user['sub_instancia']
                texto = 'Confirmado en Subdistrito' + org_user['subdistrito'] + ' de ' + org_user['distrito']
                SubdistritoPersona.objects.create(persona=p, subdistrito=org_user['instancia'])
            elif org_user['org'] == 'Personal':
                texto = 'Confirmado en  CGE'
            else:
                texto = 'Sin Confirmar'
            p.validado = 1
            p.validado_por = texto
            p.save()
            # PROCESO DE ASIGNAR PERMISO EXCEPCIONAL PARA NO TOCAR LA OPCIÓN EDITAR DE POST_SAVE #####################
            usuario = get_current_user()
            grupo = usuario.grupo_organizacion
            grupo_padre = grupo.get_ancestors()
            filtro = Q(content_type=ContentType.objects.get_for_model(p),
                        object_pk=p.pk)
            UserObjectPermission.objects.filter(filtro).delete()
            GroupObjectPermission.objects.filter(filtro).delete()
            [assign_perm(x + Persona.__name__.lower(), grupo, p) for x in ['view_', 'change_', 'delete_']]
            assign_perm('view_' + Persona.__name__.lower(), grupo_padre, p)
            if str(Group.objects.get(id=grupo.id)) == 'personal-CGE':
                [assign_perm(x + Persona.__name__.lower(), Group.objects.get(name='material-CGE'), p) for x in
                 ['view_']]
            # FIN PROCESO DE ASIGNAR PERMISO EXCEPCIONAL #############################################################
            data['validado'] = True
            data['mensaje'] = 'Datos validados de: ' + p.NombreCompleto()
        if accion == 'validar_local':
            try:
                id_local = request.POST['id_local']
                Local.objects.filter(id=id_local).update(validado=1)
                data['validado'] = True
                local = Local.objects.get(id=id_local)
                data['mensaje'] = 'Datos validados del local: ' + local.nombre
            except:
                data['mensaje'] = 'El local no a sido validado, contactese con el administrador'
        if accion == 'resetear_personal':
            try:
                id_persona = request.POST['id_persona']
                mi_persona = Persona.objects.get(id=id_persona)
                mi_persona.validado = 0
                mi_persona.validado_por = 'Sin confirmar'
                mi_persona.save()

                SubdistritoPersona.objects.filter(persona=mi_persona).delete()

                grupos_para_asignar = Group.objects.filter(
                    Q(gurpo_del_subdistrito__isnull=False) | Q(gurpo_del_distrito__isnull=False) | Q(name='personal-CGE'))

                filters = Q(content_type=ContentType.objects.get_for_model(mi_persona),
                            object_pk=mi_persona.pk)
                UserObjectPermission.objects.filter(filters).delete()
                GroupObjectPermission.objects.filter(filters).delete()
                [assign_perm('change_' + Persona.__name__.lower(), g, mi_persona) for g in grupos_para_asignar]
                data['reseteado'] = True
            except:
                data['mensaje'] = 'La persona no ha sido reseteada al estado no validado'
        return JsonResponse(data, safe=False)
