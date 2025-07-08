from django.contrib import messages
from django.db.models import Value, F, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormGuiaAutoridades
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import GuiaAutoridades, Cargo, Persona, PuestoGuiaAutoridades, DistritoGuia, \
    DistribucionPersonalDistrito


class ListarGuiaDistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id_del_distrito = request.POST['id_del_distrito']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['puesto_texto', 'persona_guia__grado__grado', 'persona_guia__dni', 'persona_guia__nombre',
                      'persona_guia__apellido', 'persona_guia__nro_tel']
            columnas = ('id', 'persona', 'puesto_texto', 'gde_guia', 'tel_guia', 'editar', 'eliminar', 'org_texto')
            agregados = {'persona': Concat(
                F('persona_guia__grado__grado'), Value(' '),
                F('persona_guia__nombre'), Value(' '),
                F('persona_guia__apellido'), Value(' DNI: '),
                F('persona_guia__dni'),
                Value(' Cel: '),
                F('persona_guia__nro_tel'),
                output_field=CharField())
            }
            otros_filtros = {'guia_guia_distrito__dist': id_del_distrito}
            con_permisos = True
            lista_guia_distrito = listarParaDatatables(GuiaAutoridades, ORDENAR_COLUMNAS, buscar, agregados,
                                                       columnas,
                                                       otros_filtros,
                                                       con_permisos, request.POST)
            data = dict()
            data['data'] = lista_guia_distrito['items']
            data['draw'] = lista_guia_distrito['draw']
            data['recordsTotal'] = lista_guia_distrito['total']
            data['recordsFiltered'] = lista_guia_distrito['count']
            # print(data)
            return JsonResponse(data, safe=False)


class CrearGuiaDistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                form = FormGuiaAutoridades(request.POST)
                ########################################################################
                q_guia_organizacion = None
                organizacion = organizacion_del_usuario()['org']
                if organizacion == 'distrito':
                    q_guia_organizacion = GuiaAutoridades.objects.filter(
                        guia_guia_distrito__dist=organizacion_del_usuario()['instancia'])
                q_a_excluir = PuestoGuiaAutoridades.objects.filter(
                    guia__in=list(q_guia_organizacion.values_list('id', flat=True))).values_list('puesto', flat=True)
                form.fields['puesto_guia'].queryset = Cargo.objects.filter(guia=True).exclude(id__in=q_a_excluir).order_by('prioridad')
                ########################################################################
                if form.is_valid():
                    instancia = form.save(commit=False)
                    organizacion = organizacion_del_usuario()['org']
                    ######################
                    integrante = form.cleaned_data.get('persona_guia')
                    if integrante:
                        Persona.objects.filter(id=integrante.id).update(tiene_cargo=True,
                                                                        num_cargos=F('num_cargos') + 1)
                    ######################
                    puestos = form.cleaned_data.get('puesto_guia')
                    instancia.puesto_texto = ', '.join(list(puestos.values_list('cargo', flat=True).distinct()))
                    ##################### Distrito en texto para la guia
                    if organizacion == 'distrito':
                        instancia.org_texto = 'Distrito ' + str(organizacion_del_usuario()['distrito'])
                    ######################
                    instancia.save()
                    ######################M2M a puestos
                    instancia.puesto_guia.set(puestos)
                    ######################
                    if organizacion == 'distrito':
                        dato = DistritoGuia()
                        dato.guia = instancia
                        dato.dist = organizacion_del_usuario()['instancia']
                        dato.save()
                        ######################
                        # Creo una instancia de DistribucionPersonalCdoGrlElect para que se agregue a la estructora de la organización
                        dis_pers = DistribucionPersonalDistrito()
                        dis_pers.integrante = integrante
                        dis_pers.distrito = organizacion_del_usuario()['instancia']
                        dis_pers.cargo = puestos.order_by('prioridad')[0]
                        dis_pers.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Persona registrada'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/distritos/guia/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormGuiaAutoridades()
                ########################################################################
                q_guia_organizacion = None
                organizacion = organizacion_del_usuario()['org']
                if organizacion == 'distrito':
                    q_guia_organizacion = GuiaAutoridades.objects.filter(
                        guia_guia_distrito__dist=organizacion_del_usuario()['instancia'])
                q_a_excluir = PuestoGuiaAutoridades.objects.filter(
                    guia__in=list(q_guia_organizacion.values_list('id', flat=True))).values_list('puesto', flat=True)
                form.fields['puesto_guia'].queryset = Cargo.objects.filter(guia=True).exclude(id__in=q_a_excluir).order_by('prioridad')
                ########################################################################
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/distritos/guia/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class ActualizarGuiaDistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(GuiaAutoridades, pk=kwargs['pk'])
                form = FormGuiaAutoridades(request.POST, instance=instancia)
                ########################################################################
                q_guia_organizacion = None
                organizacion = organizacion_del_usuario()['org']
                q_i = instancia.puesto_guia.all()
                if organizacion == 'distrito':
                    q_guia_organizacion = GuiaAutoridades.objects.filter(
                        guia_guia_distrito__dist=organizacion_del_usuario()['instancia'])
                q_a_excluir = PuestoGuiaAutoridades.objects.filter(
                    guia__in=list(q_guia_organizacion.values_list('id', flat=True))).values_list('puesto',
                                                                                                 flat=True).exclude(
                    puesto__in=q_i).values_list('puesto', flat=True)
                form.fields['puesto_guia'].queryset = Cargo.objects.filter(guia=True).exclude(id__in=q_a_excluir).order_by('prioridad')
                ########################################################################
                if form.is_valid():
                    instancia = form.save(commit=False)
                    # ######################
                    puestos = form.cleaned_data.get('puesto_guia')
                    instancia.puesto_texto = ', '.join(list(puestos.values_list('cargo', flat=True).distinct()))
                    instancia.save()
                    ######################M2M a puestos
                    PuestoGuiaAutoridades.objects.filter(guia=instancia).delete()
                    instancia.puesto_guia.set(puestos)
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Persona registrada'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'editar'}
                data['html_form'] = render_to_string('AppElecciones/distritos/guia/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                instancia = get_object_or_404(GuiaAutoridades, pk=kwargs['pk'])
                form = FormGuiaAutoridades(instance=instancia)
                ########################################################################
                q_guia_organizacion = None
                organizacion = organizacion_del_usuario()['org']
                q_i = instancia.puesto_guia.all()
                if organizacion == 'distrito':
                    q_guia_organizacion = GuiaAutoridades.objects.filter(
                        guia_guia_distrito__dist=organizacion_del_usuario()['instancia'])
                q_a_excluir = PuestoGuiaAutoridades.objects.filter(
                    guia__in=list(q_guia_organizacion.values_list('id', flat=True))).values_list('puesto',
                                                                                                 flat=True).exclude(
                    puesto__in=q_i).values_list('puesto', flat=True)
                form.fields['puesto_guia'].queryset = Cargo.objects.filter(guia=True).exclude(id__in=q_a_excluir).order_by('prioridad')
                ########################################################################
                context = {'form': form, 'accion': 'editar'}
                data['html_form'] = render_to_string('AppElecciones/distritos/guia/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class EliminarGuiaDistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            GuiaAutoridades, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                ###############################---->Reseteo las banderas de la persona
                Persona.objects.filter(id=instancia.persona_guia.id).update(
                    tiene_cargo=False, num_cargos=0)
                ###############################---->Borro los datos M2M
                PuestoGuiaAutoridades.objects.filter(guia=instancia).delete()
                ###############################---->Borro los datos de la relación de la guía y el Distrito
                DistritoGuia.objects.filter(guia=instancia).delete()
                ###############################---->Borro la persona de la organización del Distrito
                DistribucionPersonalDistrito.objects.filter(integrante=instancia.persona_guia.id).delete()
                ###############################---->Borro la instancia
                instancia.delete()
                data['permitido'] = True
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')
