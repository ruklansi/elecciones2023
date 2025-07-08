from django.urls import reverse_lazy
from django.views.generic import TemplateView


class Reportes(TemplateView):
    template_name = 'AppElecciones/reportes/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listados y reportes'
        return context
