from django.conf import settings
import geopandas
import plotly.express as px 
from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from django.conf import settings


from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

HOST = settings.DATABASES['default']['HOST']
NAME= settings.DATABASES['default']['NAME']
PASS=settings.DATABASES['default']['PASSWORD']
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)

sql='select * from locales_validados'
df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
df['lon'] = df['ubicacion'].x
df['lat'] = df['ubicacion'].y
app = DjangoDash(name='Locales',  external_stylesheets=[dbc.themes.DARKLY])
import shapely
sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
def crear_mapa(datos_mapa, zoom, lat_cen=None, lon_cen=None):
    px.set_mapbox_access_token('pk.eyJ1IjoiemFsaXRvYXIiLCJhIjoiYVJFNTlfbyJ9.mPX8qTsRUGOOETl0CtA-Pg')
    punto = shapely.Point(-59.5236, -51.7963)  # Longitud, Latitud (centro del círculo)
    gdf_circulo = geopandas.GeoDataFrame(geometry=[punto], crs="EPSG:4326")
    # Proyectar a UTM para un buffer preciso en metros
    gdf_circulo = gdf_circulo.to_crs("EPSG:32721")  # UTM zona 21S (ajusta según la ubicación)
    gdf_circulo['geometry'] = gdf_circulo.geometry.buffer(280000)  # Buffer de 10 km
    gdf_circulo = gdf_circulo.to_crs("EPSG:4326")  # Volver a WGS84 para Mapbox
    if lat_cen and lon_cen:
        center = dict(lat=lat_cen, lon=lon_cen)
    else:
        center = dict()
    mapa = px.scatter_mapbox(data_frame=datos_mapa, lat="lat", lon="lon",
                             hover_name="nombre",
                             color='validado',
                             color_continuous_scale=[[0, 'red'], [0.5, 'orange'], [1.0, 'green']],
                             range_color=[0, 1],
                           
                             hover_data=dict(distrito=True,
                                             subdistrito=True,
                                             nombre=True,
                                             seccion=True,
                                             circuito=True,
                                             direccion=True,
                                             grado_jefe_local=True,
                                             nombre_jefe_local=True,
                                             apellido_jefe_local=True,
                                             telefono_jefe_local=True,
                                             castidad_auxiliares=True,
                                             cant_efectivos=True,
                                             lat=False,
                                             lon=False,
                                             ),
                              zoom=zoom, height=700, center=center,
                              
                             )
    mapa.update_traces(

        marker={'size': 13},
        hovertemplate="<br>".join(["<b>Nombre:</b> %{customdata[2]}",
                                                  "<b>Distrito:</b> %{customdata[0]}",
                                                  "<b>Subdistrito:</b> %{customdata[1]}",
                                                  "<b>Sección:</b> %{customdata[3]}",
                                                  "<b>Circuito:</b> %{customdata[4]}",
                                                  "<b>Dirección:</b> %{customdata[5]}",
                                                  "<b>J loc:</b> %{customdata[6]} %{customdata[8]} %{customdata[7]}",
                                                  "<b>Tel J Loc:</b> %{customdata[9]}",
                                                  "<b>Auxiliares:</b> %{customdata[10]}",
                                                  "<b>Seg Ext:</b> %{customdata[11]}",

                                                  ]), )
    mapa.update_layout(hoverlabel_bgcolor='#ffffff',coloraxis_showscale=False,

                       mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
                       )
    mapa.update_geos(fitbounds='locations')
    mapa.add_choroplethmapbox(
        geojson=gdf_circulo.__geo_interface__,
        locations=gdf_circulo.index,
        z=[1] * len(gdf_circulo),
        colorscale=[[0, 'rgba(170, 211, 223, 1)'], [1, 'rgba(170, 211, 223, 1)']],
        showscale=False,
          hoverinfo='text',  # Activar etiqueta al pasar el cursor
         text=['Islas Malvinas'] * len(gdf_poligono),  # Etiqueta para el polígono
        marker_line_color='rgba(170, 211, 223, 0.6)',  # Borde igual al fondo
        marker_line_width=1,
        
    )

# Agregar la capa del polígono (encima del círculo, debajo del mapa coroplético principal)
    mapa.add_choroplethmapbox(
        geojson=poligono_geojson,
        locations=gdf_poligono.index,
        z=[1] * len(gdf_poligono),
        colorscale=[[0, 'rgb(242, 239, 233, 0.6)'], [1, 'rgb(242, 239, 233, 0.6)']],
        showscale=False,
        hoverinfo='text',  # Activar etiqueta al pasar el cursor
         text=['Islas Malvinas'] * len(gdf_poligono),  # Etiqueta para el polígono
    )
    return mapa


