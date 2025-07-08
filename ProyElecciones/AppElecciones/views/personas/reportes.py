import io
import os

import xlsxwriter
from crum import get_current_user
from django.contrib import messages
from django.db.models import Case, When, Value, F
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views import View
from guardian.shortcuts import get_objects_for_user
from xhtml2pdf import pisa

from AppElecciones.Reportes.Personas.exportarPersonas import PersonaRecurso
from AppElecciones.models import Persona, Fuerza, Jerarquia, CamposEnMayusculas, exportarpersonal
from ProyElecciones import settings


def get_simple_table_data():
    # Simulate a more complex table read.

    lista_fuerza = Fuerza.objects.all().order_by('orden')
    lista_jer = Jerarquia.objects.all().order_by('orden')
    lista_total = [['JERARQUIA'] + list(lista_fuerza.values_list('fuerza', flat=True)) + ['TOTAL', 'PORCENTAJE']]
    cant_fuerza = {}

    for j in lista_jer:
        lista_j = [j.jerarquia]
        cant_j = 0
        for f in lista_fuerza:
            cant = get_objects_for_user(get_current_user(),'view_persona',Persona,accept_global_perms=False).filter(grado__jerarquia=j, fuerza=f,validado=1,tiene_cargo=True).count()
            if f.id in cant_fuerza.keys():
                cant_fuerza[f.id] += cant
            else:
                cant_fuerza[f.id] = cant
            lista_j.append(cant)
            cant_j += cant
        lista_j.append(cant_j)
        total = sum(cant_fuerza.values())
        total_t = Persona.objects.filter(validado=1,tiene_cargo=True).count()
        lista_j.append("{:.2f}%".format(cant_j / total_t * 100))
        lista_total.append(lista_j)

    lista_total.append(['TOTAL'] + list(cant_fuerza.values()) + [total_t])
    lista_total.append(['PORCENTAJE'] + ["{:.2f}%".format(x / total_t * 100) for x in cant_fuerza.values()])
    return lista_total

