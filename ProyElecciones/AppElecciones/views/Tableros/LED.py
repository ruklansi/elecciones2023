import os
from django.conf import settings
import geopandas
import pandas as pd
#from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import shapely
from django_plotly_dash import DjangoDash
from shapely.geometry import Point
import textwrap
HOST ='localhost' #settings.DATABASES['default']['HOST']
NAME= 'elecciones23'#settings.DATABASES['default']['NAME']
PASS='4rcg1s2024'#settings.DATABASES['default']['PASSWORD']
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)


sql="""
 SELECT * FROM public.lsitado_led
 """
df = geopandas.GeoDataFrame.from_postgis(sql, conn,geom_col='ubicacion')
df.to_crs(epsg=4326, inplace=True)
distritos=df.drop_duplicates('distrito')['distrito'].sort_values()

sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
def estado_urnas(distrito):
    if distrito and distrito != 'TODOS':
        sql_mesas="""
        SELECT * FROM public.mesas_estados where distrito='"""+distrito+"""'"""
    else:
        sql_mesas="""
        SELECT * FROM public.mesas_estados """   
    df_mesas= pd.read_sql(sql_mesas, conn)
    df_mesas=df_mesas.drop(columns=['punto', ])
    urnas=len(df_mesas)-df_mesas['entrego_correo'].sum()
    urnas_en_correo=df_mesas['entrego_correo'].sum()-df_mesas['entrego_urna_en_led'].sum()

    urnas_en_led=df_mesas['entrego_urna_en_led'].sum()
    return [str(urnas),str(urnas_en_correo),str(urnas_en_led)]

def graf_lugares(df):
    # Contar la cantidad de mesas por estado
    estado_counts = df['tipo'].value_counts()

    # Crear un DataFrame para el gráfico de torta
    df_pie = pd.DataFrame({
        'Tipo': estado_counts.index,
        'Cantidad': estado_counts.values
    })

    # Crear el gráfico de torta con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Tipo', title='Tipo',hole=.4,
                 )

    # Personalizar el gráfico
    fig.update_traces(textposition='inside', textinfo='percent+label',marker=dict(
            colors=["#b5c717", "#FF1E00", "#FF9900"]))

    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=500,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=10
                               ,legend=dict(orientation="h", ))
    # Mostrar el gráfico
    
    return fig

def graf_personal(df):
    # Contar la cantidad de mesas por estado
    df_pie = df.groupby('fuerza')['cant_personal'].sum().reset_index()
    df_pie.columns = ['Fuerza', 'Cantidad']

    # Crear un DataFrame para el gráfico de torta
    # df_pie = pd.DataFrame({
    #     'Fuerza': estado_counts.index,
    #     'Cantidad': estado_counts.values
    # })

    # Crear el gráfico de torta con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Fuerza', title='Distribucion por fuerza',hole=.4,
                 )

    # Personalizar el gráfico
    fig.update_traces(textposition='inside', textinfo='percent+label',marker=dict(
            colors=["#b5c717", "#FF1E00", "#FF9900"]))

    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=500,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=10
                               ,legend=dict(orientation="h", ))
    # Mostrar el gráfico
    
    return fig

def get_points_center_and_zoom(df,):
    df['lon'] = df['ubicacion'].x
    df['lat'] = df['ubicacion'].y
    # Calcular centroide (promedio de lat y lon)
    lat_cen = df['lat'].mean()
    lon_cen = df['lon'].mean()

    # Calcular extensión para determinar zoom
    if len(df) > 1:
        max_diff = max(df['lat'].max() - df['lat'].min(), df['lon'].max() - df['lon'].min())
        if max_diff > 5:
            zoom = 3  # Áreas grandes
        elif max_diff > 2:
            zoom = 8  # Áreas medianas
        elif max_diff > 0.5:
            zoom = 10  # Áreas pequeñas
        else:
            zoom = 11  # Áreas muy pequeñas o puntos cercanos
    else:
        zoom = 12  # Zoom fijo para un solo punto

    return zoom,lat_cen, lon_cen, 

sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
def crear_mapa(df, zoom, lat_cen=None, lon_cen=None):
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
    df['lon'] = df['ubicacion'].x
    df['lat'] = df['ubicacion'].y
    if lat_cen and lon_cen:
        center = dict(lat=lat_cen, lon=lon_cen)
    else:
        center = dict(lat=-34.603722,lon=-58.381592)  # Default center (Buenos Aires)
    df['detalle2'] = ['<br>'.join(textwrap.wrap(x, width=50)) for x in df['obs']]   
    
    mapa = px.scatter_mapbox(data_frame=df, lat="lat", lon="lon",
                             hover_name="tipo",
                             color='tipo',
                             category_orders={'gender': ['Media', 'Alta', 'Critica']},
                        color_discrete_sequence=["#656d1c", "#8b5f26","#830b0b" ],
                           
                             hover_data=dict(distrito=True,
                                             tipo=True,
                                             fecha_fin=True,
                                             fecha_inicio=True,
                                             obs=True,
                                             fuerza=True,
                                             direccion=True,
                                             cant_personal=True,
                                             lat=False,
                                             lon=False,
                                             ),
                              zoom=zoom, height=800, center=center,
                              
                             )
    mapa.update_traces(

        marker={'size': 13},
        hovertemplate="<br>".join(["<b>Tipo:</b> %{customdata[1]}","<b>Fecha Inicio:</b> %{customdata[2]}",
                                                  "<b>Fecha Fin:</b> %{customdata[3]}",
                                                  "<b>Distrito:</b> %{customdata[0]}",
                                                  "<b>Fuerza:</b> %{customdata[5]}",
                                                  "<b>Cant Pers:</b> %{customdata[7]}",
                                                  "<b>Obs:</b> %{customdata[4]}",
                                                  "<b>Dirección:</b> %{customdata[6]}",
                                                  
                                                  

                                                  ]), )
    mapa.update_layout(legend_title_text='Tipos LED',hoverlabel_bgcolor="#FFFFFF",coloraxis_showscale=False,showlegend=True,font_size=11,
                       legend=dict( orientation="h", yanchor="top",  y=0.99, xanchor="left",  x=0.01),

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


def crear_indicadores(data,accion):
    #data = df_data.drop(columns=['geom', ])
    color='#ffffff'
    if accion=='lugares':
        valor=len(data)
        titulo='LUGARES CON CUSTODIA'
    if accion=='personal':
        valor=data['cant_personal'].sum()
        titulo='CANTIDAD DE PERSONAL'   
         

    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size": 80}, 'valueformat': 'f'},
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}),
        
        )
    

    graf_total.update_layout(autosize=True, height=245, title_text=titulo,legend_title_font_size=80, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)' ,
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color=color

        ))
    return graf_total



app = DjangoDash(name='led', external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('ESTADO DE LUGARES DE ESCUTINIO DEFINITIVO', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in distritos],placeholder='DISTRITO' )]),
            dbc.Row([dbc.Col([html.H3('URNAS EN LOCAL', style={'textAlign': 'center', 'background-color': '#ff0000'})]),
                     dbc.Col([html.H3(id='urnas', children=[estado_urnas('TODOS')[0]])]),
                     dbc.Col([html.H3('EN CORREO', style={'textAlign': 'center', 'background-color': '#e6e600'})]),
                     dbc.Col([html.H3(id='urnas_correo', children=[estado_urnas('TODOS')[1]])]),
                     dbc.Col([html.H3('URNAS EN LED', style={'textAlign': 'center', 'background-color': '#267300'})]),
                     dbc.Col([html.H3(id='urnas_led', children=[estado_urnas('TODOS')[2]])])
                                                
        ]),                    
            dbc.Row([dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-2", children=[dcc.Graph(id='lugares', figure=crear_indicadores(df,'lugares'))], type="default")]),
                              
                              dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='graf_lugares',figure=graf_lugares(df) )], type="default")])
                              ], style={"height": "100%", }
                             , md=3),
                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='mapa', figure=crear_mapa(df,3))], type="default")])], style={"height": "100%", }, md=5),

                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='personal',figure=crear_indicadores(df,'personal') )], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='graf_personal',figure=graf_personal(df) )], type="default")]),
                              ],style={"height": "100%", },md=4),
                     ], className="g-0", ),
             dcc.Interval(
                id='interval-component',
                interval=120 * 1000,  # in milliseconds
                n_intervals=0
            )
        ]
    )

@app.callback([Output('mapa', 'figure'),
               Output('lugares', 'figure'),
               Output('graf_lugares', 'figure'),
               Output('personal', 'figure'),
               Output('graf_personal', 'figure'),
               Output('urnas','children'),
               Output('urnas_correo','children'),
               Output('urnas_led','children')
               ],Input('selec_distrito', 'value'),Input('interval-component', 'n_intervals'),prevent_initial_call=True)
def actualizar_mapa(distrito,intervalo,**kwargs):
    
    
    lat_cen = None
    lon_cen = None
    zoom = 3
    
    if distrito and distrito != 'TODOS':
        sql=""" SELECT * FROM public.lsitado_led  where distrito='"""+distrito+"""'"""
        df = geopandas.GeoDataFrame.from_postgis(sql, conn,geom_col='ubicacion')
        df.to_crs(epsg=4326, inplace=True)
        esta_urnas=estado_urnas(distrito)
        
        zoom, lat_cen, lon_cen = get_points_center_and_zoom(df)    
    else:
        sql=""" SELECT * FROM public.lsitado_led """
        df = geopandas.GeoDataFrame.from_postgis(sql, conn,geom_col='ubicacion')
        df.to_crs(epsg=4326, inplace=True)
        zoom, lat_cen, lon_cen = get_points_center_and_zoom(df)  
        esta_urnas=estado_urnas('TODOS') 
    return crear_mapa(df,zoom,lat_cen, lon_cen),crear_indicadores(df,'lugares'),graf_lugares(df),crear_indicadores(df,'personal'),graf_personal(df,),esta_urnas[0],esta_urnas[1],esta_urnas[2]

#@app.callback()