df1 = df.drop(columns=['ubicacion', ])
data_table = dash_table.DataTable(df1.to_dict('records'),
                                  [{"name": i, "id": i.lower()} for i in ['Nombre',]],
                                  id='datatable',
                                  editable=False,
                                  filter_action="native",
                                  sort_action="native",
                                  sort_mode="multi",
                                  selected_columns=[],
                                  selected_rows=[],

                                  page_action="native",
                                  page_current=0,
                                  page_size=20,
                                  style_cell={'textAlign': 'center'},
                                  style_data={
                                      'color': 'black',
                                      'backgroundColor': 'white'

                                  },
                                  style_data_conditional=[
                                      {
                                          "if": {"state": "active"},  # 'active' | 'selected'
                                          "backgroundColor": "rgb(102, 102, 102)",
                                          "border": "3px solid white",
                                          "color": "white",
                                      },
                                      {
                                          'if': {
                                              'state': 'selected'  # 'active' | 'selected'
                                          },
                                          'backgroundColor': 'rgba(0, 116, 217, 0.3)'
                                      },
                                  ],
                                  style_header={
                                      'backgroundColor': 'rgb(210, 210, 210)',
                                      'color': 'black',
                                      'fontWeight': 'bold'
                                  }

                                  )
df1 = df.drop(columns=['ubicacion', ])
datos_tabla = df1.to_dict('records')
datos_mapa = df
option_sub = [{}]
zoom = 3

todos = [{"label": 'TODOS', "value": 'TODOS'}]


def crear_indicadores(df_data,tipo):
    data = df_data.drop(columns=['ubicacion', ])
    
    if tipo=='total':
        valor=data.shape[0]
        titulo='LOCALES'
        color='rgb(255, 194, 102)'
    if tipo=='mesas':
        valor=data['cantidad_mesas'].sum() 
        titulo='MESAS'   
        color='rgb(255, 194, 102)'
    if tipo=='validados':
        valor=data[data['validado']==1].shape[0]
        titulo='VALIDADOS'
        color='rgb(0, 230, 0)'
    if tipo=='no_validados':
        valor=data[data['validado']==0].shape[0]
        titulo='NO VALIDADOS' 
        color='rgb(255, 71, 26)' 
    if tipo=='seg_int':
        valor=data[data['jefe_local_id'].notnull()].shape[0]
        titulo='CON SEG INT'
        color='rgb(0, 230, 0)'
    if tipo=='no_seg_int':
        valor=data[data['jefe_local_id'].isnull()].shape[0]
        titulo='SIN SEG INT' 
        color='rgb(255, 71, 26)'   
    if tipo=='seg_ext':
        valor=data[data['cant_efectivos']!=0].shape[0]
        titulo='CON SEG EXT'
        color='rgb(0, 230, 0)'
    if tipo=='no_seg_ext':
        valor=data[data['cant_efectivos']==0].shape[0]
        titulo='SIN SEG EXT' 
        color='rgb(255, 71, 26)'       
    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size": 30}, 'valueformat': ',.0f', },
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}))

    graf_total.update_layout(autosize=True, height=180, title_text=titulo, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)',
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color=color

        ))
  
    return graf_total


app.layout = html.Div(
    [
        dbc.Row([html.H1('LOCALES DE VOTACIÓN', style={'textAlign': 'center', 'background-color': '#267300'})],
                className="g-0"),

        dbc.Row([dbc.Col([dbc.Select(id="selec_distrito", options=todos + [{"label": x, "value": x} for x in df[
            'distrito'].drop_duplicates().sort_values()], placeholder='DISTRITO')]),
                 dbc.Col([dbc.Select(id="selec_subdistrito", placeholder='SUBDISTRITO')]),
                 dbc.Col([dbc.Select(id="selec_seccion", placeholder='SECCION')]),
                 dbc.Col([dbc.Select(id="selec_circuito", placeholder='CIRCUITO')])

                 ], style={'marginBottom' : '10px',}),

        dbc.Row([dbc.Col([dbc.Select(id="estado", options=todos + [{"label": 'VALIDADO', "value": '1'} ,{"label": 'NO VALIDADO', "value": '0'}], placeholder='ESTADO')]),

                 ], style={'marginBottom' : '10px',}),
dbc.Row([
        dbc.Col([
            dbc.Row([dcc.Loading(id="ls-loading-2", children=[dcc.Graph(id='graf_total', figure=crear_indicadores(df,'total'))],type="default")]),
            dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='graf_validados', figure=crear_indicadores(df,'validados'))],type="default")]),
            dbc.Row([dcc.Loading(id="ls-loading-7", children=[dcc.Graph(id='seg_int', figure=crear_indicadores(df,'seg_int'))],type="default")]),
            dbc.Row([dcc.Loading(id="ls-loading-8", children=[dcc.Graph(id='seg_ext', figure=crear_indicadores(df,'seg_ext'))],type="default")]),
        ],md=2),
        dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-1", children=[dcc.Graph(id='graf_mesas', figure=crear_indicadores(df,'mesas'))],type="default")]),
                dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='graf_no_val', figure=crear_indicadores(df,'no_validados'))],type="default")]),
                dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='no_seg_int', figure=crear_indicadores(df,'no_seg_int'))],type="default")]),
                dbc.Row([dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='no_seg_ext', figure=crear_indicadores(df,'no_seg_ext'))],type="default")]),
        ],md=2),
        dbc.Col([

            dbc.Row(dcc.Loading(id="ls-loading-0", children=[dcc.Graph(id='mapa', figure=crear_mapa(datos_mapa, zoom))], type="default")),
            
        ],md=5),

        dbc.Col(dcc.Loading(id="ls-loading-10", children=[data_table], type="default"),md=3),
]) ,
dcc.Interval(
                id='interval-component',
                interval=60 * 2000,  # in milliseconds
                n_intervals=0
            ),
           
 dcc.Interval(
                id='interval-component1',
                interval=60 * 2000,  # in milliseconds
                n_intervals=0
            )

    ]
)


