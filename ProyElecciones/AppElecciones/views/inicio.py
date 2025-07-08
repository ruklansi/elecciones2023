from django.views.generic import TemplateView


class Inicio(TemplateView):
    template_name = 'AppElecciones/inicio/inicio.html'

    def dispatch(self, *args, **kwargs):
        return super(Inicio, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Inicio'
        return context

