from crum import get_current_user
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from guardian.shortcuts import get_objects_for_user
from model_utils import Choices
from AppAdministracion.models import CamposEnMayusculas
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Distrito, Fuerza, Subdistrito, Seccion, Circuito, Persona, Grado, SubdistritoPersona
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from AppElecciones.forms import FormPersona, FormBuscarPersona
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import View
from django.db.models import ProtectedError, F, Value, Case, When, Func, CharField
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from guardian.mixins import PermissionRequiredMixin as guardianPermisos


class ListadoPersonalValidado(PermisoDesdeDjango, ListView):
    model = Persona
    template_name = "AppElecciones/personas/listado.html"
    permission_required = 'AppElecciones.view_persona'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            puesto = request.POST.get('puesto', None)
            fuerza = request.POST.get('fuerza', None)

            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'), ('2', 'apellido'), ('3', 'dni'))
            buscar = ['nombre', 'apellido',  'dni', 'validado_por' ]
            columnas = ('id', 'distrito__distrito', 'grado__grado', 'nombre', 'apellido', 'fuerza__fuerza', 'puesto', 'dni', 'es_conductor',
                        'tiene_cargo', 'editar', 'eliminar', 'validado_por')
            cge_url = reverse_lazy('detalles-cdogrlelect', args=[64])
            distrito_url = reverse_lazy('detalles-distito', args=[32])
            subdis_url = reverse_lazy('detalles-subdistito', args=[32])
            sec_url = reverse_lazy('detalles-seccion', args=[32])
            local_url = reverse_lazy('detalles-local', args=[32])
            agregados = {'puesto': Case(
                # Aca pongo código duro en el id del anchor en 1 porque se que es un singleton CdoGrlElect
                When(persona_guia__isnull=False,
                     then=Concat(
                                 Value(''),
                                 F('persona_guia__puesto_texto'),
                                 output_field=CamposEnMayusculas())),
                When(cge_persona__isnull=False,
                     then=Concat(Value('<a href="' + cge_url[:-2]), F('cge_persona__cge__id'), Value('">'),
                                 F('cge_persona__cargo__cargo'),
                                 Value(' '),
                                 F('cge_persona__designacion'),
                                 Value(' CGE '),
                                 Value('</a>'), output_field=CamposEnMayusculas())),
                When(reserva_cge_persona__isnull=False,
                     then=Concat(Value('<a href="' + cge_url[:-2]), F('reserva_cge_persona__cge__id'), Value('">'),
                                 Value('Reserva CGE '),
                                 Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(distrito_persona__isnull=False,
                     then=Concat(Value('<a href="' + distrito_url[:-2]), F('distrito_persona__distrito__id'),
                                 Value('">'),
                                 F('distrito_persona__cargo__cargo'),
                                 Value(' '),
                                 F('distrito_persona__designacion'),
                                 Value(' Distrito '),
                                 F('distrito_persona__distrito__distrito'),
                                 Value('</a>'), output_field=CamposEnMayusculas())),
                When(res_dis_personal__isnull=False,
                     then=Concat(Value('<a href="' + distrito_url[:-2]), F('res_dis_personal__distrito__id'),
                                 Value('">'),
                                 Value('Reserva Distrito '),
                                 F('res_dis_personal__distrito__distrito'),
                                 Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(sub_personal__isnull=False,
                     then=Concat(Value('<a href="' + subdis_url[:-2]), F('sub_personal__subdistrito__id'),
                                 Value('">'), F('sub_personal__cargo__cargo'),
                                 Value(' '),
                                 F('sub_personal__designacion'),
                                 Value(' Subdistrito '),
                                 F('sub_personal__subdistrito__subdistrito'), Value(' Distrito '),
                                 F('sub_personal__subdistrito__distrito__distrito'), Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(res_sub_personal__isnull=False,
                     then=Concat(Value('<a href="' + subdis_url[:-2]), F('res_sub_personal__subdistrito__id'),
                                 Value('">'), Value('Reserva Subdistrito '),
                                 F('res_sub_personal__subdistrito__subdistrito'),
                                 Value(' Distrito '),
                                 F('res_sub_personal__subdistrito__distrito__distrito'), Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(sec_personal__isnull=False,
                     then=Concat(Value('<a href="' + sec_url[:-2]), F('sec_personal__seccion__id'),
                                 Value('">'), F('sec_personal__cargo__cargo'), Value(' Sección '),
                                 F('sec_personal__seccion__seccion'),
                                 Value(' Distrito '),
                                 F('sec_personal__seccion__distrito__distrito'), Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(jefe_local__isnull=False,
                     then=Concat(Value('<a href="' + local_url[:-2]), F('jefe_local__local__id'),
                                 Value('">'), Value('Jefe local '), F('jefe_local__local__nombre'), Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                When(aux_local__isnull=False,
                     then=Concat(Value('<a href="' + local_url[:-2]), F('aux_local__seg_interna_local__local__id'),
                                 Value('">'), Value('Aux Local '), F('aux_local__seg_interna_local__local__nombre'),
                                 Value('</a>'),
                                 output_field=CamposEnMayusculas())),
                default=Value('Sin puesto')),

            }

            otros_filtros = {'validado': 1}
            if fuerza != '':
                otros_filtros['fuerza'] = fuerza
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            if puesto != '':
                if puesto == 'conpuesto':
                    otros_filtros['tiene_cargo'] = True
                if puesto == 'sinpuesto':
                    otros_filtros['tiene_cargo'] = False
                if puesto == 'conductor':
                    otros_filtros['es_conductor'] = True

            con_permisos = True

            personas = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                            con_permisos, request.POST)
            result = dict()
            # result['pepe'] = personas['dni_no_encontrado']
            result['data'] = personas['items']
            result['draw'] = personas['draw']
            result['recordsTotal'] = personas['total']
            result['recordsFiltered'] = personas['count']
            #print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Personal validado'
        context['listado_url'] = reverse_lazy('listado-de-personas')
        context['crear_url'] = reverse_lazy('crear-persona')
        context['buscar_persona'] = FormBuscarPersona()
        return context


class ListadoPersonalNoValidado(PermisoDesdeDjango, ListView):
    model = Persona
    template_name = "AppElecciones/personas/listado_novalidado.html"
    permission_required = 'AppElecciones.ver_personas_no_validados_persona'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            fuerza = request.POST.get('fuerza', None)
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'), ('2', 'apellido'), ('3', 'dni'))
            buscar = ['grado__grado', 'nombre', 'apellido', 'fuerza__fuerza', 'dni', 'nro_tel']
            columnas = ('id', 'grado__grado', 'nombre', 'apellido', 'fuerza__fuerza', 'dni', 'nro_tel')
            agregados = None
            otros_filtros = {'validado': 0}
            if fuerza != '':
                otros_filtros['fuerza'] = fuerza
            con_permisos = False
            personas = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                            con_permisos, request.POST)
            result = dict()
            result['data'] = personas['items']
            result['draw'] = personas['draw']
            result['recordsTotal'] = personas['total']
            result['recordsFiltered'] = personas['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Personal no validado'
        context['listado_url'] = reverse_lazy('listado-de-personas')
        context['crear_url'] = reverse_lazy('crear-persona')
        context['buscar_persona'] = FormBuscarPersona()
        return context


class CrearPersona(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Persona
    form_class = FormPersona
    template_name = 'AppElecciones/personas/crear.html'
    success_message = 'Persona agregada'
    permission_required = 'AppElecciones.add_persona'
    raise_exception = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            instancia = form.save(commit=False)
            org_user = organizacion_del_usuario()
            if org_user['org'] == 'distrito':
                instancia.distrito = org_user['instancia']
                texto = 'Confirmado en ' + org_user['distrito']
            elif org_user['org'] == 'subdistrito':
                instancia.distrito = org_user['sub_instancia']
                texto = 'Confirmado en Subdistrito' + org_user['subdistrito'] + ' de ' + org_user['distrito']
            elif org_user['org'] == 'Personal':
                texto = 'Confirmado en  CGE'
            else:
                texto = 'Sin Confirmar'
            instancia.validado_por = texto
            instancia.save()

            if org_user['org'] == 'subdistrito':
                SubdistritoPersona.objects.create(persona=instancia, subdistrito=org_user['instancia'])
            super(CrearPersona, self).form_valid(form)
            return HttpResponseRedirect(self.get_success_url())

        self.object = None
        # Return class-based view form_invalid to generate form with errors
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('listado-de-personas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar personal'
        return context


class ActualizarPersona(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = Persona
    form_class = FormPersona
    template_name = 'AppElecciones/personas/crear.html'
    success_message = 'Persona actualizada'
    permission_required = 'AppElecciones.change_persona'
    raise_exception = True
    accept_global_perms = False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        org_user = organizacion_del_usuario()
        if org_user['org'] == 'distrito':
            self.object.distrito = org_user['instancia']
            texto = 'Confirmado en ' + org_user['distrito']
        elif org_user['org'] == 'subdistrito':
            self.object.distrito = org_user['sub_instancia']
            texto = 'Confirmado en Subdistrito' + org_user['subdistrito'] + ' de ' + org_user['distrito']
        elif org_user['org'] == 'Personal':
            texto = 'Confirmado en  CGE'
        else:
            texto = 'Sin Confirmar'
        self.object.validado_por = texto
        self.object.validado = 1
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('listado-de-personas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Persona'
        return context


class EliminarPersona(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = Persona
    template_name = 'AppElecciones/personas/eliminar.html'
    success_url = reverse_lazy('listado-de-personas')
    permission_required = 'AppElecciones.delete_persona'
    raise_exception = True
    accept_global_perms = False

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            # Este if lo puse porque el auxiliar tiene una relacion muchos a muchos y porque no se puede usar PROTECT en esa relacion
            if not self.object.tiene_cargo:
                SubdistritoPersona.objects.filter(persona=self.object).delete()
                self.object.delete()
                messages.success(
                    # self.request, (str(self.object) + " eliminado"))
                    self.request, "Persona eliminada")
            else:
                messages.success(self.request, ("Imposible eliminar al " +
                                                str(self.object) + " porque ha sido asignado en un puesto. Elimínelo del mismo primero para borrarlos definitivamente."))
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            messages.success(self.request, ("Imposible eliminar al " +
                                            str(self.object) + " porque ha sido asignado a un puesto. Elimínilo de ese puesto primero para borrarlos definitivamente."))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Persona'
        return context


class DetallePersona(DetailView):
    model = Persona
    template_name = 'AppElecciones/personas/detalles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Datos del '
        return context


class FiltrosParaPersonasAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        resultado = dict()
        accion = (request.POST['accion'])
        if accion == 'cargar-distritos':
            data = []
            # usuario = request.user
            # for i in get_objects_for_user(usuario, 'view_distrito', Distrito).all().order_by('distrito'):
            for i in Distrito.objects.all().order_by('distrito'):
                if i.distrito != '--':
                    data.append({'id': i.id, 'distrito': i.distrito})
            resultado['datos'] = data
            resultado['hay_distritos'] = True
        if accion == 'cargar-fuerzas-pers-no-validado':
            data = []
            for f in Fuerza.objects.all().order_by('fuerza'):
                data.append({'id': f.id, 'fuerza': f.fuerza})
            resultado['datos'] = data
            resultado['hay_fuerza'] = True
        if accion == 'cargar-fuerzas-pers-validado':
            data = []
            usuario = get_current_user()
            query = get_objects_for_user(usuario, 'view_persona', Persona, accept_global_perms=False).values('id')
            for f in Fuerza.objects.filter(fuerza_a_la_que_pertenece__in=query).order_by('fuerza').distinct():
                data.append({'id': f.id, 'fuerza': f.fuerza})
            resultado['datos'] = data
            resultado['hay_fuerza'] = True
        if accion == 'filtrar-subdistritos':
            sub = Subdistrito.objects.filter(distrito_id=request.POST['id'])
            if sub:
                data = []
                for s in Subdistrito.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': s.id, 'subdistrito': s.subdistrito})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = True
            elif not sub:
                data = []
                for t in Seccion.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': t.id, 'seccion': t.seccion})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = False
        if accion == 'filtrar-seccion':
            data = []
            # aca el id es un subdistrito
            for s in Seccion.objects.filter(subdistrito_id=request.POST['id']):
                data.append({'id': s.id, 'seccion': s.seccion})
            resultado['datos'] = data
            resultado['hay_seccion'] = True
        if accion == 'filtrar-circuito':
            data = []
            for c in Circuito.objects.filter(seccion_id=request.POST['id']):
                data.append({'id': c.id, 'circuito': c.circuito})
            resultado['datos'] = data
            resultado['hay_circuito'] = True
        return JsonResponse(resultado, safe=False)


class ListarFuerzaAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            accion = (request.POST['accion'])
            if accion == 'cargar-grado':
                if request.is_ajax():
                    datos = list(
                        Grado.objects.filter(fuerza=request.POST['id']).order_by('grado').values('id', 'grado'))
        return JsonResponse(datos, safe=False)


class ResumenDePersonalAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.method == 'POST':
            if request.is_ajax():
                # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset

                # https://riptutorial.com/django/example/19739/count-the-number-of-foreign-relations

                total_general = Persona.objects.count()
                data['total_general'] = total_general
                total_general_con_puesto = Persona.objects.filter(
                    tiene_cargo=False).count()
                data['total_general_con_puesto'] = total_general_con_puesto
                total_general_sin_puesto = Persona.objects.filter(
                    tiene_cargo=True).count()
                data['total_general_sin_puesto'] = total_general_sin_puesto
                return JsonResponse(data, safe=False)


class DetallePersonaComoConductor(DetailView):
    model = Persona
    template_name = 'AppElecciones/personas/detalle.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                resultado = dict()
                # Evalúo si se lo empleo en el CGE
                cge_veh_propio = self.model.objects.filter(id=instancia.id, veh_pro_cge_persona__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_pro_cge_persona__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_pro_cge_persona__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_pro_cge_persona__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_pro_cge_persona__tareas'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona', flat=True).first()
                try:
                    datos_cge_veh_p = list(cge_veh_propio)
                except:
                    datos_cge_veh_p = []
                cge_veh_contratado = self.model.objects.filter(id=instancia.id, veh_con_cge_persona__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_con_cge_persona__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_pro_cge_persona__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_con_cge_persona__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_con_cge_persona__tareas'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona', flat=True).first()
                try:
                    datos_cge_veh_c = list(cge_veh_contratado)
                except:
                    datos_cge_veh_c = []

                # Evalúo si se lo empleo en el Distrito
                distrito_veh_propio = self.model.objects.filter(id=instancia.id, veh_pro_dis_persona__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_pro_dis_persona__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_pro_dis_persona__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(
                                                      F('veh_pro_dis_persona__hasta'),
                                                      Value('dd/MM/yyyy'),
                                                      function='to_char',
                                                      output_field=CharField()
                                                  ),
                                                  Value(' Tarea: '),
                                                  F('veh_pro_dis_persona__tareas__tareas'),
                                                  Value(' Distrito: '),
                                                  F('veh_pro_dis_persona__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_distrito_veh_p = list(distrito_veh_propio)
                except:
                    datos_distrito_veh_p = []
                distrito_veh_contratado = self.model.objects.filter(id=instancia.id,
                                                                    veh_con_dis_personal__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_con_dis_personal__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_con_dis_personal__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(
                                                      F('veh_con_dis_personal__hasta'),
                                                      Value('dd/MM/yyyy'),
                                                      function='to_char',
                                                      output_field=CharField()
                                                  ),
                                                  Value(' Tarea: '),
                                                  F('veh_con_dis_personal__tareas__tareas'),
                                                  Value(' Distrito: '),
                                                  F('veh_con_dis_personal__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_distrito_veh_c = list(distrito_veh_contratado)
                except:
                    datos_distrito_veh_c = []

                # Evalúo si se lo empleo en el Distrito
                subdistrito_veh_propio = self.model.objects.filter(id=instancia.id, veh_pro_sub_persona__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_pro_sub_persona__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_pro_sub_persona__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_pro_sub_persona__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_pro_sub_persona__tareas__tareas'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_pro_sub_persona__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_pro_sub_persona__subdistrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_subdistrito_veh_p = list(subdistrito_veh_propio)
                except:
                    datos_subdistrito_veh_p = []

                subdistrito_veh_contratado = self.model.objects.filter(id=instancia.id,
                                                                       veh_con_sub_personal__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_con_sub_personal__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_con_sub_personal__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_con_sub_personal__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_con_sub_personal__tareas__tareas'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_con_sub_personal__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_con_sub_personal__subdistrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_subdistrito_veh_c = list(subdistrito_veh_contratado)
                except:
                    datos_subdistrito_veh_c = []

                seccion_veh_propio = self.model.objects.filter(id=instancia.id, veh_prop_personal_sec__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_prop_personal_sec__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_prop_personal_sec__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_prop_personal_sec__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_prop_personal_sec__tareas__tareas'),
                                                  Value(' Sección: '),
                                                  F('veh_prop_personal_sec__seccion__seccion'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_prop_personal_sec__seccion__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_prop_personal_sec__seccion__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_seccion_veh_p = list(seccion_veh_propio)
                except:
                    datos_seccion_veh_p = []

                seccion_veh_contratado = self.model.objects.filter(id=instancia.id,
                                                                   veh_cont_personal_sec__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_cont_personal_sec__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_cont_personal_sec__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_cont_personal_sec__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_cont_personal_sec__tareas__tareas'),
                                                  Value(' Sección: '),
                                                  F('veh_cont_personal_sec__seccion__seccion'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_cont_personal_sec__seccion__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_cont_personal_sec__seccion__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_seccion_veh_c = list(seccion_veh_contratado)
                except:
                    datos_seccion_veh_c = []

                context = {'persona': {'grado': instancia.grado.grado,
                                       'nombre': instancia.nombre,
                                       'apellido': instancia.apellido,
                                       'dni': instancia.dni,
                                       'fuerza': instancia.fuerza.fuerza,
                                       'cge_veh_propio': datos_cge_veh_p,
                                       'cge_veh_contratado': datos_cge_veh_c,
                                       'distrito_veh_propio': datos_distrito_veh_p,
                                       'distrito_veh_contratado': datos_distrito_veh_c,
                                       'subdistrito_veh_propio': datos_subdistrito_veh_p,
                                       'subdistrito_veh_contratado': datos_subdistrito_veh_c,
                                       'seccion_veh_propio': datos_seccion_veh_p,
                                       'seccion_veh_contratado': datos_seccion_veh_c,
                                       }}
                resultado['resultado'] = render_to_string('AppElecciones/personas/detalle.html',
                                                          context, request=request)
                return JsonResponse(resultado, safe=False)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')
