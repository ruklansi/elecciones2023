import io
import os

import xlsxwriter

from django.db.models import Case, When, Value,F,Q, OuterRef, Count, Subquery, Sum, IntegerField, BooleanField, Func

from django.http import HttpResponse

from django.views import View

from django.db import connection
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

from AppElecciones.funciones_comunes import organizacion_del_usuario


def get_simple_table_data():
    id_distrito = ''
    org = organizacion_del_usuario()
    if org['org'] == 'distrito':
        distrito = org['instancia']
        id_distrito = distrito.id
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM public.datos_generales")
    if id_distrito:
        return [list(x) for x in cursor.fetchall() if x[0]==id_distrito]
    else:
        return [list(x) for x in cursor.fetchall()]
class exportarResumenGeneral(View):
    def get(self, request):
        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        
        worksheet = workbook.add_worksheet('RESUMEN')

        dic = {'bold': 1, 'font_color': 'black', 'font_name': 'Times New Roman', 'align': 'vcenter','align':'center',
                 'fg_color': 'white', 'border': 1, 'text_wrap': 1}
        tit= workbook.add_format(dic)
        worksheet.merge_range(2,2,1,5,'CANTIDAD DE LOCALES',tit)
        worksheet.merge_range(2, 6, 1, 8, 'CANTIDAD DE MESAS', tit)
        worksheet.merge_range(2, 9, 1, 10, 'UUPP', tit)
        worksheet.merge_range(2, 11, 1, 12, 'CENTRO DE TRANSMISION DE DATOS', tit)
        worksheet.merge_range(2, 14, 1, 16, 'CANTIDAD TOTAL DE', tit)
        dic_f={'bold': 1,'font_color':'black','font_name':'Times New Roman','align':'vcenter','align':'center','fg_color':'white','border':1,'text_wrap':1}
        bold = workbook.add_format(dic_f)
        dic_f['fg_color'] ='#cce6ff'
        bold2 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 17, 1, 24, 'PERSONAL CUSTODIA DENTRO DEL LOCAL', bold2)
        [worksheet.write(3,y+17,x,bold2) for y ,x in enumerate(['EA','ARA','FAA','GN','PNA','PFA','PSA','SPF'])]
        dic_f['fg_color'] = '#ffccb3'
        bold3 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 25, 1, 31, 'PERSONAL SEGURIDAD EXTERIOR LOCAL', bold3)
        [worksheet.write(3, y + 25, x, bold3) for y, x in
         enumerate(['GN', 'PNA', 'PFA', 'PSA', 'SPF','SPP','PP'])]
        dic_f['fg_color'] = '#ace600'
        bold4 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 32, 1, 41, 'EEMM - Planas Mayores - Pto Cdo(DIS - SUB - SEC - CIR)', bold4)
        [worksheet.write(3, y + 32, x, bold4) for y, x in
         enumerate(['EA','FAA','ARA','GN','PNA','PFA','PSA','SPF','SPP','PP'])]
        dic_f['fg_color'] = '#ecb3ff'
        bold5 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 42, 1, 51, 'RESERVAS', bold5)
        [worksheet.write(3, y + 42, x, bold5) for y, x in
         enumerate(['EA', 'ARA', 'FAA', 'GN', 'PNA', 'PFA', 'PSA', 'SPF', 'SPP', 'PP'])]
        dic_f['fg_color'] = '#ffcc80'
        bold6 = workbook.add_format(dic_f)
       # worksheet.merge_range(1, 51, 1, 60, 'CUSTODIA LAME/CGD/DEPOSITOS/LED', bold6)
        dic_f['fg_color'] = '#79d279'
        bold7 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 52, 1, 61, 'CUSTODIA LAME/CGD/DEPOSITOS/LED', bold7)
        [worksheet.write(3, y + 52, x, bold7) for y, x in
         enumerate(['EA', 'ARA', 'FAA', 'GN', 'PNA', 'PFA', 'PSA', 'SPF', 'SPP', 'PP','Conductores'])]
        dic_f['fg_color'] = '#ffff1a'
        bold8 = workbook.add_format(dic_f)
        worksheet.merge_range(1, 63, 1, 74, 'TOTAL', bold8)
        [worksheet.write(3, y + 63, x, bold8) for y, x in
         enumerate(['EA', 'ARA', 'FAA','Total', 'GN', 'PNA', 'PFA', 'PSA', 'SPF','Total', 'SPP', 'PP','Total'])]
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
        datos_distritos = get_simple_table_data()
        fila2=['Nro', 'Distrito', 'Nacional/Mixtas', 'Extrangeras', 'Sin mesa','Total',
          'Mixtas', 'Extrageros', 'Total', 'Cantidad UUPP', 'Cantidad SACAS',
          'Locales', 'SED', 'Votos', 'Sub Elect', 'Seciones', 'Circuitos',
          'FFAA', 'FFSS',
          'FFSS', 'FFPPPP',
          'FFAA', 'FFSS', 'FFPPPP',
          'FFAA', 'FFSS', 'FFPPPP',
          'FFAA', 'FFSS', 'FFPPPP',

         ]
        col_num=0
        row_num=2
        for data in fila2:
            if col_num>=17 and col_num<=24 :
                f=bold2
            elif col_num>=25 and col_num<=31:
                f = bold3
            elif col_num>=32 and col_num<=41:
                f = bold4
            elif col_num >= 42 and col_num <= 51:
                f = bold5
            elif col_num >= 52 and col_num <= 61:
                f = bold7
            elif col_num >= 62 and col_num <= 71:
                f = bold7
            else:
                f=bold
            if data=='FFAA':
                worksheet.merge_range(row_num,col_num,row_num,col_num+2,data,f)
                col_num+=3
            elif data == 'FFSS':
                worksheet.merge_range(row_num, col_num, row_num, col_num + 4, data, f)
                col_num+=5
            elif data == 'FFPPPP':
                worksheet.merge_range(row_num, col_num, row_num, col_num + 1, data, f)
                col_num+=2
            else:
                worksheet.write(3,col_num,data,f)
                col_num+=1
        col_num += 1
        worksheet.merge_range(row_num, col_num, row_num, col_num + 3, 'FFAA', bold8)
        col_num += 4
        worksheet.merge_range(row_num, col_num, row_num, col_num + 5, 'FFSS', bold8)
        col_num += 6
        worksheet.merge_range(row_num, col_num, row_num, col_num + 2, 'FFPPPP', bold8)
        col_num += 3
        row_num+=1
        for d in datos_distritos:
            row_num+=1
            worksheet.write_row(row_num,0,d)
        worksheet.merge_range(2, 76, 2, 80, 'OFICIALES', tit)
        worksheet.merge_range(1, 76, 1, 86, 'CANTIDAD DE VEHICULOS', tit)
        worksheet.merge_range(2, 81, 2, 86, 'CONTRATADOS', tit)
        [worksheet.write(3, y + 76, x, tit) for y, x in
         enumerate(['Camión', 'Auto', 'Colectivo', 'Moto', 'Mula', 'Camioneta', 'Colectivo', 'Camioneta', 'Auto', 'Heli', 'Moto'])]
        #worksheet.set_column(1, 9, 25)
        #worksheet.set_column(9, 9, 10)
        leftcol = workbook.add_format()
        leftcol.set_align('left')
        for col_num in range(2,87):
            if col_num>=17 and col_num<=24 :
                f=bold2
            elif col_num>=25 and col_num<=31:
                f = bold3
            elif col_num>=32 and col_num<=41:
                f = bold4
            elif col_num >= 42 and col_num <= 51:
                f = bold5
            elif col_num >= 52 and col_num <= 61:
                f = bold7
            elif col_num >= 62 and col_num <= 75:
                f = bold8
            else:
                f=bold
            worksheet.write_formula(xl_rowcol_to_cell(28,col_num), '=SUM('+xl_range(4,col_num,27,col_num)+')',f)
        worksheet.merge_range(28, 0, 28, 1, 'TOTALES', f)
        for col_num in [17,32,42,52,63]:
            if col_num>=17 and col_num<=24 :
                f=bold2
            elif col_num>=25 and col_num<=31:
                f = bold3
            elif col_num>=32 and col_num<=41:
                f = bold4
            elif col_num >= 42 and col_num <= 51:
                f = bold5
            elif col_num >= 52 and col_num <= 61:
                f = bold7
            elif col_num >= 62 and col_num <= 75:
                f = bold8
            else:
                f=bold
            worksheet.merge_range(29, col_num, 29, col_num+2,'=SUM('+xl_range(28,col_num,28,col_num+2)+')' , f)
        for col_num in [20,25,35,45,55,67]:
            if col_num>=17 and col_num<=24 :
                f=bold2
            elif col_num>=25 and col_num<=31:
                f = bold3
            elif col_num>=32 and col_num<=41:
                f = bold4
            elif col_num >= 42 and col_num <= 51:
                f = bold5
            elif col_num >= 52 and col_num <= 61:
                f = bold7
            elif col_num >= 62 and col_num <= 75:
                f = bold8
            else:
                f=bold
            worksheet.merge_range(29, col_num, 29, col_num+4,'=SUM('+xl_range(28,col_num,28,col_num+4)+')' , f)

        for col_num in [30,40,50,60,73]:
            if col_num>=17 and col_num<=24 :
                f=bold2
            elif col_num>=25 and col_num<=31:
                f = bold3
            elif col_num>=32 and col_num<=41:
                f = bold4
            elif col_num >= 42 and col_num <= 51:
                f = bold5
            elif col_num >= 52 and col_num <= 61:
                f = bold7
            elif col_num >= 62 and col_num <= 75:
                f = bold8
            else:
                f=bold
            worksheet.merge_range(29, col_num, 29, col_num+1,'=SUM('+xl_range(28,col_num,28,col_num+1)+')' , f)
        worksheet.merge_range(29, 76, 29, 80,'=SUM('+xl_range(28,76,28,80)+')' , bold)
        worksheet.merge_range(29, 81, 29, 86, '=SUM(' + xl_range(28, 81, 28, 86) + ')', bold)
        worksheet.merge_range(30, 76, 30, 86, '=SUM(' + xl_range(28, 76, 28, 86) + ')', bold)
        worksheet.merge_range(30, 63, 30, 75, '=SUM(' + xl_range(29, 62, 29, 75) + ')', bold8)
        worksheet.merge_range(30, 52, 30, 61, '=SUM(' + xl_range(28, 52, 28, 61) + ')', bold7)
        worksheet.merge_range(30, 42, 30, 51, '=SUM(' + xl_range(28, 42, 28, 51) + ')', bold5)
        worksheet.merge_range(30, 32, 30, 41, '=SUM(' + xl_range(28, 32, 28, 41) + ')', bold4)
        worksheet.merge_range(30, 25, 30, 31, '=SUM(' + xl_range(28, 25, 28, 31) + ')', bold3)
        worksheet.merge_range(30, 17, 30, 24, '=SUM(' + xl_range(28, 17, 28, 24) + ')', bold2)
        worksheet.write(29,62,'=BK29',bold4)
#
        worksheet1 = workbook.add_worksheet('LED_LAME')
        worksheet1.set_column(0, 6, 25)
        worksheet1.merge_range(0, 0, 0, 7, 'LISTADO DE LAME/LED', tit)
        id_distrito = ''
        org = organizacion_del_usuario()
        [worksheet1.write(2, y , x, tit) for y, x in
         enumerate(
             ['Distrito','Tipo','Dirección','Obs','Estado','Cant Personal','Fuerza'])]
        if org['org'] == 'distrito':
            distrito = org['instancia']
            id_distrito = distrito.distrito
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.listado_led_excel")
        if id_distrito:
            leds= [list(x) for x in cursor.fetchall() if x[1] == id_distrito]
        else:
            leds = [list(x) for x in cursor.fetchall()]
            row_num=2
        for l in leds:
            row_num += 1
            worksheet1.write_row(row_num, 0, l)

        workbook.close()

        # Rewind the buffer.
        output.seek(0)
        control = 1
        nombre_archvivo = 'Resumen-general.xlsx'
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment;'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response

