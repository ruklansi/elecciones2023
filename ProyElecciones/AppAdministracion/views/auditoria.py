# from django.contrib.admin.models import LogEntry
from auditlog.models import LogEntry
from django.http import JsonResponse
from django.views.generic import ListView
from model_utils import Choices
from AppAdministracion.listadoParaDatatebles import listarParaDatatables
from django.utils import timezone
from AppAdministracion.forms import BuscarForm
from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango


class ListadoAuditorias(PermisoDesdeDjango, ListView):
    model = LogEntry
    template_name = "AppAdministracion/auditoria/listadoAuditoria.html"
    permission_required = 'AppAdministracion.view_usuario'
    raise_exception = True
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            fecha_inicio=timezone.make_aware(datetime.strptime(request.POST.get('fecha_inicio',''), '%Y-%m-%d %H:%M:%S'))
            fecha_fin = timezone.make_aware(datetime.strptime(request.POST.get('fecha_fin',''), '%Y-%m-%d %H:%M:%S'))
            ORDENAR_COLUMNAS = Choices(('0', 'timestamp'))
            buscar = ['timestamp','actor_id__first_name', 'actor_id__last_name', 'content_type__model','action', 'object_repr', 'changes']
            columnas = ('id', 'timestamp','actor_id__first_name', 'actor_id__last_name', 'content_type__model','action', 'object_repr', 'changes')
            agregados = None
            otros_filtros={'timestamp__range':[fecha_inicio, fecha_fin]}
            con_permisos=False
            auditoria = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar,agregados,columnas,otros_filtros, con_permisos, request.POST)
            resultado = dict()
            resultado['data'] = auditoria['items']
            resultado['draw'] = auditoria['draw']
            resultado['recordsTotal'] = auditoria['total']
            resultado['recordsFiltered'] = auditoria['count']
        return JsonResponse(resultado, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rango'] = BuscarForm()
        context['titulo'] = 'Detalle de las actividades del usuario en el sistema'
        return context