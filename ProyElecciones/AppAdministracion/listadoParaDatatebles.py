from crum import get_current_user
from django.db.models import Q, F, Value, OuterRef, Subquery,BooleanField
from django.db.models.functions import Concat, Coalesce
from guardian.shortcuts import get_objects_for_user


def listarParaDatatables(modelo=None,ORDENAR_COLUMNAS=None,buscar=None,agregados=None,columnas=None,otros_filtros=None,con_permisos=False,kwargs=None):
    draw = int(kwargs.get('draw', None))
    length = int(kwargs.get('length', None))
    start = int(kwargs.get('start', None))
    search_value = kwargs.get('search[value]', None)
    order_column = kwargs.get('order[0][column]', None)
    order = kwargs.get('order[0][dir]', None)
    order_column = ORDENAR_COLUMNAS[order_column]
    # django orm '-' -> desc
    if order == 'asc':
        order_column = '-' + order_column
    queryset = []
    usuario = get_current_user()

    if con_permisos:
        queryset = get_objects_for_user(usuario, 'view_'+modelo.__name__.lower(), modelo).all()
        sub_editar = get_objects_for_user(usuario, 'change_'+modelo.__name__.lower(), modelo, accept_global_perms=True).filter(id=OuterRef('pk')).annotate(
            edit=Value(True)).values('edit')
        sub_eliminar = get_objects_for_user(usuario, 'delete_'+modelo.__name__.lower(), modelo, accept_global_perms=True).filter(id=OuterRef('pk')).annotate(
            elimin=Value(True)).values('elimin')
        queryset = queryset.annotate(editar=Coalesce(Subquery(sub_editar, output_field=BooleanField()), False),
                                     eliminar=Coalesce(Subquery(sub_eliminar, output_field=BooleanField()), False))
    else:
        queryset=modelo.objects.all()

    total = queryset.count()

    if otros_filtros:
        queryset= queryset.filter(**otros_filtros)

    if search_value:
        filtro={}
        for y in buscar:
            filtro[y+'__icontains']=search_value
        queryset = queryset.filter(
            Q(**filtro,_connector=Q.OR)
        )

    count = queryset.count()

    queryset = queryset.order_by(order_column)[start:start + length]

    if agregados:
        queryset = queryset.annotate(**agregados)

    if columnas:
        data = list(queryset.values(*columnas))
    else:
        data=list(queryset.values())

    return {
        'items': data,
        'count': count,
        'total': total,
        'draw': draw
    }