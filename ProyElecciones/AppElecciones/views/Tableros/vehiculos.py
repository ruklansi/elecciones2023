from django.views.generic import TemplateView
from AppElecciones.views.Tableros import novedades,telegramas,LED, app_dash_vehiculos,locales,repliegue,despliegue,recepcion_mat_elec,despliegue_pc,repliegue_pc,personal,resumen_general


class TableroVehiculos(TemplateView):
   template_name = 'AppElecciones/Tableros/vehiculos.html'

   def dispatch(self, *args, **kwargs):
       return super(TableroVehiculos, self).dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de vehículos'
       return context

class TableroLocales(TemplateView):
   template_name = 'AppElecciones/Tableros/locales.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Locales'
       return context
class TableroNovedades(TemplateView):
   template_name = 'AppElecciones/Tableros/novedades_sms.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Novedades'
       return context

class TableroRepliegue(TemplateView):
   template_name = 'AppElecciones/Tableros/repliegue.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Repliegue'
       return context

class TableroDespliegue(TemplateView):
   template_name = 'AppElecciones/Tableros/despliegue.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Despliegue'
       return context

class TableroRecepMatElec(TemplateView):
   template_name = 'AppElecciones/Tableros/recepcion_mat_elec.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Recepción Material Electoral'
       return context
   
class TableroDesplieguePC(TemplateView):
   template_name = 'AppElecciones/Tableros/despliegue_pc.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de despliegue puesto comando, gueso y pelotón adelantado'
       return context   

class TableroReplieguePC(TemplateView):
   template_name = 'AppElecciones/Tableros/repliegue_pc.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de repliegue puesto comando, gueso y pelotón adelantado'
       return context 
     
class TableroPersonal(TemplateView):
   template_name = 'AppElecciones/Tableros/personal.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de distribución de personal'
       return context  
   
     
class TableroResumenGeneral(TemplateView):
   template_name = 'AppElecciones/Tableros/resumen_general.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Resumen General'
       return context     
   
class TableroNovedades(TemplateView):
   template_name = 'AppElecciones/Tableros/novedades.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Novedades'
       return context        
   
class TableroLED(TemplateView):
   template_name = 'AppElecciones/Tableros/led.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de LED'
       return context   
   
class TableroTelegramas(TemplateView):
   template_name = 'AppElecciones/Tableros/telegramas.html'

   def dispatch(self, *args, **kwargs):
       return super().dispatch(*args, **kwargs)

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['titulo'] = 'Tablero de Telegramas'
       return context      