def exportarPersonas(request):
    persona_recurso = PersonaRecurso()

    usuario = request.user
    persona_permiso = get_objects_for_user(usuario, 'view_persona', Persona, accept_global_perms=False).values('id')
    queryset = exportarpersonal.objects.filter(id__in=persona_permiso)
    # queryset = queryset_.annotate(puesto=Case(
    #     When(cge_persona__isnull=False,
    #          then=Concat(F('cge_persona__cargo__cargo'),
    #                      Value(' '),
    #                      F('cge_persona__designacion'),
    #                      Value(' CGE '),
    #                      output_field=CamposEnMayusculas())),
    #     When(reserva_cge_persona__isnull=False,
    #          then=Concat(Value('Reserva CGE '),
    #                      Value(' '),
    #                      output_field=CamposEnMayusculas())),
    #     When(distrito_persona__isnull=False,
    #          then=Concat(F('distrito_persona__cargo__cargo'),
    #                      Value(' '),
    #                      F('distrito_persona__designacion'),
    #                      Value(' Distrito '),
    #                      F('distrito_persona__distrito__distrito'),
    #                      output_field=CamposEnMayusculas())),
    #     When(res_dis_personal__isnull=False,
    #          then=Concat(Value('Reserva Distrito '),
    #                      F('res_dis_personal__distrito__distrito'),
    #                      output_field=CamposEnMayusculas())),
    #     When(sub_personal__isnull=False,
    #          then=Concat(F('sub_personal__cargo__cargo'),
    #                      Value(' '),
    #                      F('sub_personal__designacion'),
    #                      Value(' Subdistrito '),
    #                      F('sub_personal__subdistrito__subdistrito'), Value(' Distrito '),
    #                      F('sub_personal__subdistrito__distrito__distrito'),
    #                      output_field=CamposEnMayusculas())),
    #     When(res_sub_personal__isnull=False,
    #          then=Concat(Value('Reserva Subdistrito '),
    #                      F('res_sub_personal__subdistrito__subdistrito'),
    #                      Value(' Distrito '),
    #                      F('res_sub_personal__subdistrito__distrito__distrito'),
    #                      output_field=CamposEnMayusculas())),
    #     When(sec_personal__isnull=False,
    #          then=Concat(F('sec_personal__cargo__cargo'), Value(' Sección '),
    #                      F('sec_personal__seccion__seccion'),
    #                      Value(' Distrito '),
    #                      F('sec_personal__seccion__distrito__distrito'),
    #                      output_field=CamposEnMayusculas())),
    #     When(jefe_local__isnull=False,
    #          then=Concat(Value('Jefe local '),
    #                      F('jefe_local__local__nombre'),
    #                      output_field=CamposEnMayusculas())),
    #     When(aux_local__isnull=False,
    #          then=Concat(Value('Aux Local '), F('aux_local__seg_interna_local__local__nombre'),
    #                      output_field=CamposEnMayusculas())),
    #     default=Value('Sin puesto'))).annotate(dis_cge=Case(
    #     When(cge_persona__isnull=False,
    #          then=Concat(Value('CGE'),
    #                      Value(''),
    #                      output_field=CamposEnMayusculas())),
    #     When(reserva_cge_persona__isnull=False,
    #          then=Concat(Value('CGE'),
    #                      Value(''),
    #                      output_field=CamposEnMayusculas())),
    #     default=F('distrito__distrito'))).annotate(subdis=Case(
    #     When(sub_personal__isnull=False,
    #          then=Concat(F('sub_personal__subdistrito__subdistrito'),
    #                      Value(''),
    #                      output_field=CamposEnMayusculas())),
    #     When(res_sub_personal__isnull=False,
    #          then=Concat(F('res_sub_personal__subdistrito__subdistrito'),
    #                      Value(''),
    #                      output_field=CamposEnMayusculas())),
    #     default=Value('--')))
    if queryset:
        control = 1
        nombre_archvivo = 'Personal.xls'
        dataset = persona_recurso.export(queryset)
        response = HttpResponse(dataset.xls,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response
    else:
        control = 0
        response = HttpResponse()
        # Agregar los parámetros como encabezados
        response['X-control'] = control
        return response

class exportarResumenPersonalJerarquiaTipo(View):
    def get(self, request):

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        bold.set_font_color('white')
        bold.set_font_name('Times New Roman')
        bold.set_align('center')
        bold.set_align('vcenter')
        bold.set_fg_color('#205C90')
        bold.set_border(1)
        bold.set_text_wrap()
        bold2 = workbook.add_format({'bold': 1})
        bold2.set_font_name('Times New Roman')
        bold2.set_align('left')
        bold2.set_fg_color('#C5D9F1')
        bold2.set_border(1)
        bold2.set_text_wrap()
        total = workbook.add_format({'bold': 1})
        total.set_font_name('Times New Roman')
        total.set_align('center')
        total.set_fg_color('#E6B8B7')
        total.set_border(1)
        total.set_text_wrap()
        porcentaje = workbook.add_format({'bold': 1})
        porcentaje.set_font_name('Times New Roman')
        porcentaje.set_align('center')
        porcentaje.set_fg_color('#EBF1DE')
        porcentaje.set_border(1)
        porcentaje.set_text_wrap()

        # Get some data to write to the spreadsheet.
        data = get_simple_table_data()

        # Write some test data.
        for row_num, columns in enumerate(data):
            for col_num, cell_data in enumerate(columns):
                if row_num == 0:
                    worksheet.write(row_num, col_num, cell_data, bold)
                elif col_num == 0 and row_num != 14 and row_num != 15 and col_num != 9 and col_num != 10:
                    worksheet.write(row_num, col_num, cell_data, bold2)
                elif row_num == 14:
                    worksheet.write(row_num, col_num, cell_data, total)
                elif row_num == 15:
                    worksheet.write(row_num, col_num, cell_data, porcentaje)
                elif col_num == 9:
                    worksheet.write(row_num, col_num, cell_data, total)
                elif col_num == 10:
                    worksheet.write(row_num, col_num, cell_data, porcentaje)
                else:
                    worksheet.write(row_num, col_num, cell_data)
        # worksheet.write_dynamic_array_formula('B13:H13', '=B2:B12+C2:C12)')
        # worksheet.write_formula('B13', '=SUM(B2:B12)')
        # Close the workbook before sending the data.
        worksheet.set_column(1, 9, 25)
        worksheet.set_column(9, 9, 10)
        leftcol = workbook.add_format()
        leftcol.set_align('left')
        worksheet.set_column(0, 0, 35, leftcol)
        worksheet.set_column(10, 10, 15, leftcol)
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = 'resumen_pers_jearaquia.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

class exportarResumenPersonalJerarquiaTipoPdf(View):
    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    def get(self, request, *args, **kwargs):

        data = get_simple_table_data()
        datos = []
        if data:
            for row_num, columns in enumerate(data):
                if row_num > 1:
                    datos.append(columns)
            template = loader.get_template(
                'AppElecciones/personas/resumen-por-jerarquiaytipo-pdf.html')
            context = {
                'data': datos,
                'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')

            # Si lo activamos se descarga el archivo
            # response['Content-Disposition'] = 'attachment; filename="Movimientos.pdf"'

            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            if pisa_status.err:
                return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')
            return response
        messages.warning(request, "No hay registros para exportar")
        return redirect("reportes")