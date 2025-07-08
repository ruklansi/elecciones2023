from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView


def permission_denied(request, exception):
    context = {}
    messages.error(request, 'No tiene permisos para llevar a cabo esta acción')
    # return render(request, 'errores/403.html', context, status=403)
    return redirect('inicio')


def error_404(request, exception):
    context = {}
    messages.error(request, 'La página que está buscando no se ha encontrado. Es posible que se haya eliminado, haya cambiado su nombre o no esté disponible.')
    return redirect('inicio')


def error_500(request, *args, **argv):
    return render(request, 'AppElecciones/errores/500.html', status=500)

class error_505(TemplateView):
    template_name = "AppElecciones/errores/500.html"

    @classmethod
    def as_error_view(cls):

        v = cls.as_view()
        def view(request):
            r = v(request)
            r.render()
            return r
        return view

# def bad_request(request):
#     context = {}
#     return render(request, 'errores/400.html', context, status=400)

# def server_error(request):
#     context = {}
#     return render(request, 'errores/500.html', context, status=500)
