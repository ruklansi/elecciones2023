from .middleware import RequestMiddleware
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps

#https://medium.com/@dbsiavichay/como-crear-registros-de-auditoria-para-tu-proyecto-en-django-usando-el-admin-log-d3e1bf375ff4

@receiver(post_save)
def audit_log(sender, instance, created, raw, update_fields, **kwargs):

    # Lista de los modelos que se requienran que escuche
    # list_dimae = [z.__name__ for z in apps.get_app_config('AppAdministracion').get_models()]
    # list_of_models =  [z.__name__ for z in apps.get_app_config('appNovedades').get_models()] + list_dimae
    # list_elecciones = [z.__name__ for z in apps.get_app_config('AppElecciones').get_models()]
    list_of_models = [z.__name__ for z in apps.get_app_config('AppAdministracion').get_models()]
    if sender.__name__ not in list_of_models:
        return
    user = get_user()
    if created:
        if user:
            if not user.is_staff:
                instance.save_addition(user)
    elif not raw:
        if user:
            if not user.is_staff:
                instance.save_edition(user)


@receiver(post_delete)
def audit_delete_log(sender, instance, **kwargs):
    # Lista de los modelos que se requienran que escuche
    # list_dimae = [z.__name__ for z in apps.get_app_config('appDimae').get_models()]
    # list_of_models = [z.__name__ for z in apps.get_app_config('appNovedades').get_models()] + list_dimae
    list_of_models = [z.__name__ for z in apps.get_app_config('AppAdministracion').get_models()]

    if sender.__name__ not in list_of_models:
        return
    user = get_user()
    if not user.is_staff:
        instance.save_deletion(user)


def get_user():
    thread_local = RequestMiddleware.thread_local
    user = None
    if hasattr(thread_local, 'user'):
        if thread_local.user.is_active:
            user = thread_local.user
    else:
        user = None
    return user

