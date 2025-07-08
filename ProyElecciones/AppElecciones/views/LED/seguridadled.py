from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormSegLedFFAA, FormSegLedFFSeguridad
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import SegEnLedFuerzaSeguridad, SegEnLedFuerzaArmada, Fuerza, Led, FuerzaSeguridad


# De aca en adelante el CRUD de Fuerzas Armadas en los led

class ListarSegLedFFAAAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id_del_led = request.POST['id_led']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['fecha_inicio', 'fecha_fin', 'fuerza_armada__fuerza', 'cant_personal']
            columnas = ('id', 'fecha_inicio', 'fecha_fin', 'fuerza_armada__fuerza', 'cant_personal', 'eliminar')
            agregados = None
            otros_filtros = {'led': id_del_led}
            con_permisos = True
            lista_seg_led_ffaa = listarParaDatatables(SegEnLedFuerzaArmada, ORDENAR_COLUMNAS, buscar, agregados,
                                                      columnas,
                                                      otros_filtros,
                                                      con_permisos, request.POST)
            data = dict()
            data['data'] = lista_seg_led_ffaa['items']
            data['draw'] = lista_seg_led_ffaa['draw']
            data['recordsTotal'] = lista_seg_led_ffaa['total']
            data['recordsFiltered'] = lista_seg_led_ffaa['count']
            # print(data)
            return JsonResponse(data, safe=False)


class CrearSegLedFFAA(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *arg, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                id_led = request.POST['id_led']
                form = FormSegLedFFAA(request.POST)

                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_armada'].queryset = Fuerza.objects.exclude(
                    id__in=[x.fuerza_armada.id for x in SegEnLedFuerzaArmada.objects.filter(led=id_led)])
                if form.is_valid():
                    instancia = form.save(commit=False)
                    led_ = Led.objects.get(id=id_led)
                    instancia.led = led_
                    instancia.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
        else:
            if request.is_ajax():
                # https://docs.djangoproject.com/en/3.0/ref/models/querysets
                id_led = request.GET['id_led']
                form = FormSegLedFFAA(request.GET)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar

                form.fields['fuerza_armada'].queryset = Fuerza.objects.exclude(
                    id__in=[x.fuerza_armada.id for x in SegEnLedFuerzaArmada.objects.filter(led=id_led)])
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffaa/crear.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                id_led = request.GET['id_led']
                form = FormSegLedFFAA()
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_armada'].queryset = Fuerza.objects.exclude(
                    id__in=[x.fuerza_armada.id for x in SegEnLedFuerzaArmada.objects.filter(led=id_led)])
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffaa/crear.html', context, request=request)
        return JsonResponse(data)


class ActualizarSegLedFFAA(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(
                    SegEnLedFuerzaArmada, pk=kwargs['pk'])
                form = FormSegLedFFAA(
                    request.POST, instance=instancia)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_armada'].queryset = Fuerza.objects.exclude(
                    id__in=[x.fuerza_armada.id for x in SegEnLedFuerzaArmada.objects.filter(led=instancia.id)])
                if form.is_valid():
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                    context = {'form': form}
                    data['html_form'] = render_to_string(
                        'AppElecciones/LED/segledffaa/actualizar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            SegEnLedFuerzaArmada, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormSegLedFFAA(instance=instancia)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_armada'].queryset = Fuerza.objects.exclude(
                    id__in=[x.fuerza_armada.id for x in SegEnLedFuerzaArmada.objects.filter(led=instancia.id)])
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffaa/actualizar.html', context, request=request)
        return JsonResponse(data)


class EliminarSegLedFFAA(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            SegEnLedFuerzaArmada, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)


# De aca en adelante el CRUD de Fuerzas de Seguridad en los led


class ListarSegLedFFSegAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id_del_led = request.POST['id_led']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['fecha_inicio', 'fecha_fin', 'fuerza_seguridad__fuerza_seg', 'cant_personal']
            columnas = ('id', 'fecha_inicio', 'fecha_fin', 'fuerza_seguridad__fuerza_seg', 'cant_personal', 'eliminar')
            agregados = None
            otros_filtros = {'led': id_del_led}
            con_permisos = True
            lista_seg_led_ffseg = listarParaDatatables(SegEnLedFuerzaSeguridad, ORDENAR_COLUMNAS, buscar, agregados,
                                                       columnas,
                                                       otros_filtros,
                                                       con_permisos, request.POST)

            data = dict()
            data['data'] = lista_seg_led_ffseg['items']
            data['draw'] = lista_seg_led_ffseg['draw']
            data['recordsTotal'] = lista_seg_led_ffseg['total']
            data['recordsFiltered'] = lista_seg_led_ffseg['count']
            # print(data)
            return JsonResponse(data, safe=False)


class CrearSegLedFFSeg(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *arg, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_led = request.POST['id_led']

            if request.is_ajax():
                form = FormSegLedFFSeguridad(request.POST)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_seguridad'].queryset = FuerzaSeguridad.objects.exclude(
                    id__in=[x.fuerza_seguridad.id for x in SegEnLedFuerzaSeguridad.objects.filter(led=id_led)])
                if form.is_valid():
                    instancia = form.save(commit=False)
                    led_ = Led.objects.get(id=id_led)
                    instancia.led = led_
                    instancia.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffseg/crear.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                id_led = request.GET['id_led']
                form = FormSegLedFFSeguridad()
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_seguridad'].queryset = FuerzaSeguridad.objects.exclude(
                    id__in=[x.fuerza_seguridad.id for x in SegEnLedFuerzaSeguridad.objects.filter(led=id_led)])
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffseg/crear.html', context, request=request)
        return JsonResponse(data)


class ActualizarSegLedFFSeg(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(
                    SegEnLedFuerzaSeguridad, pk=kwargs['pk'])
                form = FormSegLedFFSeguridad(
                    request.POST, instance=instancia)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_seguridad'].queryset = FuerzaSeguridad.objects.exclude(
                    id__in=[x.fuerza_seguridad.id for x in SegEnLedFuerzaSeguridad.objects.filter(led=instancia.id)])
                if form.is_valid():
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                    context = {'form': form}
                    data['html_form'] = render_to_string(
                        'AppElecciones/LED/segledffseg/actualizar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            SegEnLedFuerzaSeguridad, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormSegLedFFSeguridad(instance=instancia)
                # Hay que sobreescribir este queryset del horario aca si o si para que en el select solo se muestren los horarios que faltan cargar
                form.fields['fuerza_seguridad'].queryset = FuerzaSeguridad.objects.exclude(
                    id__in=[x.fuerza_seguridad.id for x in SegEnLedFuerzaSeguridad.objects.filter(led=instancia.id)])
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/LED/segledffseg/actualizar.html', context, request=request)
        return JsonResponse(data)


class EliminarSegLedFFSeg(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            SegEnLedFuerzaSeguridad, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)