@app.callback(
    Output('mapa', 'figure', ), Output('selec_subdistrito', 'options'),
    [Input('selec_distrito', 'value'), Input('selec_subdistrito', 'value'),
     Input('selec_seccion', 'value'),
     Input('selec_circuito', 'value'), Input('datatable', 'active_cell'), Input('datatable', "derived_virtual_data"),Input('interval-component', 'n_intervals')], [State('datatable', 'data')],
    prevent_initial_call=True
)
def actualizar_mapa(distrito, subdistrito, seccion, circuito, data, nueva_tabla,intervalo,tabla,**kwargs):
    datos_mapa = df
    option_sub = [{"label": 'TODOS', "value": 'TODOS'}]
    zoom = 3
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_sub = todos + [{"label": x, "value": x} for x in
                              datos_mapa['subdistrito'].drop_duplicates().sort_values()]
        zoom = 5
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        zoom = 7
    if seccion and seccion != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['seccion'] == seccion]
        zoom = 9
    if circuito and circuito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['circuito'] == circuito]
        zoom = 12
    if nueva_tabla:
        a=[x['id'] for x in nueva_tabla]    
        datos_mapa=datos_mapa[datos_mapa['id'].isin(a)]
    if data:
       
        if nueva_tabla:
            tabla=nueva_tabla
        lat_cen = tabla[data['row']]['lat']
        lon_cen = tabla[data['row']]['lon']
        zoom = 18
        return crear_mapa(df, zoom, lat_cen, lon_cen), option_sub

    return crear_mapa(datos_mapa, zoom), option_sub


@app.callback(
    Output('selec_seccion', 'options'),
    [Input('selec_subdistrito', 'value'), Input('selec_distrito', 'value')],State('selec_seccion', 'value'), prevent_initial_call=True
)
def actualizar_sec(subdistrito, distrito,seccion,**kwargs):
    option_sec=[{"label": 'TODOS', "value": 'TODOS'},{"label": seccion, "value": seccion}]
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_sec = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        option_sec = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    return option_sec


@app.callback(
    Output('selec_circuito', 'options'),
    [Input('selec_subdistrito', 'value'), Input('selec_distrito', 'value'), Input('selec_seccion', 'value')],State('selec_circuito', 'value'),
    prevent_initial_call=True
)
def actualizar_cir(subdistrito, distrito, seccion,circuito,**kwargs):
    option_cir=[{"label": 'TODOS', "value": 'TODOS'},{"label": circuito, "value": circuito}]
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if seccion and seccion != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['seccion'] == seccion]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['circuito'].drop_duplicates().sort_values()]

    return option_cir


@app.callback(
    Output('datatable', 'data'), Output('datatable', "active_cell"), Output('datatable', 'selected_cells'),
    Output('graf_total', 'figure'), Output('graf_mesas', 'figure'),Output('seg_int', 'figure'),
    Output('seg_ext', 'figure'),Output('graf_validados', 'figure'),Output('graf_no_val', 'figure'),
    Output('no_seg_int', 'figure'),Output('no_seg_ext', 'figure'),
    [Input('selec_distrito', 'value'), Input('selec_subdistrito', 'value'), Input('selec_seccion', 'value'),
     Input('selec_circuito', 'value'),Input('interval-component1', 'n_intervals'),Input('estado', 'value')
     ], prevent_initial_call=True
)
def actualizar_tabla(distrito, subdistrito, seccion, circuito,intervalo,estado,**kwargs):
    datos=df
    datos_tabla=df.drop(columns=['ubicacion', ]).to_dict('records')
    if distrito and distrito != 'TODOS':
        datos = df[df['distrito'] == distrito]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if subdistrito and subdistrito != 'TODOS':
        datos = datos[datos['subdistrito'] == subdistrito]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if seccion and seccion != 'TODOS':
        datos = datos[datos['seccion'] == seccion]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if circuito and circuito != 'TODOS':
        datos = datos[datos['circuito'] == circuito]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if estado and estado!='TODOS' :
        datos = datos[datos['validado'] == int(estado)]
        df1 = datos.drop(columns=['ubicacion', ])  
        datos_tabla = df1.to_dict('records')
    return datos_tabla, None, [], crear_indicadores(datos,'total'),crear_indicadores(datos,'mesas'),crear_indicadores(datos,'seg_int'),crear_indicadores(datos,'seg_ext'),crear_indicadores(datos,'validados'),crear_indicadores(datos,'no_validados'),crear_indicadores(datos,'no_seg_int'),crear_indicadores(datos,'no_seg_ext')
