from crum import get_current_user
from django import template

from AppElecciones.funciones_comunes import organizacion_del_usuario

register = template.Library()


@register.filter('tiene_subdistrito')
def tiene_subdistrito(usuario):
    dato = organizacion_del_usuario(usuario)['tiene_subdistrito']
    if dato == 'si':
        return True
    if dato == 'no':
        return False

# <!--        (1, 'adminsistema'),-->
# <!--        (2, 'cge'),-->
# <!--        (3, 'distrito'),-->
# <!--        (4, 'subdistrito'),-->
# <!--        (5, 'seccion'),-->
# <!--        (6, 'circuito'),-->
# <!--        (7, 'personal'),-->
# <!--        (8, 'logistica'),-->
# <!--        (9, 'personal-CGE'),-->
# <!--        (10, 'material-CGE'),-->
# <!--        (100, 'sin rol'),-->
# @register.simple_tag
# def rol():
@register.filter('rol')
def rol(usuario):
   if get_current_user().rol == 1:
        return 'Administrador'
   if get_current_user().rol == 2:
        return 'Lector CGE'
   elif get_current_user().rol == 3:
        return 'Distrito ' + organizacion_del_usuario()['distrito']
   elif get_current_user().rol == 4:
        return 'Subdistrito '+ organizacion_del_usuario()['subdistrito'] + ' ' + organizacion_del_usuario()['distrito']
   elif get_current_user().rol == 9:
        return 'Personal CGE'
   elif get_current_user().rol == 10:
        return 'Material CGE'
